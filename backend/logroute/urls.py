"""Root URL configuration — health check, API proxy, OpenAPI schema, Swagger UI, and SPA fallback."""

from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    """Return a simple JSON health-check response."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check),
    path("api/", include("trips.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("", TemplateView.as_view(template_name="index.html")),
]
