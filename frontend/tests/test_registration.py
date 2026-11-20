import os
import unittest
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QDialog

from gui.windows.registration_window import RegistrationWindow


class RegistrationWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.api = Mock()
        self.window = RegistrationWindow(api_client=self.api)

    def tearDown(self):
        self.window.close()

    def test_registration_validates_required_fields_and_confirmation(self):
        self.window.submit()
        self.assertIn("Complete all fields", self.window.status.text())
        self.api.register_institution_administrator.assert_not_called()

        self.window.institution_name.setText("Example University")
        self.window.administrator_name.setText("Taylor Administrator")
        self.window.username.setText("taylor-admin")
        self.window.email.setText("taylor@example.test")
        self.window.password.setText("Strong!Password2026")
        self.window.confirm_password.setText("different-password")
        self.window.submit()

        self.assertIn("passwords do not match", self.window.status.text())
        self.api.register_institution_administrator.assert_not_called()

    def test_successful_registration_confirms_account_and_closes(self):
        self.window.institution_name.setText("Example University")
        self.window.administrator_name.setText("Taylor Administrator")
        self.window.username.setText("taylor-admin")
        self.window.email.setText("taylor@example.test")
        self.window.password.setText("Strong!Password2026")
        self.window.confirm_password.setText("Strong!Password2026")
        self.api.register_institution_administrator.return_value = {
            "detail": "created"
        }

        self.window.submit()
        self.wait_for(lambda: self.window._registered)
        self.wait_for(lambda: self.window._worker is None)

        self.api.register_institution_administrator.assert_called_once_with(
            "Example University",
            "Taylor Administrator",
            "taylor-admin",
            "taylor@example.test",
            "Strong!Password2026",
            "Strong!Password2026",
        )
        self.assertIn("account created", self.window.status.text())
        self.window.submit()
        self.assertEqual(self.window.result(), QDialog.DialogCode.Accepted)

    @staticmethod
    def wait_for(condition, timeout_ms=3000):
        elapsed = 0
        while not condition() and elapsed < timeout_ms:
            QTest.qWait(20)
            QCoreApplication.processEvents()
            elapsed += 20
        if not condition():
            raise AssertionError("Timed out waiting for registration worker.")


if __name__ == "__main__":
    unittest.main()
