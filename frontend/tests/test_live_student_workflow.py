import os
import unittest
import uuid
import getpass
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtTest import QTest

from api_client import ApiClient
from gui.app_state import AppState
from gui.pages import students_page
from gui.pages.students_page import StudentsPage
from programme import Programme


LIVE_TEST_ENABLED = os.environ.get("EXAM_RUN_LIVE_STUDENT_TESTS") == "YES"


@unittest.skipUnless(
    LIVE_TEST_ENABLED,
    "Set EXAM_RUN_LIVE_STUDENT_TESTS=YES to run against PostgreSQL.",
)
class LiveStudentWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        username = os.environ.get("EXAM_LIVE_TEST_USERNAME")
        if not username:
            self.skipTest(
                "Set EXAM_LIVE_TEST_USERNAME to use an existing local account."
            )

        self.api = ApiClient()
        self.addCleanup(self.api.close)
        password = os.environ.get("EXAM_LIVE_TEST_PASSWORD")
        if not password:
            password = getpass.getpass("Existing backend account password: ")
        self.api.login(username, password)
        self.programmes = [
            Programme(
                row["programme_code"],
                row["programme_name"],
                row["programme_id"],
            )
            for row in self.api.get("/api/programmes/")
            if row["is_active"]
        ]
        if not self.programmes:
            self.skipTest("The database has no active programme for the test.")

        self.admission_number = f"INT-{uuid.uuid4().hex[:20]}"
        if any(
            row["admission_number"] == self.admission_number
            for row in self.api.list_students(search=self.admission_number)
        ):
            self.skipTest("Generated test admission number already exists.")
        self.addCleanup(self._delete_only_test_record)

    def _delete_only_test_record(self):
        if not self.api.token:
            return
        matching = [
            row
            for row in self.api.list_students(search=self.admission_number)
            if row["admission_number"] == self.admission_number
        ]
        for row in matching:
            self.api.delete_student(row["student_id"])

    def make_state(self):
        state = AppState.__new__(AppState)
        state.api = self.api
        state.programmes = self.programmes
        state.username = "live-admin"
        state.account = {"username": "live-admin", "role": "institution_admin"}
        return state

    def wait_for(self, condition, timeout_ms=10000):
        elapsed = 0
        while not condition() and elapsed < timeout_ms:
            QTest.qWait(20)
            elapsed += 20
        self.assertTrue(condition(), "Timed out waiting for live API operation.")

    @staticmethod
    def student_values(admission_number, first_name, programme_code):
        return {
            "student_id": admission_number,
            "first_name": first_name,
            "last_name": "Workflow",
            "name": f"{first_name} Workflow",
            "age": 20,
            "gender": "Other",
            "programme": programme_code,
        }

    def test_pyqt_student_crud_search_and_database_persistence(self):
        programme = self.programmes[0]
        initial = self.student_values(
            self.admission_number,
            "Integration",
            programme.code,
        )
        state = self.make_state()
        page = StudentsPage(state)
        self.addCleanup(page.close)

        with patch.object(students_page.QMessageBox, "critical"), patch.object(
            students_page.QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            page.refresh()
            self.wait_for(lambda: page._worker is None)

            add_dialog = Mock()
            add_dialog.exec.return_value = QDialog.DialogCode.Accepted
            add_dialog.values.return_value = initial
            with patch.object(
                students_page, "StudentDialog", return_value=add_dialog
            ):
                page.add_student()
            self.wait_for(
                lambda: page._worker is None
                and any(
                    page.table.item(row, 0).text() == self.admission_number
                    for row in range(page.table.rowCount())
                )
            )

            page.search.setText(self.admission_number)
            self.wait_for(lambda: page._worker is not None)
            self.wait_for(lambda: page._worker is None)
            self.wait_for(
                lambda: page._worker is None
                and page.table.rowCount() == 1
            )
            self.assertEqual(
                self.api.list_students(search=self.admission_number)[0][
                    "admission_number"
                ],
                self.admission_number,
            )

            page.table.setCurrentCell(0, 0)
            updated = self.student_values(
                self.admission_number,
                "Updated",
                programme.code,
            )
            edit_dialog = Mock()
            edit_dialog.exec.return_value = QDialog.DialogCode.Accepted
            edit_dialog.values.return_value = updated
            with patch.object(
                students_page, "StudentDialog", return_value=edit_dialog
            ):
                page.edit_student()
                self.wait_for(
                    lambda: page._worker is None
                    and page.table.rowCount() == 1
                    and page.table.item(0, 1).text() == "Updated Workflow"
                )

            student_id = self.api.list_students(
                search=self.admission_number
            )[0]["student_id"]
            reloaded_state = self.make_state()
            reloaded_page = StudentsPage(reloaded_state)
            self.addCleanup(reloaded_page.close)
            reloaded_page.search.setText(self.admission_number)
            reloaded_page.search_timer.stop()
            reloaded_page.refresh()
            self.wait_for(
                lambda: reloaded_page._worker is None
                and reloaded_page.table.rowCount() == 1
                and reloaded_page.table.item(0, 1).text() == "Updated Workflow"
            )

            reloaded_page.table.setCurrentCell(0, 0)
            reloaded_page.delete_student()
            self.wait_for(
                lambda: reloaded_page._worker is None
                and reloaded_page.table.rowCount() == 0
            )
            self.assertFalse(
                any(
                    row["student_id"] == student_id
                    for row in self.api.list_students(
                        search=self.admission_number
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()
