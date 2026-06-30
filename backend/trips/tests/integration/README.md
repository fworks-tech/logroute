# Integration Tests

Full-stack tests exercising the HTTP API through DRF's `APIClient`.
Django ORM is active (SQLite). External API calls are mocked at the
HTTP boundary. Run with `pytest -m integration` or as part of the full suite.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `conftest.py` | *(inherited from `tests/conftest.py`)* Shared fixtures: `api_client`, `user`, `authenticated_client`, `sample_trip_data`. Clears throttle cache before each test. |
| `test_api_endpoint.py` | Endpoint tests: health check, user registration, JWT token, geocode search, route planning (with mocked gateways). |
| `test_reference_api.py` | All 8 HOS reference endpoints: correct status codes, response shapes, 404 for unknown exception ID, category filtering. |
