from dataclasses import dataclass, field
from datetime import date


@dataclass
class Location:
    name: str
    lat: float
    lon: float


@dataclass
class LogbookEvent:
    status: str
    start_hour: float
    end_hour: float
    duration_hours: float
    label: str
    location: str = ""
    marker_type: str = ""


@dataclass
class LogbookDay:
    day: int
    date_offset: int
    date: str
    from_location: str
    to_location: str
    events: list
    daily_miles: float = 0.0
    cumulative_miles: float = 0.0
    total_driving_hours: float = 0.0
    total_on_duty_hours: float = 0.0
    cycle_hours_after_day: float = 0.0
    row_totals: dict = field(default_factory=dict)


@dataclass
class TripPlan:
    route_coordinates: list = field(default_factory=list)
    leg1: dict = field(default_factory=dict)
    leg2: dict = field(default_factory=dict)
    total_miles: float = 0.0
    markers: list = field(default_factory=list)
    logbook_days: list = field(default_factory=list)
    cycle_schedule: str = "70"
    cycle_max_hours: int = 70
    trip_summary: dict = field(default_factory=dict)
    locations: dict = field(default_factory=dict)
