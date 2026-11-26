from django.urls import path

from . import views

urlpatterns = [
    path("audit-logs/", views.AuditEventListView.as_view(), name="audit-logs"),
    path("audit-logs/<int:pk>/", views.AuditEventDetailView.as_view(), name="audit-log-detail"),
    path("user-sessions/", views.UserSessionListView.as_view(), name="user-sessions"),
    path("user-sessions/active/", views.ActiveUserSessionListView.as_view(), name="user-sessions-active"),
]
