class TripPlanningError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class GeocodingError(TripPlanningError):
    def __init__(self, message: str = "Geocoding failed", details: dict | None = None):
        super().__init__(message, status_code=422, details=details)


class RoutingError(TripPlanningError):
    def __init__(self, message: str = "Routing failed", details: dict | None = None):
        super().__init__(message, status_code=422, details=details)


class CircuitOpenError(TripPlanningError):
    def __init__(self, service: str, details: dict | None = None):
        super().__init__(
            f"Circuit breaker open for {service}",
            status_code=503,
            details=details or {"service": service},
        )
