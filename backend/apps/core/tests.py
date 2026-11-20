from django.test import SimpleTestCase
from rest_framework.test import APIClient

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


class DeferredAuthenticationApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_is_not_falsely_accepted_without_account_storage(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "unused", "password": "unused"},
            format="json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn("authentication", response.data["error"].lower())

    def test_academic_data_endpoints_remain_closed(self):
        responses = (
            self.client.get("/api/students/"),
            self.client.post("/api/students/", {}, format="json"),
            self.client.get("/api/results/"),
            self.client.get("/api/dashboard/"),
        )

        for response in responses:
            with self.subTest(status=response.status_code):
                self.assertEqual(response.status_code, 503)
