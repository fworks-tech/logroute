# Application Layer Tests

Test use cases in isolation with fake implementations of port interfaces.
No database, no HTTP. Each test constructs a use case with in-memory test
doubles and verifies the orchestration logic.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `test_plan_route.py` | Tests for `PlanRouteUseCase`: successful pipeline with `FakeGeocoder`/`FakeRouter`, error propagation, cache hit/miss, cycle schedule selection. |
| `test_geocode_search.py` | Tests for `GeocodeSearchUseCase`: short query rejection, cached results, API error handling. |
| `test_get_hos_reference.py` | Tests for `HosReferenceUseCase`: all 8 endpoints return correct data shapes, exception detail returns 404 for unknown ID, category filtering works. |
