from django.utils import timezone
from rest_framework import generics, permissions

from apps.accounts.permissions import IsInstitutionAdministrator

from .models import AuditEvent, UserSession
from .serializers import AuditEventSerializer, UserSessionSerializer


class AuditEventListView(generics.ListAPIView):
    serializer_class = AuditEventSerializer
    permission_classes = [IsInstitutionAdministrator]
    filterset_fields = ["event_type", "username", "success"]
    search_fields = ["username", "action", "target_model", "target_id", "endpoint"]
    ordering_fields = ["timestamp", "id"]

    def get_queryset(self):
        qs = AuditEvent.objects.all()
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start:
            qs = qs.filter(timestamp__gte=start)
        if end:
            qs = qs.filter(timestamp__lte=end)
        return qs


class AuditEventDetailView(generics.RetrieveAPIView):
    serializer_class = AuditEventSerializer
    permission_classes = [IsInstitutionAdministrator]
    queryset = AuditEvent.objects.all()


class UserSessionListView(generics.ListAPIView):
    serializer_class = UserSessionSerializer
    permission_classes = [IsInstitutionAdministrator]
    filterset_fields = ["status", "username"]
    search_fields = ["username"]
    ordering_fields = ["login_at", "id"]

    def get_queryset(self):
        qs = UserSession.objects.all()
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start:
            qs = qs.filter(login_at__gte=start)
        if end:
            qs = qs.filter(login_at__lte=end)
        return qs


class ActiveUserSessionListView(generics.ListAPIView):
    serializer_class = UserSessionSerializer
    permission_classes = [IsInstitutionAdministrator]

    def get_queryset(self):
        return UserSession.objects.filter(status=UserSession.Status.ACTIVE)
