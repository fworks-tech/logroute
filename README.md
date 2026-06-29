# LogRoute

> **FMCSA-compliant ELD logbook & route planner** — Plan trips, enforce Hours of Service rules, and generate DOT-ready daily log sheets in one click.

[![GitHub](https://img.shields.io/badge/source-github-0D3B4E?style=flat&logo=github)](https://github.com/fworks-tech/logroute)
[![Frontend](https://img.shields.io/badge/frontend-vercel-000?style=flat&logo=vercel)](https://logroute-app.vercel.app)
[![Backend](https://img.shields.io/badge/backend-railway-0B0D0E?style=flat&logo=railway)](https://logroute-api-backend-production.up.railway.app)
[![License](https://img.shields.io/badge/license-MIT-3DA639?style=flat)]()

---

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && .\venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Open **http://localhost:3000** — frontend proxies `/api` to `:8000`.

> Local dev uses SQLite. For PostgreSQL: `docker compose -f docker/docker-compose.yml up -d` and set `DATABASE_URL` in `.env`.

---

## How It Works

```
TripForm ──► POST /api/plan-route/ ──► TripResults
  (4 inputs)        │                     ├── RouteMap (Leaflet + OSM)
                    │                     ├── LogbookCanvas (FMCSA §395.8)
                    ▼                     └── StatCards
              Django REST API
                    │
          ┌─────────┼──────────┐
          ▼         ▼          ▼
     Nominatim     OSRM     HOS Engine
    (geocode)   (routing)   (FMCSA rules)
```

1. Enter current location, pickup, dropoff, and cycle hours used
2. Backend geocodes all 3 addresses via Nominatim (cached 24h)
3. OSRM calculates the driving route (origin → pickup → dropoff)
4. HOS Engine simulates the trip enforcing all FMCSA rules
5. Frontend renders the interactive map, ELD log sheets, and trip summary

---

## API

### `POST /api/plan-route/`

```json
{
  "current_location": "Chicago, IL",
  "pickup_location": "Chicago, IL",
  "dropoff_location": "Dallas, TX",
  "cycle_hours_used": 20
}
```

Returns route polyline, map markers, multi-day logbook, and trip summary.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plan-route/` | POST | Plan a trip & generate logbook |
| `/api/geocode/` | GET | Location autocomplete (`?q=Chicago`) |
| `/api/auth/token/` | POST | JWT token obtain |
| `/api/auth/register/` | POST | User registration |
| `/api/hos/summary/` | GET | FMCSA HOS rules summary |
| `/api/hos/limits/` | GET | Driving limits reference |
| `/api/docs/` | GET | Swagger UI (backend running) |

---

## FMCSA Rules Enforced

| Rule | Limit | Enforcement |
|------|-------|-------------|
| Driving limit | 11 hrs / shift | 10-hr reset after limit reached |
| On-duty window | 14 hrs / shift | No driving past 14th hour |
| Mandatory break | 30 min after 8h driving | Break inserted automatically |
| Cycle limit | 70h/8d or 60h/7d | 34-hr restart if cycle is full |
| Fuel stops | Every 1,000 mi | 30 min ON_DUTY_NOT_DRIVING |
| Pickup / Dropoff | 1 hr each | ON_DUTY_NOT_DRIVING |

---

## Project Structure

```
├── frontend/                  React 19 + Vite + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── atoms/         LoadingButton, StatCard, StatusChip, ErrorBoundary
│   │   │   ├── molecules/     ErrorAlert, LogbookDayDetail
│   │   │   └── organisms/     TripForm, TripResults, RouteMap, LogbookCanvas
│   │   ├── hooks/             useTripPlanner, useGeocodeSearch, useLogbookNavigation
│   │   ├── lib/               API client, Zod schemas, logger, redaction
│   │   ├── store/             Zustand — trip results, session history
│   │   └── types/             TypeScript interfaces
│   └── package.json
│
├── backend/                   Django 4.2 + DRF
│   ├── logroute/              Project settings & root URL routing
│   └── trips/                 Core app (views, serializers, routing, hos_engine, services)
│
├── docker/
│   └── docker-compose.yml     PostgreSQL + Redis
│
└── docs/                      FMCSA rulebook & OpenAPI spec
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript 5.5, MUI 6, Zustand, TanStack Query, Leaflet |
| Backend | Django 4.2, DRF 3.15, DRF Spectacular, SimpleJWT |
| Database | PostgreSQL / SQLite (auto-detected) |
| Geocoding | Nominatim (OSM) — free, cached 24h |
| Routing | OSRM (OSM) — free, cached 48h |
| HOS Engine | Custom FMCSA rule simulator |

---

## Deployment

| Service | URL |
|---------|-----|
| Frontend | [logroute-app.vercel.app](https://logroute-app.vercel.app) |
| Backend | `logroute-api-backend-production.up.railway.app` |
| Source | [github.com/fworks-tech/logroute](https://github.com/fworks-tech/logroute) |

Auto-deploys from `main`. Frontend proxies `/api/*` to the Railway backend.

---

## Development

```bash
# Backend
python manage.py runserver          # Dev server :8000
pytest                               # 39+ tests, 87% coverage, 70% min
coverage html                        # Open backend/htmlcov/index.html

# Frontend
npm run dev                          # Vite dev server :3000
npm run build                        # tsc + vite production build
npm run test:unit                    # Vitest (single run)
npm run test:e2e                     # Playwright e2e
npm run lint                         # tsc --noEmit + ESLint (tsdoc/syntax)

# API docs (backend running)
http://localhost:8000/api/docs/      # Swagger UI
```

---

## License

MIT
