import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtTest import QTest

from gui.app_state import AppState
from gui.pages import dashboard_page
from gui.pages import students_page
from gui.pages.dashboard_page import DashboardPage
from gui.pages.results_page import ResultsPage
from gui.pages.students_page import StudentDialog, StudentsPage
from programme import Programme
from storage import InstitutionNameStore


class StudentIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_app_state_updates_institution_through_backend_api(self):
        state = AppState.__new__(AppState)
        state.api = Mock()
        state.api.update_institution_name.return_value = {
            "institution": "Sierra Grammar School"
        }
        state.account = {"institution": "Scaling Grammar School"}
        state.institution_name = "Scaling Grammar School"
        state.institution_store = Mock()

        updated = state.update_institution_name("Sierra Grammar School")

        state.api.update_institution_name.assert_called_once_with(
            "Sierra Grammar School"
        )
        state.institution_store.save.assert_called_once_with(
            "Sierra Grammar School"
        )
        self.assertEqual(updated, "Sierra Grammar School")
        self.assertEqual(state.institution_name, "Sierra Grammar School")
        self.assertEqual(
            state.account["institution"],
            "Sierra Grammar School",
        )

    def test_app_state_loads_institution_from_backend_not_json(self):
        state = AppState.__new__(AppState)
        state.api = Mock()
        state.api.get.return_value = {
            "institution": "Limkokwing University"
        }
        state.account = {"institution": "Scaling Grammar School"}
        state.institution_name = "Scaling Grammar School"
        state.institution_store = Mock()

        loaded = state.load_institution_name()

        state.api.get.assert_called_once_with("/api/auth/me/")
        state.institution_store.save.assert_called_once_with(
            "Limkokwing University"
        )
        self.assertEqual(loaded, "Limkokwing University")
        self.assertEqual(state.institution_name, "Limkokwing University")
        self.assertEqual(
            state.account["institution"],
            "Limkokwing University",
        )

    def test_institution_name_store_persists_separate_from_student_data(self):
        with tempfile.TemporaryDirectory() as directory:
            settings_path = os.path.join(directory, "institution_settings.json")
            records_path = os.path.join(directory, "records.json")
            store = InstitutionNameStore(settings_path)

            store.save("Sierra Grammar School")
            reloaded = InstitutionNameStore(settings_path)

            self.assertEqual(
                reloaded.load("Scaling Grammar School"),
                "Sierra Grammar School",
            )
            self.assertFalse(os.path.exists(records_path))

    def test_dashboard_institution_edit_updates_welcome_immediately(self):
        state = Mock()
        state.account = {
            "username": "institution-admin",
            "role": "institution_admin",
            "institution": "Scaling Grammar School",
        }
        state.username = "institution-admin"
        state.institution_name = "Scaling Grammar School"
        state.is_admin = True
        state.load_dashboard.return_value = {
            "counts": {
                "students": 0,
                "programmes": 0,
                "modules": 0,
                "examinations": 0,
                "results": 0,
            },
            "recent_results": [],
        }
        state.update_institution_name.side_effect = (
            lambda name: setattr(state, "institution_name", name) or name
        )
        page = DashboardPage(state)

        self.assertEqual(
            page.welcome_title.text(),
            "Welcome to Scaling Grammar School",
        )
        with patch.object(
            dashboard_page.QDialog,
            "exec",
            return_value=QDialog.DialogCode.Accepted,
        ), patch.object(
            dashboard_page.QLineEdit,
            "text",
            return_value="Sierra Grammar School",
        ):
            page.edit_institution_name()
        self.assertEqual(
            page.welcome_title.text(),
            "Welcome to Sierra Grammar School",
        )

        with patch.object(
            dashboard_page.QDialog,
            "exec",
            return_value=QDialog.DialogCode.Rejected,
        ):
            page.edit_institution_name()
        self.assertEqual(
            page.welcome_title.text(),
            "Welcome to Sierra Grammar School",
        )

        with patch.object(
            dashboard_page.QDialog,
            "exec",
            return_value=QDialog.DialogCode.Accepted,
        ), patch.object(
            dashboard_page.QLineEdit,
            "text",
            return_value="",
        ), patch.object(dashboard_page.QMessageBox, "warning") as warning:
            page.edit_institution_name()
        warning.assert_called_once()
        self.assertEqual(
            page.welcome_title.text(),
            "Welcome to Sierra Grammar School",
        )
        page.close()

    def test_institution_admin_role_enables_administrator_capabilities(self):
        state = AppState.__new__(AppState)
        state.account = {"username": "institution-admin", "role": "institution_admin"}

        self.assertTrue(state.is_admin)

    def test_staff_role_does_not_enable_administrator_capabilities(self):
        state = AppState.__new__(AppState)
        state.account = {"username": "teacher", "role": "staff"}

        self.assertFalse(state.is_admin)

    def test_institution_admin_role_shows_result_management_controls(self):
        state = AppState.__new__(AppState)
        state.account = {"username": "institution-admin", "role": "institution_admin"}
        state.load_results = lambda: []
        page = ResultsPage(state)

        self.assertFalse(page.add_button.isHidden())
        self.assertFalse(page.edit_button.isHidden())
        self.assertFalse(page.delete_button.isHidden())

    def test_staff_role_allows_result_create_and_edit_but_hides_delete(self):
        state = AppState.__new__(AppState)
        state.account = {"username": "teacher", "role": "staff"}
        state.load_results = lambda: []
        page = ResultsPage(state)

        self.assertFalse(page.add_button.isHidden())
        self.assertFalse(page.edit_button.isHidden())
        self.assertTrue(page.delete_button.isHidden())

    def test_load_reports_extracts_student_rows_from_summary_response(self):
        state = AppState.__new__(AppState)
        state.api = Mock()
        reports = [{"student_id": "REPORT-001", "name": "Report Student"}]
        state.api.get.return_value = {"total_students": 1, "student_reports": reports}

        self.assertEqual(state.load_reports(), reports)
        state.api.get.assert_called_once_with("/api/reports/")

    def test_load_results_maps_database_ids_to_desktop_display_fields(self):
        state = AppState.__new__(AppState)
        state.api = Mock()
        state.api.get.return_value = [
            {
                "result_id": 25,
                "student_id": 9,
                "examination_id": 11,
                "score": "75.00",
                "grade": "A",
                "remarks": "",
            }
        ]
        state.api.list_students.return_value = [
            {
                "student_id": 9,
                "admission_number": "ADM-009",
                "first_name": "Ada",
                "last_name": "Example",
                "age": 20,
                "programme_id": 4,
                "programme_code": "SCI",
                "gender": None,
                "is_active": True,
            }
        ]
        state.programmes = [Programme("SCI", "Science", 4)]
        state.examinations = [SimpleNamespace(id=11, title="Final Exam")]

        results = state.load_results()

        self.assertEqual(
            results,
            [
                {
                    "id": 25,
                    "student_record_id": 9,
                    "examination_record_id": 11,
                    "student_id": "ADM-009",
                    "name": "Ada Example",
                    "programme": "SCI",
                    "subject": "Final Exam",
                    "score": "75.00",
                    "grade": "A",
                    "remarks": "",
                }
            ],
        )

    def test_api_records_map_to_existing_gui_student_shape(self):
        state = AppState.__new__(AppState)
        state.api = Mock()
        state.programmes = [Programme("SCI", "Science", 4)]
        state.api.list_students.return_value = [
            {
                "student_id": 27,
                "admission_number": "ADM-027",
                "first_name": "Ada",
                "last_name": "Example",
                "age": 21,
                "programme_id": 4,
                "programme_code": "OLD",
                "gender": None,
                "is_active": True,
            }
        ]

        records = state.load_students("Ada")

        state.api.list_students.assert_called_once_with(
            search="Ada",
            programme=None,
        )
        self.assertEqual(records[0]["id"], 27)
        self.assertEqual(records[0]["student_id"], "ADM-027")
        self.assertEqual(records[0]["name"], "Ada Example")
        self.assertEqual(records[0]["programme"], "SCI")

    def test_api_records_support_programme_filter_and_detail_retrieval(self):
        state = AppState.__new__(AppState)
        state.api = Mock()
        state.programmes = [Programme("SCI", "Science", 4)]
        row = {
            "student_id": 27,
            "admission_number": "ADM-027",
            "first_name": "Ada",
            "last_name": "Example",
            "age": 21,
            "programme_id": 4,
            "gender": None,
            "is_active": True,
        }
        state.api.list_students.return_value = [row]
        state.api.get_student.return_value = row

        filtered = state.load_students(programme=4)
        detail = state.load_student(27)

        state.api.list_students.assert_called_once_with(search="", programme=4)
        state.api.get_student.assert_called_once_with(27)
        self.assertEqual(filtered[0]["programme"], "SCI")
        self.assertEqual(detail["id"], 27)
        self.assertEqual(detail["first_name"], "Ada")

    def test_create_and_update_send_database_field_names(self):
        state = AppState.__new__(AppState)
        state.api = Mock()
        state.programmes = [Programme("SCI", "Science", 4)]
        record = {
            "student_id": "ADM-027",
            "first_name": "Ada",
            "last_name": "Example",
            "name": "Ada Example",
            "age": 21,
            "gender": "Female",
            "programme": "SCI",
        }

        state.save_record(record)
        state.update_student(27, record)

        expected = {
            "admission_number": "ADM-027",
            "first_name": "Ada",
            "last_name": "Example",
            "age": 21,
            "gender": "Female",
            "programme_id": 4,
        }
        state.api.create_student.assert_called_once_with(expected)
        state.api.update_student.assert_called_once_with(27, expected)

    def test_student_page_loads_records_without_blocking_ui(self):
        state = Mock()
        state.programmes = []
        state.load_students.return_value = [
            {
                "student_id": "ADM-027",
                "name": "Ada Example",
                "age": 21,
                "gender": None,
                "programme": "SCI",
            }
        ]
        page = StudentsPage(state)
        page.refresh()
        self.wait_for(lambda: page._worker is None)

        self.assertEqual(page.status.text(), "1 student(s).")
        self.assertEqual(page.table.item(0, 0).text(), "ADM-027")
        self.assertEqual(page.table.item(0, 3).text(), "Not provided")
        page.close()

    def test_student_dialog_requires_gender_and_values_include_selection(self):
        state = Mock()
        state.programmes = [Programme("SCI", "Science", 4)]
        dialog = StudentDialog(state)

        self.assertEqual(dialog.gender.currentText(), "Select Gender")
        dialog.first_name.setText("Ada")
        dialog.last_name.setText("Example")
        dialog.student_id.setText("ADM-027")
        dialog.programme.setCurrentIndex(0)

        with patch.object(students_page.QMessageBox, "warning") as warning:
            dialog._validate_and_accept()
        warning.assert_called_once_with(dialog, "Student", "Select a gender.")
        self.assertFalse(dialog.result() == QDialog.DialogCode.Accepted)

        dialog.gender.setCurrentIndex(dialog.gender.findText("Female"))
        self.assertEqual(dialog.values()["gender"], "Female")
        dialog.close()

    def test_student_dialog_edits_existing_gender(self):
        state = Mock()
        state.programmes = [Programme("SCI", "Science", 4)]
        record = {
            "student_id": "ADM-027",
            "first_name": "Ada",
            "last_name": "Example",
            "name": "Ada Example",
            "age": 21,
            "gender": "Other",
            "programme": "SCI",
        }

        dialog = StudentDialog(state, record)

        self.assertEqual(dialog.gender.currentText(), "Other")
        dialog.gender.setCurrentIndex(dialog.gender.findText("Male"))
        self.assertEqual(dialog.values()["gender"], "Male")
        dialog.close()

    def test_programme_filter_and_refresh_button_use_api_state(self):
        state = Mock()
        state.programmes = [Programme("SCI", "Science", 4)]
        state.load_students.return_value = []
        page = StudentsPage(state)
        page.programme_filter.setCurrentIndex(1)
        self.wait_for(lambda: page._worker is None and state.load_students.called)
        state.load_students.assert_called_with("", 4)

        page.refresh_button.click()
        self.wait_for(lambda: page._worker is None and state.load_students.call_count >= 2)
        self.assertEqual(page.status.text(), "No students found.")
        page.close()

    def test_gui_student_crud_and_search_workflow(self):
        programme = Programme("SCI", "Science", 4)
        records = []
        state = Mock()
        state.programmes = [programme]

        def find_students(search="", programme=None):
            return [
                dict(record)
                for record in records
                if (programme is None or record["programme_id"] == programme)
                and search.lower() in (
                    record["student_id"] + record["name"]
                ).lower()
            ]

        def create_student(values):
            record = {
                "id": 31,
                "student_id": values["student_id"],
                "first_name": values["first_name"],
                "last_name": values["last_name"],
                "name": values["name"],
                "age": values["age"],
                "programme": values["programme"],
                "programme_id": 4,
            }
            records.append(record)
            return record

        state.load_students.side_effect = find_students
        state.load_student.side_effect = lambda student_id: dict(
            next(record for record in records if record["id"] == student_id)
        )
        state.save_record.side_effect = create_student

        def update_student(student_id, values):
            record = next(record for record in records if record["id"] == student_id)
            record.update(values)
            return record

        def delete_student(student_id):
            records[:] = [record for record in records if record["id"] != student_id]
            return True

        state.update_student.side_effect = update_student
        state.delete_record.side_effect = delete_student
        page = StudentsPage(state)
        page.refresh()
        self.wait_for(lambda: page._worker is None)
        self.assertEqual(page.status.text(), "No students found.")

        new_values = {
            "student_id": "TEST-031",
            "first_name": "Test",
            "last_name": "Student",
            "name": "Test Student",
            "age": 20,
            "gender": "Male",
            "programme": "SCI",
        }
        add_dialog = Mock()
        add_dialog.exec.return_value = QDialog.DialogCode.Accepted
        add_dialog.values.return_value = new_values
        with patch.object(students_page, "StudentDialog", return_value=add_dialog):
            page.add_student()
        self.wait_for(lambda: page.table.rowCount() == 1 and page._worker is None)
        self.assertEqual(page.table.item(0, 0).text(), "TEST-031")
        state.save_record.assert_called_once_with(new_values)

        page.search.setText("TEST-031")
        self.wait_for(lambda: page._worker is None and state.load_students.call_count >= 2)
        self.assertEqual(page.table.rowCount(), 1)

        page.table.setCurrentCell(0, 0)
        updated_values = {
            **new_values,
            "first_name": "Updated",
            "name": "Updated Student",
        }
        edit_dialog = Mock()
        edit_dialog.exec.return_value = QDialog.DialogCode.Accepted
        edit_dialog.values.return_value = updated_values
        with patch.object(students_page, "StudentDialog", return_value=edit_dialog):
            page.edit_student()
            self.wait_for(
                lambda: state.update_student.called
                and page._worker is None
                and page.table.rowCount() == 1
                and page.table.item(0, 1).text() == "Updated Student"
            )
        state.load_student.assert_called_once_with(31)
        state.update_student.assert_called_once_with(31, updated_values)

        page.table.setCurrentCell(0, 0)
        with patch.object(
            students_page.QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            page.delete_student()
        self.wait_for(lambda: not records and page._worker is None)
        self.assertEqual(page.table.rowCount(), 0)
        state.delete_record.assert_called_once_with(31)
        page.close()

    def wait_for(self, condition, timeout_ms=3000):
        elapsed = 0
        while not condition() and elapsed < timeout_ms:
            QTest.qWait(20)
            elapsed += 20
        self.assertTrue(condition(), "Timed out waiting for GUI worker.")


if __name__ == "__main__":
    unittest.main()
