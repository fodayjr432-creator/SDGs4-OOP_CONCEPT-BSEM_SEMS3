from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import UserProfile


class AdministratorInputSerializer(serializers.Serializer):
    administrator_name = serializers.CharField(max_length=255, trim_whitespace=True)
    username = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_administrator_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Enter the administrator's full name.")
        return value

    def validate_username(self, value):
        user_model = get_user_model()
        username_field = user_model._meta.get_field(user_model.USERNAME_FIELD)
        try:
            for validator in username_field.validators:
                validator(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error
        if user_model.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    def validate_email(self, value):
        normalized_email = value.strip().casefold()
        if UserProfile.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("This email address is already in use.")
        if get_user_model().objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return normalized_email

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "The passwords do not match."}
            )

        user_model = get_user_model()
        user = user_model(
            username=attrs["username"],
            email=attrs["email"],
        )
        name_parts = attrs["administrator_name"].split(maxsplit=1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) == 2 else ""
        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": error.messages}
            ) from error
        return attrs


class InitialAdministratorSerializer(AdministratorInputSerializer):
    institution_name = serializers.CharField(max_length=255, trim_whitespace=True)

    def validate_institution_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Enter the institution name.")
        return value


class AdministratorStatusSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()


def serialize_administrator(profile):
    return {
        "id": profile.user_id,
        "username": profile.user.get_username(),
        "administrator_name": profile.administrator_name,
        "email": profile.email,
        "role": profile.role,
        "is_active": profile.user.is_active,
    }
