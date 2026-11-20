from django.db import models


class AcademicYear(models.Model):
    academic_year_id = models.AutoField(primary_key=True)
    year_name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "academic_years"
        ordering = ["-start_date"]


class Programme(models.Model):
    programme_id = models.AutoField(primary_key=True)
    programme_code = models.CharField(max_length=10, unique=True)
    programme_name = models.CharField(max_length=150, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    modules = models.ManyToManyField(
        "Module",
        through="ProgrammeModule",
        related_name="programmes",
    )

    class Meta:
        managed = False
        db_table = "programmes"
        ordering = ["programme_code"]

    def __str__(self):
        return f"{self.programme_code} - {self.programme_name}"


class Module(models.Model):
    module_id = models.AutoField(primary_key=True)
    module_code = models.CharField(max_length=15)
    module_name = models.CharField(max_length=150)
    level = models.CharField(max_length=10, default="1")
    semester = models.CharField(max_length=10, default="1")
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "modules"
        ordering = ["module_code"]

    def __str__(self):
        return f"{self.module_code} - {self.module_name}"


class ProgrammeModule(models.Model):
    pk = models.CompositePrimaryKey("programme", "module")
    programme = models.ForeignKey(
        Programme,
        db_column="programme_id",
        on_delete=models.DO_NOTHING,
    )
    module = models.ForeignKey(
        Module,
        db_column="module_id",
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        managed = False
        db_table = "programme_modules"
