# LogRoute Frontend

React 19 single-page application for FMCSA-compliant ELD logbook and route planning. Dark-themed, interactive map, canvas-based log sheets with PDF export.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Build | Vite 6 |
| UI | React 19, TypeScript 5.5, Material-UI 6, Emotion |
| State | TanStack Query 5 (server), Zustand 5 (client) |
| Forms | react-hook-form 7 + Zod 3 + @hookform/resolvers |
| Maps | Leaflet 1.9 + react-leaflet 5 + CartoDB dark tiles |
| Logbook | HTML5 Canvas (960×780, 15-min grid) + jsPDF 4.2 export |
| Charts | Recharts 2.12 (daily hours breakdown) |
| Animations | Motion 12 |
| HTTP | Axios 1.7 with correlation IDs + PII redaction logging |
| Testing | Vitest (unit), Playwright 1.60 (e2e) |

## Prerequisites

- Node 18+
- LogRoute backend running on `http://localhost:8000`

## Setup

```bash
cd frontend
npm install --legacy-peer-deps   # Required: React 19 + MUI 6 peer dep conflicts
npm run dev                      # Vite dev server on http://localhost:3000
```

Vite proxies `/api/*` requests to `http://localhost:8000` (configured in `vite.config.ts`).

## Commands

```bash
npm run dev                     # Dev server (:3000), proxies /api to :8000
npm run build                   # tsc && vite build → frontend/dist/
npm run lint                    # tsc --noEmit (no ESLint configured)
npm run test                    # vitest (watch mode)
npm run test:unit               # vitest --run (single run)
npm run test:e2e                # playwright test
npm run generate:api-client     # Regenerate API client from backend schema
npm run preview                 # Preview production build
```

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx                # App entry: React 19 + TanStack Query + Theme + ErrorBoundary
│   ├── App.tsx                 # Root layout: sidebar (440px) + full-screen Leaflet map
│   ├── index.css               # Leaflet CSS import + base styles
│   ├── theme.ts                # MUI 6 dark theme (amber #f59e0b primary, ELD colors)
│   ├── components/
│   │   ├── TripForm.tsx         # 3-location form with geocode autocomplete + Zod validation
│   │   ├── TripResults.tsx      # Trip summary stats + route map + daily breakdown + logbook
│   │   ├── LogbookCanvas.tsx    # HTML5 Canvas FMCSA log sheet (960×780, 15-min grid, PDF export)
│   │   ├── RouteMap.tsx         # Leaflet map with amber polyline, SVG markers, legend
│   │   ├── SessionPanel.tsx     # Session history popover with 70hr cycle tracker
│   │   ├── ErrorBoundary.tsx    # Class-based error boundary with retry
│   │   ├── ErrorAlert.tsx       # Alert with retry/dismiss for retryable API errors
│   │   └── ui/                 # Reusable UI primitives
│   │       ├── LoadingButton.tsx    # Button with spinner
│   │       ├── StatCard.tsx         # Metric card (icon + value + label)
│   │       ├── SectionPaper.tsx     # Section wrapper (title + divider + content)
│   │       ├── StatusChip.tsx       # Color-coded duty status chip
│   │       └── LogbookDayDetail.tsx # Accordion table of day events
│   ├── hooks/
│   │   ├── useTripPlanner.ts   # TanStack Query mutation → planRoute API call
│   │   ├── useGeocodeSearch.ts # Debounced geocode autocomplete (300ms, min 2 chars)
│   │   ├── useLogbookNavigation.ts  # Multi-day logbook tabs (prev/next)
│   │   ├── useEldColors.ts     # Duty status color constants
│   │   └── useResponsive.ts    # MUI breakpoint helpers
│   ├── store/
│   │   └── tripStore.ts        # Zustand store: result, loading, error, sessionTrips
│   ├── lib/
│   │   ├── api.ts              # Axios client + request/response logging + PII redaction
│   │   ├── schema.ts           # Zod schema for trip form validation
│   │   ├── logger.ts           # Custom Logger with correlation IDs, dev styling, prod JSON
│   │   ├── redaction.ts        # PII redaction (locations, coordinates, keys, phone, email)
│   │   ├── mapConfig.ts        # Marker config (colors, emoji, labels)
│   │   └── api-client/         # Auto-generated (DO NOT EDIT) — regenerate with generate:api-client
│   └── types/
│       └── trip.ts             # TypeScript types (RouteCoordinate, LogbookDay, TripSummary, etc.)
├── index.html                  # HTML entry: Leaflet CSS CDN, Google Fonts, Inter
├── vite.config.ts              # Vite config: React plugin, @/ alias, /api proxy
├── tsconfig.json               # Strict TS, noUnusedLocals/Parameters: true, @/* path alias
└── package.json
```

## Architecture

### Data flow

```
TripForm (Zod validation) 
  → useTripPlanner (TanStack Query mutation)
    → planRoute() (Axios POST /api/plan-route/)
      → Backend processes (geocode → OSRM → HOS)
    → Zustand store updated (setResult)
  → TripResults renders (summary + map + logbook)
  → Session history updated (addSessionTrip)
```

### State management

- **Server state**: TanStack Query (`staleTime: 60s`, `retry: 1`) manages the plan-route API call
- **Client state**: Zustand store (`tripStore.ts`) holds the current result, loading state, error object, and session trip list
- **Form state**: react-hook-form with Zod schema validation (3 locations: 2–500 chars, cycle hours: 0–69.5)

### Key features

- **Geocode autocomplete**: Debounced (300ms) search via `/api/geocode/`, Nominatim limited to US, 5 results
- **Route map**: CartoDB dark tiles, amber polyline (weight 4), SVG drop-pin markers with first-letter labels, legend, fit-bounds
- **ELD Logbook**: Canvas-rendered FMCSA Form LM-1 (960×780), 24-hour grid with 15-minute tick marks, colored duty segments, row totals, recap, remarks, multi-day navigation with tabs, PDF download via jsPDF
- **Session history**: Zustand-persisted list of planned trips with cumulative hours tracker (70hr cycle warning)

### Production build

`npm run build` → `frontend/dist/`. Django serves `/` as a `TemplateView` pointing to `index.html`, and `collectstatic` copies assets to `staticfiles/` for Gunicorn. Single-process deployment.

## Conventions

- **No ESLint**. Linting = `tsc --noEmit`. Unused locals/params flagged (`noUnusedLocals`, `noUnusedParameters`).
- **`@/`** path alias → `frontend/src/`
- **API client** under `lib/api-client/` is auto-generated. Manual edits will be overwritten.
- **`npm install --legacy-peer-deps`** required every time (React 19 + MUI 6 conflict).
- Component, hook, and UI primitive barrel exports at `index.ts` in each directory.

## Testing

```bash
npm run test:unit                # Vitest all tests
npm run test:e2e                 # Playwright (e2e/ dir currently empty)
npm run lint                     # tsc --noEmit type-check
```

No component tests exist yet. The `e2e/` directory is a placeholder for Playwright tests.

## Environment

| Variable | Default | Notes |
|----------|---------|-------|
| `VITE_API_URL` | `http://localhost:8000` | Backend base URL (used by API client) |

The dev server proxies `/api/*` to `localhost:8000`, so the app works without setting `VITE_API_URL` in development.
