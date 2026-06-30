# LogRoute Backend — Architecture

> Django 4.2 + DRF 3.15 backend for the LogRoute ELD & Route Planner.
> Full API docs at `/api/docs/` (Swagger UI) when the server is running.

---

## Project Structure

```
backend/
├── logroute/              # Django project configuration
│   ├── settings.py        # DB, cache, CORS, auth, logging — all env-driven
│   ├── urls.py            # Root URL conf: health, API proxy, Swagger, SPA fallback
│   └── wsgi.py            # WSGI entry for Gunicorn
│
├── trips/                 # Core application
│   ├── views.py           # 5 API views (PlanRoute, GeocodeSearch, TokenObtain, Register, HealthCheck)
│   ├── serializers.py     # 12 serializers (input validation, output formatting, user/trip models)
│   ├── services.py        # TripPlanningService — orchestrates the 5-step pipeline
│   ├── hos_engine.py      # FMCSA HOS rule simulator (11h, 14h, 30min, 10h, 70h/8d)
│   ├── routing.py         # Nominatim + OSRM clients with caching, retry, circuit breakers
│   ├── error_handler.py   # Exception hierarchy + RetryConfig + CircuitBreaker
│   ├── throttles.py       # Rate limit classes (PlanRoute: 100/hr, Auth: 20/hr)
│   ├── middleware.py      # Request logging (UUID, timing) + JSON error handler
│   ├── models.py          # Trip model with statuses and JSON fields
│   ├── reference_views.py # 9 read-only HOS reference endpoints
│   ├── urls.py            # Route definitions for all API endpoints
│   └── tests/             # pytest suite (39 tests, 87% coverage)
│
├── manage.py              # Django CLI entry point
└── requirements.txt
```

---

## Request Lifecycle

Every HTTP request flows through this chain:

```
HTTP Request
      │
      ▼
┌──────────────────────────────────────────────────┐
│              Middleware Stack                     │
│                                                   │
│  1. corsheaders.middleware.CorsMiddleware         │
│     → Adds CORS headers from CORS_ALLOWED_ORIGINS │
│                                                   │
│  2. SecurityMiddleware                            │
│     → HSTS, X-Content-Type-Options, etc.          │
│                                                   │
│  3. CommonMiddleware                              │
│     → URL rewriting, APPEND_SLASH                 │
│                                                   │
│  4. RequestLoggingMiddleware (trips/middleware.py) │
│     → Generates request_id (UUID hex[:12])        │
│     → Measures duration_ms                        │
│     → Logs method, path, status_code, duration    │
│     → Sets X-Request-ID response header           │
│                                                   │
│  5. ErrorHandlingMiddleware (trips/middleware.py)  │
│     → Catches unhandled exceptions                │
│     → Returns JSON 500 with request_id            │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│               URL Resolution                      │
│                                                   │
│  /health/              → health_check()           │
│  /api/plan-route/      → PlanRouteView.post()     │
│  /api/geocode/         → GeocodeSearchView.get()  │
│  /api/auth/token/      → TokenObtainView.post()   │
│  /api/auth/register/   → UserRegistrationView.post│
│  /api/hos/summary/     → HosSummaryView.get()     │
│  /api/hos/limits/      → HosLimitsView.get()      │
│  /api/schema/          → SpectacularAPIView       │
│  /api/docs/            → SwaggerUI                │
│  /                     → React SPA (TemplateView) │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
          (see detailed flow below)
```

---

## Main Flow: `POST /api/plan-route/`

This is the core endpoint. Here is every step with exact file references:

```
PlanRouteView.post()                          # trips/views.py:40
  │
  ├─ TripInputSerializer(data=request.data)    # trips/serializers.py:13
  │  Validates: locations (min 2 chars), cycle_hours (0-70),
  │  schedule (60/70), optional trip_date/tractor/trailer/shipper
  │  Returns 400 if invalid
  │
  ├─ TripPlanningService.plan_route(...)       # trips/services.py:11
  │  │
  │  ├─ 1. geocode(current_location)          # trips/routing.py:73
  │  │    → Nominatim API (cached 24h)
  │  │    → 3 retries with exponential backoff (1s→2s→4s)
  │  │    → Circuit breaker (5 failures, 60s recovery)
  │  │    → Returns (lat, lon) tuple
  │  │    → Raises GeocodingError on failure
  │  │
  │  ├─ 2. geocode(pickup_location)           # same path
  │  │
  │  ├─ 3. geocode(dropoff_location)          # same path
  │  │
  │  ├─ 4. get_route(current_ll, pickup_ll, dropoff_ll)  # trips/routing.py:134
  │  │    → OSRM API (cached 48h)
  │  │    → Same retry + circuit breaker as geocode
  │  │    → Validates 2 legs, min 0.1mi, max 10,000mi
  │  │    → Returns {coordinates: [[lon,lat],...], legs: [...]}
  │  │    → Raises RoutingError on failure
  │  │
  │  ├─ 5. simulate_trip(total_distance,       # trips/hos_engine.py:74
  │  │         leg1_hours, leg2_hours,
  │  │         cycle_hours_used, ...)
  │  │    → Cached 24h (deterministic for given inputs)
  │  │    → Simulates driving with FMCSA rules
  │  │    → Returns {logbook_days, total_trip_hours, ...}
  │  │
  │  └─ 6. Transform & build markers
  │       → Convert hours to HH:MM format
  │       → Build start/pickup/dropoff markers from geocoded coords
  │       → Build fuel/rest markers from logbook events
  │       → Return complete response dict
  │
  └─ Response with route_coordinates, markers,
     logbook_days, trip_summary, metadata
```

### Response shape

```json
{
  "route_coordinates": [[lng, lat], ...],
  "markers": [{ "id": "start", "lat": ..., "lon": ..., "type": "start", "label": "Chicago, IL", "time": "08:00" }, ...],
  "logbook_days": [{
    "day": 0,
    "date": "06/29/2026",
    "from_location": "Chicago, IL",
    "to_location": "Dallas, TX",
    "daily_miles": 925.3,
    "events": [{ "status": "DRIVING", "start_time": "08:00", "end_time": "12:00", ... }],
    "row_totals": { "driving_hours": 10.5, ... }
  }],
  "trip_summary": { "total_distance_miles": 925.3, "total_driving_hours": 10.5, ... }
}
```

---

## HOS Engine — Execution Model

File: `trips/hos_engine.py`

The engine simulates a trip hour-by-hour using a shared mutable state dict. The top-level function `simulate_trip()` defines 7 nested closures that read/write this state:

```
simulate_trip()
  │
  ├─ State initialization
  │   cycle_hours ← current_cycle_used_hours
  │   shift_drive ← 0  (driving hours this shift, max 11)
  │   shift_on_duty ← 0 (on-duty hours this shift, max 14)
  │   drive_since_break ← 0 (max 8 before mandatory 30min break)
  │   miles_since_fuel ← 0 (fuel stop every 1,000 mi)
  │
  ├─ Nested closures (they mutate state via nonlocal)
  │   add_event()         → Appends {status, start_hour, end_hour, label} to events list
  │   start_shift_if_needed() → Records shift_start when first going on-duty
  │   on_duty_elapsed()   → current_time - shift_start (hours)
  │   remaining_window()  → max(0, 14 - on_duty_elapsed)
  │   remaining_drive()   → max(0, 11 - shift_drive)
  │   remaining_break()   → max(0, 8 - drive_since_break)
  │   remaining_cycle()   → max(0, cycle_limit - cycle_hours)
  │   do_rest()           → 10h SLEEPER_BERTH, resets shift counters
  │   do_cycle_rest()     → 34h SLEEPER_BERTH, resets cycle + shift counters
  │   do_break()          → 0.5h OFF_DUTY, resets drive_since_break
  │   do_fuel()           → 0.5h ON_DUTY_NOT_DRIVING, resets miles_since_fuel
  │   drive_segment()     → Main loop: drives in compliant chunks
  │   do_on_duty_nd()     → ON_DUTY_NOT_DRIVING (pickup/dropoff)
  │
  ├─ Simulation steps
  │   drive_segment(leg1_hours, leg1_miles, "Driving to Pickup")
  │   do_on_duty_nd(1.0, "Pickup", pickup_location)
  │   drive_segment(leg2_hours, leg2_miles, "Driving to Dropoff")
  │   do_on_duty_nd(1.0, "Dropoff", to_location)
  │
  └─ Day grouping
      Split events by 24-hr windows
      Snap all events to 15-min intervals (FMCSA §395.8)
      Fill gaps with OFF_DUTY
      Compute row_totals, cycle_hours_after_day, daily_miles
```

### drive_segment — the core loop

```
while remaining_hours > 0:
  1. Check if rest is needed (cycle full → 34h restart, shift exhausted → 10h rest)
  2. Find the binding cap: min(remaining_drive, remaining_window,
     remaining_break, remaining_cycle, miles_to_fuel / avg_speed)
  3. Drive the chunk → add_event("DRIVING", chunk_hours)
  4. Update state (shift_drive, shift_on_duty, cycle_hours, miles_since_fuel)
  5. Post-chunk checks: fuel stop if 1,000mi reached, break if 8h driving reached
```

---

## Resiliency Patterns

### Caching (Django cache framework)

| Call | Cache TTL | Key Prefix |
|------|-----------|------------|
| `geocode(address)` | 24h (86400s) | `geocode_<md5>` |
| `geocode_search(query)` | 24h (86400s) | `geocode_search_<md5>` |
| `get_route(...)` | 48h (172800s) | `route_<md5>` |
| `simulate_trip(...)` | 24h (86400s) | `hos_simulation_<md5>` |

All cache keys are MD5 hashes of serialised function arguments. Cache backend is `LocMemCache` by default, switches to `RedisCache` when `REDIS_URL` is set.

### Retry (`with_retry` decorator — `error_handler.py:54`)

```
RetryConfig(max_retries=3, base_delay=1.0, max_delay=8.0, backoff_factor=2.0)
  → attempt 1: wait 1s
  → attempt 2: wait 2s
  → attempt 3: wait 4s (capped at max_delay=8s)
  → raises last exception
```

Applied to `_geocode_call`, `_geocode_search_call`, `_get_route_call`.

### Circuit Breaker (`CircuitBreaker` — `error_handler.py:86`)

```
States: CLOSED → (5 failures) → OPEN → (60s timeout) → HALF_OPEN → (1 success) → CLOSED
                                                  → (1 failure) → OPEN
```

| Breaker | Service | Threshold | Recovery |
|---------|---------|-----------|----------|
| `nominatim_breaker` | Nominatim | 5 failures | 60s |
| `osrm_breaker` | OSRM | 5 failures | 60s |

When OPEN, `execute()` raises `CircuitOpenError` (HTTP 503) without calling the service.

---

## Error Hierarchy

```
TripPlanningError (base)                    # trips/error_handler.py:10
  status_code: int (default 400)
  details: dict

├── GeocodingError                           # trips/error_handler.py:17
│   status_code: 422
│   Raised when Nominatim cannot geocode
│
├── RoutingError                             # trips/error_handler.py:22
│   status_code: 422
│   Raised when OSRM cannot find a route
│
└── CircuitOpenError                         # trips/error_handler.py:27
    status_code: 503
    details: { "service": "nominatim" | "osrm" }
    Raised when a circuit breaker blocks the call
```

Views catch `TripPlanningError` and return the status code + error message + details in the response body. Unhandled exceptions fall through to `ErrorHandlingMiddleware` which returns a generic JSON 500.

---

## Auth Flow

```
UserRegistrationView.post()                 # trips/views.py:103
  → UserRegistrationSerializer.create()
  → Creates user with username/email/password
  → Returns 201

TokenObtainView.post()                      # trips/views.py:92
  → CustomTokenObtainPairSerializer.get_token()
    → Extends JWT with email + username claims
  → Returns { access, refresh }
```

Both endpoints throttled at 20/hr via `AuthThrottle`. The frontend currently does not implement auth — these endpoints exist for future use.

---

## Testing

```
pytest                                    # 39 tests, 87% coverage, min 70%
pytest -m unit                            # Unit tests only
pytest -m "not slow"                      # Skip slow tests
coverage html                             # Open backend/htmlcov/index.html
```

| Test file | What it covers |
|-----------|---------------|
| `tests/test_hos_engine.py` | HOS simulation: short/long trips, cycle restarts, fuel stops, breaks, 15-min snapping |
| `tests/test_api_endpoint.py` | Plan route (input validation, success, geocode/routing errors), health check, auth |
| `tests/test_reference_api.py` | All 9 HOS reference endpoints return correct schemas |

Fixtures (`conftest.py`): `api_client`, `user`, `trip_data` — shared across test files.
