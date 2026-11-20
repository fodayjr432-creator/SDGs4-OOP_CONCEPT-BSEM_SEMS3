from django.test import SimpleTestCase

from apps.academics.models import AcademicYear, Module, Programme
from apps.examinations.models import Examination, Question
from apps.results.models import ExamResult, ResultAudit
from apps.students.models import Student


class ExistingSchemaMappingTests(SimpleTestCase):
    def test_models_map_to_existing_tables_without_managing_schema(self):
        expected_tables = {
            AcademicYear: "academic_years",
            Programme: "programmes",
            Module: "modules",
            Student: "students",
            Examination: "examinations",
            Question: "questions",
            ExamResult: "exam_results",
            ResultAudit: "result_audit",
        }

        for model, table_name in expected_tables.items():
            with self.subTest(model=model.__name__):
                self.assertEqual(model._meta.db_table, table_name)
                self.assertFalse(model._meta.managed)

    def test_programme_module_link_uses_existing_join_table(self):
        self.assertEqual(Programme.modules.through._meta.db_table, "programme_modules")
        self.assertFalse(Programme.modules.through._meta.managed)
