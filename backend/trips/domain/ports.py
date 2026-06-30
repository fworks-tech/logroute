from typing import Any, Protocol


class Geocoder(Protocol):
    def geocode(self, address: str) -> tuple[float, float]:
        ...

    def search(self, query: str) -> list[dict]:
        ...


class Router(Protocol):
    def get_route(
        self,
        origin_ll: tuple[float, float],
        waypoint_ll: tuple[float, float],
        dest_ll: tuple[float, float],
    ) -> dict:
        ...


class CacheService(Protocol):
    def get(self, key: str) -> Any | None:
        ...

    def set(self, key: str, value: Any, timeout: int) -> None:
        ...

    def delete(self, key: str) -> None:
        ...


class TripRepository(Protocol):
    def save(self, trip: Any) -> int:
        ...

    def get_by_id(self, trip_id: int, user_id: int) -> Any | None:
        ...

    def list_by_user(self, user_id: int) -> list:
        ...


class HosReferenceRepository(Protocol):
    def get_summary(self) -> dict:
        ...

    def get_compliance_requirements(self) -> dict:
        ...

    def get_commerce_definitions(self) -> dict:
        ...

    def get_duty_status_definitions(self) -> dict:
        ...

    def get_limits(self) -> dict:
        ...

    def get_exceptions(self, category: str | None = None) -> list[dict]:
        ...

    def get_exception_by_id(self, exception_id: str) -> dict | None:
        ...

    def get_logging_requirements(self) -> dict:
        ...

    def get_resource_links(self) -> dict:
        ...
