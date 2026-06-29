import json
import os
from functools import wraps

import requests
from django.core.cache import cache

from .error_handler import GeocodingError, RetryConfig, RoutingError, nominatim_breaker, osrm_breaker, with_retry

NOMINATIM_URL = os.environ.get("NOMINATIM_URL", "https://nominatim.openstreetmap.org/search")
OSRM_URL = os.environ.get("OSRM_URL", "https://router.project-osrm.org/route/v1/driving")
USER_AGENT = os.environ.get("API_USER_AGENT", "LogRoute/1.0 (support@logroute.app)")
NOMINATIM_TIMEOUT = int(os.environ.get("NOMINATIM_TIMEOUT", "10"))
OSRM_TIMEOUT = int(os.environ.get("OSRM_TIMEOUT", "30"))
GEOCODE_CACHE_TIMEOUT = int(os.environ.get("GEOCODE_CACHE_TIMEOUT", "86400"))
ROUTE_CACHE_TIMEOUT = int(os.environ.get("ROUTE_CACHE_TIMEOUT", "172800"))
MIN_ROUTE_DISTANCE = 0.1
MAX_ROUTE_DISTANCE = 10000


def _make_cache_key(prefix: str, *args, **kwargs) -> str:
    """Build a deterministic cache key from a prefix and serialised positional/keyword arguments.

    Args:
        prefix: Cache key prefix distinguishing the call type (e.g. 'geocode', 'route').
        *args: Positional arguments to include in the key.
        **kwargs: Keyword arguments to include in the key.

    Returns:
        A string cache key suitable for Django's cache framework.
    """
    import hashlib
    args_key = json.dumps(args, sort_keys=True, default=str)
    kwargs_key = json.dumps(sorted(kwargs.items()), default=str)
    combined = f"{args_key}{kwargs_key}"
    hash_val = hashlib.md5(combined.encode()).hexdigest()
    return f"{prefix}_{hash_val}"


def _validate_route(legs: list[dict]) -> None:
    """Validate that the route has exactly two legs within acceptable distance bounds.

    Args:
        legs: List of leg dicts with 'distance_miles' keys.

    Raises:
        ValueError: If leg count is not 2 or distances are out of range.
    """
    if not legs or len(legs) != 2:
        raise ValueError("Route must have exactly 2 legs (origin->waypoint->destination).")
    leg1_miles = legs[0]["distance_miles"]
    leg2_miles = legs[1]["distance_miles"]
    if leg2_miles < MIN_ROUTE_DISTANCE:
        raise ValueError("Pickup to dropoff distance must be at least 0.1 miles.")
    total_miles = leg1_miles + leg2_miles
    if total_miles > MAX_ROUTE_DISTANCE:
        raise ValueError(f"Route distance {total_miles:.1f} miles exceeds maximum of {MAX_ROUTE_DISTANCE} miles.")


def _cached_api_call(timeout: int, key_prefix: str):
    """Decorator that caches API call results in Django's cache framework.

    Args:
        timeout: Cache timeout in seconds.
        key_prefix: Prefix for the cache key.

    Returns:
        A decorator that wraps a function with caching logic.
    """

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


@_cached_api_call(GEOCODE_CACHE_TIMEOUT, "geocode")
@with_retry(RetryConfig(max_retries=3, base_delay=1.0, max_delay=8.0))
def _geocode_call(address: str) -> tuple[float, float]:
    """Call the Nominatim geocoding API for a single address.

    Args:
        address: Human-readable location string to geocode.

    Returns:
        A (latitude, longitude) tuple.

    Raises:
        ValueError: If the address cannot be geocoded.
    """
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


def geocode(address: str) -> tuple[float, float]:
    """Geocode a location string through the circuit-broken, cached Nominatim call.

    Args:
        address: Location name to geocode.

    Returns:
        A (latitude, longitude) tuple.

    Raises:
        GeocodingError: If the geocoding service fails.
    """
    try:
        return nominatim_breaker.execute(_geocode_call, address)
    except requests.exceptions.Timeout:
        raise
    except (requests.exceptions.RequestException, ValueError) as e:
        raise GeocodingError("Unable to look up location. Please try again.") from e


@_cached_api_call(GEOCODE_CACHE_TIMEOUT, "geocode_search")
@with_retry(RetryConfig(max_retries=3, base_delay=1.0, max_delay=8.0))
def _geocode_search_call(query: str) -> list[dict]:
    """Call the Nominatim search API for autocomplete suggestions.

    Args:
        query: Partial location search string.

    Returns:
        A list of geocoding result dicts with display_name, lat, lon.
    """
    resp = requests.get(
        NOMINATIM_URL,
        params={"q": query, "format": "json", "limit": 5, "countrycodes": "us"},
        headers={"User-Agent": USER_AGENT},
        timeout=NOMINATIM_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def geocode_search(query: str) -> list[dict]:
    """Search locations via the circuit-broken, cached Nominatim search.

    Args:
        query: Partial location string to search.

    Returns:
        A list of location suggestion dicts.

    Raises:
        GeocodingError: If the search service fails.
    """
    try:
        return nominatim_breaker.execute(_geocode_search_call, query)
    except (requests.exceptions.RequestException, ValueError) as e:
        raise GeocodingError("Unable to search locations. Please try again.") from e


@_cached_api_call(ROUTE_CACHE_TIMEOUT, "route")
@with_retry(RetryConfig(max_retries=3, base_delay=1.0, max_delay=8.0))
def _get_route_call(
    origin_ll: tuple[float, float],
    waypoint_ll: tuple[float, float],
    dest_ll: tuple[float, float],
) -> dict:
    """Call the OSRM routing API for a three-point route (origin -> waypoint -> destination).

    Args:
        origin_ll: (lat, lon) of the starting location.
        waypoint_ll: (lat, lon) of the pickup location.
        dest_ll: (lat, lon) of the dropoff location.

    Returns:
        A dict with 'coordinates' (list of [lon, lat]) and 'legs' (list of leg dicts).

    Raises:
        ValueError: If OSRM cannot find a route or validation fails.
    """
    coords_str = f"{origin_ll[1]},{origin_ll[0]};{waypoint_ll[1]},{waypoint_ll[0]};{dest_ll[1]},{dest_ll[0]}"
    resp = requests.get(
        f"{OSRM_URL}/{coords_str}",
        params={"overview": "full", "geometries": "geojson", "steps": "false"},
        timeout=OSRM_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("OSRM could not find a route between the provided locations.")

    route = data["routes"][0]
    legs = []
    for leg in route["legs"]:
        legs.append({
            "distance_miles": leg["distance"] / 1609.344,
            "duration_hours": leg["duration"] / 3600,
        })

    _validate_route(legs)
    coordinates = route["geometry"]["coordinates"]
    return {"coordinates": coordinates, "legs": legs}


def get_route(
    origin_ll: tuple[float, float],
    waypoint_ll: tuple[float, float],
    dest_ll: tuple[float, float],
) -> dict:
    """Fetch a route from OSRM through the circuit breaker with caching and validation.

    Args:
        origin_ll: (lat, lon) of the starting location.
        waypoint_ll: (lat, lon) of the pickup location.
        dest_ll: (lat, lon) of the dropoff location.

    Returns:
        A route dict with 'coordinates' and 'legs'.

    Raises:
        RoutingError: If the routing service fails.
    """
    try:
        return osrm_breaker.execute(_get_route_call, origin_ll, waypoint_ll, dest_ll)
    except requests.exceptions.Timeout:
        raise
    except (requests.exceptions.RequestException, ValueError) as e:
        raise RoutingError("Unable to calculate route. Please try again.") from e
