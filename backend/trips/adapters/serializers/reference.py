from rest_framework import serializers


class HosSummarySerializer(serializers.Serializer):
    guide_title = serializers.CharField()
    audience = serializers.CharField()
    disclaimer = serializers.CharField()
    governing_regulation = serializers.CharField()


class ComplianceRequirementsSerializer(serializers.Serializer):
    applies_when = serializers.ListField(child=serializers.CharField())
    key_reference = serializers.CharField()


class CommerceDefinitionsSerializer(serializers.Serializer):
    interstate = serializers.DictField()
    intrastate = serializers.DictField()


class DutyStatusDefinitionsSerializer(serializers.Serializer):
    on_duty = serializers.DictField()
    off_duty = serializers.DictField()
    personal_conveyance = serializers.DictField()
    yard_moves = serializers.DictField()


class HosLimitsSerializer(serializers.Serializer):
    fourteen_hour_window = serializers.DictField()
    eleven_hour_limit = serializers.DictField()
    sleeper_berth = serializers.DictField()
    thirty_minute_break = serializers.DictField()
    weekly_limit = serializers.DictField()
    restart = serializers.DictField()


class HosExceptionSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    cfr_section = serializers.CharField()
    exception_type = serializers.ListField(child=serializers.CharField())
    conditions = serializers.ListField(child=serializers.CharField())
    notes = serializers.CharField(allow_null=True)


class LoggingRequirementsSerializer(serializers.Serializer):
    primary_method = serializers.CharField()
    eld_info_url = serializers.URLField()
    paper_log_allowed_when = serializers.ListField(child=serializers.CharField())
    required_rods_fields = serializers.ListField(child=serializers.CharField())


class ResourceLinksSerializer(serializers.Serializer):
    hos_web_page = serializers.URLField()
    eld_information = serializers.URLField()
    personal_conveyance_guidance = serializers.URLField()
    information_line = serializers.CharField()
    email = serializers.EmailField()
