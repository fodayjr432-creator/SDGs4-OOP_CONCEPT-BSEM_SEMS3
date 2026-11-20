from django.core.management.base import BaseCommand

from django.db import connection


class Command(BaseCommand):
    help = "Verify the configured PostgreSQL connection without changing its schema."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_schema()")
            database_name, schema_name = cursor.fetchone()
        self.stdout.write(
            self.style.SUCCESS(
                f"Connected to PostgreSQL database {database_name!r}, "
                f"schema {schema_name!r}; no schema changes were made."
            )
        )
