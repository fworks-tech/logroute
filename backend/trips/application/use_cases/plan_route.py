from datetime import date

from trips.domain.hos_engine import simulate_trip
from trips.application.dto import PlanRouteRequest, PlanRouteResponse


class PlanRouteUseCase:
    def __init__(self, geocoder, router, cache):
        self._geocoder = geocoder
        self._router = router
        self._cache = cache

    def execute(self, request: PlanRouteRequest) -> PlanRouteResponse:
        cache_key = self._make_cache_key(request)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return PlanRouteResponse(**cached)

        current_ll = self._geocoder.geocode(request.current_location)
        pickup_ll = self._geocoder.geocode(request.pickup_location)
        dropoff_ll = self._geocoder.geocode(request.dropoff_location)

        route = self._router.get_route(current_ll, pickup_ll, dropoff_ll)

        leg1 = route["legs"][0]
        leg2 = route["legs"][1]
        total_miles = leg1["distance_miles"] + leg2["distance_miles"]

        logbook = simulate_trip(
            total_distance_miles=total_miles,
            leg1_hours=leg1["duration_hours"],
            leg2_hours=leg2["duration_hours"],
            current_cycle_used_hours=request.cycle_hours_used,
            leg1_miles=leg1["distance_miles"],
            leg2_miles=leg2["distance_miles"],
            start_date=request.start_date,
            from_location=request.current_location,
            pickup_location=request.pickup_location,
            to_location=request.dropoff_location,
            cycle_schedule=request.cycle_schedule,
        )

        if cache_key:
            self._cache.set(cache_key, self._to_cachable(logbook, route, leg1, leg2, total_miles, current_ll, pickup_ll, dropoff_ll, request), 86400)

        return self._build_response(logbook, route, leg1, leg2, total_miles, current_ll, pickup_ll, dropoff_ll, request)

    def _build_response(self, logbook, route, leg1, leg2, total_miles, current_ll, pickup_ll, dropoff_ll, request):
        event_times = self._build_event_times(logbook)
        markers = self._build_markers(current_ll, pickup_ll, dropoff_ll, event_times, request)
        stop_markers = self._build_stop_markers(route["coordinates"], logbook)
        markers.extend(stop_markers)
        logbook_days = self._transform_logbook(logbook)

        return PlanRouteResponse(
            route_coordinates=route["coordinates"],
            leg1=leg1,
            leg2=leg2,
            total_miles=total_miles,
            markers=markers,
            logbook_days=logbook_days,
            cycle_schedule=logbook.get("cycle_schedule", "70"),
            cycle_max_hours=logbook.get("cycle_max_hours", 70),
            trip_summary={
                "total_distance_miles": round(total_miles, 1),
                "total_trip_hours": round(logbook["total_trip_hours"], 1),
                "total_driving_hours": round(logbook["total_driving_hours"], 1),
                "total_drive_hours": round(logbook["total_driving_hours"], 1),
                "legs": 2,
                "rest_stops": logbook["num_rest_stops"],
                "fuel_stops": logbook["num_fuel_stops"],
                "num_fuel_stops": logbook["num_fuel_stops"],
                "num_rest_stops": logbook["num_rest_stops"],
                "leg_1_miles": round(leg1["distance_miles"], 1),
                "leg_2_miles": round(leg2["distance_miles"], 1),
            },
            locations={
                "current": {"ll": current_ll, "name": request.current_location},
                "pickup": {"ll": pickup_ll, "name": request.pickup_location},
                "dropoff": {"ll": dropoff_ll, "name": request.dropoff_location},
            },
        )

    @staticmethod
    def _build_event_times(logbook):
        event_times = {}
        for day in logbook.get("logbook_days", []):
            for ev in day.get("events", []):
                label_key = ev.get("label", "").lower()
                if label_key and label_key not in event_times:
                    h = int(ev["start_hour"])
                    m = int((ev["start_hour"] - h) * 60)
                    event_times[label_key] = f"{h:02d}:{m:02d}"
        return event_times

    @staticmethod
    def _build_markers(current_ll, pickup_ll, dropoff_ll, event_times, request):
        return [
            {
                "id": "start",
                "lat": current_ll[0],
                "lon": current_ll[1],
                "type": "start",
                "label": request.current_location,
                "time": event_times.get("driving") or event_times.get(request.current_location.lower(), ""),
            },
            {
                "id": "pickup",
                "lat": pickup_ll[0],
                "lon": pickup_ll[1],
                "type": "pickup",
                "label": request.pickup_location,
                "time": event_times.get("pickup", ""),
            },
            {
                "id": "dropoff",
                "lat": dropoff_ll[0],
                "lon": dropoff_ll[1],
                "type": "dropoff",
                "label": request.dropoff_location,
                "time": event_times.get("dropoff", ""),
            },
        ]

    @staticmethod
    def _build_stop_markers(coordinates, logbook):
        total_trip_hours = logbook.get("total_trip_hours", 0)
        if total_trip_hours <= 0 or not coordinates:
            return []
        all_events = []
        for day in logbook.get("logbook_days", []):
            day_offset_hours = day["date_offset"] * 24.0
            for ev in day.get("events", []):
                marker_type = ev.get("marker_type", "")
                if not marker_type:
                    continue
                hours = int(ev["start_hour"] + day_offset_hours)
                minutes = int((ev["start_hour"] + day_offset_hours - hours) * 60)
                all_events.append({
                    "label": ev["label"],
                    "abs_start": ev["start_hour"] + day_offset_hours,
                    "time": f"{hours % 24:02d}:{minutes:02d}",
                    "marker_type": marker_type,
                })
        markers = []
        n = len(coordinates)
        for i, ev in enumerate(all_events):
            fraction = ev["abs_start"] / total_trip_hours
            fraction = max(0.0, min(1.0, fraction))
            idx = int(fraction * (n - 1))
            lon, lat = coordinates[idx]
            markers.append({
                "id": f"stop-{i}",
                "lat": lat,
                "lon": lon,
                "type": ev["marker_type"],
                "label": ev["label"],
                "time": ev["time"],
            })
        return markers

    @staticmethod
    def _transform_logbook(logbook):
        logbook_days_transformed = []
        for day in logbook["logbook_days"]:
            events_transformed = []
            for ev in day["events"]:
                start_hours = int(ev["start_hour"])
                start_mins = int((ev["start_hour"] - start_hours) * 60)
                end_hours = int(ev["end_hour"])
                end_mins = int((ev["end_hour"] - end_hours) * 60)
                marker_type = ev.get("marker_type", "")
                transformed = {
                    "status": ev["status"],
                    "start_time": f"{start_hours:02d}:{start_mins:02d}",
                    "end_time": f"{end_hours:02d}:{end_mins:02d}",
                    "duration_hours": round(ev["end_hour"] - ev["start_hour"], 2),
                    "label": ev["label"],
                    "location": ev.get("location", ""),
                }
                if marker_type:
                    transformed["marker_type"] = marker_type
                events_transformed.append(transformed)
            logbook_days_transformed.append({
                "day": day["day"],
                "date_offset": day["date_offset"],
                "date": day["date"],
                "from_location": day["from_location"],
                "to_location": day["to_location"],
                "daily_miles": day["daily_miles"],
                "cumulative_miles": day["cumulative_miles"],
                "total_driving_hours": day["total_driving_hours"],
                "total_on_duty_hours": day["total_on_duty_hours"],
                "cycle_hours_after_day": day["cycle_hours_after_day"],
                "row_totals": day["row_totals"],
                "events": events_transformed,
            })
        return logbook_days_transformed

    @staticmethod
    def _to_cachable(logbook, route, leg1, leg2, total_miles, current_ll, pickup_ll, dropoff_ll, request):
        return {
            "route_coordinates": route["coordinates"],
            "leg1": leg1,
            "leg2": leg2,
            "total_miles": total_miles,
            "cycle_schedule": logbook.get("cycle_schedule", "70"),
            "cycle_max_hours": logbook.get("cycle_max_hours", 70),
            "locations": {
                "current": {"ll": current_ll, "name": request.current_location},
                "pickup": {"ll": pickup_ll, "name": request.pickup_location},
                "dropoff": {"ll": dropoff_ll, "name": request.dropoff_location},
            },
        }

    @staticmethod
    def _make_cache_key(request):
        import hashlib, json
        raw = json.dumps({
            "current_location": request.current_location,
            "pickup_location": request.pickup_location,
            "dropoff_location": request.dropoff_location,
            "cycle_hours_used": request.cycle_hours_used,
            "start_date": request.start_date.isoformat() if request.start_date else None,
            "cycle_schedule": request.cycle_schedule,
        }, sort_keys=True)
        return f"plan_route_{hashlib.md5(raw.encode()).hexdigest()}"
