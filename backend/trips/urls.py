from django.urls import path

from .reference_views import (
    CommerceDefinitionsView,
    ComplianceRequirementsView,
    DutyStatusDefinitionsView,
    HosExceptionDetailView,
    HosExceptionsView,
    HosLimitsView,
    HosSummaryView,
    LoggingRequirementsView,
    ResourceLinksView,
)
from .views import (
    GeocodeSearchView,
    PlanRouteView,
    TokenObtainView,
    UserRegistrationView,
)

urlpatterns = [
    # Trip planning
    path("plan-route/", PlanRouteView.as_view(), name="plan-route"),
    path("geocode/", GeocodeSearchView.as_view(), name="geocode-search"),
    # Auth
    path("auth/token/", TokenObtainView.as_view(), name="token-obtain"),
    path("auth/register/", UserRegistrationView.as_view(), name="user-register"),
    # FMCSA HOS Reference
    path("hos/summary/", HosSummaryView.as_view(), name="hos-summary"),
    path("hos/compliance/", ComplianceRequirementsView.as_view(), name="hos-compliance"),
    path("hos/commerce/", CommerceDefinitionsView.as_view(), name="hos-commerce"),
    path("hos/duty-status/", DutyStatusDefinitionsView.as_view(), name="hos-duty-status"),
    path("hos/limits/", HosLimitsView.as_view(), name="hos-limits"),
    path("hos/exceptions/", HosExceptionsView.as_view(), name="hos-exceptions"),
    path("hos/exceptions/<str:exception_id>/", HosExceptionDetailView.as_view(), name="hos-exception-detail"),
    path("hos/logging/", LoggingRequirementsView.as_view(), name="hos-logging"),
    path("hos/resources/", ResourceLinksView.as_view(), name="hos-resources"),
]
