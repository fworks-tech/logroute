"""Django app configuration for the trips application."""

from django.apps import AppConfig


class TripsConfig(AppConfig):
    """Configuration for the trips app — trip planning, geocoding, routing, and HOS simulation."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "trips"
    verbose_name = "Trip Planning"
