from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Unavailable until authentication storage is approved and implemented."

    def add_arguments(self, parser):
        parser.add_argument("--role", choices=("admin", "lecturer"), required=True)

    def handle(self, *args, **options):
        raise CommandError(
            "No account table exists in the inspected PostgreSQL schema. "
            "No account was created; authentication is deferred."
        )
