from getpass import getpass

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from rest_framework.authtoken.models import Token

from apps.accounts.models import UserProfile


class Command(BaseCommand):
    help = "Safely reset an institution administrator's password."

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            profile = UserProfile.objects.select_related("user").get(
                user__username=options["username"],
                role=UserProfile.Role.INSTITUTION_ADMIN,
            )
        except UserProfile.DoesNotExist as error:
            raise CommandError("Institution administrator not found.") from error

        password = getpass("New password: ")
        confirmation = getpass("Confirm new password: ")
        if password != confirmation:
            raise CommandError("The passwords do not match.")

        try:
            password_validation.validate_password(password, user=profile.user)
        except DjangoValidationError as error:
            raise CommandError("; ".join(error.messages)) from error

        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=profile.user_id)
            user.set_password(password)
            user.save(update_fields=["password"])
            Token.objects.filter(user=user).delete()

        self.stdout.write(
            self.style.SUCCESS("Administrator password reset; existing tokens revoked.")
        )
