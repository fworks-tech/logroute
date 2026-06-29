# LogRoute Backend

Django 4.2 REST API for the LogRoute ELD & Route Planner. Geocodes locations (Nominatim), calculates routes (OSRM), and simulates FMCSA Hours of Service regulations.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2 + Django REST Framework 3.15 |
| Auth | SimpleJWT (access 60 min, refresh 7 days) |
| Schema | drf-spectacular (OpenAPI, Swagger UI at `/api/docs/`) |
| Database | PostgreSQL (auto-detected from `DATABASE_URL`), falls back to SQLite |
| Cache | LocMemCache by default, Redis when `REDIS_URL` is set |
| External APIs | Nominatim (geocoding, 24h cache), OSRM (routing, 48h cache) |
| Testing | pytest 8.4 + pytest-django + pytest-cov (threshold 70%) |

## Prerequisites

- Python 3.11+
- PostgreSQL + Redis (optional — via `docker compose -f docker/docker-compose.yml up -d`, or omit for SQLite fallback)

## Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

The root `.env` is auto-loaded by `python-dotenv`. Copy defaults:

```bash
copy ..\.env.example ..\.env
```

To use SQLite instead of PostgreSQL (no Docker needed), comment out or remove `DATABASE_URL` from `.env`:

```ini
# DATABASE_URL=postgresql://logroute:logroute@localhost:5432/logroute
```

Then:

```bash
python manage.py migrate
python manage.py runserver
```

Server starts on `http://localhost:8000`.

## Commands

```bash
python manage.py runserver          # Dev server (auto-reload)
pytest                              # All tests (coverage min 70%)
pytest -m unit                      # Unit tests only
pytest -m "not slow"                # Skip slow tests
coverage html                       # Generate HTML coverage report (backend/htmlcov/)
python manage.py collectstatic      # Production: collect frontend dist
```

## Project Structure

```
backend/
├── logroute/               # Django project package
│   ├── settings.py         # All config (DB, cache, CORS, auth, logging)
│   ├── urls.py             # Root URL conf (health, API, docs, React SPA)
│   └── wsgi.py             # WSGI entry for Gunicorn
├── trips/                  # Core app
│   ├── models.py           # Trip model (statuses, JSON fields for route/logbook)
│   ├── views.py            # PlanRoute, GeocodeSearch, TokenObtain, Register
│   ├── serializers.py      # Input/output serializers, JWT custom claims
│   ├── services.py         # TripPlanningService (geocode → route → HOS → transform)
│   ├── hos_engine.py       # FMCSA HOS simulation (11/14/30min/10/70 rules)
│   ├── routing.py          # Nominatim + OSRM clients with cache, retry, circuit breaker
│   ├── error_handler.py    # TripPlanningError, GeocodingError, RoutingError, CircuitBreaker
│   ├── throttles.py        # PlanRouteThrottle (10/hr), AuthThrottle (20/hr)
│   ├── middleware.py        # Request logging (UUID, timing) + JSON error handler
│   └── tests/              # pytest tests
│       ├── conftest.py      # Fixtures (api_client, user, trip data)
│       ├── test_hos_engine.py
│       └── test_api_endpoint.py
├── manage.py               # Django CLI entry
└── requirements.txt
```

## API Endpoints

| Method | Path | Description | Auth | Throttle |
|--------|------|-------------|------|----------|
| GET | `/health/` | Health check → `{"status": "ok"}` | None | — |
| POST | `/api/plan-route/` | Plan route (geocode → OSRM → HOS → result) | None | 10/hr |
| GET | `/api/geocode/?q=<query>` | Geocode autocomplete (Nominatim, US only, max 5) | None | — |
| POST | `/api/auth/token/` | JWT token obtain | None | 20/hr |
| POST | `/api/auth/register/` | User registration | None | 20/hr |
| GET | `/api/schema/` | OpenAPI schema (drf-spectacular) | None | — |
| GET | `/api/docs/` | Swagger UI | None | — |

### `POST /api/plan-route/`

**Input:**
```json
{
  "current_location": "Chicago, IL",
  "pickup_location": "Indianapolis, IN",
  "dropoff_location": "Dallas, TX",
  "cycle_hours_used": 10,
  "trip_date": "2026-06-29",
  "tractor_number": "TRAC-001",
  "trailer_number": "TRAIL-002",
  "shipper_name": "Acme Corp"
}
```

**Output:** Route coordinates (GeoJSON), map markers, logbook days with 15-min snapped events, trip summary (distance, hours, stops).

## Architecture

### Request flow

```
TripForm → POST /api/plan-route/ → TripInputSerializer validates
  → geocode(current, pickup, dropoff) via Nominatim (24h cache, 3x retry, circuit breaker)
  → get_route(origin, waypoint, dest) via OSRM (48h cache, 3x retry, circuit breaker)
  → simulate_trip(distance, hours, cycle) → HOS engine
  → Transform logbook (hours → HH:MM format, build markers)
  → Return complete response
```

### HOS Engine Rules (hos_engine.py)

| Rule | Value |
|------|-------|
| Max driving per shift | 11 hours |
| Max on-duty window per shift | 14 hours (once started, clock runs) |
| Mandatory break | 30 min after 8 hours driving |
| Shift reset | 10 hours sleeper-berth/off-duty |
| Rolling cycle limit | 70 hours / 8 days |
| Fuel stops | 30 min every 1,000 miles |
| Pickup/Dropoff | 1 hour each (on-duty not driving) |

The engine snapshots all events to 15-minute intervals (FMCSA requirement).

### Resiliency

- **Caching**: Geocode (24h), route (48h), HOS simulation (24h) — all via Django cache framework
- **Retry**: 3 attempts with exponential backoff (1s → 2s → 4s base) for Nominatim and OSRM
- **Circuit breakers**: Per-service, threshold 5 failures, 60s recovery, thread-safe

### Production deployment

Multi-stage Docker build (`docker/Dockerfile`): Node 18 → frontend build → Python 3.11 → Gunicorn (4 workers). The React build is served as static files via Django's `TemplateView` (single process).

## Testing

```bash
pytest                              # All tests (requires DB)
pytest trips/tests/test_hos_engine.py   # HOS engine only
pytest -k "test_short_trip"         # Single test
```

Coverage threshold is 70% (`--cov-fail-under=70`). Report written to `backend/htmlcov/`.

## Environment Variables

See `.env.example` at repo root. Key vars:

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `sqlite:///db.sqlite3` | PostgreSQL: `postgresql://user:pass@host:5432/dbname` |
| `REDIS_URL` | (none) | Redis: `redis://localhost:6379/0`, enables RedisCache |
| `DEBUG` | `True` | Set `False` in production |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | Access token expiry |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | `7` | Refresh token expiry |
