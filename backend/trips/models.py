from django.conf import settings
from django.db import models


class Trip(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trips", db_index=True)
    current_location = models.CharField(max_length=255, blank=True, default="")
    pickup_location = models.CharField(max_length=255, blank=True, default="")
    dropoff_location = models.CharField(max_length=255, blank=True, default="")
    cycle_hours_used = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    cycle_schedule = models.CharField(max_length=2, choices=[("60", "60-hour / 7-day"), ("70", "70-hour / 8-day")], default="70")
    trip_date = models.DateField(null=True, blank=True)
    tractor_number = models.CharField(max_length=50, blank=True, default="")
    trailer_number = models.CharField(max_length=50, blank=True, default="")
    shipper_name = models.CharField(max_length=255, blank=True, default="")
    route_coordinates = models.JSONField(default=list, blank=True)
    markers = models.JSONField(default=list, blank=True)
    logbook_days = models.JSONField(default=list, blank=True)
    trip_summary = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "trip"
        verbose_name_plural = "trips"

    def __str__(self):
        return f"Trip {self.pk} - {self.pickup_location} to {self.dropoff_location}"
