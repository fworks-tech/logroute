import json
import os
from functools import wraps

import requests
from django.core.cache import cache

from trips.infrastructure.resilience import RetryConfig, osrm_breaker, with_retry
from trips.domain.exceptions import RoutingError

OSRM_URL = os.environ.get("OSRM_URL", "https://router.project-osrm.org/route/v1/driving")
OSRM_TIMEOUT = int(os.environ.get("OSRM_TIMEOUT", "30"))
ROUTE_CACHE_TIMEOUT = int(os.environ.get("ROUTE_CACHE_TIMEOUT", "172800"))
MIN_ROUTE_DISTANCE = 0.1
MAX_ROUTE_DISTANCE = 10000


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


class OSRMRouter:
    def __init__(self):
        self._route_cached = _cached_api_call(ROUTE_CACHE_TIMEOUT, "route")(
            with_retry(RetryConfig(max_retries=3, base_delay=1.0, max_delay=8.0))(
                self._get_route_call
            )
        )

    def get_route(
        self,
        origin_ll: tuple[float, float],
        waypoint_ll: tuple[float, float],
        dest_ll: tuple[float, float],
    ) -> dict:
        try:
            return osrm_breaker.execute(self._route_cached, origin_ll, waypoint_ll, dest_ll)
        except requests.exceptions.Timeout:
            raise
        except (requests.exceptions.RequestException, ValueError) as e:
            raise RoutingError("Unable to calculate route. Please try again.") from e

    @staticmethod
    def _get_route_call(
        origin_ll: tuple[float, float],
        waypoint_ll: tuple[float, float],
        dest_ll: tuple[float, float],
    ) -> dict:
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

        OSRMRouter._validate_route(legs)
        coordinates = route["geometry"]["coordinates"]
        return {"coordinates": coordinates, "legs": legs}

    @staticmethod
    def _validate_route(legs: list[dict]) -> None:
        if not legs or len(legs) != 2:
            raise ValueError("Route must have exactly 2 legs (origin->waypoint->destination).")
        leg1_miles = legs[0]["distance_miles"]
        leg2_miles = legs[1]["distance_miles"]
        if leg2_miles < MIN_ROUTE_DISTANCE:
            raise ValueError("Pickup to dropoff distance must be at least 0.1 miles.")
        total_miles = leg1_miles + leg2_miles
        if total_miles > MAX_ROUTE_DISTANCE:
            raise ValueError(
                f"Route distance {total_miles:.1f} miles exceeds maximum of {MAX_ROUTE_DISTANCE} miles."
            )
