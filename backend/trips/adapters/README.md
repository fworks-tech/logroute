# Interface Adapters Layer

Converts between the use-case/DTO world and external frameworks.
Depends on `domain/` (for port interfaces and entities) and `application/`
(for use cases and DTOs).

## Sub-packages

| Package | Purpose |
|---------|---------|
| `controllers/` | DRF API views — thin HTTP handlers that parse requests, construct use cases with concrete adapters, call use cases, and return responses. |
| `serializers/` | DRF serializers — request validation and response formatting, mapping between HTTP payloads and application DTOs. |
| `repositories/` | Implementations of domain port interfaces that talk to Django ORM or static data. |
| `gateways/` | Implementations of domain port interfaces that talk to external APIs (Nominatim, OSRM) via HTTP. |
| `cache/` | Implementation of the `CacheService` port wrapping `django.core.cache`. |
