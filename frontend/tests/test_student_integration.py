import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtTest import QTest

from gui.app_state import AppState
from gui.pages import students_page
from gui.pages.students_page import StudentsPage
from programme import Programme


class StudentIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

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
            "programme": "SCI",
        }

        state.save_record(record)
        state.update_student(27, record)

        expected = {
            "admission_number": "ADM-027",
            "first_name": "Ada",
            "last_name": "Example",
            "age": 21,
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
                "programme": "SCI",
            }
        ]
        page = StudentsPage(state)
        page.refresh()
        self.wait_for(lambda: page._worker is None)

        self.assertEqual(page.status.text(), "1 student(s).")
        self.assertEqual(page.table.item(0, 0).text(), "ADM-027")
        page.close()

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
