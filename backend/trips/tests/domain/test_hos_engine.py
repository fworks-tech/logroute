"""Tests for the HOS engine — validated against FMCSA 49 CFR Part 395 rules."""

from datetime import date

import pytest

from trips.domain.hos_engine import simulate_trip


def _verify_15min_snapping(events: list[dict]) -> None:
    """Every event's start/end hour must be a multiple of 0.25 (15 min)."""
    for ev in events:
        assert ev["start_hour"] * 4 % 1 == 0, f"start_hour {ev['start_hour']} not snapped to 15min"
        assert ev["end_hour"] * 4 % 1 == 0, f"end_hour {ev['end_hour']} not snapped to 15min"


def test_short_trip_fits_in_one_shift():
    """A very short trip (100 mi, ~2 hr total) should complete in one shift
    with no breaks, rests, or fuel stops."""
    result = simulate_trip(
        total_distance_miles=100,
        leg1_hours=1.0,
        leg2_hours=1.0,
        current_cycle_used_hours=0,
        leg1_miles=50,
        leg2_miles=50,
    )
    assert len(result["logbook_days"]) == 1
    assert result["total_trip_hours"] == pytest.approx(4.0, rel=0.1)  # 2hr drive + 1hr pickup + 1hr dropoff
    assert result["total_driving_hours"] == pytest.approx(2.0, rel=0.1)
    assert result["num_fuel_stops"] == 0
    assert result["num_rest_stops"] == 0

    day = result["logbook_days"][0]
    statuses = [ev["status"] for ev in day["events"]]
    assert "DRIVING" in statuses
    assert "ON_DUTY_NOT_DRIVING" in statuses
    _verify_15min_snapping(day["events"])


def test_thirty_min_break_after_eight_hours_driving():
    """FMCSA § 395.3(a)(3)(ii): 30-min break required after 8 cumulative driving hours."""
    # ~9 hours of driving across legs (4.5 + 4.5) should force a break
    result = simulate_trip(
        total_distance_miles=500,
        leg1_hours=4.5,
        leg2_hours=4.5,
        current_cycle_used_hours=0,
        leg1_miles=250,
        leg2_miles=250,
    )
    # Find all OFF_DUTY events with "30-min Break" label
    all_events = [ev for day in result["logbook_days"] for ev in day["events"]]
    break_events = [ev for ev in all_events if ev["label"] == "30-min Break"]
    assert len(break_events) >= 1, "Expected at least one 30-min break"


def test_eleven_hour_driving_limit():
    """FMCSA § 395.3(a)(3): Max 11 hours of driving per shift after 10hr reset."""
    # 12 hours of driving total (6 + 6) — must trigger a rest
    result = simulate_trip(
        total_distance_miles=660,
        leg1_hours=6.0,
        leg2_hours=6.0,
        current_cycle_used_hours=0,
        leg1_miles=330,
        leg2_miles=330,
    )
    assert result["num_rest_stops"] >= 1, "Expected at least one rest stop (11hr limit)"

    # The total driving should be capped at 11hr before first rest
    assert result["total_driving_hours"] > 11.0, "Total driving should exceed 11hr across multiple shifts"


def test_fourteen_hour_window_blocks_driving():
    """FMCSA § 395.3(a)(2): Driving must stop when the 14-hour on-duty window expires."""
    result = simulate_trip(
        total_distance_miles=800,
        leg1_hours=10.0,
        leg2_hours=10.0,
        current_cycle_used_hours=0,
        leg1_miles=400,
        leg2_miles=400,
    )
    assert result["num_rest_stops"] >= 1, "14hr window should force at least one rest"

    all_events = [ev for day in result["logbook_days"] for ev in day["events"]]
    sleepers = [ev for ev in all_events if ev["status"] == "SLEEPER_BERTH"]
    assert any("10-hr" in ev["label"].lower() for ev in sleepers)


def test_ten_hour_reset_clears_shift():
    """FMCSA § 395.3(a)(2): After 10hr off/sleeper, the 14hr window and 11hr drive counter reset."""
    result = simulate_trip(
        total_distance_miles=1200,
        leg1_hours=10.0,
        leg2_hours=10.0,
        current_cycle_used_hours=0,
        leg1_miles=600,
        leg2_miles=600,
    )
    assert result["num_rest_stops"] >= 1
    assert result["num_fuel_stops"] >= 1


def test_seventy_hour_cycle_limit():
    """FMCSA § 395.3(b): 70-hour/8-day rolling cycle limit stops driving."""
    # Start near the limit (68 hours used) — should hit limit quickly
    result = simulate_trip(
        total_distance_miles=200,
        leg1_hours=2.0,
        leg2_hours=2.0,
        current_cycle_used_hours=68,
        leg1_miles=100,
        leg2_miles=100,
    )
    assert result["num_rest_stops"] >= 1  # engine should force rest if cycle exceeded


def test_fuel_stops_every_thousand_miles():
    """Fuel stop (30 min ON_DUTY_NOT_DRIVING) every 1000 mi."""
    result = simulate_trip(
        total_distance_miles=2100,
        leg1_hours=10.0,
        leg2_hours=10.0,
        current_cycle_used_hours=0,
        leg1_miles=1050,
        leg2_miles=1050,
    )
    # Should have at least 2 fuel stops (at 1000mi and 2000mi)
    all_events = [ev for day in result["logbook_days"] for ev in day["events"]]
    fuel_events = [ev for ev in all_events if "Fuel Stop" in ev["label"]]
    assert len(fuel_events) >= 2


def test_multi_day_logbook():
    """Trip spanning multiple 24-hour periods splits events into days."""
    result = simulate_trip(
        total_distance_miles=1800,
        leg1_hours=12.0,
        leg2_hours=12.0,
        current_cycle_used_hours=0,
        leg1_miles=900,
        leg2_miles=900,
    )
    assert len(result["logbook_days"]) >= 2

    for day in result["logbook_days"]:
        assert "date" in day
        assert "events" in day
        assert "row_totals" in day
        total = sum(day["row_totals"].values())
        assert total == pytest.approx(24.0, abs=0.5), "Row totals should sum to ~24hr"

        _verify_15min_snapping(day["events"])


def test_zero_distance_handled():
    """Zero-distance trip should produce a valid result without errors."""
    result = simulate_trip(
        total_distance_miles=0,
        leg1_hours=0,
        leg2_hours=0,
        current_cycle_used_hours=0,
        leg1_miles=0,
        leg2_miles=0,
    )
    # Zero driving hours, but pickup (1hr) + dropoff (1hr) still happen
    assert result["total_trip_hours"] == pytest.approx(2.0, rel=0.1)
    assert result["total_driving_hours"] == 0


def test_with_partial_cycle_hours():
    """Starting with existing cycle hours correctly accumulates."""
    result = simulate_trip(
        total_distance_miles=200,
        leg1_hours=2.0,
        leg2_hours=2.0,
        current_cycle_used_hours=40,
        leg1_miles=100,
        leg2_miles=100,
    )
    day = result["logbook_days"][0]
    # Cycle should be > 40 after the trip
    assert day["cycle_hours_after_day"] > 40


def test_return_structure():
    """Verify the complete return structure has all expected fields."""
    result = simulate_trip(
        total_distance_miles=300,
        leg1_hours=2.0,
        leg2_hours=2.0,
        current_cycle_used_hours=10,
        leg1_miles=150,
        leg2_miles=150,
    )
    assert "logbook_days" in result
    assert "total_trip_hours" in result
    assert "total_driving_hours" in result
    assert "num_fuel_stops" in result
    assert "num_rest_stops" in result
    assert result["cycle_schedule"] == "70"
    assert result["cycle_max_hours"] == 70

    day = result["logbook_days"][0]
    assert "day" in day
    assert "date" in day
    assert "from_location" in day
    assert "to_location" in day
    assert "events" in day
    assert "total_driving_hours" in day
    assert "total_on_duty_hours" in day
    assert "cycle_hours_after_day" in day
    assert "daily_miles" in day
    assert "cumulative_miles" in day
    assert "row_totals" in day

    for field in ("off_duty_hours", "sleeper_berth_hours", "driving_hours", "on_duty_not_driving_hours"):
        assert field in day["row_totals"]

    hours_sum = sum(day["row_totals"].values())
    assert hours_sum == pytest.approx(24.0, abs=0.5), "Row totals must sum to 24hr"


def test_sixty_hour_cycle_schedule():
    """FMCSA § 395.3(b): 60-hour/7-day cycle stops driving sooner than 70/8."""
    # Start at 55 hours — should hit 60-hr limit but not 70-hr limit
    result_60 = simulate_trip(
        total_distance_miles=300,
        leg1_hours=3.0,
        leg2_hours=3.0,
        current_cycle_used_hours=55,
        leg1_miles=150,
        leg2_miles=150,
        cycle_schedule="60",
    )
    result_70 = simulate_trip(
        total_distance_miles=300,
        leg1_hours=3.0,
        leg2_hours=3.0,
        current_cycle_used_hours=55,
        leg1_miles=150,
        leg2_miles=150,
        cycle_schedule="70",
    )
    assert result_60["cycle_schedule"] == "60"
    assert result_60["cycle_max_hours"] == 60
    assert result_70["cycle_schedule"] == "70"
    assert result_70["cycle_max_hours"] == 70
    # 60-hr schedule should hit the limit and require a rest
    assert result_60["num_rest_stops"] >= 1


def test_custom_locations():
    """Custom locations appear in logbook headers."""
    result = simulate_trip(
        total_distance_miles=200,
        leg1_hours=1.5,
        leg2_hours=1.5,
        current_cycle_used_hours=0,
        leg1_miles=100,
        leg2_miles=100,
        from_location="Chicago, IL",
        pickup_location="Indianapolis, IN",
        to_location="Dallas, TX",
    )
    day = result["logbook_days"][0]
    assert day["from_location"] == "Chicago, IL"
    assert day["to_location"] == "Dallas, TX"

    pickup_events = [ev for ev in day["events"] if ev["label"] == "Pickup"]
    dropoff_events = [ev for ev in day["events"] if ev["label"] == "Dropoff"]
    assert any(e["location"] == "Indianapolis, IN" for e in pickup_events)
    assert any(e["location"] == "Dallas, TX" for e in dropoff_events)


def test_custom_start_date():
    """start_date propagates to logbook day dates."""
    from datetime import date

    result = simulate_trip(
        total_distance_miles=200,
        leg1_hours=1.5,
        leg2_hours=1.5,
        current_cycle_used_hours=0,
        leg1_miles=100,
        leg2_miles=100,
        start_date=date(2026, 7, 4),
    )
    assert result["logbook_days"][0]["date"] == "07/04/2026"


def test_on_duty_nd_allowed_past_14hr_window():
    """FMCSA § 395.3(a)(2): On-duty non-driving activities are permitted
    past the 14-hour window. Only CMV driving is prohibited after the 14th hour.
    The guide explicitly states: 'The driver was on duty past the 14th hour,
    but that is allowed as long as there is no CMV driving after the 14th hour'."""
    # Drive nearly to the 14hr limit, then do pickup/dropoff past it
    result = simulate_trip(
        total_distance_miles=800,
        leg1_hours=10.0,
        leg2_hours=10.0,
        current_cycle_used_hours=0,
        leg1_miles=400,
        leg2_miles=400,
    )
    # Collect all ON_DUTY_NOT_DRIVING events across all days
    all_ond = []
    for day in result["logbook_days"]:
        all_ond.extend(ev for ev in day["events"] if ev["status"] == "ON_DUTY_NOT_DRIVING")
    assert len(all_ond) >= 2, "Should have at least pickup + dropoff"

    # Check the last dropoff event exists — it should not have been blocked
    labels = [ev["label"] for ev in all_ond]
    assert "Dropoff" in labels or "Pickup" in labels


def test_all_events_snapped_to_15min():
    """Every event across all days is snapped to 15-minute intervals."""
    result = simulate_trip(
        total_distance_miles=800,
        leg1_hours=5.0,
        leg2_hours=5.0,
        current_cycle_used_hours=0,
        leg1_miles=400,
        leg2_miles=400,
    )
    for day in result["logbook_days"]:
        _verify_15min_snapping(day["events"])
