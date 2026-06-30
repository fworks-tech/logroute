from trips.domain import hos_reference as data


class StaticDataHosReferenceRepository:
    def get_summary(self) -> dict:
        return data.HOS_SUMMARY

    def get_compliance_requirements(self) -> dict:
        return data.COMPLIANCE_REQUIREMENTS

    def get_commerce_definitions(self) -> dict:
        return data.COMMERCE_DEFINITIONS

    def get_duty_status_definitions(self) -> dict:
        return data.DUTY_STATUS_DEFINITIONS

    def get_limits(self) -> dict:
        return data.HOS_LIMITS

    def get_exceptions(self, category: str | None = None) -> list[dict]:
        if category:
            return [e for e in data.HOS_EXCEPTIONS if category.lower() in e["title"].lower()]
        return list(data.HOS_EXCEPTIONS)

    def get_exception_by_id(self, exception_id: str) -> dict | None:
        for exc in data.HOS_EXCEPTIONS:
            if exc["id"] == exception_id:
                return exc
        return None

    def get_logging_requirements(self) -> dict:
        return data.LOGGING_REQUIREMENTS

    def get_resource_links(self) -> dict:
        return data.RESOURCE_LINKS
