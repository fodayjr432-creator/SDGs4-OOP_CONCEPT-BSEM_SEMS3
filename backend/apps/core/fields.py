from datetime import datetime, timezone as datetime_timezone

from django.db import models
from django.utils import timezone


class UTCNaiveDateTimeField(models.DateTimeField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        if not isinstance(value, datetime):
            value = self.to_python(value)
        if timezone.is_naive(value):
            return timezone.make_aware(value, datetime_timezone.utc)
        return value
