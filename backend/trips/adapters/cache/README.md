# Cache Adapter

Implements the `CacheService` port defined in `domain/ports.py`.
The only file in the codebase that directly imports `django.core.cache`.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `django_cache.py` | `DjangoCache(CacheService)`. Wraps Django's cache framework with `get(key)`, `set(key, value, timeout)`, `delete(key)` methods matching the domain port protocol. |
