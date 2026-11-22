from rest_framework.permissions import BasePermission, SAFE_METHODS

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


class IsInstitutionUser(BasePermission):
    message = "An active institution account is required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and UserProfile.objects.filter(user_id=user.pk).exists()
        )


class IsInstitutionStaffOrAdministrator(IsInstitutionUser):
    message = "Institution staff or administrator access is required."


class IsInstitutionAdministratorOrReadOnly(IsInstitutionUser):
    message = "Only institution administrators can change this record."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        return bool(
            UserProfile.objects.filter(
                user_id=request.user.pk,
                role=UserProfile.Role.INSTITUTION_ADMIN,
            ).exists()
        )
