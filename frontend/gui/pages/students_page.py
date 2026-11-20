from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QDialog, QLabel, QComboBox, QSpinBox, QDialogButtonBox, QMessageBox,
)

from gui.components.data_table import DataTable
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
        self.first_name = QLineEdit(record["name"].split(" ")[0] if record else "")
        layout.addWidget(self.first_name)
        layout.addWidget(QLabel("Last Name"))
        last_name = " ".join(record["name"].split(" ")[1:]) if record else ""
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
            "age": self.age.value(),
            "programme": self.programme.currentData(),
        }


class StudentsPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by name or student ID")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)
        self.add_button = QPushButton("Add Student")
        self.add_button.clicked.connect(self.add_student)
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("secondary")
        self.edit_button.clicked.connect(self.edit_student)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("danger")
        self.delete_button.clicked.connect(self.delete_student)
        for button in (self.add_button, self.edit_button, self.delete_button):
            button.setVisible(state.is_admin)
            toolbar.addWidget(button)
        layout.addLayout(toolbar)

        self.table = DataTable(("Student ID", "Name", "Age", "Programme"))
        layout.addWidget(self.table)

    def refresh(self):
        query = self.search.text().strip().lower() if hasattr(self, "search") else ""
        try:
            records = self.state.load_records()
        except ApiError as error:
            QMessageBox.critical(self, "Students", str(error))
            return
        unique = {}
        for record in records:
            unique[record.get("student_id")] = record
        rows = []
        for record in unique.values():
            if query in str(record.get("student_id", "")).lower() or query in str(record.get("name", "")).lower():
                rows.append((
                    record.get("student_id", ""),
                    record.get("name", ""),
                    record.get("age", ""),
                    record.get("programme", ""),
                ))
        self.table.populate(rows)
        self._records = list(unique.values())

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
        if not values["programme"]:
            QMessageBox.warning(self, "Student", "Create a programme first.")
            return
        try:
            programme = next(p for p in self.state.programmes if p.code == values["programme"])
            Student.create_student(values["student_id"], values["name"], values["age"], programme)
        except (ValueError, StopIteration) as error:
            QMessageBox.critical(self, "Student", str(error))
            return
        try:
            self.state.save_record(values)
            QMessageBox.information(self, "Student", "Student registered successfully.")
            self.refresh()
        except ApiError as error:
            QMessageBox.critical(self, "Student", str(error))

    def edit_student(self):
        record = self.selected_record()
        if record is None:
            return
        dialog = StudentDialog(self.state, record, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        if not values["programme"]:
            QMessageBox.warning(self, "Student", "Create a programme first.")
            return
        try:
            programme = next(p for p in self.state.programmes if p.code == values["programme"])
            Student.create_student(values["student_id"], values["name"], values["age"], programme)
        except (ValueError, StopIteration) as error:
            QMessageBox.critical(self, "Student", str(error))
            return
        try:
            self.state.update_student(record["id"], values)
            QMessageBox.information(self, "Student", "Student updated successfully.")
            self.refresh()
        except ApiError as error:
            QMessageBox.critical(self, "Student", str(error))

    def delete_student(self):
        record = self.selected_record()
        if record is None:
            return
        if QMessageBox.question(
            self, "Delete Student",
            f"Delete {record['name']} and all of their results?",
        ) == QMessageBox.StandardButton.Yes:
            try:
                self.state.delete_record(record["id"])
                QMessageBox.information(self, "Student", "Student record deleted.")
                self.refresh()
            except ApiError as error:
                QMessageBox.critical(self, "Student", str(error))
