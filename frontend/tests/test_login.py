import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest

from api_client import ApiClient, ApiError
from gui.windows.login_window import LoginWindow


BACKEND_STATUS = {"authentication_configured": True}
REGISTRATION_STATUS = {"registration_open": True}


class LoginWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.registration_status_patch = patch.object(
            ApiClient,
            "registration_status",
            return_value=REGISTRATION_STATUS,
        )
        self.registration_status_patch.start()
        with patch.object(
            ApiClient,
            "status",
            return_value=BACKEND_STATUS,
        ):
            self.window = LoginWindow()
        self.window.show()
        self.wait_for(lambda: self.window.login_button.isEnabled())

    def tearDown(self):
        self.window.close()
        self.wait_for(lambda: self.window._worker is None)
        self.registration_status_patch.stop()

    def wait_for(self, condition, timeout_ms=3000):
        elapsed = 0
        while not condition() and elapsed < timeout_ms:
            QTest.qWait(20)
            elapsed += 20
        self.assertTrue(condition(), "Timed out waiting for GUI worker.")

    def test_successful_login_opens_protected_window(self):
        self.window.username.setText("actual-user")
        self.window.password.setText("entered-password")

        def authenticate(username, password):
            self.window.api.token = "returned-token"
            return {"token": "returned-token", "username": username}

        with patch.object(
            self.window.api,
            "login",
            side_effect=authenticate,
        ) as login, patch(
            "gui.windows.login_window.AppState"
        ) as app_state, patch(
            "gui.windows.main_window.MainWindow"
        ) as main_window:
            self.window.login()
            self.wait_for(lambda: self.window.main_window is not None)

        login.assert_called_once_with("actual-user", "entered-password")
        self.assertEqual(self.window.api.token, "returned-token")
        app_state.assert_called_once_with(
            username="actual-user",
            api_client=self.window.api,
            account={"token": "returned-token", "username": "actual-user"},
        )
        main_window.assert_called_once()
        main_window.return_value.show.assert_called_once()

    def test_invalid_credentials_keep_protected_window_closed(self):
        self.window.username.setText("actual-user")
        self.window.password.setText("wrong-password")
        with patch.object(
            self.window.api,
            "login",
            side_effect=ApiError("Invalid credentials."),
        ):
            self.window.login()
            self.wait_for(lambda: self.window.login_button.isEnabled())

        self.assertEqual(self.window.status.text(), "Invalid credentials.")
        self.assertIsNone(self.window.main_window)

    def test_empty_fields_do_not_send_authentication_request(self):
        with patch.object(self.window.api, "login") as login:
            self.window.login()

        login.assert_not_called()
        self.assertEqual(self.window.status.text(), "Enter both username and password.")
        self.assertTrue(self.window.login_button.isEnabled())

    def test_authentication_unavailable_prevents_login(self):
        self.window._authentication_available = False
        with patch.object(self.window.api, "login") as login:
            self.window.login()

        login.assert_not_called()
        self.assertIsNone(self.window.main_window)
        self.assertIn("authentication available", self.window.status.text())

    def test_first_time_setup_opens_registration_dialog(self):
        with patch(
            "gui.windows.login_window.RegistrationWindow"
        ) as registration_window:
            registration_window.return_value.exec.return_value = 0
            self.window.open_registration()

        registration_window.assert_called_once_with(self.window.api, self.window)
        registration_window.return_value.registration_succeeded.connect.assert_called_once()
        registration_window.return_value.exec.assert_called_once()

    def test_registration_route_is_hidden_after_first_setup(self):
        self.window._registration_status_received({"registration_open": False})

        self.assertFalse(self.window.registration_button.isVisible())
        self.assertFalse(self.window.registration_button.isEnabled())

    def test_repeated_submission_is_ignored_while_processing(self):
        self.window.username.setText("actual-user")
        self.window.password.setText("entered-password")
        operation_started = Mock()

        def delayed_login(*_args):
            operation_started()
            QTest.qWait(100)
            raise ApiError("Invalid credentials.")

        with patch.object(self.window.api, "login", side_effect=delayed_login):
            self.window.login()
            self.window.login()
            self.wait_for(lambda: self.window.login_button.isEnabled())

        operation_started.assert_called_once()
        self.assertIsNone(self.window.main_window)


if __name__ == "__main__":
    unittest.main()
