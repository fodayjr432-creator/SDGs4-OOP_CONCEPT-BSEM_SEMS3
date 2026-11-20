from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Unavailable until authentication storage is approved and implemented."

    def handle(self, *args, **options):
        raise CommandError(
            "No account table exists in the inspected PostgreSQL schema. "
            "No administrator was created; authentication is deferred."
        )
