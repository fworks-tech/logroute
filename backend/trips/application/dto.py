from dataclasses import dataclass, field
from datetime import date


@dataclass
class PlanRouteRequest:
    current_location: str
    pickup_location: str
    dropoff_location: str
    cycle_hours_used: float
    start_date: date | None = None
    cycle_schedule: str = "70"


@dataclass
class PlanRouteResponse:
    route_coordinates: list = field(default_factory=list)
    markers: list = field(default_factory=list)
    logbook_days: list = field(default_factory=list)
    trip_summary: dict = field(default_factory=dict)
    cycle_schedule: str = "70"
    cycle_max_hours: int = 70
    locations: dict = field(default_factory=dict)
    leg1: dict = field(default_factory=dict)
    leg2: dict = field(default_factory=dict)
    total_miles: float = 0.0


@dataclass
class GeocodeSearchRequest:
    query: str


@dataclass
class GeocodeSearchResponse:
    results: list = field(default_factory=list)
