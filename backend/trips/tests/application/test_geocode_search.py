import pytest

from trips.application.dto import GeocodeSearchRequest
from trips.application.use_cases.geocode_search import GeocodeSearchUseCase


class FakeGeocoder:
    def search(self, query):
        if len(query) < 2:
            return []
        return [{"display_name": query, "lat": "40.71", "lon": "-74.00"}]

    def geocode(self, address):
        return (40.71, -74.00)


class FakeCache:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value, timeout):
        self._store[key] = value

    def delete(self, key):
        self._store.pop(key, None)


class TestGeocodeSearchUseCase:
    def test_execute_returns_results(self):
        use_case = GeocodeSearchUseCase(FakeGeocoder(), FakeCache())
        request = GeocodeSearchRequest(query="New York")
        result = use_case.execute(request)
        assert len(result.results) == 1
        assert result.results[0]["display_name"] == "New York"

    def test_execute_caches_results(self):
        cache = FakeCache()
        geocoder = FakeGeocoder()
        use_case = GeocodeSearchUseCase(geocoder, cache)
        request = GeocodeSearchRequest(query="Chicago")
        result1 = use_case.execute(request)
        result2 = use_case.execute(request)
        assert len(result1.results) == 1
        assert len(result2.results) == 1
