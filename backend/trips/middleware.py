import logging
import time
import uuid
from contextvars import ContextVar

from django.http import JsonResponse

logger = logging.getLogger("logroute.requests")

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestLoggingMiddleware:
    """Middleware that logs every request with a unique ID, method, path, status, and duration."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = uuid.uuid4().hex[:12]
        request_id_var.set(request_id)

        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = round((time.monotonic() - start) * 1000, 1)

        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        response["X-Request-ID"] = request_id
        return response


class ErrorHandlingMiddleware:
    """Middleware that catches unhandled exceptions and returns a JSON 500 response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        request_id = request_id_var.get("")
        logger.exception(
            "unhandled_exception",
            extra={"request_id": request_id, "path": request.path},
        )
        return JsonResponse(
            {"error": "Internal server error", "request_id": request_id},
            status=500,
        )
