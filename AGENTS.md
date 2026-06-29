# LogRoute — Agent Guide

## Quick start

```bash
# Backend
cd backend
python -m venv venv && .\venv\Scripts\activate  # Windows, or source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Backend on `:8000`, frontend on `:3000` (proxies `/api` to backend).

**Live app:** https://logroute-app.vercel.app
**GitHub:** https://github.com/fworks-tech/logroute

## Commands

| Scope | Command | What it does |
|-------|---------|-------------|
| Frontend | `npm run dev` | Vite dev server (`:3000`) |
| Frontend | `npm run build` | `tsc && vite build` |
| Frontend | `npm run lint` | `tsc --noEmit` (no ESLint configured) |
| Frontend | `npm run test` | `vitest` (watch mode) |
| Frontend | `npm run test:unit` | `vitest --run` (single run) |
| Frontend | `npm run test:e2e` | `playwright test` |
| Frontend | `npm run generate:api-client` | Regenerates API client from schema |
| Backend | `pytest` | Coverage threshold 70%, verbose, HTML report |
| Backend | `pytest -m unit` | Unit tests only |
| Backend | `pytest -m "not slow"` | Skip slow tests |
| Backend | `coverage html` | Generate coverage report |
| Docker | `docker compose -f docker/docker-compose.yml up -d` | Start PostgreSQL + Redis |

## Architecture

**Monorepo with no workspace tooling** — two independent sub-projects under `backend/` and `frontend/`.

**Backend**: Django 4.2 + DRF 3.15. Entry: `backend/manage.py`. Core app is `trips/`.

**Frontend**: Vite 6 + React 19 + TypeScript 5.5 + MUI 6. Entry: `frontend/src/main.tsx`.

**External dependencies**: Nominatim (geocoding), OSRM (routing) — both free OSM services. The backend calls them with caching (24h/48h), retry (3 attempts, exponential backoff), and circuit breakers (failure threshold: 5, recovery: 60s).

## Key flows

**Route planning**: TripForm → `POST /api/plan-route/` → geocode 3 locations → OSRM route → HOS simulation → return route + logbook days + trip summary. HOS engine (`trips/hos_engine.py`) simulates FMCSA rules: 11h drive limit, 14h window, 30min break after 8h, 10h reset, 70h/8-day cycle, 30min fuel stops every 1000mi, 1h pickup/dropoff.

## Conventions & gotchas

- **`npm install --legacy-peer-deps`** is required (React 19 + MUI 6 peer dep conflicts).
- **No ESLint.** Linting is `tsc --noEmit` only. `noUnusedLocals` and `noUnusedParameters` are `true` — unused vars fail lint.
- **`@/`** path alias in frontend maps to `frontend/src/`.
- **API client** under `frontend/src/lib/api-client/` is auto-generated (`npm run generate:api-client`). Manual changes there will be overwritten.
- **Zustand store** at `frontend/src/store/tripStore.ts` manages trip results, loading state, errors, and session history.
- **TanStack Query** configured with `staleTime: 60000`, `retry: 1` in `main.tsx`.
- **Auth**: SimpleJWT with access (60min) and refresh (7d) tokens.
- **Database**: Auto-detects PostgreSQL from `DATABASE_URL`, falls back to SQLite.
- **Cache**: In-memory `LocMemCache` by default, switches to Redis if `REDIS_URL` is set.
- **Test coverage**: backend pytest enforces 70% min (`--cov-fail-under=70`). HTML report written to `backend/htmlcov/`.
- **No CI workflows** exist yet. No pre-commit hooks configured.
- **Docker** for infra only (PostgreSQL + Redis). Dev workflow runs via `manage.py runserver` + `npm run dev`.
- **React app** is served as a single Django TemplateView in production (build goes to `frontend/dist/`, Django serves it after `collectstatic`).
