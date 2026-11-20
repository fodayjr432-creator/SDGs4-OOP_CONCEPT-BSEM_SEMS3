from django.db import models
from django.db.models.expressions import RawSQL
from django.db.models.functions import Now

from apps.examinations.models import Examination
from apps.students.models import Student


class ExamResult(models.Model):
    class Grade(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"
        F = "F", "F"

    result_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        db_column="student_id",
        related_name="exam_results",
        on_delete=models.DO_NOTHING,
    )
    examination = models.ForeignKey(
        Examination,
        db_column="examination_id",
        related_name="results",
        on_delete=models.DO_NOTHING,
    )
    score = models.DecimalField(max_digits=6, decimal_places=2)
    grade = models.CharField(max_length=1, choices=Grade.choices, default=Grade.F)
    remarks = models.TextField(null=True, blank=True)
    date_recorded = models.DateTimeField(db_default=Now())
    last_updated = models.DateTimeField(db_default=Now())

    class Meta:
        managed = False
        db_table = "exam_results"
        ordering = ["-date_recorded", "-result_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "examination"],
                name="uq_student_examination",
            )
        ]


class ResultAudit(models.Model):
    class ActionType(models.TextChoices):
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"

    audit_id = models.BigAutoField(primary_key=True)
    result_id = models.IntegerField(null=True, blank=True)
    action_type = models.CharField(max_length=10, choices=ActionType.choices)
    old_record = models.JSONField(null=True, blank=True)
    new_record = models.JSONField(null=True, blank=True)
    action_time = models.DateTimeField(db_default=Now())
    database_user = models.TextField(db_default=RawSQL("CURRENT_USER", []))

    class Meta:
        managed = False
        db_table = "result_audit"
        ordering = ["-action_time", "-audit_id"]
