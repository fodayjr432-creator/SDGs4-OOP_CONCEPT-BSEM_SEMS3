from django.db import models
from django.db.models.functions import Now

from apps.academics.models import Programme
from apps.core.fields import UTCNaiveDateTimeField


class Student(models.Model):
    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        OTHER = "Other", "Other"

    student_id = models.AutoField(primary_key=True)
    admission_number = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(
        max_length=15,
        choices=Gender.choices,
        null=True,
        blank=True,
    )
    programme = models.ForeignKey(
        Programme,
        db_column="programme_id",
        related_name="students",
        on_delete=models.DO_NOTHING,
    )
    date_registered = UTCNaiveDateTimeField(db_default=Now())
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "students"
        ordering = ["admission_number"]

    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name}"
