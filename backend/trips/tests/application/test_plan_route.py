from datetime import date

import pytest

from trips.application.dto import PlanRouteRequest
from trips.application.use_cases.plan_route import PlanRouteUseCase
from trips.domain.value_objects import Coordinates


class FakeGeocoder:
    def __init__(self):
        self.call_count = 0

    def geocode(self, address):
        self.call_count += 1
        return (40.7128, -74.0060)

    def search(self, query):
        return []


class FakeRouter:
    def get_route(self, origin_ll, waypoint_ll, dest_ll):
        return {
            "coordinates": [[-74.0060, 40.7128], [-87.6298, 41.8781]],
            "legs": [
                {"distance_miles": 100.0, "duration_hours": 2.0},
                {"distance_miles": 200.0, "duration_hours": 4.0},
            ],
        }


class FakeCache:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value, timeout):
        self._store[key] = value

    def delete(self, key):
        self._store.pop(key, None)


class TestPlanRouteUseCase:
    def test_execute_returns_response_with_all_fields(self):
        use_case = PlanRouteUseCase(FakeGeocoder(), FakeRouter(), FakeCache())
        request = PlanRouteRequest(
            current_location="New York, NY",
            pickup_location="Philadelphia, PA",
            dropoff_location="Chicago, IL",
            cycle_hours_used=0,
            cycle_schedule="70",
        )
        result = use_case.execute(request)
        assert result.total_miles == 300.0
        assert result.cycle_schedule == "70"
        assert result.cycle_max_hours == 70
        assert len(result.markers) >= 3
        assert len(result.logbook_days) > 0
        assert result.trip_summary["total_distance_miles"] == 300.0

    def test_execute_with_sixty_hour_cycle(self):
        use_case = PlanRouteUseCase(FakeGeocoder(), FakeRouter(), FakeCache())
        request = PlanRouteRequest(
            current_location="NYC",
            pickup_location="Philly",
            dropoff_location="Chicago",
            cycle_hours_used=10,
            cycle_schedule="60",
        )
        result = use_case.execute(request)
        assert result.cycle_schedule == "60"
        assert result.cycle_max_hours == 60

    def test_execute_caches_and_returns_cached(self):
        cache = FakeCache()
        use_case = PlanRouteUseCase(FakeGeocoder(), FakeRouter(), cache)
        request = PlanRouteRequest(
            current_location="NYC",
            pickup_location="Philly",
            dropoff_location="Chicago",
            cycle_hours_used=0,
        )
        result1 = use_case.execute(request)
        result2 = use_case.execute(request)
        assert result1.total_miles == result2.total_miles
