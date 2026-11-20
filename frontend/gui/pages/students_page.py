from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QDialog, QLabel, QComboBox, QSpinBox, QDialogButtonBox, QMessageBox,
)
from PyQt6.QtCore import QTimer

from gui.components.data_table import DataTable
from gui.api_worker import ApiWorker
from student import Student
from api_client import ApiError


class StudentDialog(QDialog):
    def __init__(self, state, record=None, parent=None):
        super().__init__(parent)
        self.state = state
        self.record = record
        self.setWindowTitle("Add Student" if record is None else "Edit Student")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Student ID"))
        self.student_id = QLineEdit(record["student_id"] if record else "")
        layout.addWidget(self.student_id)
        layout.addWidget(QLabel("First Name"))
        self.first_name = QLineEdit(
            record.get("first_name", record["name"].split(" ")[0])
            if record
            else ""
        )
        layout.addWidget(self.first_name)
        layout.addWidget(QLabel("Last Name"))
        last_name = (
            record.get(
                "last_name",
                " ".join(record["name"].split(" ")[1:]),
            )
            if record
            else ""
        )
        self.last_name = QLineEdit(last_name)
        layout.addWidget(self.last_name)
        layout.addWidget(QLabel("Age"))
        self.age = QSpinBox()
        self.age.setRange(0, 120)
        self.age.setValue(record["age"] if record else 18)
        layout.addWidget(self.age)
        layout.addWidget(QLabel("Programme"))
        self.programme = QComboBox()
        for programme in state.programmes:
            if not programme.active:
                continue
            self.programme.addItem(f"{programme.code} - {programme.name}", programme.code)
        if record:
            index = self.programme.findData(record.get("programme"))
            if index >= 0:
                self.programme.setCurrentIndex(index)
        layout.addWidget(self.programme)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        name = f"{self.first_name.text().strip()} {self.last_name.text().strip()}".strip()
        return {
            "student_id": self.student_id.text().strip(),
            "name": name,
            "first_name": self.first_name.text().strip(),
            "last_name": self.last_name.text().strip(),
            "age": self.age.value(),
            "programme": self.programme.currentData(),
        }


class StudentsPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self._worker = None
        self._refresh_requested = False
        self._records = []
        self._pending_edit = None
        self._success_message = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by name or student ID")
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(250)
        self.search_timer.timeout.connect(self.refresh)
        self.search.textChanged.connect(lambda _text: self.search_timer.start())
        toolbar.addWidget(self.search)
        self.programme_filter = QComboBox()
        self.programme_filter.addItem("All programmes", None)
        for programme in state.programmes:
            self.programme_filter.addItem(
                f"{programme.code} - {programme.name}",
                programme.id,
            )
        self.programme_filter.currentIndexChanged.connect(
            lambda _index: self.search_timer.start()
        )
        toolbar.addWidget(self.programme_filter)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)
        toolbar.addWidget(self.refresh_button)
        self.add_button = QPushButton("Add Student")
        self.add_button.clicked.connect(self.add_student)
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("secondary")
        self.edit_button.clicked.connect(self.edit_student)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("danger")
        self.delete_button.clicked.connect(self.delete_student)
        for button in (self.add_button, self.edit_button, self.delete_button):
            toolbar.addWidget(button)
        layout.addLayout(toolbar)

        self.status = QLabel("")
        self.status.setMinimumHeight(20)
        layout.addWidget(self.status)
        self.table = DataTable(("Student ID", "Name", "Age", "Programme"))
        layout.addWidget(self.table)

    def refresh(self):
        if self._worker is not None:
            self._refresh_requested = True
            return
        query = self.search.text().strip()
        programme_id = self.programme_filter.currentData()
        self.status.setText("Loading students…")
        self._run_api_task(
            lambda: self.state.load_students(query, programme_id),
            self._show_students,
            self._show_error,
        )

    def _run_api_task(self, operation, succeeded, failed):
        if self._worker is not None:
            return
        self._set_busy(True)
        worker = ApiWorker(operation, self)
        worker.succeeded.connect(succeeded)
        worker.failed.connect(failed)
        worker.finished.connect(self._api_task_finished)
        self._worker = worker
        worker.start()

    def _set_busy(self, busy):
        self.search.setEnabled(not busy)
        self.programme_filter.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        for button in (self.add_button, self.edit_button, self.delete_button):
            button.setEnabled(not busy)

    def _api_task_finished(self):
        worker = self._worker
        self._worker = None
        self._set_busy(False)
        if worker is not None:
            worker.deleteLater()
        if self._pending_edit is not None:
            record, details = self._pending_edit
            self._pending_edit = None
            self._open_edit_dialog(record, details)
        if self._refresh_requested:
            self._refresh_requested = False
            self.refresh()

    def _show_students(self, records):
        self._records = records
        self.table.populate(
            [
                (
                    record["student_id"],
                    record["name"],
                    record["age"],
                    record["programme"],
                )
                for record in records
            ]
        )
        count_message = f"{len(records)} student(s)." if records else "No students found."
        self.status.setText(
            f"{self._success_message} {count_message}".strip()
            if self._success_message
            else count_message
        )
        self._success_message = ""

    def _show_error(self, message):
        self.status.setText("Could not load or save students.")
        QMessageBox.critical(self, "Students", str(message))
        if isinstance(message, ApiError) and message.status_code == 401:
            main_window = self.window()
            if hasattr(main_window, "logout"):
                main_window.logout()

    def _validate_values(self, values):
        if not values["programme"]:
            QMessageBox.warning(self, "Student", "Select a programme.")
            return False
        if not values["student_id"]:
            QMessageBox.warning(self, "Student", "Student ID is required.")
            return False
        if not Student.is_valid_name(values["first_name"]):
            QMessageBox.warning(
                self, "Student", "First name must contain letters and spaces only."
            )
            return False
        if not Student.is_valid_name(values["last_name"]):
            QMessageBox.warning(
                self, "Student", "Last name must contain letters and spaces only."
            )
            return False
        return True

    def selected_record(self):
        row = self.table.selected_row()
        if row < 0:
            QMessageBox.warning(self, "Student", "Select a student from the table.")
            return None
        student_id = self.table.item(row, 0).text()
        return next(
            (record for record in self._records
             if record.get("student_id") == student_id),
            None,
        )

    def add_student(self):
        dialog = StudentDialog(self.state, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        if not self._validate_values(values):
            return
        try:
            programme = next(p for p in self.state.programmes if p.code == values["programme"])
            Student.create_student(values["student_id"], values["name"], values["age"], programme)
        except (ValueError, StopIteration) as error:
            QMessageBox.critical(self, "Student", str(error))
            return
        try:
            self._run_api_task(
                lambda: self.state.save_record(values),
                lambda _created: self._student_saved("Student registered successfully."),
                self._show_error,
            )
        except ApiError as error:
            QMessageBox.critical(self, "Student", str(error))

    def edit_student(self):
        record = self.selected_record()
        if record is None:
            return
        self.status.setText("Loading student details…")
        self._run_api_task(
            lambda: self.state.load_student(record["id"]),
            lambda details: setattr(self, "_pending_edit", (record, details)),
            self._show_error,
        )

    def _open_edit_dialog(self, record, details):
        dialog = StudentDialog(self.state, details, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        if not self._validate_values(values):
            return
        try:
            programme = next(p for p in self.state.programmes if p.code == values["programme"])
            Student.create_student(values["student_id"], values["name"], values["age"], programme)
        except (ValueError, StopIteration) as error:
            QMessageBox.critical(self, "Student", str(error))
            return
        try:
            self._run_api_task(
                lambda: self.state.update_student(record["id"], values),
                lambda _updated: self._student_saved("Student updated successfully."),
                self._show_error,
            )
        except ApiError as error:
            QMessageBox.critical(self, "Student", str(error))

    def _student_saved(self, message):
        self._success_message = message
        self._refresh_requested = True

    def delete_student(self):
        record = self.selected_record()
        if record is None:
            return
        if QMessageBox.question(
            self, "Delete Student",
            f"Delete {record['name']} if they have no recorded results?",
        ) == QMessageBox.StandardButton.Yes:
            self._run_api_task(
                lambda: self.state.delete_record(record["id"]),
                lambda _deleted: self._student_saved("Student record deleted."),
                self._show_error,
            )
