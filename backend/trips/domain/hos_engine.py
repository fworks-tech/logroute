from __future__ import annotations

from datetime import date, timedelta

FUEL_INTERVAL_MILES = 1000.0
FUEL_STOP_HOURS = 0.5
PICKUP_HOURS = 1.0
DROPOFF_HOURS = 1.0
MAX_DRIVE_PER_SHIFT = 11.0
MAX_WINDOW_PER_SHIFT = 14.0
BREAK_DRIVE_THRESHOLD = 8.0
BREAK_DURATION = 0.5
REST_DURATION = 10.0

CYCLE_LIMITS = {
    "60": {"hours": 60.0, "days": 7},
    "70": {"hours": 70.0, "days": 8},
}


def _snap_to_15min(hour: float) -> float:
    return round(hour * 4) / 4


def simulate_trip(
    total_distance_miles: float,
    leg1_hours: float,
    leg2_hours: float,
    current_cycle_used_hours: float,
    leg1_miles: float,
    leg2_miles: float,
    start_date: date | None = None,
    from_location: str = "Current Location",
    pickup_location: str = "Pickup Location",
    to_location: str = "Dropoff Location",
    cycle_schedule: str = "70",
) -> dict:
    schedule = CYCLE_LIMITS.get(cycle_schedule, CYCLE_LIMITS["70"])
    max_cycle_hours = schedule["hours"]

    if start_date is None:
        start_date = date.today()

    events: list[dict] = []
    current_time = 0.0

    state = {
        "cycle_hours": current_cycle_used_hours,
        "shift_drive": 0.0,
        "shift_on_duty": 0.0,
        "shift_start": None,
        "drive_since_break": 0.0,
        "miles_since_fuel": 0.0,
        "num_fuel_stops": 0,
        "num_rest_stops": 0,
        "cycle_snapshots": [],
    }

    if (leg1_hours + leg2_hours) > 0:
        avg_speed = total_distance_miles / (leg1_hours + leg2_hours)
    else:
        avg_speed = 55.0

    def add_event(status, duration, label, location="", marker_type=""):
        nonlocal current_time
        if duration <= 0:
            return
        event = {
            "status": status,
            "start_hour": round(current_time, 4),
            "end_hour": round(current_time + duration, 4),
            "duration_hours": round(duration, 4),
            "label": label,
            "location": location,
        }
        if marker_type:
            event["marker_type"] = marker_type
        events.append(event)
        current_time += duration

    def start_shift_if_needed():
        if state["shift_start"] is None:
            state["shift_start"] = current_time

    def on_duty_elapsed():
        if state["shift_start"] is None:
            return 0.0
        return current_time - state["shift_start"]

    def remaining_window():
        return max(0.0, MAX_WINDOW_PER_SHIFT - on_duty_elapsed())

    def remaining_drive():
        return max(0.0, MAX_DRIVE_PER_SHIFT - state["shift_drive"])

    def remaining_break_drive():
        return max(0.0, BREAK_DRIVE_THRESHOLD - state["drive_since_break"])

    def remaining_cycle():
        return max(0.0, max_cycle_hours - state["cycle_hours"])

    def do_rest(label="Rest (10-hr Reset)"):
        add_event("SLEEPER_BERTH", REST_DURATION, label, marker_type="rest")
        state["shift_drive"] = 0.0
        state["shift_on_duty"] = 0.0
        state["shift_start"] = None
        state["drive_since_break"] = 0.0
        state["num_rest_stops"] += 1

    def do_cycle_rest():
        add_event("SLEEPER_BERTH", 34.0, "34-hr Restart", marker_type="rest")
        state["cycle_hours"] = 0.0
        state["shift_drive"] = 0.0
        state["shift_on_duty"] = 0.0
        state["shift_start"] = None
        state["drive_since_break"] = 0.0
        state["num_rest_stops"] += 1

    def do_break():
        add_event("OFF_DUTY", BREAK_DURATION, "30-min Break")
        state["drive_since_break"] = 0.0

    def do_fuel(label="Fuel Stop"):
        start_shift_if_needed()
        add_event("ON_DUTY_NOT_DRIVING", FUEL_STOP_HOURS, label, marker_type="fuel")
        state["shift_on_duty"] += FUEL_STOP_HOURS
        state["cycle_hours"] += FUEL_STOP_HOURS
        state["miles_since_fuel"] = 0.0
        state["num_fuel_stops"] += 1

    def drive_segment(hours, miles, label):
        remaining_hours = hours
        remaining_miles = miles
        max_iterations = 1000
        iterations = 0

        while remaining_hours > 0.001 and iterations < max_iterations:
            iterations += 1

            if state["cycle_hours"] >= max_cycle_hours:
                do_cycle_rest()
                continue
            if remaining_drive() <= 0.001 or remaining_window() <= 0.001:
                do_rest()
                continue

            cap_drive = remaining_drive()
            cap_window = remaining_window()
            cap_break = remaining_break_drive()
            cap_cycle = remaining_cycle()
            miles_to_fuel = max(0.0, FUEL_INTERVAL_MILES - state["miles_since_fuel"])
            cap_fuel_hours = miles_to_fuel / avg_speed if avg_speed > 0 else float("inf")

            chunk_hours = min(remaining_hours, cap_drive, cap_window, cap_break, cap_cycle, cap_fuel_hours)
            chunk_hours = max(chunk_hours, 0.0)

            if chunk_hours <= 0.001:
                if remaining_cycle() <= 0.001:
                    do_cycle_rest()
                elif remaining_break_drive() <= 0.001:
                    do_break()
                elif remaining_drive() <= 0.001 or remaining_window() <= 0.001:
                    do_rest()
                else:
                    do_fuel()
                continue

            chunk_miles = (
                (chunk_hours / remaining_hours) * remaining_miles if remaining_hours > 0 else 0.0
            )

            start_shift_if_needed()
            add_event("DRIVING", chunk_hours, label)
            state["shift_drive"] += chunk_hours
            state["shift_on_duty"] += chunk_hours
            state["drive_since_break"] += chunk_hours
            state["cycle_hours"] += chunk_hours
            state["miles_since_fuel"] += chunk_miles

            remaining_hours -= chunk_hours
            remaining_miles -= chunk_miles

            if state["miles_since_fuel"] >= FUEL_INTERVAL_MILES - 0.001 and remaining_hours > 0.001:
                do_fuel()
            if state["drive_since_break"] >= BREAK_DRIVE_THRESHOLD - 0.001 and remaining_hours > 0.001:
                do_break()

    def do_on_duty_nd(duration, label, location=""):
        start_shift_if_needed()
        if remaining_cycle() < duration:
            do_cycle_rest()
            start_shift_if_needed()
        add_event("ON_DUTY_NOT_DRIVING", duration, label, location)
        state["shift_on_duty"] += duration
        state["cycle_hours"] += duration

    drive_segment(leg1_hours, leg1_miles, "Driving to Pickup")
    do_on_duty_nd(PICKUP_HOURS, "Pickup", pickup_location)
    drive_segment(leg2_hours, leg2_miles, "Driving to Dropoff")
    do_on_duty_nd(DROPOFF_HOURS, "Dropoff", to_location)

    total_trip_hours = current_time
    num_days = int(total_trip_hours / 24) + 1

    logbook_days = []
    total_driving_hours = 0.0
    cumulative_miles = 0.0

    for day in range(num_days):
        day_start = day * 24.0
        day_end = day_start + 24.0

        day_events = []
        day_drive = 0.0
        day_on_duty = 0.0
        day_miles = 0.0
        day_off_duty = 0.0
        day_sleeper = 0.0
        day_on_duty_nd = 0.0

        for ev in events:
            seg_start = max(ev["start_hour"], day_start)
            seg_end = min(ev["end_hour"], day_end)
            if seg_end <= seg_start:
                continue

            duration = seg_end - seg_start
            snapped_start = _snap_to_15min(seg_start - day_start)
            snapped_end = _snap_to_15min(seg_end - day_start)
            snapped_duration = snapped_end - snapped_start
            clipped = {
                "status": ev["status"],
                "start_hour": snapped_start,
                "end_hour": snapped_end,
                "duration_hours": max(0.0, snapped_duration),
                "label": ev["label"],
                "location": ev.get("location", ""),
            }
            if snapped_duration > 0:
                day_events.append(clipped)

            if ev["status"] == "DRIVING":
                day_drive += duration
                day_miles += (
                    (duration / (leg1_hours + leg2_hours)) * total_distance_miles
                    if (leg1_hours + leg2_hours) > 0 else 0
                )
            if ev["status"] in ("DRIVING", "ON_DUTY_NOT_DRIVING"):
                day_on_duty += duration
            if ev["status"] == "OFF_DUTY":
                day_off_duty += duration
            if ev["status"] == "SLEEPER_BERTH":
                day_sleeper += duration
            if ev["status"] == "ON_DUTY_NOT_DRIVING":
                day_on_duty_nd += duration

        day_events_filled = []
        cursor = 0.0
        for ev in sorted(day_events, key=lambda e: e["start_hour"]):
            if ev["start_hour"] > cursor + 0.001:
                gap_duration = ev["start_hour"] - cursor
                snapped_end = _snap_to_15min(ev["start_hour"])
                day_events_filled.append({
                    "status": "OFF_DUTY",
                    "start_hour": _snap_to_15min(cursor),
                    "end_hour": snapped_end,
                    "duration_hours": round(snapped_end - _snap_to_15min(cursor), 4),
                    "label": "Off Duty",
                    "location": "",
                })
                day_off_duty += gap_duration
            day_events_filled.append(ev)
            cursor = ev["end_hour"]

        if cursor < 24.0 - 0.001:
            gap_duration = 24.0 - cursor
            snapped_cursor = _snap_to_15min(cursor)
            day_events_filled.append({
                "status": "OFF_DUTY",
                "start_hour": snapped_cursor,
                "end_hour": 24.0,
                "duration_hours": round(24.0 - snapped_cursor, 4),
                "label": "Off Duty",
                "location": "",
            })
            day_off_duty += gap_duration

        total_driving_hours += day_drive
        cumulative_miles += day_miles

        replay_cycle = current_cycle_used_hours
        for ev in events:
            if ev["start_hour"] >= day_end:
                break
            if ev["end_hour"] <= day_end:
                if ev["status"] in ("DRIVING", "ON_DUTY_NOT_DRIVING"):
                    replay_cycle += ev["duration_hours"]
                elif ev.get("label") == "34-hr Restart":
                    replay_cycle = 0.0
            elif ev.get("label") == "34-hr Restart":
                replay_cycle = 0.0
        cycle_through_day = min(replay_cycle, max_cycle_hours)

        day_date = start_date + timedelta(days=day)
        day_date_str = day_date.strftime("%m/%d/%Y")

        logbook_days.append({
            "day": day,
            "date_offset": day,
            "date": day_date_str,
            "from_location": from_location,
            "to_location": to_location,
            "events": day_events_filled,
            "total_driving_hours": round(day_drive, 2),
            "total_on_duty_hours": round(day_on_duty, 2),
            "cycle_hours_after_day": round(cycle_through_day, 2),
            "daily_miles": round(day_miles, 1),
            "cumulative_miles": round(cumulative_miles, 1),
            "row_totals": {
                "off_duty_hours": round(day_off_duty, 2),
                "sleeper_berth_hours": round(day_sleeper, 2),
                "driving_hours": round(day_drive, 2),
                "on_duty_not_driving_hours": round(day_on_duty_nd, 2),
            },
        })

    return {
        "logbook_days": logbook_days,
        "total_trip_hours": round(total_trip_hours, 2),
        "total_driving_hours": round(total_driving_hours, 2),
        "num_fuel_stops": state["num_fuel_stops"],
        "num_rest_stops": state["num_rest_stops"],
        "cycle_schedule": cycle_schedule,
        "cycle_max_hours": int(max_cycle_hours),
    }
