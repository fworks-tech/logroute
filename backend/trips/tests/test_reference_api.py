"""Tests for the FMCSA HOS Reference API (/hos/* endpoints)."""

import pytest
from django.urls import reverse


class TestHosReferenceAPI:
    def test_hos_summary(self, api_client):
        response = api_client.get(reverse("hos-summary"))
        assert response.status_code == 200
        data = response.json()
        assert data["guide_title"] == "Interstate Truck Driver's Guide to Hours of Service"
        assert data["governing_regulation"] == "49 CFR Part 395"

    def test_hos_compliance(self, api_client):
        response = api_client.get(reverse("hos-compliance"))
        assert response.status_code == 200
        data = response.json()
        assert len(data["applies_when"]) >= 3
        assert "10,001 lbs" in data["applies_when"][2]

    def test_hos_commerce(self, api_client):
        response = api_client.get(reverse("hos-commerce"))
        assert response.status_code == 200
        data = response.json()
        assert "interstate" in data
        assert "intrastate" in data
        assert "cfr_reference" in data["interstate"]

    def test_hos_duty_status(self, api_client):
        response = api_client.get(reverse("hos-duty-status"))
        assert response.status_code == 200
        data = response.json()
        assert "on_duty" in data
        assert "off_duty" in data
        assert "personal_conveyance" in data
        assert "yard_moves" in data
        assert "includes" in data["on_duty"]

    def test_hos_limits(self, api_client):
        response = api_client.get(reverse("hos-limits"))
        assert response.status_code == 200
        data = response.json()
        assert data["fourteen_hour_window"]["window_hours"] == 14
        assert data["eleven_hour_limit"]["max_driving_hours"] == 11
        assert data["weekly_limit"]["sixty_hour_seven_day"]["hours"] == 60
        assert data["weekly_limit"]["seventy_hour_eight_day"]["hours"] == 70
        assert data["restart"]["hours_required"] == 34

    def test_hos_exceptions_list(self, api_client):
        response = api_client.get(reverse("hos-exceptions"))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 8
        ids = [e["id"] for e in data]
        assert "cdl-short-haul" in ids
        assert "adverse-driving-conditions" in ids

    def test_hos_exceptions_filtered_by_category(self, api_client):
        response = api_client.get(f"{reverse('hos-exceptions')}?category=short")
        assert response.status_code == 200
        data = response.json()
        assert all("short" in e["title"].lower() for e in data)

    def test_hos_exception_detail(self, api_client):
        response = api_client.get(
            reverse("hos-exception-detail", kwargs={"exception_id": "cdl-short-haul"})
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "cdl-short-haul"
        assert data["cfr_section"] == "§ 395.1(e)(1)"

    def test_hos_exception_detail_not_found(self, api_client):
        response = api_client.get(
            reverse("hos-exception-detail", kwargs={"exception_id": "nonexistent"})
        )
        assert response.status_code == 404
        assert "error" in response.json()

    def test_hos_logging(self, api_client):
        response = api_client.get(reverse("hos-logging"))
        assert response.status_code == 200
        data = response.json()
        assert data["primary_method"] == "ELD"
        assert "Date" in data["required_rods_fields"]

    def test_hos_resources(self, api_client):
        response = api_client.get(reverse("hos-resources"))
        assert response.status_code == 200
        data = response.json()
        assert "fmcsa.dot.gov" in data["hos_web_page"]
        assert data["information_line"] == "1-800-832-5660"
