"""Test fixtures and configuration for the trips app.

Ensures SQLite is used for tests so no external PostgreSQL is required.
Catches Redis connection errors gracefully (optional dependency).
"""

import os

# Force SQLite for tests — must be set before any Django import.
os.environ.setdefault("DATABASE_URL", "sqlite:///test_db.sqlite3")

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


@pytest.fixture(autouse=True)
def _clear_throttle_cache():
    from django.core.cache import cache
    try:
        cache.clear()
    except ConnectionError:
        pass  # Redis is optional; skip if unavailable


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def sample_trip_data():
    return {
        "pickup_location": "Dallas, TX",
        "dropoff_location": "Houston, TX",
        "current_location": "Dallas, TX",
        "cycle_hours_used": 0,
        "tractor_number": "T-1234",
        "trailer_number": "TR-5678",
        "shipper_name": "Acme Logistics",
    }


@pytest.fixture
def sample_geocode_response():
    return [
        {
            "lat": "32.7767",
            "lon": "-96.7970",
            "display_name": "Dallas, Dallas County, Texas, United States",
            "address": {"city": "Dallas", "state": "Texas", "country": "United States"},
        }
    ]
