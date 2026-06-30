# Domain Layer — Enterprise Business Rules

Pure Python. Zero imports from Django, DRF, requests, or any framework.
The innermost layer of Clean Architecture — has no knowledge of anything outside itself.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `entities.py` | Core domain objects as `@dataclass`: `Location`, `TripPlan`, `LogbookDay`, `LogbookEvent`. Framework-agnostic representations of the trip domain. |
| `value_objects.py` | Immutable value types: `Coordinates(lat, lon)`, `CycleHours(float)`, `RouteLeg(distance_miles, duration_hours)`. |
| `enums.py` | String enums: `DutyStatus` (`DRIVING`, `OFF_DUTY`, `SLEEPER_BERTH`, `ON_DUTY_NOT_DRIVING`), `CycleSchedule` (`60`, `70`), `TripStatus` (`DRAFT`, `PLANNED`, etc.). |
| `exceptions.py` | Exception hierarchy: `TripPlanningError(status_code, details)` → `GeocodingError`, `RoutingError`. Raised by use cases when operations fail. |
| `ports.py` | `typing.Protocol` interfaces defining boundaries: `Geocoder`, `Router`, `TripRepository`, `CacheService`, `HosReferenceRepository`. Adapters implement these. |
| `hos_engine.py` | FMCSA HOS rules simulation. Pure function `simulate_trip(...)` — no caching, no I/O. Transforms distance/hours into structured logbook events. |
| `hos_reference.py` | Static reference data mirroring the FMCSA HOS guide OpenAPI spec. All module-level dicts/lists, no classes or functions. |
