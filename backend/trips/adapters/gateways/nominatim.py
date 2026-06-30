import json
import os
from functools import wraps

import requests
from django.core.cache import cache

from trips.infrastructure.resilience import RetryConfig, nominatim_breaker, with_retry
from trips.domain.exceptions import GeocodingError

NOMINATIM_URL = os.environ.get("NOMINATIM_URL", "https://nominatim.openstreetmap.org/search")
USER_AGENT = os.environ.get("API_USER_AGENT", "LogRoute/1.0 (support@logroute.app)")
NOMINATIM_TIMEOUT = int(os.environ.get("NOMINATIM_TIMEOUT", "10"))
GEOCODE_CACHE_TIMEOUT = int(os.environ.get("GEOCODE_CACHE_TIMEOUT", "86400"))


def _make_cache_key(prefix: str, *args, **kwargs) -> str:
    import hashlib
    args_key = json.dumps(args, sort_keys=True, default=str)
    kwargs_key = json.dumps(sorted(kwargs.items()), default=str)
    combined = f"{args_key}{kwargs_key}"
    hash_val = hashlib.md5(combined.encode()).hexdigest()
    return f"{prefix}_{hash_val}"


def _cached_api_call(timeout: int, key_prefix: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = _make_cache_key(key_prefix, *args, **kwargs)
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


class NominatimGeocoder:
    def __init__(self):
        self._geocode_cached = _cached_api_call(GEOCODE_CACHE_TIMEOUT, "geocode")(
            _with_retry(self._geocode_call)
        )
        self._search_cached = _cached_api_call(GEOCODE_CACHE_TIMEOUT, "geocode_search")(
            _with_retry(self._geocode_search_call)
        )

    def geocode(self, address: str) -> tuple[float, float]:
        try:
            return nominatim_breaker.execute(self._geocode_cached, address)
        except requests.exceptions.Timeout:
            raise
        except (requests.exceptions.RequestException, ValueError) as e:
            raise GeocodingError("Unable to look up location. Please try again.") from e

    def search(self, query: str) -> list[dict]:
        try:
            return nominatim_breaker.execute(self._search_cached, query)
        except (requests.exceptions.RequestException, ValueError) as e:
            raise GeocodingError("Unable to search locations. Please try again.") from e

    @staticmethod
    def _geocode_call(address: str) -> tuple[float, float]:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=NOMINATIM_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            raise ValueError(f"Could not geocode address: '{address}'. Please check the spelling.")
        return float(data[0]["lat"]), float(data[0]["lon"])

    @staticmethod
    def _geocode_search_call(query: str) -> list[dict]:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 5, "countrycodes": "us"},
            headers={"User-Agent": USER_AGENT},
            timeout=NOMINATIM_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()


def _with_retry(func):
    return with_retry(RetryConfig(max_retries=3, base_delay=1.0, max_delay=8.0))(func)
