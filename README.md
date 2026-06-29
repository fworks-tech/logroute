# LogRoute

> **FMCSA-compliant ELD logbook & route planner** — Plan trips, enforce Hours of Service rules, and generate DOT-ready daily log sheets in one click.

**Live app:** [https://logroute-app.vercel.app](https://logroute-app.vercel.app)

---

## Overview

LogRoute takes trip details (current location, pickup, dropoff, cycle hours used) and outputs an interactive route map with fuel/rest markers and rendered FMCSA daily log sheets.

**Inputs:**
- Current location
- Pickup location
- Dropoff location
- Current cycle hours used

**Outputs:**
- Interactive route map with markers (fuel, rest, pickup, dropoff)
- FMCSA-compliant ELD daily log sheets
- Trip summary statistics (distance, duration, stops)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19, TypeScript 5.5, MUI 6, Zustand, TanStack Query, Leaflet |
| **Backend** | Django 4.2, DRF 3.15, DRF Spectacular (OpenAPI), SimpleJWT |
| **Database** | PostgreSQL 15 (Railway) / SQLite (local dev) |
| **API Design** | Atomic Design (`atoms/`, `molecules/`, `organisms/`) |
| **Geocoding** | Nominatim (OpenStreetMap) — free |
| **Routing** | OSRM (OpenStreetMap) — free |
| **HOS Engine** | Custom FMCSA rule simulator |

**Deployment:**

| Service | Provider | URL |
|---------|----------|-----|
| Frontend | Vercel | [logroute-app.vercel.app](https://logroute-app.vercel.app) |
| Backend | Railway | `logroute-api-backend-production.up.railway.app` |
| Database | Railway PostgreSQL | Internal, auto-provisioned |
| Source | GitHub | [github.com/fworks-tech/logroute](https://github.com/fworks-tech/logroute) |

---

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && .\venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000

# Frontend (separate terminal)
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Open **http://localhost:3000**

> Local dev uses SQLite by default. For PostgreSQL: `docker compose -f docker/docker-compose.yml up -d` and set `DATABASE_URL` in `.env`.

---

## How It Works

```
TripForm ──► POST /api/plan-route/ ──► TripResults
  (4 inputs)         │                    ├── RouteMap (Leaflet + OSM)
                     │                    ├── LogbookCanvas (MCSA-5890)
                     ▼                    └── StatCards
              Django REST API
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Nominatim       OSRM       HOS Engine
  (geocode 3x)  (2 legs)     (5 FMCSA rules)
```

### Step by step

1. **You enter** — current location, pickup, dropoff, cycle hours used
2. **Backend geocodes** all 3 addresses via Nominatim (cached 24h)
3. **OSRM calculates** the driving route (current→pickup→dropoff)
4. **HOS Engine simulates** the trip enforcing all FMCSA rules
5. **Response** — route coordinates, markers, logbook days, summary
6. **Frontend renders** — interactive map + ELD log sheets + stats

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

**Response** — route polyline, map markers, multi-day logbook, trip summary.

Full OpenAPI schema at [`/api/schema/`](https://logroute-api-backend-production.up.railway.app/api/schema/) (backend must be running).

### Other endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/geocode/` | GET | Nominatim search suggestions (`?q=Chicago`) |
| `/api/auth/token/` | POST | JWT token obtain |
| `/api/auth/register/` | POST | User registration |
| `/api/hos/summary/` | GET | FMCSA HOS rules summary |
| `/api/hos/compliance/` | GET | Compliance requirements |
| `/api/hos/limits/` | GET | Driving limits reference |
| `/api/docs/` | GET | Swagger UI (backend only) |

---

## FMCSA Rules Enforced

| # | Rule | Value | What happens |
|---|------|-------|-------------|
| 1 | **Driving limit** | 11 hrs/shift | 10hr reset after 11h driving |
| 2 | **On-duty window** | 14 hrs/shift | No driving after 14h on-duty |
| 3 | **Mandatory break** | 30 min after 8h driving | Break inserted automatically |
| 4 | **Cycle limit** | 70hr/8day (or 60hr/7day) | 34-hr restart if cycle is full |
| 5 | **Fuel stop** | Every 1,000 mi | 30-min ON_DUTY_NOT_DRIVING |
| 6 | **Pickup/Dropoff** | 1 hr each | ON_DUTY_NOT_DRIVING at each |

---

## Project Structure

```
logroute/
├── frontend/                          # React 19 + Vite + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── atoms/                 # Smallest primitives
│   │   │   │   ├── LoadingButton.tsx
│   │   │   │   ├── StatCard.tsx
│   │   │   │   ├── SectionPaper.tsx
│   │   │   │   ├── StatusChip.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   ├── molecules/             # Simple combinations
│   │   │   │   ├── ErrorAlert.tsx
│   │   │   │   └── LogbookDayDetail.tsx
│   │   │   └── organisms/             # Complex sections
│   │   │       ├── TripForm.tsx        # Route planner form
│   │   │       ├── TripResults.tsx     # Results dashboard
│   │   │       ├── RouteMap.tsx        # Interactive Leaflet map
│   │   │       ├── LogbookCanvas.tsx   # FMCSA ELD log sheet
│   │   │       └── SessionPanel.tsx    # Trip history
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── lib/                       # API client, Zod schemas, logger
│   │   ├── store/                     # Zustand state management
│   │   ├── types/                     # TypeScript interfaces
│   │   ├── theme.ts                   # MUI theme
│   │   ├── App.tsx                    # Main app layout
│   │   └── main.tsx                   # Entry point
│   ├── vercel.json                    # Vercel deployment config
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                           # Django 4.2 + DRF
│   ├── logroute/                      # Django project config
│   │   ├── settings.py                # Env-driven configuration
│   │   ├── urls.py                    # API routes + SPA fallback
│   │   └── wsgi.py
│   ├── trips/                         # Core application
│   │   ├── views.py                   # PlanRoute, Geocode, Auth views
│   │   ├── serializers.py             # Request/response validation
│   │   ├── routing.py                 # Nominatim + OSRM integration
│   │   ├── hos_engine.py              # FMCSA HOS rule simulator
│   │   ├── services.py                # Trip planning orchestrator
│   │   ├── error_handler.py           # Circuit breaker + retry
│   │   ├── middleware.py              # Request logging + error handling
│   │   ├── throttles.py               # Rate limiting
│   │   ├── models.py                  # Trip model
│   │   └── tests/                     # 39 tests, 87% coverage
│   ├── manage.py
│   └── requirements.txt
│
├── docker/
│   └── docker-compose.yml             # PostgreSQL + Redis
│
├── docs/
│   ├── fmcsahos395driversguidetohos2022042801.md       # FMCSA rulebook
│   └── fmcsahos395driversguidetohos2022042801.openapi.yaml  # OpenAPI spec
│
└── vercel.json                        # Root Vercel deployment config
```

---

## Deployment

### Frontend (Vercel)

Auto-deploys from `main` branch. Config in `vercel.json`:
- Build: `cd frontend && npm run build` → `frontend/dist/`
- API proxy: `/api/*` → Railway backend
- SPA fallback: all routes → `/index.html`

### Backend (Railway)

Deployed from GitHub repo. Environment variables:
```
DJANGO_SECRET_KEY=<auto-generated>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=logroute-app.vercel.app,.railway.app,.up.railway.app
CORS_ALLOWED_ORIGINS=https://logroute-app.vercel.app
DATABASE_URL=postgresql://...         # Auto-provisioned by Railway
```

---

## Development

```bash
# Backend
python manage.py runserver              # Dev server (port 8000)
pytest                                  # 39 tests, 87% coverage
coverage html                           # HTML coverage report

# Frontend
npm run dev                             # Vite dev server (port 3000)
npm run build                           # tsc + vite production build
npm run test:unit                       # Vitest unit tests
npm run test:e2e                        # Playwright e2e tests

# API docs (backend running)
http://localhost:8000/api/docs/         # Swagger UI
http://localhost:8000/api/schema/       # OpenAPI JSON
```

---

## License

MIT
