from getpass import getpass

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import Institution, UserProfile


class Command(BaseCommand):
    help = "Create an institution administrator or staff account."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--role", choices=("admin", "lecturer"), required=True)
        parser.add_argument("--name", required=True)
        parser.add_argument("--email", required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"].strip()
        name = options["name"].strip()
        email = options["email"].strip().casefold()

        if not username or not name or not email:
            raise CommandError("Username, name, and email are required.")
        if User.objects.filter(username__iexact=username).exists():
            raise CommandError("This username is already in use.")
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError("This email address is already in use.")
        if UserProfile.objects.filter(email__iexact=email).exists():
            raise CommandError("This email address is already in use.")

        try:
            institution = Institution.objects.get(is_singleton=True)
        except Institution.DoesNotExist as error:
            raise CommandError(
                "Create the institution through first-time administrator registration first."
            ) from error

        password = getpass("Password: ")
        confirmation = getpass("Confirm password: ")
        if password != confirmation:
            raise CommandError("The passwords do not match.")

        role = (
            UserProfile.Role.INSTITUTION_ADMIN
            if options["role"] == "admin"
            else UserProfile.Role.STAFF
        )
        name_parts = name.split(maxsplit=1)
        candidate = User(username=username, email=email)
        candidate.first_name = name_parts[0]
        candidate.last_name = name_parts[1] if len(name_parts) == 2 else ""

        try:
            password_validation.validate_password(password, user=candidate)
        except DjangoValidationError as error:
            raise CommandError("; ".join(error.messages)) from error

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=candidate.first_name,
                last_name=candidate.last_name,
            )
            UserProfile.objects.create(
                user=user,
                institution=institution,
                administrator_name=name,
                email=email,
                role=role,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{options['role'].title()} account '{username}' created."
            )
        )
