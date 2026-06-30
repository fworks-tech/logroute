"""API endpoint tests for LogRoute — validated against actual URL patterns."""

import pytest
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestHealthCheck:
    def test_health_check(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "ok"


@pytest.mark.django_db
class TestUserRegistration:
    def test_register_user(self, api_client):
        response = api_client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "ComplexPass123!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "User registered successfully"

    def test_register_user_missing_fields(self, api_client):
        response = api_client.post(
            "/api/auth/register/",
            {"username": "newuser"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_user(self, api_client, user):
        response = api_client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "email": "another@example.com",
                "password": "ComplexPass123!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenObtain:
    def test_obtain_token(self, api_client, user):
        response = api_client.post(
            "/api/auth/token/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_obtain_token_invalid_credentials(self, api_client):
        response = api_client.post(
            "/api/auth/token/",
            {"username": "wrong", "password": "wrong"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGeocodeSearch:
    def test_geocode_search_empty_query(self, api_client):
        response = api_client.get("/api/geocode/?q=")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_geocode_search_short_query(self, api_client):
        response = api_client.get("/api/geocode/?q=a")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_geocode_search_missing_query(self, api_client):
        response = api_client.get("/api/geocode/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


@pytest.mark.django_db
class TestPlanRoute:
    def test_plan_route_missing_fields(self, api_client):
        response = api_client.post("/api/plan-route/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_plan_route_validation(self, api_client):
        response = api_client.post(
            "/api/plan-route/",
            {
                "current_location": "",
                "pickup_location": "",
                "dropoff_location": "",
                "cycle_hours_used": -1,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("trips.adapters.gateways.nominatim.NominatimGeocoder.geocode")
    @patch("trips.adapters.gateways.osrm.OSRMRouter.get_route")
    def test_plan_route_with_cycle_schedule(self, mock_get_route, mock_geocode, api_client):
        mock_geocode.return_value = (40.7128, -74.0060)
        mock_get_route.return_value = {
            "coordinates": [[-74.0060, 40.7128], [-87.6298, 41.8781]],
            "legs": [
                {"distance_miles": 100.0, "duration_hours": 2.0},
                {"distance_miles": 200.0, "duration_hours": 4.0},
            ],
        }
        response = api_client.post(
            "/api/plan-route/",
            {
                "current_location": "New York, NY",
                "pickup_location": "Philadelphia, PA",
                "dropoff_location": "Chicago, IL",
                "cycle_hours_used": 10,
                "cycle_schedule": "60",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["cycle_schedule"] == "60"
        assert data["cycle_max_hours"] == 60


