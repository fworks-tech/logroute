from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from trips.application.use_cases.get_hos_reference import HosReferenceUseCase
from trips.adapters.repositories.hos_reference_repository import StaticDataHosReferenceRepository
from trips.adapters.serializers.reference import (
    CommerceDefinitionsSerializer,
    ComplianceRequirementsSerializer,
    DutyStatusDefinitionsSerializer,
    HosExceptionSerializer,
    HosLimitsSerializer,
    HosSummarySerializer,
    LoggingRequirementsSerializer,
    ResourceLinksSerializer,
)


class HosSummaryView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        serializer = HosSummarySerializer(data=use_case.get_summary())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ComplianceRequirementsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        serializer = ComplianceRequirementsSerializer(data=use_case.get_compliance_requirements())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CommerceDefinitionsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        serializer = CommerceDefinitionsSerializer(data=use_case.get_commerce_definitions())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class DutyStatusDefinitionsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        serializer = DutyStatusDefinitionsSerializer(data=use_case.get_duty_status_definitions())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class HosLimitsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        serializer = HosLimitsSerializer(data=use_case.get_limits())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class HosExceptionsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        category = request.query_params.get("category")
        exceptions = use_case.get_exceptions(category)
        serializer = HosExceptionSerializer(data=exceptions, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class HosExceptionDetailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, exception_id):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        exc = use_case.get_exception_by_id(exception_id)
        if exc is not None:
            serializer = HosExceptionSerializer(data=exc)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        return Response(
            {"error": f"Exception '{exception_id}' not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


class LoggingRequirementsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        serializer = LoggingRequirementsSerializer(data=use_case.get_logging_requirements())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ResourceLinksView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        use_case = HosReferenceUseCase(StaticDataHosReferenceRepository())
        serializer = ResourceLinksSerializer(data=use_case.get_resource_links())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
