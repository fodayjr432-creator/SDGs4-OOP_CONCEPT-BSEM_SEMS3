from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from api_client import ApiError
from gui.components.data_table import DataTable


class ResultDialog(QDialog):
    def __init__(self, state, result=None, parent=None):
        super().__init__(parent)
        self.state = state
        self.result = result
        self.setWindowTitle("Record Result" if result is None else "Edit Result")
        self.setMinimumWidth(470)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Student"))
        self.student = QComboBox()
        for item in state.load_records():
            self.student.addItem(
                f"{item['student_id']} - {item['name']}", item["id"]
            )
        layout.addWidget(self.student)

        layout.addWidget(QLabel("Examination"))
        self.examination = QComboBox()
        for examination in state.examinations:
            self.examination.addItem(
                f"{examination.exam_id} - {examination.title}",
                examination.id,
            )
        self.examination.currentIndexChanged.connect(self._set_score_limit)
        layout.addWidget(self.examination)

        layout.addWidget(QLabel("Score"))
        self.score = QDoubleSpinBox()
        self.score.setDecimals(2)
        self.score.setRange(0, 1000)
        if result:
            self.score.setValue(float(result["score"]))
        layout.addWidget(self.score)

        layout.addWidget(QLabel("Remarks"))
        self.remarks = QTextEdit()
        self.remarks.setMaximumHeight(100)
        if result:
            self.remarks.setPlainText(result.get("remarks", ""))
        layout.addWidget(self.remarks)

        if result:
            self.student.setCurrentIndex(
                self.student.findData(result["student_record_id"])
            )
            self.examination.setCurrentIndex(
                self.examination.findData(result["examination_record_id"])
            )
            self.student.setEnabled(False)
            self.examination.setEnabled(False)
        self._set_score_limit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _set_score_limit(self):
        examination_id = self.examination.currentData()
        examination = next(
            (item for item in self.state.examinations
             if item.id == examination_id),
            None,
        )
        if examination:
            self.score.setMaximum(examination.total_marks)


class ResultsPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search results")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)
        self.add_button = QPushButton("Record Result")
        self.add_button.clicked.connect(self.record_result)
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("secondary")
        self.edit_button.clicked.connect(self.edit_result)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("danger")
        self.delete_button.clicked.connect(self.delete_result)
        self.add_button.setVisible(
            state.account.get("role") in {"admin", "institution_admin", "lecturer", "staff"}
        )
        self.edit_button.setVisible(
            state.account.get("role") in {"admin", "institution_admin", "lecturer", "staff"}
        )
        self.delete_button.setVisible(state.is_admin)
        for button in (self.add_button, self.edit_button, self.delete_button):
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        self.table = DataTable(
            ("Student ID", "Student", "Programme", "Subject", "Score", "Grade")
        )
        layout.addWidget(self.table)
        self._results = []

    def refresh(self):
        try:
            self._results = self.state.load_results()
            self.table.populate(
                [
                    (
                        result["student_id"],
                        result["name"],
                        result["programme"],
                        result["subject"],
                        result["score"],
                        result["grade"],
                    )
                    for result in self._results
                ]
            )
        except ApiError as error:
            QMessageBox.critical(self, "Results", str(error))

    def _selected_result(self):
        row = self.table.selected_row()
        if row < 0:
            QMessageBox.warning(self, "Result", "Select a result.")
            return None
        return self._results[row]

    def record_result(self):
        try:
            if not self.state.load_records():
                QMessageBox.warning(self, "Result", "Register a student first.")
                return
            self.state.refresh_reference_data()
            if not self.state.examinations:
                QMessageBox.warning(self, "Result", "Create an examination first.")
                return
            dialog = ResultDialog(self.state, parent=self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            self.state.create_result(
                {
                    "student_id": dialog.student.currentData(),
                    "examination_id": dialog.examination.currentData(),
                    "score": dialog.score.value(),
                    "remarks": dialog.remarks.toPlainText(),
                }
            )
            QMessageBox.information(self, "Result", "Result recorded successfully.")
            self.refresh()
        except ApiError as error:
            QMessageBox.critical(self, "Result", str(error))

    def edit_result(self):
        result = self._selected_result()
        if result is None:
            return
        try:
            self.state.refresh_reference_data()
            dialog = ResultDialog(self.state, result, parent=self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            self.state.update_result(
                result["id"],
                {
                    "score": dialog.score.value(),
                    "remarks": dialog.remarks.toPlainText(),
                },
            )
            QMessageBox.information(self, "Result", "Result updated.")
            self.refresh()
        except ApiError as error:
            QMessageBox.critical(self, "Result", str(error))

    def delete_result(self):
        result = self._selected_result()
        if result is None:
            return
        if QMessageBox.question(
            self,
            "Delete Result",
            "Delete this examination result?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.state.delete_result(result["id"])
            QMessageBox.information(self, "Result", "Result deleted.")
            self.refresh()
        except ApiError as error:
            QMessageBox.critical(self, "Result", str(error))
