"""Django admin configuration for the trips application."""

from django.contrib import admin

from .models import Trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin interface for managing trip plans."""

    list_display = [
        "id",
        "user",
        "current_location",
        "pickup_location",
        "dropoff_location",
        "cycle_hours_used",
        "cycle_schedule",
        "status",
        "created_at",
    ]
    list_filter = ["status", "cycle_schedule", "created_at"]
    search_fields = [
        "current_location",
        "pickup_location",
        "dropoff_location",
        "shipper_name",
        "user__username",
    ]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 25
