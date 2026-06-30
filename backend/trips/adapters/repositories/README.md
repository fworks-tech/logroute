# Repositories — Port Implementations

Concrete implementations of the repository port interfaces defined in
`domain/ports.py`. One file per port.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `trip_repository.py` | `DjangoOrmTripRepository(TripRepository)`. Maps between domain entities (`TripPlan`, `Location`) and the Django ORM `Trip` model. All Django ORM access is confined here. |
| `hos_reference_repository.py` | `StaticDataHosReferenceRepository(HosReferenceRepository)`. Reads from the static dicts/lists in `domain/hos_reference.py`. |
