# Application Layer — Use Cases

Orchestrates domain logic. Depends ONLY on `domain/` — no framework imports.
Each use case is a class with a single responsibility, receiving its port
dependencies (defined in `domain/ports.py`) via constructor injection.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `dto.py` | Input/output data transfer objects: `PlanRouteRequest`, `PlanRouteResponse`, `GeocodeSearchRequest`, `GeocodeSearchResponse`, etc. Typed dataclasses. |
| `use_cases/__init__.py` | Package marker |
| `use_cases/plan_route.py` | `PlanRouteUseCase(geocoder, router, hos_engine, cache)`. Full trip pipeline: geocode 3 locations → route via OSRM → run HOS simulation → build markers. Handles caching at this level. |
| `use_cases/geocode_search.py` | `GeocodeSearchUseCase(geocoder, cache)`. Autocomplete location search via Nominatim with caching. |
| `use_cases/get_hos_reference.py` | `HosReferenceUseCase(reference_repo)`. 8 methods serving FMCSA HOS reference data: `get_summary()`, `get_limits()`, `get_exceptions(category)`, `get_exception_by_id(id)`, etc. |
