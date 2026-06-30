"""
HOS (Hours of Service) Engine — FMCSA Property-Carrying Rules Simulator.

Rules enforced:
  - 11-hour driving limit per shift
  - 14-hour on-duty window per shift (once started, clock runs)
  - 30-minute mandatory break after 8 cumulative driving hours within a shift
  - 10-hour sleeper-berth / off-duty reset between shifts
  - 60-hour/7-day or 70-hour/8-day rolling cycle limit (configurable)
  - Fuel stop (ON_DUTY_NOT_DRIVING, 0.5 hr) every 1,000 miles
  - 1 hour ON_DUTY_NOT_DRIVING for pickup
  - 1 hour ON_DUTY_NOT_DRIVING for dropoff
"""

from __future__ import annotations

import json
from datetime import date, timedelta

from django.core.cache import cache

FUEL_INTERVAL_MILES = 1000.0
FUEL_STOP_HOURS = 0.5  # 30 minutes
PICKUP_HOURS = 1.0
DROPOFF_HOURS = 1.0
MAX_DRIVE_PER_SHIFT = 11.0
MAX_WINDOW_PER_SHIFT = 14.0  # on-duty window
BREAK_DRIVE_THRESHOLD = 8.0  # drive hours before mandatory 30-min break
BREAK_DURATION = 0.5  # 30 minutes
REST_DURATION = 10.0  # 10-hour reset

CYCLE_LIMITS = {
    "60": {"hours": 60.0, "days": 7},
    "70": {"hours": 70.0, "days": 8},
}

# Cache HOS simulations for 24 hours (they're deterministic for given inputs)
HOS_CACHE_TIMEOUT = 86400


def _snap_to_15min(hour: float) -> float:
    """Snap hour value to nearest 15-minute increment (0.25-hour intervals)."""
    return round(hour * 4) / 4


def _make_hos_cache_key(
    total_distance_miles: float,
    leg1_hours: float,
    leg2_hours: float,
    current_cycle_used_hours: float,
    leg1_miles: float,
    leg2_miles: float,
    start_date: date | None = None,
    cycle_schedule: str = "70",
) -> str:
    """Generate cache key for HOS simulation parameters (memcached-safe)."""
    import hashlib

    params = {
        "total_distance_miles": total_distance_miles,
        "leg1_hours": leg1_hours,
        "leg2_hours": leg2_hours,
        "current_cycle_used_hours": current_cycle_used_hours,
        "leg1_miles": leg1_miles,
        "leg2_miles": leg2_miles,
        "start_date": start_date.isoformat() if start_date else None,
        "cycle_schedule": cycle_schedule,
    }
    params_json = json.dumps(params, sort_keys=True)
    hash_val = hashlib.md5(params_json.encode()).hexdigest()
    return f"hos_simulation_{hash_val}"


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
    """
    Simulate the full trip and return structured logbook data.

    leg1 = current_location -> pickup
    leg2 = pickup -> dropoff

    Args:
        total_distance_miles: Combined distance of both legs in miles.
        leg1_hours: Estimated driving hours for leg 1 (current → pickup).
        leg2_hours: Estimated driving hours for leg 2 (pickup → dropoff).
        current_cycle_used_hours: Hours already used in the current 60/70-hour cycle.
        leg1_miles: Distance of leg 1 in miles.
        leg2_miles: Distance of leg 2 in miles.
        start_date: Optional start date; defaults to today.
        from_location: Starting location name for the log header.
        pickup_location: Pickup location name for the log header.
        to_location: Destination location name for the log header.
        cycle_schedule: "60" for 60-hour/7-day or "70" for 70-hour/8-day.

    Returns:
        A dict with logbook_days (list of day dicts), total_trip_hours,
        total_driving_hours, num_fuel_stops, num_rest_stops, cycle_schedule,
        and cycle_max_hours.
    """
    schedule = CYCLE_LIMITS.get(cycle_schedule, CYCLE_LIMITS["70"])
    max_cycle_hours = schedule["hours"]

    if start_date is None:
        start_date = date.today()
    # Check cache first
    cache_key = _make_hos_cache_key(
        total_distance_miles,
        leg1_hours,
        leg2_hours,
        current_cycle_used_hours,
        leg1_miles,
        leg2_miles,
        start_date,
        cycle_schedule,
    )
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    events: list[dict] = []
    current_time = 0.0  # hours elapsed since trip start

    # --- Mutable state (use a dict so nested helpers can mutate) ---
    state = {
        "cycle_hours": current_cycle_used_hours,  # rolling cycle total
        "shift_drive": 0.0,  # driving hours this shift (max 11)
        "shift_on_duty": 0.0,  # on-duty hours this shift (max 14 window)
        "shift_start": None,  # absolute hour when this shift started
        "drive_since_break": 0.0,  # driving since last 30-min break (max 8)
        "miles_since_fuel": 0.0,
        "num_fuel_stops": 0,
        "num_rest_stops": 0,
        "cycle_snapshots": [],  # (end_of_day_hour, cycle_hours) snapshots at day boundaries
    }

    # Average speed across entire trip (for mile-tracking within timed legs)
    if (leg1_hours + leg2_hours) > 0:
        avg_speed = total_distance_miles / (leg1_hours + leg2_hours)
    else:
        avg_speed = 55.0  # fallback

    # ------------------------------------------------------------------ helpers

    def add_event(
        status: str,
        duration: float,
        label: str,
        location: str = "",
        marker_type: str = "",
    ) -> None:
        """Append a logbook event and advance the simulation clock."""
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

    def start_shift_if_needed() -> None:
        """Record shift start time when first going on-duty."""
        if state["shift_start"] is None:
            state["shift_start"] = current_time

    def on_duty_elapsed() -> float:
        """Hours elapsed in current on-duty window."""
        if state["shift_start"] is None:
            return 0.0
        return current_time - state["shift_start"]

    def remaining_window() -> float:
        """Hours left in 14-hr on-duty window."""
        return max(0.0, MAX_WINDOW_PER_SHIFT - on_duty_elapsed())

    def remaining_drive() -> float:
        """Hours of driving left this shift."""
        return max(0.0, MAX_DRIVE_PER_SHIFT - state["shift_drive"])

    def remaining_break_drive() -> float:
        """Hours of driving before mandatory 30-min break."""
        return max(0.0, BREAK_DRIVE_THRESHOLD - state["drive_since_break"])

    def remaining_cycle() -> float:
        """Hours left in the current cycle (60/7 or 70/8)."""
        return max(0.0, max_cycle_hours - state["cycle_hours"])

    def do_rest(label: str = "Rest (10-hr Reset)") -> None:
        """Insert a 10-hour sleeper-berth rest and reset shift counters."""
        add_event("SLEEPER_BERTH", REST_DURATION, label, marker_type="rest")
        state["shift_drive"] = 0.0
        state["shift_on_duty"] = 0.0
        state["shift_start"] = None
        state["drive_since_break"] = 0.0
        state["num_rest_stops"] += 1

    def do_cycle_rest() -> None:
        """Insert a 34-hour rest which resets the 60/70-hour cycle counter to zero.

        Per FMCSA § 395.3(c): 34+ consecutive hours off duty resets the
        60- or 70-hour weekly clock to zero.  This is optional, not mandatory.
        """
        add_event("SLEEPER_BERTH", 34.0, "34-hr Restart", marker_type="rest")
        state["cycle_hours"] = 0.0
        state["shift_drive"] = 0.0
        state["shift_on_duty"] = 0.0
        state["shift_start"] = None
        state["drive_since_break"] = 0.0
        state["num_rest_stops"] += 1

    def do_break() -> None:
        """Insert a mandatory 30-minute off-duty break."""
        add_event("OFF_DUTY", BREAK_DURATION, "30-min Break")
        state["drive_since_break"] = 0.0
        # The 14-hr window keeps running; shift_on_duty accumulates implicitly
        # (break counts against the window but not against driving hours)

    def do_fuel(label: str = "Fuel Stop") -> None:
        """Insert a 30-minute on-duty fuel stop."""
        start_shift_if_needed()
        add_event("ON_DUTY_NOT_DRIVING", FUEL_STOP_HOURS, label, marker_type="fuel")
        state["shift_on_duty"] += FUEL_STOP_HOURS
        state["cycle_hours"] += FUEL_STOP_HOURS
        state["miles_since_fuel"] = 0.0
        state["num_fuel_stops"] += 1

    def drive_segment(hours: float, miles: float, label: str) -> None:
        """
        Drive a segment, breaking it into compliant chunks and inserting
        mandatory breaks, rests, and fuel stops as needed.
        """
        remaining_hours = hours
        remaining_miles = miles
        max_iterations = 1000  # Prevent infinite loops

        iterations = 0
        while remaining_hours > 0.001 and iterations < max_iterations:
            iterations += 1
            # --- Check if rest is immediately required ---
            if state["cycle_hours"] >= max_cycle_hours:
                do_cycle_rest()
                continue
            if remaining_drive() <= 0.001 or remaining_window() <= 0.001:
                do_rest()
                continue

            # --- How much can we drive before hitting a limit? ---
            # Candidate caps (all in hours)
            cap_drive = remaining_drive()
            cap_window = remaining_window()
            cap_break = remaining_break_drive()
            cap_cycle = remaining_cycle()
            # Miles-to-fuel in hours at current speed
            miles_to_fuel = max(0.0, FUEL_INTERVAL_MILES - state["miles_since_fuel"])
            cap_fuel_hours = (
                miles_to_fuel / avg_speed if avg_speed > 0 else float("inf")
            )

            # Smallest binding cap
            chunk_hours = min(
                remaining_hours,
                cap_drive,
                cap_window,
                cap_break,
                cap_cycle,
                cap_fuel_hours,
            )
            chunk_hours = max(chunk_hours, 0.0)

            if chunk_hours <= 0.001:
                # Determine why we're stuck and resolve
                if remaining_cycle() <= 0.001:
                    do_cycle_rest()
                elif remaining_break_drive() <= 0.001:
                    do_break()
                elif remaining_drive() <= 0.001 or remaining_window() <= 0.001:
                    do_rest()
                else:
                    # Fuel stop needed before we can continue
                    do_fuel()
                continue

            chunk_miles = (
                (chunk_hours / remaining_hours) * remaining_miles
                if remaining_hours > 0
                else 0.0
            )

            # --- Drive the chunk ---
            start_shift_if_needed()
            add_event("DRIVING", chunk_hours, label)
            state["shift_drive"] += chunk_hours
            state["shift_on_duty"] += chunk_hours
            state["drive_since_break"] += chunk_hours
            state["cycle_hours"] += chunk_hours
            state["miles_since_fuel"] += chunk_miles

            remaining_hours -= chunk_hours
            remaining_miles -= chunk_miles

            # --- Post-chunk checks ---
            # Fuel stop if we've hit 1,000 miles and still have more driving
            if (
                state["miles_since_fuel"] >= FUEL_INTERVAL_MILES - 0.001
                and remaining_hours > 0.001
            ):
                do_fuel()

            # Mandatory break if 8 hrs driving reached and still more to drive
            if (
                state["drive_since_break"] >= BREAK_DRIVE_THRESHOLD - 0.001
                and remaining_hours > 0.001
            ):
                do_break()

    def do_on_duty_nd(duration: float, label: str, location: str = "") -> None:
        """On-Duty Not Driving activity (pickup, dropoff, fuel).

        Per FMCSA § 395.3(a)(2), on-duty non-driving activities are permitted
        past the 14-hour window — only CMV driving is prohibited after the
        14th hour.  Therefore we only check the cycle limit here, not the
        remaining on-duty window.
        """
        start_shift_if_needed()
        if remaining_cycle() < duration:
            do_cycle_rest()
            start_shift_if_needed()
        add_event("ON_DUTY_NOT_DRIVING", duration, label, location)
        state["shift_on_duty"] += duration
        state["cycle_hours"] += duration

    # ------------------------------------------------------------------ simulate

    # Leg 1: Current location -> Pickup
    drive_segment(leg1_hours, leg1_miles, "Driving to Pickup")

    # Pickup activity
    do_on_duty_nd(PICKUP_HOURS, "Pickup", pickup_location)

    # Leg 2: Pickup -> Dropoff
    drive_segment(leg2_hours, leg2_miles, "Driving to Dropoff")

    # Dropoff activity
    do_on_duty_nd(DROPOFF_HOURS, "Dropoff", to_location)

    # ------------------------------------------------------------------ group by day

    total_trip_hours = current_time
    num_days = int(total_trip_hours / 24) + 1

    logbook_days = []
    total_driving_hours = 0.0
    cumulative_miles = 0.0
    cumulative_on_duty_hours = 0.0

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
            # Clip event to this 24-hour window
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
                    if (leg1_hours + leg2_hours) > 0
                    else 0
                )
            if ev["status"] in ("DRIVING", "ON_DUTY_NOT_DRIVING"):
                day_on_duty += duration
            if ev["status"] == "OFF_DUTY":
                day_off_duty += duration
            if ev["status"] == "SLEEPER_BERTH":
                day_sleeper += duration
            if ev["status"] == "ON_DUTY_NOT_DRIVING":
                day_on_duty_nd += duration

        # Fill gaps with OFF_DUTY
        day_events_filled = []
        cursor = 0.0
        for ev in sorted(day_events, key=lambda e: e["start_hour"]):
            if ev["start_hour"] > cursor + 0.001:
                gap_duration = ev["start_hour"] - cursor
                snapped_end = _snap_to_15min(ev["start_hour"])
                day_events_filled.append(
                    {
                        "status": "OFF_DUTY",
                        "start_hour": _snap_to_15min(cursor),
                        "end_hour": snapped_end,
                        "duration_hours": round(
                            snapped_end - _snap_to_15min(cursor), 4
                        ),
                        "label": "Off Duty",
                        "location": "",
                    }
                )
                day_off_duty += gap_duration
            day_events_filled.append(ev)
            cursor = ev["end_hour"]

        if cursor < 24.0 - 0.001:
            gap_duration = 24.0 - cursor
            snapped_cursor = _snap_to_15min(cursor)
            day_events_filled.append(
                {
                    "status": "OFF_DUTY",
                    "start_hour": snapped_cursor,
                    "end_hour": 24.0,
                    "duration_hours": round(24.0 - snapped_cursor, 4),
                    "label": "Off Duty",
                    "location": "",
                }
            )
            day_off_duty += gap_duration

        total_driving_hours += day_drive
        cumulative_miles += day_miles
        cumulative_on_duty_hours += day_on_duty

        # Compute cycle hours through this day by replaying events
        # (accounts for 34-hour restarts that reset the cycle counter)
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

        logbook_days.append(
            {
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
            }
        )

    result = {
        "logbook_days": logbook_days,
        "total_trip_hours": round(total_trip_hours, 2),
        "total_driving_hours": round(total_driving_hours, 2),
        "num_fuel_stops": state["num_fuel_stops"],
        "num_rest_stops": state["num_rest_stops"],
        "cycle_schedule": cycle_schedule,
        "cycle_max_hours": int(max_cycle_hours),
    }

    # Cache the result for future identical requests
    cache.set(cache_key, result, HOS_CACHE_TIMEOUT)

    return result

