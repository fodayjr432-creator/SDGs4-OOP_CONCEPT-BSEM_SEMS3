from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from rest_framework.test import APIClient

from apps.academics.models import AcademicYear, Module, Programme
from apps.examinations.models import Examination
from apps.results.models import ExamResult
from apps.students.models import Student


TEST_MODELS = (
    AcademicYear,
    Programme,
    Module,
    Student,
    Examination,
    ExamResult,
)


class AuthAndStudentApiTests(TestCase):
    @classmethod
    def setUpClass(cls):
        with connection.schema_editor() as editor:
            for model in TEST_MODELS:
                editor.create_model(model)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        with connection.schema_editor() as editor:
            for model in reversed(TEST_MODELS):
                editor.delete_model(model)

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student-api-test",
            password="test-only-password",
        )
        self.programme = Programme.objects.create(
            programme_code="TST",
            programme_name="Test Programme",
            is_active=True,
        )
        self.client = APIClient()

    def login(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "student-api-test",
                "password": "test-only-password",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        return token

    def student_payload(self, **overrides):
        return {
            "admission_number": "TEST-001",
            "first_name": "Test",
            "last_name": "Student",
            "age": 20,
            "programme_id": self.programme.pk,
            **overrides,
        }

    def test_login_success_invalid_credentials_and_protected_access(self):
        unauthenticated = self.client.get("/api/students/")
        self.assertEqual(unauthenticated.status_code, 401)

        invalid = self.client.post(
            "/api/auth/login/",
            {"username": "student-api-test", "password": "incorrect"},
            format="json",
        )
        self.assertEqual(invalid.status_code, 401)

        self.login()
        self.assertEqual(self.client.get("/api/students/").status_code, 200)

    def test_student_create_retrieve_search_and_update(self):
        self.login()
        created = self.client.post(
            "/api/students/",
            self.student_payload(),
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        student_id = created.data["student_id"]
        self.assertEqual(created.data["admission_number"], "TEST-001")

        retrieved = self.client.get(f"/api/students/{student_id}/")
        self.assertEqual(retrieved.status_code, 200)
        self.assertEqual(retrieved.data["first_name"], "Test")

        searched = self.client.get("/api/students/?search=TEST-001")
        self.assertEqual(searched.status_code, 200)
        self.assertEqual(len(searched.data), 1)

        updated = self.client.put(
            f"/api/students/{student_id}/",
            self.student_payload(first_name="Updated"),
            format="json",
        )
        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertEqual(updated.data["first_name"], "Updated")
        self.assertEqual(
            Student.objects.get(pk=student_id).first_name,
            "Updated",
        )

    def test_student_rejects_duplicate_and_invalid_values(self):
        self.login()
        first = self.client.post(
            "/api/students/", self.student_payload(), format="json"
        )
        self.assertEqual(first.status_code, 201, first.data)

        duplicate = self.client.post(
            "/api/students/",
            self.student_payload(first_name="Other"),
            format="json",
        )
        self.assertEqual(duplicate.status_code, 400)

        invalid_age = self.client.post(
            "/api/students/",
            self.student_payload(admission_number="TEST-002", age=121),
            format="json",
        )
        self.assertEqual(invalid_age.status_code, 400)

        missing_name = self.client.post(
            "/api/students/",
            self.student_payload(admission_number="TEST-003", last_name=""),
            format="json",
        )
        self.assertEqual(missing_name.status_code, 400)

    def test_student_delete_without_results(self):
        self.login()
        student = self.client.post(
            "/api/students/", self.student_payload(), format="json"
        )
        self.assertEqual(student.status_code, 201, student.data)
        student_id = student.data["student_id"]

        response = self.client.delete(f"/api/students/{student_id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Student.objects.filter(pk=student_id).exists())

    def test_student_with_results_cannot_be_deleted(self):
        self.login()
        student = self.client.post(
            "/api/students/", self.student_payload(), format="json"
        )
        self.assertEqual(student.status_code, 201, student.data)
        student_id = student.data["student_id"]
        academic_year = AcademicYear.objects.create(
            year_name="2099/2100",
            start_date="2099-01-01",
            end_date="2100-01-01",
            is_current=False,
        )
        module = Module.objects.create(
            module_code="TST101",
            module_name="Test Module",
        )
        examination = Examination.objects.create(
            examination_code="TST-EXAM",
            examination_title="Test Exam",
            module=module,
            academic_year=academic_year,
            examination_type=Examination.ExaminationType.FINAL,
        )
        ExamResult.objects.create(
            student_id=student_id,
            examination=examination,
            score=75,
            grade="A",
        )

        response = self.client.delete(f"/api/students/{student_id}/")
        self.assertEqual(response.status_code, 409)
        self.assertTrue(Student.objects.filter(pk=student_id).exists())

    def test_logout_revokes_token_and_clears_client_credentials(self):
        token = self.login()
        logout = self.client.post("/api/auth/logout/")
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(self.client.get("/api/students/").status_code, 401)
        self.assertTrue(token)
