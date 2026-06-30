import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from trips.domain.exceptions import TripPlanningError
from trips.application.use_cases.plan_route import PlanRouteUseCase, PlanRouteRequest
from trips.application.use_cases.geocode_search import GeocodeSearchUseCase, GeocodeSearchRequest
from trips.adapters.gateways.nominatim import NominatimGeocoder
from trips.adapters.gateways.osrm import OSRMRouter
from trips.adapters.cache.django_cache import DjangoCache
from trips.adapters.serializers.trip import TripInputSerializer
from trips.throttles import PlanRouteThrottle

logger = logging.getLogger("logroute.controllers.trip")


class PlanRouteView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PlanRouteThrottle]

    def post(self, request):
        serializer = TripInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        use_case = PlanRouteUseCase(
            geocoder=NominatimGeocoder(),
            router=OSRMRouter(),
            cache=DjangoCache(),
        )
        req = PlanRouteRequest(
            current_location=data["current_location"],
            pickup_location=data["pickup_location"],
            dropoff_location=data["dropoff_location"],
            cycle_hours_used=data["cycle_hours_used"],
            start_date=data.get("trip_date"),
            cycle_schedule=data.get("cycle_schedule", "70"),
        )
        try:
            result = use_case.execute(req)
            return Response({
                "route_coordinates": result.route_coordinates,
                "markers": result.markers,
                "logbook_days": result.logbook_days,
                "trip_summary": result.trip_summary,
                "trip_date": data.get("trip_date"),
                "tractor_number": data.get("tractor_number", ""),
                "trailer_number": data.get("trailer_number", ""),
                "shipper_name": data.get("shipper_name", ""),
                "cycle_schedule": result.cycle_schedule,
                "cycle_max_hours": result.cycle_max_hours,
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

        use_case = GeocodeSearchUseCase(
            geocoder=NominatimGeocoder(),
            cache=DjangoCache(),
        )
        try:
            result = use_case.execute(GeocodeSearchRequest(query=query))
            return Response(result.results, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Geocode search failed for query: %s", query)
            return Response([], status=status.HTTP_200_OK)
