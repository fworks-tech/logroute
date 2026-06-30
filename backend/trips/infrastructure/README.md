# Infrastructure Layer — Framework & Cross-Cutting Concerns

The outermost layer. Contains code that is tightly coupled to Django,
DRF, or the execution environment. Cannot be imported by `domain/`,
`application/`, or `adapters/` (except via injection).

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `resilience.py` | `CircuitBreaker(service_name, failure_threshold, recovery_timeout)` — thread-safe state machine. `RetryConfig` + `with_retry` decorator — exponential backoff. Both used by gateways. |
| `middleware.py` | Django middleware: request ID injection (`X-Request-ID`), request timing, `JsonResponse` for 500 errors. Kept from the original codebase. |
