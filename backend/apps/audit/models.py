import uuid

from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "LOGIN_SUCCESS", "Login success"
        LOGIN_FAILED = "LOGIN_FAILED", "Login failed"
        LOGOUT = "LOGOUT", "Logout"
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        ACCOUNT_ACTIVATED = "ACCOUNT_ACTIVATED", "Account activated"
        ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED", "Account deactivated"
        OTHER = "OTHER", "Other"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    username = models.CharField(max_length=150, blank=True, default="")
    user_role = models.CharField(max_length=64, blank=True, default="")
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    action = models.CharField(max_length=255)
    target_model = models.CharField(max_length=128, blank=True, default="")
    target_id = models.CharField(max_length=128, blank=True, default="")
    http_method = models.CharField(max_length=16, blank=True, default="")
    endpoint = models.CharField(max_length=255, blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp", "-id"]
        indexes = [
            models.Index(fields=["event_type", "-timestamp"]),
            models.Index(fields=["username", "-timestamp"]),
            models.Index(fields=["success", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.timestamp} {self.username} {self.event_type}"


class UserSession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        EXPIRED = "EXPIRED", "Expired"
        UNKNOWN = "UNKNOWN", "Unknown"

    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_sessions",
    )
    username = models.CharField(max_length=150, blank=True, default="")
    login_at = models.DateTimeField()
    logout_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-login_at", "-id"]
        indexes = [
            models.Index(fields=["status", "-login_at"]),
            models.Index(fields=["username", "-login_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.logout_at is not None and self.login_at is not None:
            delta = self.logout_at - self.login_at
            self.duration_seconds = max(0, int(delta.total_seconds()))
            if self.status == self.Status.ACTIVE:
                self.status = self.Status.COMPLETED
        super().save(*args, **kwargs)
