# Controllers — DRF API Views

Thin HTTP layer. Each view:
1. Parses and validates the request (via DRF serializers)
2. Constructs a use case with concrete adapter dependencies (manual DI)
3. Calls the use case
4. Returns the response

No business logic here — all decisions belong in `application/use_cases/`.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `trip_controller.py` | `PlanRouteView` (POST /api/plan-route/), `GeocodeSearchView` (GET /api/geocode/). |
| `auth_controller.py` | `TokenObtainView` (POST /api/auth/token/), `UserRegistrationView` (POST /api/auth/register/). |
| `reference_controller.py` | All 8 HOS reference views: summary, compliance, commerce, duty-status, limits, exceptions (list + detail), logging, resources. |
