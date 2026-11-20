from rest_framework.permissions import BasePermission

from .models import UserProfile


class IsInstitutionAdministrator(BasePermission):
    message = "Institution administrator access is required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and UserProfile.objects.filter(
                user_id=user.pk,
                role=UserProfile.Role.INSTITUTION_ADMIN,
            ).exists()
        )
