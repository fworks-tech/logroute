"""
FMCSA HOS Reference API — serves structured reference data from the
Interstate Truck Driver's Guide to Hours of Service (April 2022).

These endpoints mirror the OpenAPI specification in
docs/fmcsahos395driversguidetohos2022042801.openapi.yaml.
"""

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .hos_reference import (
    COMPLIANCE_REQUIREMENTS,
    COMMERCE_DEFINITIONS,
    DUTY_STATUS_DEFINITIONS,
    HOS_EXCEPTIONS,
    HOS_LIMITS,
    HOS_SUMMARY,
    LOGGING_REQUIREMENTS,
    RESOURCE_LINKS,
)


class HosSummarySerializer(serializers.Serializer):
    """Serialize the HOS guide overview with title, audience, disclaimer, and regulation reference."""

    guide_title = serializers.CharField()
    audience = serializers.CharField()
    disclaimer = serializers.CharField()
    governing_regulation = serializers.CharField()


class HosSummaryView(APIView):
    """Return the FMCSA HOS guide overview and disclaimer."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return the FMCSA HOS guide overview."""
        serializer = HosSummarySerializer(data=HOS_SUMMARY)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ComplianceRequirementsSerializer(serializers.Serializer):
    """Serialize the conditions under which FMCSA HOS rules apply."""

    applies_when = serializers.ListField(child=serializers.CharField())
    key_reference = serializers.CharField()


class ComplianceRequirementsView(APIView):
    """Return the conditions under which FMCSA HOS rules apply."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return the FMCSA compliance requirements."""
        serializer = ComplianceRequirementsSerializer(data=COMPLIANCE_REQUIREMENTS)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CommerceDefinitionsSerializer(serializers.Serializer):
    """Serialize interstate and intrastate commerce definitions."""

    interstate = serializers.DictField()
    intrastate = serializers.DictField()


class CommerceDefinitionsView(APIView):
    """Return interstate and intrastate commerce definitions."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return the interstate and intrastate commerce definitions."""
        serializer = CommerceDefinitionsSerializer(data=COMMERCE_DEFINITIONS)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class DutyStatusDefinitionsSerializer(serializers.Serializer):
    """Serialize the definitions for on-duty, off-duty, personal conveyance, and yard moves."""

    on_duty = serializers.DictField()
    off_duty = serializers.DictField()
    personal_conveyance = serializers.DictField()
    yard_moves = serializers.DictField()


class DutyStatusDefinitionsView(APIView):
    """Return the definitions for on-duty, off-duty, personal conveyance, and yard moves."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return the duty status definitions."""
        serializer = DutyStatusDefinitionsSerializer(data=DUTY_STATUS_DEFINITIONS)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class HosLimitsSerializer(serializers.Serializer):
    """Serialize the core FMCSA HOS limits: 14-hr window, 11-hr drive, sleeper berth, 30-min break, weekly limit, restart."""

    fourteen_hour_window = serializers.DictField()
    eleven_hour_limit = serializers.DictField()
    sleeper_berth = serializers.DictField()
    thirty_minute_break = serializers.DictField()
    weekly_limit = serializers.DictField()
    restart = serializers.DictField()


class HosLimitsView(APIView):
    """Return the core FMCSA HOS limits (14-hr window, 11-hr drive, break, weekly cycle, restart)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return the HOS driving limits reference."""
        serializer = HosLimitsSerializer(data=HOS_LIMITS)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class HosExceptionSerializer(serializers.Serializer):
    """Serialize a single HOS exception with its conditions and CFR reference."""

    id = serializers.CharField()
    title = serializers.CharField()
    cfr_section = serializers.CharField()
    exception_type = serializers.ListField(child=serializers.CharField())
    conditions = serializers.ListField(child=serializers.CharField())
    notes = serializers.CharField(allow_null=True)


class HosExceptionsView(APIView):
    """Return all HOS exceptions, optionally filtered by query parameter."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return all HOS exceptions, optionally filtered by a category query parameter."""
        category = request.query_params.get("category")
        filtered = HOS_EXCEPTIONS
        if category:
            filtered = [e for e in filtered if category.lower() in e["title"].lower()]
        serializer = HosExceptionSerializer(data=filtered, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class HosExceptionDetailView(APIView):
    """Return a single HOS exception by its ID."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, exception_id):
        """Return a single HOS exception by its ID, or 404 if not found."""
        for exc in HOS_EXCEPTIONS:
            if exc["id"] == exception_id:
                serializer = HosExceptionSerializer(data=exc)
                serializer.is_valid(raise_exception=True)
                return Response(serializer.data)
        return Response(
            {"error": f"Exception '{exception_id}' not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


class LoggingRequirementsSerializer(serializers.Serializer):
    """Serialize the ELD logging requirements with primary method, paper-log allowances, and required RODS fields."""

    primary_method = serializers.CharField()
    eld_info_url = serializers.URLField()
    paper_log_allowed_when = serializers.ListField(child=serializers.CharField())
    required_rods_fields = serializers.ListField(child=serializers.CharField())


class LoggingRequirementsView(APIView):
    """Return ELD logging requirements and paper-log allowances."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return the ELD logging requirements."""
        serializer = LoggingRequirementsSerializer(data=LOGGING_REQUIREMENTS)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ResourceLinksSerializer(serializers.Serializer):
    """Serialize FMCSA resource links and contact information."""

    hos_web_page = serializers.URLField()
    eld_information = serializers.URLField()
    personal_conveyance_guidance = serializers.URLField()
    information_line = serializers.CharField()
    email = serializers.EmailField()


class ResourceLinksView(APIView):
    """Return helpful FMCSA resource links and contact information."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return the FMCSA resource links."""
        serializer = ResourceLinksSerializer(data=RESOURCE_LINKS)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
