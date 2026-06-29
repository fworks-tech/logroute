# LogRoute

> **FMCSA-compliant ELD logbook & route planner** — Plan trips, enforce Hours of Service rules, and generate DOT-ready daily log sheets in one click.

---

## Overview

LogRoute is a full-stack monolith that takes trip details (current location, pickup, dropoff, cycle hours used) and outputs an interactive route map with fuel/rest markers and rendered FMCSA daily log sheets. No external API keys required — uses free OpenStreetMap services.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript 5.5, Material-UI v6, Zustand, TanStack Query, react-leaflet |
| Backend | Django 4.2, Django REST Framework 3.15, DRF Spectacular (OpenAPI) |
| Database | PostgreSQL 15 (Docker) / SQLite (local dev) |
| Geocoding | Nominatim (OpenStreetMap) — free |
| Routing | OSRM (OpenStreetMap) — free |
| Simulation | Custom HOS Engine — all 5 FMCSA rules |

---

## Quick Start

```bash
# Clone & enter
git clone <repo-url>
cd logroute

# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate       # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000

# Frontend (separate terminal)
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Open **http://localhost:3000**

> **No Docker required by default** — the app uses SQLite for local development.  
> To use PostgreSQL: `docker compose -f docker\docker-compose.yml up -d` and set `DATABASE_URL` in `.env`.

---

## How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│                                                                  │
│   TripForm ──► POST /api/plan-route/ ──► TripResults             │
│     (4 inputs)          │                    ├── RouteMap        │
│                         │                    ├── LogbookCanvas   │
│                         ▼                    └── Stats           │
│                   Django REST API                                │
│                         │                                        │
│          ┌──────────────┼──────────────┐                         │
│          ▼              ▼              ▼                         │
│     Nominatim        OSRM         HOS Engine                     │
│   (geocoding)     (routing)     (simulation)                     │
│   3 locations     2 legs        5 FMCSA rules                    │
└──────────────────────────────────────────────────────────────────┘
```

### Step by step

1. **You enter** — current location, pickup, dropoff, and cycle hours used
2. **Backend geocodes** all 3 addresses via Nominatim
3. **OSRM calculates** the driving route (2 legs: current→pickup, pickup→dropoff)
4. **HOS Engine simulates** the trip enforcing all 5 FMCSA rules
5. **Response returns** — route coordinates, markers, logbook days, summary
6. **Frontend renders** — interactive map with amber polyline + canvas log sheets

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

**Response** — route polyline, map markers with labels, multi-day logbook with HOS events, and trip statistics.

```
200 OK
{
  "route_coordinates": [[lon, lat], ...],
  "markers": [{ "type": "start|pickup|dropoff|fuel|rest", "lat": ..., "lon": ..., "label": "..." }],
  "logbook_days": [
    {
      "day": 1,
      "date": "06/29/2026",
      "events": [{ "status": "DRIVING", "start_time": "08:00", "end_time": "19:00", "duration_hours": 11, "label": "Driving to Pickup" }],
      "row_totals": { "driving_hours": 11, "on_duty_not_driving_hours": 1, ... }
    }
  ],
  "trip_summary": {
    "total_distance_miles": 966.9,
    "total_trip_hours": 29.6,
    "total_driving_hours": 17.1,
    "fuel_stops": 0,
    "rest_stops": 1
  }
}
```

---

## FMCSA Rules Enforced

| # | Rule | Value | What happens |
|---|------|-------|-------------|
| 1 | **Driving limit** | 11 hrs/shift | Rest reset enforced after 11h driving |
| 2 | **On-duty window** | 14 hrs/shift | Cannot drive after 14h on-duty |
| 3 | **Mandatory break** | 30 min after 8h driving | Break inserted automatically |
| 4 | **Cycle limit** | 70 hrs / 8 days | 34-hr reset if cycle is full |
| 5 | **Fuel stop** | Every 1,000 mi | 30-min ON_DUTY_NOT_DRIVING |
| 6 | **Pickup/Dropoff** | 1 hr each | ON_DUTY_NOT_DRIVING at each location |

---

## ELD Log Sheet

The `LogbookCanvas` renders realistic **FMCSA Form MCSA-5890** style log sheets:

```
┌──────────────────────────────────────────────────────────────┐
│  DRIVER'S DAILY LOG                                          │
│  Date: 06/29/2026    Carrier: LogRoute Transport             │
│  From: Chicago, IL   To: Dallas, TX                          │
│  Tractor: TRAC-001   Trailer: TRAIL-002                      │
├──────────────────────────────────────────────────────────────┤
│       │ 1  2  3  4  5  6  7  8  9  10 11 12 ... 24         │
│───────┼──────────────────────────────────────────────────────│
│Off    │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│Duty   │                                                      │
│───────┼──────────────────────────────────────────────────────│
│Sleeper│                                                      │
│Berth  │                                                      │
│───────┼──────────────────────────────────────────────────────│
│Driving│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓              │
│       │                                                      │
│───────┼──────────────────────────────────────────────────────│
│On-Duty│          ▓▓▓▓▓▓▓▓▓▓▓▓                                │
│Not Drv│                                                      │
├──────────────────────────────────────────────────────────────┤
│ REMARKS:  Chicago, IL (Pickup)                               │
│           Dallas, TX (Dropoff)                                │
├──────────────────────────────────────────────────────────────┤
│ A. On Duty Today: 12.0h   B. Available: 52.0h   C. 70h Cap│
└──────────────────────────────────────────────────────────────┘
```

- White paper background with black grid — authentic FMCSA look
- Colored duty status segments with duration labels
- Remarks section for location annotations
- Cycle recap (70hr/8-day tracking)
- Multi-day support with tab navigation
- Console-free, print-friendly

---

## Project Structure

```
logroute/
├── frontend/                         # React 19 + TypeScript + MUI
│   ├── src/
│   │   ├── components/
│   │   │   ├── TripForm.tsx          # Route planner form (4 inputs)
│   │   │   ├── TripResults.tsx       # Results dashboard
│   │   │   ├── RouteMap.tsx          # Interactive route map
│   │   │   ├── LogbookCanvas.tsx     # FMCSA ELD log sheet renderer
│   │   │   ├── ErrorAlert.tsx        # Error display
│   │   │   └── ui/                   # Reusable UI primitives
│   │   ├── hooks/                    # useTripPlanner, useEldColors, etc.
│   │   ├── lib/                      # API client, Zod schemas, logger
│   │   ├── store/                    # Zustand state
│   │   ├── types/                    # TypeScript interfaces
│   │   ├── theme.ts                  # Dark + amber MUI theme
│   │   ├── App.tsx                   # Main app with sidebar + map
│   │   └── main.tsx                  # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                          # Django 4.2 + DRF
│   ├── logroute/                     # Django project
│   │   ├── settings.py
│   │   ├── urls.py                   # API routes + SPA catch-all
│   │   └── wsgi.py
│   ├── trips/                        # Core app
│   │   ├── views.py                  # PlanRouteView, GeocodeSearchView
│   │   ├── serializers.py            # Request/response validation
│   │   ├── routing.py                # Nominatim + OSRM integration
│   │   ├── hos_engine.py             # FMCSA HOS rule simulator
│   │   ├── services.py               # TripPlanningService orchestrator
│   │   ├── error_handler.py          # Circuit breaker + retry logic
│   │   └── models.py                 # Trip model
│   ├── manage.py
│   └── requirements.txt
│
├── docker/
│   ├── Dockerfile                    # Multi-stage production build
│   └── docker-compose.yml            # PostgreSQL + Redis
│
├── scripts/
│   └── bootstrap.ps1                 # Windows one-click setup
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_CONTRACT.md
│   └── HOS_ENGINE.md
│
└── .env.example
```

---

## Deployment (single process)

Django serves the React build as static files — one process, one port, simple to deploy.

```bash
cd frontend && npm run build
cd ../backend && python manage.py collectstatic --noinput
gunicorn logroute.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## Development

```bash
# Backend commands (from backend/)
python manage.py runserver          # Start dev server
python manage.py test trips/        # Run tests
python manage.py shell              # Django shell
http://localhost:8000/api/docs/      # Swagger UI

# Frontend commands (from frontend/)
npm run dev                          # Vite dev server (port 3000)
npm run build                        # Production build
npm run test                         # Run tests
npm run lint                         # TypeScript check
```

---

## License

MIT
