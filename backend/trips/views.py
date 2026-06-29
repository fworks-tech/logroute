import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .error_handler import TripPlanningError
from .models import Trip
from .routing import geocode_search
from .serializers import (
    CustomTokenObtainPairSerializer,
    HealthCheckSerializer,
    TripInputSerializer,
    UserRegistrationSerializer,
)
from .services import TripPlanningService
from .throttles import AuthThrottle, PlanRouteThrottle

logger = logging.getLogger("logroute.views")


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = HealthCheckSerializer(data={"status": "ok"})
        serializer.is_valid()
        return Response(serializer.data)


class PlanRouteView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PlanRouteThrottle]

    def post(self, request):
        serializer = TripInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            result = TripPlanningService.plan_route(
                current_location=data["current_location"],
                pickup_location=data["pickup_location"],
                dropoff_location=data["dropoff_location"],
                cycle_hours_used=data["cycle_hours_used"],
                start_date=data.get("trip_date"),
                cycle_schedule=data.get("cycle_schedule", "70"),
            )
            return Response({
                "route_coordinates": result["route_coordinates"],
                "markers": result["markers"],
                "logbook_days": result["logbook_days"],
                "trip_summary": result["trip_summary"],
                "trip_date": data.get("trip_date"),
                "tractor_number": data.get("tractor_number", ""),
                "trailer_number": data.get("trailer_number", ""),
                "shipper_name": data.get("shipper_name", ""),
                "cycle_schedule": result.get("cycle_schedule", "70"),
                "cycle_max_hours": result.get("cycle_max_hours", 70),
            })
        except TripPlanningError as exc:
            return Response(
                {"error": str(exc), "details": getattr(exc, "details", str(exc))},
                status=getattr(exc, "status_code", status.HTTP_502_BAD_GATEWAY),
            )


class GeocodeSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 2:
            return Response([], status=status.HTTP_200_OK)

        try:
            results = geocode_search(query)
            return Response(results, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Geocode search failed for query: %s", query)
            return Response([], status=status.HTTP_200_OK)


class TokenObtainView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )

