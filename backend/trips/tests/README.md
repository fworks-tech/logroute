# Tests — Organized by Clean Architecture Layer

## Structure

| Directory | Django? | Speed | What it tests |
|-----------|---------|-------|---------------|
| `domain/` | No | ~ms | Pure domain functions on dataclasses. No mocks. Run without Django. |
| `application/` | No | ~ms | Use cases with in-memory test doubles (FakeGeocoder, FakeRouter, etc.). Run without Django. |
| `integration/` | Yes | ~sec | Full HTTP stack via DRF `APIClient`. Mock at the HTTP boundary. |

## Running

```bash
pytest -m unit          # domain + application (fast)
pytest -m integration   # integration only
pytest                  # all (70% coverage threshold)
```
