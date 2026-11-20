import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLineEdit
from PyQt6.QtTest import QTest

from api_client import ApiClient, ApiError
from gui.windows.login_window import LoginWindow


BACKEND_STATUS = {
    "status": "ok",
    "database": "postgresql",
    "authentication_configured": False,
    "data_api_available": False,
}


class LoginWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        with patch.object(ApiClient, "status", return_value=BACKEND_STATUS):
            self.window = LoginWindow()
        self.window.show()
        QTest.qWait(20)

    def tearDown(self):
        self.window.close()

    def test_authentication_deferred_message_is_shown(self):
        self.assertIn("authentication is not configured", self.window.status.text())
        self.assertIn("Sign-in is unavailable", self.window.status.text())

    def test_empty_fields_are_reported_without_authentication(self):
        self.window.login()

        self.assertEqual(
            self.window.status.text(),
            "Enter both username and password.",
        )
        self.assertFalse(self.window._processing)
        self.assertTrue(self.window.login_button.isEnabled())

    def test_password_visibility_can_be_toggled(self):
        self.assertEqual(
            self.window.password.echoMode(),
            QLineEdit.EchoMode.Password,
        )
        self.window.password_toggle.click()
        self.assertEqual(
            self.window.password.echoMode(),
            QLineEdit.EchoMode.Normal,
        )
        self.window.password_toggle.click()
        self.assertEqual(
            self.window.password.echoMode(),
            QLineEdit.EchoMode.Password,
        )

    def test_backend_authentication_unavailable_restores_the_form(self):
        self.window.username.setText("entered-user")
        self.window.password.setText("entered-password")
        with patch.object(
            self.window.api,
            "login",
            side_effect=ApiError("Authentication is not configured."),
        ):
            self.window.login()
            QTest.qWait(50)

        self.assertEqual(
            self.window.status.text(),
            "Authentication is not configured.",
        )
        self.assertTrue(self.window.login_button.isEnabled())
        self.assertTrue(self.window.username.isEnabled())
        self.assertTrue(self.window.password.isEnabled())
        self.assertIsNone(self.window.main_window)

    def test_enter_submits_from_the_password_field(self):
        self.window.username.setText("entered-user")
        self.window.username.setFocus()
        QTest.keyClick(self.window.username, Qt.Key.Key_Return)
        self.assertTrue(self.window.password.hasFocus())

        self.window.password.setText("entered-password")
        with patch.object(
            self.window.api,
            "login",
            side_effect=ApiError("Authentication is not configured."),
        ):
            QTest.keyClick(self.window.password, Qt.Key.Key_Return)
            QTest.qWait(50)

        self.assertIsNone(self.window.main_window)
        self.assertTrue(self.window.login_button.isEnabled())

    def test_repeated_submission_is_ignored_while_processing(self):
        self.window.username.setText("entered-user")
        self.window.password.setText("entered-password")
        with patch.object(
            self.window.api,
            "login",
            side_effect=ApiError("Authentication is not configured."),
        ) as login_mock:
            self.window.login()
            self.window.login()
            self.assertFalse(self.window.login_button.isEnabled())
            QTest.qWait(50)

        login_mock.assert_called_once_with("entered-user", "entered-password")


if __name__ == "__main__":
    unittest.main()
