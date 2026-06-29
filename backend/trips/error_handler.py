import logging
import time
from dataclasses import dataclass, field
from functools import wraps
from threading import Lock

logger = logging.getLogger("logroute.errors")


class TripPlanningError(Exception):
    """Base exception for trip planning failures with HTTP status code and optional details."""

    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class GeocodingError(TripPlanningError):
    """Raised when the geocoding service (Nominatim) cannot resolve a location."""

    def __init__(self, message: str = "Geocoding failed", details: dict | None = None):
        super().__init__(message, status_code=422, details=details)


class RoutingError(TripPlanningError):
    """Raised when the OSRM routing service cannot compute a route."""

    def __init__(self, message: str = "Routing failed", details: dict | None = None):
        super().__init__(message, status_code=422, details=details)


class CircuitOpenError(TripPlanningError):
    """Raised when a circuit breaker is open and the service call is blocked."""

    def __init__(self, service: str, details: dict | None = None):
        super().__init__(
            f"Circuit breaker open for {service}",
            status_code=503,
            details=details or {"service": service},
        )


@dataclass
class RetryConfig:
    """Configuration for the exponential-backoff retry decorator."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    retryable_exceptions: tuple = (Exception,)


def with_retry(config: RetryConfig | None = None):
    """Decorator that retries a function with exponential backoff on failure.

    Args:
        config: A RetryConfig instance controlling retry behaviour.

    Returns:
        A decorator that wraps the target function with retry logic.
    """
    config = config or RetryConfig()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.base_delay

            for attempt in range(1, config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as exc:
                    last_exception = exc
                    if attempt == config.max_retries:
                        break
                    logger.warning(
                        "retry",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "delay": delay,
                            "error": str(exc),
                        },
                    )
                    time.sleep(delay)
                    delay = min(delay * config.backoff_factor, config.max_delay)

            raise last_exception

        return wrapper

    return decorator


class CircuitBreaker:
    """Thread-safe circuit breaker that opens after a configurable failure threshold.

    Attributes:
        CLOSED: Normal operational state.
        OPEN: Service calls are blocked.
        HALF_OPEN: Trial state after recovery timeout to test if the service has recovered.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, service_name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """Initialise the circuit breaker.

        Args:
            service_name: Human-readable name for the downstream service.
            failure_threshold: Consecutive failures required to open the circuit.
            recovery_timeout: Seconds after which an open circuit transitions to half-open.
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = self.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._lock = Lock()

    @property
    def state(self) -> str:
        with self._lock:
            if self._state == self.OPEN and self._last_failure_time is not None:
                if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                    self._state = self.HALF_OPEN
            return self._state

    def record_success(self):
        """Record a successful call and reset the failure count back to closed state."""
        with self._lock:
            self._failure_count = 0
            self._state = self.CLOSED

    def record_failure(self):
        """Record a failed call and open the circuit if the failure threshold is reached."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._failure_count >= self.failure_threshold:
                self._state = self.OPEN
                logger.warning(
                    "circuit_open",
                    extra={"service": self.service_name, "failures": self._failure_count},
                )

    def execute(self, func, *args, **kwargs):
        """Execute a function under circuit-breaker protection.

        Args:
            func: The callable to execute.
            *args: Positional arguments forwarded to func.
            **kwargs: Keyword arguments forwarded to func.

        Returns:
            The return value of func.

        Raises:
            CircuitOpenError: If the circuit is open.
        """
        current_state = self.state
        if current_state == self.OPEN:
            raise CircuitOpenError(self.service_name)
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except CircuitOpenError:
            raise
        except Exception:
            self.record_failure()
            raise


nominatim_breaker = CircuitBreaker("nominatim", failure_threshold=5, recovery_timeout=60)
osrm_breaker = CircuitBreaker("osrm", failure_threshold=5, recovery_timeout=60)
