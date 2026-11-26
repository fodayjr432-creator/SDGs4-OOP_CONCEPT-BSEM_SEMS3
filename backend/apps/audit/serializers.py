from rest_framework import serializers

from .models import AuditEvent, UserSession


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "user",
            "username",
            "user_role",
            "event_type",
            "action",
            "target_model",
            "target_id",
            "http_method",
            "endpoint",
            "ip_address",
            "success",
            "timestamp",
        ]


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = [
            "id",
            "session_id",
            "user",
            "username",
            "login_at",
            "logout_at",
            "status",
            "duration_seconds",
            "ip_address",
            "last_activity_at",
        ]
