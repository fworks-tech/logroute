import pytest

from trips.application.use_cases.get_hos_reference import HosReferenceUseCase


class FakeReferenceRepo:
    def get_summary(self):
        return {"guide_title": "test", "audience": "drivers", "disclaimer": "", "governing_regulation": "49 CFR 395"}

    def get_compliance_requirements(self):
        return {"applies_when": ["operating a CMV"], "key_reference": "49 CFR 395.1"}

    def get_commerce_definitions(self):
        return {"interstate": {}, "intrastate": {}}

    def get_duty_status_definitions(self):
        return {"on_duty": {}, "off_duty": {}, "personal_conveyance": {}, "yard_moves": {}}

    def get_limits(self):
        return {"fourteen_hour_window": {}, "eleven_hour_limit": {}, "sleeper_berth": {}, "thirty_minute_break": {}, "weekly_limit": {}, "restart": {}}

    def get_exceptions(self, category=None):
        all_exc = [
            {"id": "cdl-short-haul", "title": "CDL Short-Haul", "cfr_section": "395.1(e)(1)", "exception_type": ["short-haul"], "conditions": ["within 150 air miles"], "notes": None},
            {"id": "non-cdl-short-haul", "title": "Non-CDL Short-Haul", "cfr_section": "395.1(e)(2)", "exception_type": ["short-haul"], "conditions": ["within 150 air miles"], "notes": None},
        ]
        if category:
            return [e for e in all_exc if category.lower() in e["title"].lower()]
        return list(all_exc)

    def get_exception_by_id(self, exception_id):
        for exc in self.get_exceptions():
            if exc["id"] == exception_id:
                return exc
        return None

    def get_logging_requirements(self):
        return {"primary_method": "ELD", "eld_info_url": "http://example.com", "paper_log_allowed_when": [], "required_rods_fields": []}

    def get_resource_links(self):
        return {"hos_web_page": "http://example.com", "eld_information": "http://example.com", "personal_conveyance_guidance": "http://example.com", "information_line": "1-800-555-5555", "email": "test@example.com"}


class TestHosReferenceUseCase:
    def test_get_summary(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        result = use_case.get_summary()
        assert result["guide_title"] == "test"

    def test_get_compliance_requirements(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        result = use_case.get_compliance_requirements()
        assert "applies_when" in result

    def test_get_commerce_definitions(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        result = use_case.get_commerce_definitions()
        assert "interstate" in result

    def test_get_limits(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        result = use_case.get_limits()
        assert "fourteen_hour_window" in result

    def test_get_exceptions_list(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        results = use_case.get_exceptions()
        assert len(results) == 2

    def test_get_exceptions_filtered(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        results = use_case.get_exceptions(category="short")
        assert len(results) == 2

    def test_get_exception_by_id_found(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        result = use_case.get_exception_by_id("cdl-short-haul")
        assert result is not None
        assert result["id"] == "cdl-short-haul"

    def test_get_exception_by_id_not_found(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        result = use_case.get_exception_by_id("nonexistent")
        assert result is None

    def test_get_logging_requirements(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        result = use_case.get_logging_requirements()
        assert result["primary_method"] == "ELD"

    def test_get_resource_links(self):
        use_case = HosReferenceUseCase(FakeReferenceRepo())
        result = use_case.get_resource_links()
        assert "hos_web_page" in result
