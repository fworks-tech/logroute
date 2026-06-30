# Gateways — External API Clients

Implementations of the `Geocoder` and `Router` ports defined in `domain/ports.py`.
Each gateway wraps an external HTTP API with caching (via `CacheService`),
retry logic, and a circuit breaker (both from `infrastructure/resilience.py`).

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `nominatim.py` | `NominatimGeocoder(Geocoder)`. Two methods: `geocode(address) → Coordinates` and `search(query) → list[dict]`. Calls OpenStreetMap's Nominatim API. |
| `osrm.py` | `OSRMRouter(Router)`. Method: `get_route(origin, waypoint, dest) → RouteData`. Calls OpenStreetMap's OSRM routing API. |
