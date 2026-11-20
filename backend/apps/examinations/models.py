from django.db import models

from apps.academics.models import AcademicYear, Module


class Examination(models.Model):
    class ExaminationType(models.TextChoices):
        QUIZ = "Quiz", "Quiz"
        MIDTERM = "Midterm", "Midterm"
        FINAL = "Final", "Final"
        PRACTICAL = "Practical", "Practical"
        ASSIGNMENT = "Assignment", "Assignment"

    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

    examination_id = models.AutoField(primary_key=True)
    examination_code = models.CharField(max_length=30, unique=True)
    examination_title = models.CharField(max_length=150)
    module = models.ForeignKey(
        Module,
        db_column="module_id",
        related_name="examinations",
        on_delete=models.DO_NOTHING,
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        db_column="academic_year_id",
        related_name="examinations",
        on_delete=models.DO_NOTHING,
    )
    examination_type = models.CharField(
        max_length=30,
        choices=ExaminationType.choices,
    )
    examination_date = models.DateField(null=True, blank=True)
    maximum_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        managed = False
        db_table = "examinations"
        ordering = ["-examination_date", "examination_code"]

    def __str__(self):
        return f"{self.examination_code} - {self.examination_title}"


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "Multiple choice"
        TRUE_FALSE = "TRUE_FALSE", "True/false"
        SHORT_ANSWER = "SHORT_ANSWER", "Short answer"

    question_id = models.AutoField(primary_key=True)
    examination = models.ForeignKey(
        Examination,
        db_column="examination_id",
        related_name="questions",
        on_delete=models.DO_NOTHING,
    )
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.TextField(null=True, blank=True)
    marks = models.DecimalField(max_digits=6, decimal_places=2)
    question_order = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = "questions"
        ordering = ["question_order"]

    def __str__(self):
        return f"Question {self.question_order} for {self.examination}"
