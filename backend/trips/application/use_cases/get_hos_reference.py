class HosReferenceUseCase:
    def __init__(self, reference_repo):
        self._repo = reference_repo

    def get_summary(self) -> dict:
        return self._repo.get_summary()

    def get_compliance_requirements(self) -> dict:
        return self._repo.get_compliance_requirements()

    def get_commerce_definitions(self) -> dict:
        return self._repo.get_commerce_definitions()

    def get_duty_status_definitions(self) -> dict:
        return self._repo.get_duty_status_definitions()

    def get_limits(self) -> dict:
        return self._repo.get_limits()

    def get_exceptions(self, category: str | None = None) -> list[dict]:
        return self._repo.get_exceptions(category)

    def get_exception_by_id(self, exception_id: str) -> dict | None:
        return self._repo.get_exception_by_id(exception_id)

    def get_logging_requirements(self) -> dict:
        return self._repo.get_logging_requirements()

    def get_resource_links(self) -> dict:
        return self._repo.get_resource_links()
