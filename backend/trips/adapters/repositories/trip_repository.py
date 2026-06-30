from trips.models import Trip


class DjangoOrmTripRepository:
    def save(self, trip_data: dict) -> int:
        obj = Trip.objects.create(**trip_data)
        return obj.pk

    def get_by_id(self, trip_id: int, user_id: int) -> dict | None:
        try:
            trip = Trip.objects.get(pk=trip_id, user_id=user_id)
        except Trip.DoesNotExist:
            return None
        return self._to_dict(trip)

    def list_by_user(self, user_id: int, limit: int = 20) -> list[dict]:
        qs = Trip.objects.filter(user_id=user_id).order_by("-created_at")[:limit]
        return [self._to_dict(t) for t in qs]

    @staticmethod
    def _to_dict(trip: Trip) -> dict:
        return {
            "id": trip.pk,
            "current_location": trip.current_location,
            "pickup_location": trip.pickup_location,
            "dropoff_location": trip.dropoff_location,
            "cycle_hours_used": float(trip.cycle_hours_used),
            "cycle_schedule": trip.cycle_schedule,
            "trip_date": trip.trip_date,
            "tractor_number": trip.tractor_number,
            "trailer_number": trip.trailer_number,
            "shipper_name": trip.shipper_name,
            "route_coordinates": trip.route_coordinates,
            "markers": trip.markers,
            "logbook_days": trip.logbook_days,
            "trip_summary": trip.trip_summary,
            "status": trip.status,
            "created_at": trip.created_at.isoformat() if trip.created_at else None,
            "updated_at": trip.updated_at.isoformat() if trip.updated_at else None,
        }
