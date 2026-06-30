from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float


@dataclass(frozen=True)
class CycleHours:
    used: float
    max_hours: float
    schedule: str

    @property
    def remaining(self) -> float:
        return max(0.0, self.max_hours - self.used)


@dataclass(frozen=True)
class RouteLeg:
    distance_miles: float
    duration_hours: float
