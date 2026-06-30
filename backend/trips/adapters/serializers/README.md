# Serializers — DRF Request/Response Serialization

Maps between HTTP JSON payloads and application DTOs.
Thin validation layer — complex validation rules live in the use cases or domain.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `trip.py` | `TripInputSerializer` (request validation), `TripSerializer` (full model serializer), `TripListSerializer` (lightweight list view). |
| `auth.py` | `CustomTokenObtainPairSerializer` (JWT with email/username claims), `UserRegistrationSerializer` (user creation). |
| `reference.py` | 8 serializers matching the FMCSA HOS reference data shapes: `HosSummarySerializer`, `HosLimitsSerializer`, `HosExceptionSerializer`, etc. |
