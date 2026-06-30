from rest_framework import serializers

from trips.models import Trip

CYCLE_SCHEDULE_CHOICES = ["60", "70"]


class TripInputSerializer(serializers.Serializer):
    current_location = serializers.CharField(min_length=2, max_length=500)
    pickup_location = serializers.CharField(min_length=2, max_length=500)
    dropoff_location = serializers.CharField(min_length=2, max_length=500)
    cycle_hours_used = serializers.FloatField(min_value=0, max_value=70)
    cycle_schedule = serializers.ChoiceField(choices=CYCLE_SCHEDULE_CHOICES, default="70")
    trip_date = serializers.DateField(required=False, allow_null=True)
    tractor_number = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    trailer_number = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    shipper_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            "id", "user", "current_location", "pickup_location", "dropoff_location",
            "cycle_hours_used", "cycle_schedule", "trip_date", "tractor_number", "trailer_number",
            "shipper_name", "route_coordinates", "markers", "logbook_days",
            "trip_summary", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class TripListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            "id", "current_location", "pickup_location", "dropoff_location",
            "cycle_hours_used", "cycle_schedule", "trip_date", "status", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
