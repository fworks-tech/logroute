from enum import StrEnum


class DutyStatus(StrEnum):
    DRIVING = "DRIVING"
    OFF_DUTY = "OFF_DUTY"
    SLEEPER_BERTH = "SLEEPER_BERTH"
    ON_DUTY_NOT_DRIVING = "ON_DUTY_NOT_DRIVING"


class CycleSchedule(StrEnum):
    SIXTY = "60"
    SEVENTY = "70"


class TripStatus(StrEnum):
    DRAFT = "draft"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
