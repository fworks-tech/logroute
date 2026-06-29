import logging

from .hos_engine import simulate_trip
from .routing import geocode, get_route

logger = logging.getLogger("logroute.services")


class TripPlanningService:
    """Orchestrates the full trip-planning pipeline: geocode, route, HOS simulation, markers."""

    @staticmethod
    def plan_route(
        current_location: str,
        pickup_location: str,
        dropoff_location: str,
        cycle_hours_used: float,
        start_date=None,
        cycle_schedule: str = "70",
    ) -> dict:
        """Geocode three locations, fetch the OSRM route, run HOS simulation, and build markers.

        Args:
            current_location: Starting location name.
            pickup_location: Pickup location name.
            dropoff_location: Dropoff location name.
            cycle_hours_used: Hours already used in the current cycle.
            start_date: Optional trip start date; defaults to today.
            cycle_schedule: '60' for 60-hour/7-day or '70' for 70-hour/8-day.

        Returns:
            A dictionary containing route_coordinates, markers, logbook_days, trip_summary,
            and locations metadata.
        """
        # 1. Geocode all three locations
        current_ll = geocode(current_location)
        pickup_ll = geocode(pickup_location)
        dropoff_ll = geocode(dropoff_location)

        # 2. Fetch route from OSRM
        route = get_route(current_ll, pickup_ll, dropoff_ll)

        leg1 = route["legs"][0]
        leg2 = route["legs"][1]
        total_miles = leg1["distance_miles"] + leg2["distance_miles"]

        # 3. Run HOS simulation
        logbook = simulate_trip(
            total_distance_miles=total_miles,
            leg1_hours=leg1["duration_hours"],
            leg2_hours=leg2["duration_hours"],
            current_cycle_used_hours=cycle_hours_used,
            leg1_miles=leg1["distance_miles"],
            leg2_miles=leg2["distance_miles"],
            start_date=start_date,
            from_location=current_location,
            pickup_location=pickup_location,
            to_location=dropoff_location,
            cycle_schedule=cycle_schedule,
        )

        # Build a time lookup from logbook events (label → first event time)
        event_times: dict[str, str] = {}
        for day in logbook.get("logbook_days", []):
            for ev in day.get("events", []):
                label_key = ev.get("label", "").lower()
                if label_key and label_key not in event_times:
                    h = int(ev["start_hour"])
                    m = int((ev["start_hour"] - h) * 60)
                    event_times[label_key] = f"{h:02d}:{m:02d}"

        # 4. Build map markers
        markers = [
            {
                "id": "start",
                "lat": current_ll[0],
                "lon": current_ll[1],
                "type": "start",
                "label": current_location,
                "time": event_times.get("driving") or event_times.get(current_location.lower(), ""),
            },
            {
                "id": "pickup",
                "lat": pickup_ll[0],
                "lon": pickup_ll[1],
                "type": "pickup",
                "label": pickup_location,
                "time": event_times.get("pickup", ""),
            },
            {
                "id": "dropoff",
                "lat": dropoff_ll[0],
                "lon": dropoff_ll[1],
                "type": "dropoff",
                "label": dropoff_location,
                "time": event_times.get("dropoff", ""),
            },
        ]

        # Derive rest/fuel stop markers from raw logbook events (pre-transform)
        stop_markers = TripPlanningService._build_stop_markers(
            route["coordinates"],
            logbook,
        )
        markers.extend(stop_markers)

        # 5. Transform logbook to match frontend expectations (start_time/end_time as HH:MM)
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

        return {
            "route_coordinates": route["coordinates"],
            "leg1": leg1,
            "leg2": leg2,
            "total_miles": total_miles,
            "markers": markers,
            "logbook_days": logbook_days_transformed,
            "cycle_schedule": logbook.get("cycle_schedule", "70"),
            "cycle_max_hours": logbook.get("cycle_max_hours", 70),
            "trip_summary": {
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
            "locations": {
                "current": {"ll": current_ll, "name": current_location},
                "pickup": {"ll": pickup_ll, "name": pickup_location},
                "dropoff": {"ll": dropoff_ll, "name": dropoff_location},
            },
        }

    @staticmethod
    def _build_stop_markers(
        coordinates: list,
        logbook: dict,
    ) -> list:
        """Derive rest/fuel stop markers from raw logbook events.

        Args:
            coordinates: Route geometry as list of [lon, lat] pairs.
            logbook: Raw HOS simulation output with logbook_days and events.

        Returns:
            A list of marker dicts with id, lat, lon, type, label, and time.
        """
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
