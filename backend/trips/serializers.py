"""DRF serializers for request validation and response formatting."""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Trip

User = get_user_model()


CYCLE_SCHEDULE_CHOICES = ["60", "70"]


class TripInputSerializer(serializers.Serializer):
    """Validate and deserialize the incoming trip planning request body."""

    current_location = serializers.CharField(min_length=2, max_length=500)
    pickup_location = serializers.CharField(min_length=2, max_length=500)
    dropoff_location = serializers.CharField(min_length=2, max_length=500)
    cycle_hours_used = serializers.FloatField(min_value=0, max_value=70)
    cycle_schedule = serializers.ChoiceField(choices=CYCLE_SCHEDULE_CHOICES, default="70")
    trip_date = serializers.DateField(required=False, allow_null=True)
    tractor_number = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    trailer_number = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    shipper_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")


class MarkerSerializer(serializers.Serializer):
    """Serialize a map marker with coordinates, type, and label."""

    lat = serializers.FloatField()
    lon = serializers.FloatField()
    type = serializers.CharField(max_length=50)
    label = serializers.CharField(max_length=255)


class LogbookEventSerializer(serializers.Serializer):
    """Serialize a single ELD logbook event with duty status and time range."""

    status = serializers.CharField(max_length=50)
    start_time = serializers.CharField(max_length=5)
    end_time = serializers.CharField(max_length=5)
    duration_hours = serializers.FloatField()
    label = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)


class LogbookDaySerializer(serializers.Serializer):
    """Serialize a single logbook day with events, row totals, and cycle data."""

    day = serializers.IntegerField()
    date_offset = serializers.IntegerField()
    date = serializers.CharField(max_length=10)
    from_location = serializers.CharField(max_length=255)
    to_location = serializers.CharField(max_length=255)
    daily_miles = serializers.FloatField()
    cumulative_miles = serializers.FloatField()
    total_driving_hours = serializers.FloatField()
    total_on_duty_hours = serializers.FloatField()
    cycle_hours_after_day = serializers.FloatField()
    row_totals = serializers.DictField()
    events = LogbookEventSerializer(many=True)


class TripSummarySerializer(serializers.Serializer):
    """Serialize the trip summary with distances, hours, and stop counts."""

    total_distance_miles = serializers.FloatField()
    total_trip_hours = serializers.FloatField()
    total_driving_hours = serializers.FloatField()
    total_drive_hours = serializers.FloatField()
    legs = serializers.IntegerField()
    rest_stops = serializers.IntegerField()
    fuel_stops = serializers.IntegerField()
    num_fuel_stops = serializers.IntegerField()
    num_rest_stops = serializers.IntegerField()
    leg_1_miles = serializers.FloatField()
    leg_2_miles = serializers.FloatField()


class TripOutputSerializer(serializers.Serializer):
    """Serialize the full trip planning output returned to the frontend."""

    route_coordinates = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()))
    markers = MarkerSerializer(many=True)
    logbook_days = LogbookDaySerializer(many=True)
    trip_summary = TripSummarySerializer()
    trip_date = serializers.DateField(allow_null=True, required=False)
    tractor_number = serializers.CharField(max_length=50, allow_blank=True, required=False)
    trailer_number = serializers.CharField(max_length=50, allow_blank=True, required=False)
    shipper_name = serializers.CharField(max_length=255, allow_blank=True, required=False)
    cycle_schedule = serializers.ChoiceField(choices=CYCLE_SCHEDULE_CHOICES, default="70")
    cycle_max_hours = serializers.IntegerField(default=70)


class HealthCheckSerializer(serializers.Serializer):
    """Serialize a simple health-check response."""

    status = serializers.CharField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend SimpleJWT token with email and username claims."""

    @classmethod
    def get_token(cls, user):
        """Extend the default JWT with email and username claims."""
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Validate and create a new user with username, email, and password."""

    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        """Create a new user with the validated username, email, and password."""
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class TripSerializer(serializers.ModelSerializer):
    """Full trip serialization with all fields; used for detail and update views."""
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
        """Create a new trip, automatically assigning the authenticated user from the request context."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class TripListSerializer(serializers.ModelSerializer):
    """Lightweight trip serializer for list views, excluding heavy JSON fields."""
    class Meta:
        model = Trip
        fields = [
            "id", "current_location", "pickup_location", "dropoff_location",
            "cycle_hours_used", "cycle_schedule", "trip_date", "status", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TripCreateSerializer(serializers.Serializer):
    """Validate input for creating a new trip from the frontend form."""
    current_location = serializers.CharField(min_length=2, max_length=500)
    pickup_location = serializers.CharField(min_length=2, max_length=500)
    dropoff_location = serializers.CharField(min_length=2, max_length=500)
    cycle_hours_used = serializers.FloatField(min_value=0, max_value=70)
    cycle_schedule = serializers.ChoiceField(choices=CYCLE_SCHEDULE_CHOICES, default="70")
    trip_date = serializers.DateField(required=False, allow_null=True)
    tractor_number = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    trailer_number = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    shipper_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
