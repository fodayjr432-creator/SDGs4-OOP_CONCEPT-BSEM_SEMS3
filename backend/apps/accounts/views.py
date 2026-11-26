from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Institution, UserProfile
from .permissions import IsInstitutionAdministrator
from .serializers import (
    AdministratorInputSerializer,
    AdministratorStatusSerializer,
    InitialAdministratorSerializer,
    InstitutionNameSerializer,
    serialize_administrator,
)
from .throttles import LoginRateThrottle, RegistrationRateThrottle
from apps.audit.models import AuditEvent, UserSession


def _create_administrator(validated_data, institution):
    User = get_user_model()
    name_parts = validated_data["administrator_name"].split(maxsplit=1)
    user = User.objects.create_user(
        username=validated_data["username"],
        email=validated_data["email"],
        password=validated_data["password"],
        first_name=name_parts[0],
        last_name=name_parts[1] if len(name_parts) == 2 else "",
    )
    profile = UserProfile.objects.create(
        user=user,
        institution=institution,
        administrator_name=validated_data["administrator_name"],
        email=validated_data["email"],
        role=UserProfile.Role.INSTITUTION_ADMIN,
    )
    return profile


def _check_account_uniqueness(validated_data):
    User = get_user_model()
    errors = {}
    if User.objects.filter(username__iexact=validated_data["username"]).exists():
        errors["username"] = "This username is already in use."
    if User.objects.filter(email__iexact=validated_data["email"]).exists():
        errors["email"] = "This email address is already in use."
    if errors:
        raise ValidationError(errors)


@api_view(["GET"])
@permission_classes([AllowAny])
def registration_status(request):
    is_open = not UserProfile.objects.filter(
        role=UserProfile.Role.INSTITUTION_ADMIN
    ).exists()
    return Response({"registration_open": is_open})


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([RegistrationRateThrottle])
def register_initial_administrator(request):
    serializer = InitialAdministratorSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        with transaction.atomic():
            institution, _ = Institution.objects.get_or_create(
                is_singleton=True,
                defaults={"name": data["institution_name"]},
            )
            institution = Institution.objects.select_for_update().get(
                pk=institution.pk
            )
            if UserProfile.objects.filter(
                role=UserProfile.Role.INSTITUTION_ADMIN
            ).exists():
                return Response(
                    {"error": "Initial administrator registration is closed."},
                    status=status.HTTP_409_CONFLICT,
                )
            _check_account_uniqueness(data)
            if institution.name != data["institution_name"]:
                institution.name = data["institution_name"]
                institution.save(update_fields=["name"])
            profile = _create_administrator(data, institution)
    except IntegrityError:
        return Response(
            {"error": "Registration could not be completed. Check the account details."},
            status=status.HTTP_409_CONFLICT,
        )

    return Response(
        {
            "detail": "Institution administrator registered. Sign in to continue.",
            "institution": institution.name,
            "account": serialize_administrator(profile),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=username, password=password)
    profile = (
        UserProfile.objects.select_related("institution")
        .filter(user_id=getattr(user, "pk", None))
        .first()
        if user is not None
        else None
    )
    ip = request.META.get("REMOTE_ADDR")
    if user is None or not user.is_active or profile is None:
        AuditEvent.objects.create(
            user=None,
            username=username if isinstance(username, str) else "",
            user_role="",
            event_type=AuditEvent.EventType.LOGIN_FAILED,
            action="Failed login attempt",
            http_method=request.method,
            endpoint=request.path,
            ip_address=ip,
            success=False,
        )
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    existing_token = Token.objects.filter(user=user).first()
    token_max_age = timedelta(hours=12)
    if (
        existing_token is not None
        and timezone.now() - existing_token.created > token_max_age
    ):
        existing_token.delete()
        existing_token = None
    token = existing_token or Token.objects.create(user=user)
    AuditEvent.objects.create(
        user=user,
        username=user.get_username(),
        user_role=profile.role,
        event_type=AuditEvent.EventType.LOGIN_SUCCESS,
        action="User logged in",
        http_method=request.method,
        endpoint=request.path,
        ip_address=ip,
        success=True,
    )
    UserSession.objects.create(
        user=user,
        username=user.get_username(),
        login_at=timezone.now(),
        status=UserSession.Status.ACTIVE,
        ip_address=ip,
        last_activity_at=timezone.now(),
    )
    return Response(
        {
            "token": token.key,
            "username": user.get_username(),
            "role": profile.role,
            "administrator_name": profile.administrator_name,
            "institution": profile.institution.name,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    session = UserSession.objects.filter(user=request.user, status=UserSession.Status.ACTIVE).order_by("-login_at").first()
    if session is not None:
        session.logout_at = timezone.now()
        session.last_activity_at = timezone.now()
        session.save()
    AuditEvent.objects.create(
        user=request.user,
        username=request.user.get_username(),
        user_role=getattr(getattr(request.user, "account_profile", None), "role", ""),
        event_type=AuditEvent.EventType.LOGOUT,
        action="User logged out",
        http_method=request.method,
        endpoint=request.path,
        ip_address=request.META.get("REMOTE_ADDR"),
        success=True,
    )
    return Response({"detail": "Logged out."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    try:
        profile = user.account_profile
    except UserProfile.DoesNotExist:
        profile = None

    return Response(
        {
            "id": user.pk,
            "username": user.get_username(),
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "role": profile.role if profile else None,
            "administrator_name": profile.administrator_name if profile else None,
            "institution": profile.institution.name if profile else None,
        }
    )


@api_view(["PATCH"])
@permission_classes([IsInstitutionAdministrator])
def institution_detail(request):
    serializer = InstitutionNameSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        institution = Institution.objects.select_for_update().get(
            pk=request.user.account_profile.institution_id
        )
        institution.name = serializer.validated_data["institution_name"]
        institution.save(update_fields=["name"])

    return Response({"institution": institution.name})


@api_view(["GET", "POST"])
@permission_classes([IsInstitutionAdministrator])
def administrators(request):
    if request.method == "GET":
        profiles = UserProfile.objects.filter(
            institution=request.user.account_profile.institution,
            role=UserProfile.Role.INSTITUTION_ADMIN,
        ).select_related("user")
        return Response([serialize_administrator(profile) for profile in profiles])

    serializer = AdministratorInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        with transaction.atomic():
            institution = Institution.objects.select_for_update().get(
                pk=request.user.account_profile.institution_id
            )
            _check_account_uniqueness(serializer.validated_data)
            profile = _create_administrator(serializer.validated_data, institution)
    except IntegrityError:
        return Response(
            {"error": "The administrator could not be created. Check the account details."},
            status=status.HTTP_409_CONFLICT,
        )
    return Response(
        serialize_administrator(profile),
        status=status.HTTP_201_CREATED,
    )


@api_view(["PATCH"])
@permission_classes([IsInstitutionAdministrator])
def administrator_detail(request, user_id):
    serializer = AdministratorStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    requested_active = serializer.validated_data["is_active"]

    try:
        with transaction.atomic():
            institution = Institution.objects.select_for_update().get(
                pk=request.user.account_profile.institution_id
            )
            profile = (
                UserProfile.objects.select_related("user")
                .select_for_update()
                .get(
                    user_id=user_id,
                    institution=institution,
                    role=UserProfile.Role.INSTITUTION_ADMIN,
                )
            )
            if not requested_active:
                if profile.user_id == request.user.pk:
                    return Response(
                        {"error": "You cannot deactivate your own administrator account."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                active_admins = UserProfile.objects.filter(
                    institution=institution,
                    role=UserProfile.Role.INSTITUTION_ADMIN,
                    user__is_active=True,
                ).count()
                if profile.user.is_active and active_admins <= 1:
                    return Response(
                        {"error": "At least one active administrator must remain."},
                        status=status.HTTP_409_CONFLICT,
                    )
            profile.user.is_active = requested_active
            profile.user.save(update_fields=["is_active"])
    except UserProfile.DoesNotExist as error:
        raise NotFound("Administrator not found.") from error

    return Response(serialize_administrator(profile))
