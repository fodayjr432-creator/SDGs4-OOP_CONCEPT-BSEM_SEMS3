import json
import unittest
from unittest.mock import patch

import requests

from api_client import ApiClient, ApiError


def response(status_code, payload=None):
    result = requests.Response()
    result.status_code = status_code
    result.headers["Content-Type"] = "application/json"
    result._content = json.dumps(payload or {}).encode("utf-8")
    return result


class ApiClientTests(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient(base_url="http://example.test")

    def tearDown(self):
        self.client.close()

    def test_login_extracts_token_and_authenticated_get_sends_header(self):
        with patch.object(
            self.client._session,
            "request",
            return_value=response(200, {"token": "session-token"}),
        ) as request:
            account = self.client.login("user", "password")
            self.assertEqual(account["token"], "session-token")
            self.assertEqual(self.client.token, "session-token")

            request.return_value = response(200, [{"student_id": 8}])
            self.assertEqual(self.client.get("/students/"), [{"student_id": 8}])

        self.assertEqual(
            request.call_args.kwargs["headers"]["Authorization"],
            "Token session-token",
        )

    def test_login_rejects_empty_or_missing_token(self):
        with patch.object(
            self.client._session,
            "request",
            return_value=response(200, {"username": "user"}),
        ):
            with self.assertRaisesRegex(ApiError, "authentication response"):
                self.client.login("user", "password")
        self.assertIsNone(self.client.token)

    def test_institution_registration_sends_all_required_fields(self):
        payload = {
            "institution_name": "Example University",
            "administrator_name": "Taylor Admin",
            "username": "taylor-admin",
            "email": "taylor@example.test",
            "password": "Strong!Password2026",
            "confirm_password": "Strong!Password2026",
        }
        with patch.object(
            self.client,
            "request",
            return_value={"detail": "created"},
        ) as request:
            result = self.client.register_institution_administrator(**payload)

        self.assertEqual(result, {"detail": "created"})
        request.assert_called_once_with("POST", "/api/auth/register/", payload)

    def test_institution_name_update_uses_existing_authentication_contract(self):
        self.client.token = "session-token"
        with patch.object(
            self.client,
            "request",
            return_value={"institution": "Renamed University"},
        ) as request:
            result = self.client.update_institution_name("Renamed University")

        self.assertEqual(result["institution"], "Renamed University")
        request.assert_called_once_with(
            "PATCH",
            "/api/auth/institution/",
            {"institution_name": "Renamed University"},
        )

    def test_unauthorized_response_clears_session_token(self):
        self.client.token = "expired-token"
        with patch.object(
            self.client._session,
            "request",
            return_value=response(401, {"detail": "Invalid token."}),
        ):
            with self.assertRaisesRegex(ApiError, "Invalid token") as raised:
                self.client.get("/students/")
        self.assertEqual(raised.exception.status_code, 401)
        self.assertIsNone(self.client.token)

    def test_logout_clears_token_even_when_request_fails(self):
        self.client.token = "session-token"
        with patch.object(
            self.client._session,
            "request",
            side_effect=requests.ConnectionError("unavailable"),
        ):
            with self.assertRaises(ApiError):
                self.client.logout()
        self.assertIsNone(self.client.token)

    def test_student_helpers_use_backend_paths_and_search_parameter(self):
        self.client.token = "session-token"
        with patch.object(
            self.client._session,
            "request",
            return_value=response(200, []),
        ) as request:
            self.client.list_students(search="name")
            self.client.get_student(12)
            self.client.delete_student(12)

        self.assertIn(
            "/students/?search=name",
            request.call_args_list[0].args[1],
        )
        self.assertTrue(request.call_args_list[1].args[1].endswith("/students/12/"))
        self.assertEqual(request.call_args_list[2].args[0], "DELETE")

    def test_network_failure_does_not_expose_credentials(self):
        with patch.object(
            self.client._session,
            "request",
            side_effect=requests.Timeout("request timed out"),
        ):
            with self.assertRaises(ApiError) as raised:
                self.client.login("private-user", "private-password")
        self.assertNotIn("private-password", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
