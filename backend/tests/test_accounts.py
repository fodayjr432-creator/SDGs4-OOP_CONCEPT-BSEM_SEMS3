from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.accounts.models import Institution, UserProfile


class InstitutionAccountApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def registration_payload(self, **overrides):
        return {
            "institution_name": "Example University",
            "administrator_name": "Taylor Administrator",
            "username": "taylor-admin",
            "email": "taylor.admin@example.test",
            "password": "Secure!Password2026",
            "confirm_password": "Secure!Password2026",
            **overrides,
        }

    def register_admin(self, **overrides):
        response = self.client.post(
            "/api/auth/register/",
            self.registration_payload(**overrides),
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response

    def login_admin(self, username="taylor-admin", password="Secure!Password2026"):
        response = self.client.post(
            "/api/auth/login/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {response.data['token']}"
        )
        return response

    def test_initial_registration_creates_hashed_admin_and_closes_signup(self):
        response = self.register_admin()

        self.assertEqual(response.data["institution"], "Example University")
        self.assertNotIn("password", response.data)
        self.assertNotIn("token", response.data)
        user = get_user_model().objects.get(username="taylor-admin")
        self.assertTrue(user.check_password("Secure!Password2026"))
        self.assertNotEqual(user.password, "Secure!Password2026")
        self.assertEqual(user.account_profile.role, UserProfile.Role.INSTITUTION_ADMIN)
        self.assertEqual(user.account_profile.institution.name, "Example University")
        self.assertEqual(
            self.client.get("/api/auth/registration-status/").data,
            {"registration_open": False},
        )

    def test_duplicate_initial_registration_is_rejected(self):
        self.register_admin()

        response = self.client.post(
            "/api/auth/register/",
            self.registration_payload(
                username="another-admin",
                email="another@example.test",
            ),
            format="json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            get_user_model().objects.filter(
                account_profile__role=UserProfile.Role.INSTITUTION_ADMIN
            ).count(),
            1,
        )

    def test_duplicate_username_is_rejected(self):
        get_user_model().objects.create_user(
            username="taylor-admin",
            password="Unrelated!Password2026",
        )

        response = self.client.post(
            "/api/auth/register/",
            self.registration_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)
        self.assertEqual(UserProfile.objects.count(), 0)

    def test_duplicate_email_is_rejected(self):
        get_user_model().objects.create_user(
            username="existing-user",
            email="taylor.admin@example.test",
            password="Unrelated!Password2026",
        )

        response = self.client.post(
            "/api/auth/register/",
            self.registration_payload(username="different-admin"),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)
        self.assertEqual(UserProfile.objects.count(), 0)

    def test_weak_password_and_mismatched_confirmation_are_rejected(self):
        weak = self.client.post(
            "/api/auth/register/",
            self.registration_payload(
                password="password",
                confirm_password="password",
            ),
            format="json",
        )
        self.assertEqual(weak.status_code, 400)
        self.assertIn("password", weak.data)

        mismatch = self.client.post(
            "/api/auth/register/",
            self.registration_payload(confirm_password="Different!Password2026"),
            format="json",
        )
        self.assertEqual(mismatch.status_code, 400)
        self.assertIn("confirm_password", mismatch.data)

    def test_password_must_include_a_letter_number_and_special_character(self):
        invalid_passwords = (
            "OnlyLetters!NoDigit",
            "123456789012!",
            "NoSpecial123456",
        )
        for password in invalid_passwords:
            with self.subTest(password=password):
                response = self.client.post(
                    "/api/auth/register/",
                    self.registration_payload(
                        password=password,
                        confirm_password=password,
                    ),
                    format="json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("password", response.data)

        self.assertEqual(get_user_model().objects.count(), 0)

    def test_admin_login_rejects_bad_password_and_inactive_accounts(self):
        self.register_admin()

        incorrect = self.client.post(
            "/api/auth/login/",
            {"username": "taylor-admin", "password": "incorrect"},
            format="json",
        )
        self.assertEqual(incorrect.status_code, 401)

        user = get_user_model().objects.get(username="taylor-admin")
        user.is_active = False
        user.save(update_fields=["is_active"])
        inactive = self.client.post(
            "/api/auth/login/",
            {"username": "taylor-admin", "password": "Secure!Password2026"},
            format="json",
        )
        self.assertEqual(inactive.status_code, 401)

    def test_ordinary_user_cannot_login_or_use_administrator_apis(self):
        ordinary_user = get_user_model().objects.create_user(
            username="ordinary-user",
            password="Secure!Password2026",
        )
        login = self.client.post(
            "/api/auth/login/",
            {"username": "ordinary-user", "password": "Secure!Password2026"},
            format="json",
        )
        self.assertEqual(login.status_code, 401)

        token = Token.objects.create(user=ordinary_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        dashboard = self.client.get("/api/dashboard/")
        administrators = self.client.get("/api/auth/admins/")
        self.assertEqual(dashboard.status_code, 403)
        self.assertEqual(administrators.status_code, 403)

    def test_staff_user_cannot_login_or_access_admin_apis(self):
        institution = Institution.objects.create(name="Staff Test Institution")
        staff_user = get_user_model().objects.create_user(
            username="teacher-user",
            password="Secure!Password2026",
        )
        UserProfile.objects.create(
            user=staff_user,
            institution=institution,
            administrator_name="Teacher User",
            email="teacher@example.test",
            role=UserProfile.Role.STAFF,
        )

        login = self.client.post(
            "/api/auth/login/",
            {"username": "teacher-user", "password": "Secure!Password2026"},
            format="json",
        )
        self.assertEqual(login.status_code, 401)

        token = Token.objects.create(user=staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(self.client.get("/api/dashboard/").status_code, 403)
        self.assertEqual(self.client.get("/api/auth/admins/").status_code, 403)

    def test_token_authentication_dashboard_and_logout_invalidation(self):
        self.register_admin()
        login = self.login_admin()

        current_user = self.client.get("/api/auth/me/")
        self.assertEqual(current_user.status_code, 200)
        self.assertEqual(current_user.data["role"], UserProfile.Role.INSTITUTION_ADMIN)
        report = {
            "total_students": 0,
            "total_programmes": 0,
            "total_modules": 0,
            "total_examinations": 0,
            "total_results": 0,
        }
        with patch("config.views._report_data", return_value=report), patch(
            "config.views._recent_dashboard_results",
            return_value=[],
        ):
            dashboard = self.client.get("/api/dashboard/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(
            dashboard.data,
            {
                "counts": {
                    "students": 0,
                    "programmes": 0,
                    "modules": 0,
                    "examinations": 0,
                    "results": 0,
                },
                "recent_results": [],
            },
        )

        logout = self.client.post("/api/auth/logout/")
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(self.client.get("/api/dashboard/").status_code, 401)
        self.assertFalse(Token.objects.filter(key=login.data["token"]).exists())

    def test_administrator_can_provision_and_deactivate_another_admin(self):
        self.register_admin()
        self.login_admin()
        response = self.client.post(
            "/api/auth/admins/",
            {
                "administrator_name": "Jordan Second",
                "username": "jordan-second",
                "email": "jordan.second@example.test",
                "password": "Another!SecurePassword2026",
                "confirm_password": "Another!SecurePassword2026",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        second_user_id = response.data["id"]

        inactive = self.client.patch(
            f"/api/auth/admins/{second_user_id}/",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(inactive.status_code, 200, inactive.data)
        second_user = get_user_model().objects.get(pk=second_user_id)
        self.assertFalse(second_user.is_active)

        active = self.client.patch(
            f"/api/auth/admins/{second_user_id}/",
            {"is_active": True},
            format="json",
        )
        self.assertEqual(active.status_code, 200, active.data)
        self.assertTrue(get_user_model().objects.get(pk=second_user_id).is_active)

    def test_password_recovery_revokes_existing_tokens(self):
        self.register_admin()
        login = self.login_admin()
        token_key = login.data["token"]

        with patch(
            "apps.accounts.management.commands.reset_institution_admin_password.getpass",
            side_effect=["Changed!Password2026", "Changed!Password2026"],
        ):
            call_command(
                "reset_institution_admin_password",
                "taylor-admin",
                stdout=StringIO(),
            )

        user = get_user_model().objects.get(username="taylor-admin")
        self.assertTrue(user.check_password("Changed!Password2026"))
        self.assertFalse(Token.objects.filter(key=token_key).exists())
