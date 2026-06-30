import logging
import time
from dataclasses import dataclass, field
from functools import wraps
from threading import Lock

from trips.domain.exceptions import CircuitOpenError

logger = logging.getLogger("logroute.resilience")


@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    retryable_exceptions: tuple = (Exception,)


def with_retry(config: RetryConfig | None = None):
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
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, service_name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0):
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
        with self._lock:
            self._failure_count = 0
            self._state = self.CLOSED

    def record_failure(self):
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
