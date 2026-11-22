from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from decimal import Decimal, ROUND_HALF_UP

from api_client import ApiError
from gui.components.data_table import DataTable


def calculate_grade_preview(score, maximum_score):
    """Calculate grade preview based on score and maximum score.
    Mirrors the backend's calculate_grade function."""
    if maximum_score <= 0:
        return "F"
    percentage = Decimal(str(score)) * 100 / Decimal(str(maximum_score))
    if percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    return "F"


class ResultDialog(QDialog):
    def __init__(self, state, result=None, parent=None):
        super().__init__(parent)
        self.state = state
        self.result = result
        self.setWindowTitle("Record Result" if result is None else "Edit Result")
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Student section
        student_group = QLabel("Student Selection")
        student_group.setStyleSheet("font-weight: 600; font-size: 13px; color: #172033;")
        layout.addWidget(student_group)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        # Student search/combo
        self.student_search = QLineEdit()
        self.student_search.setPlaceholderText("Type to search by name or admission number...")
        self.student_search.textChanged.connect(self._filter_students)
        form.addRow("Search:", self.student_search)

        self.student = QComboBox()
        self.student.setMinimumWidth(300)
        self.student.currentIndexChanged.connect(self._on_student_changed)
        form.addRow("Student:", self.student)

        # Student info display (read-only)
        self.student_admission = QLabel("-")
        self.student_admission.setStyleSheet("color: #64748B; font-family: monospace;")
        form.addRow("Admission No.:", self.student_admission)

        self.student_name = QLabel("-")
        self.student_name.setStyleSheet("color: #64748B;")
        form.addRow("Full Name:", self.student_name)

        self.student_programme = QLabel("-")
        self.student_programme.setStyleSheet("color: #64748B;")
        form.addRow("Programme:", self.student_programme)

        layout.addLayout(form)

        # Examination section
        exam_group = QLabel("Examination Selection")
        exam_group.setStyleSheet("font-weight: 600; font-size: 13px; color: #172033; margin-top: 8px;")
        layout.addWidget(exam_group)

        exam_form = QFormLayout()
        exam_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        exam_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        exam_form.setHorizontalSpacing(12)
        exam_form.setVerticalSpacing(10)

        self.examination = QComboBox()
        self.examination.setMinimumWidth(300)
        self.examination.currentIndexChanged.connect(self._on_examination_changed)
        exam_form.addRow("Examination:", self.examination)

        self.exam_max_score = QLabel("-")
        self.exam_max_score.setStyleSheet("color: #64748B; font-weight: 600;")
        exam_form.addRow("Max Score:", self.exam_max_score)

        self.exam_module = QLabel("-")
        self.exam_module.setStyleSheet("color: #64748B;")
        exam_form.addRow("Module:", self.exam_module)

        self.exam_type = QLabel("-")
        self.exam_type.setStyleSheet("color: #64748B;")
        exam_form.addRow("Type:", self.exam_type)

        layout.addLayout(exam_form)

        # Score and Grade section
        score_group = QLabel("Score Entry")
        score_group.setStyleSheet("font-weight: 600; font-size: 13px; color: #172033; margin-top: 8px;")
        layout.addWidget(score_group)

        score_form = QFormLayout()
        score_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        score_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        score_form.setHorizontalSpacing(12)
        score_form.setVerticalSpacing(10)

        self.score = QDoubleSpinBox()
        self.score.setDecimals(2)
        self.score.setRange(0, 1000)
        self.score.setSingleStep(0.5)
        self.score.valueChanged.connect(self._update_grade_preview)
        if result:
            self.score.setValue(float(result["score"]))
        score_form.addRow("Score:", self.score)

        self.grade_preview = QLabel("-")
        self.grade_preview.setStyleSheet("font-size: 18px; font-weight: 700; color: #2563EB;")
        score_form.addRow("Grade Preview:", self.grade_preview)

        layout.addLayout(score_form)

        # Remarks
        layout.addWidget(QLabel("Remarks"))
        self.remarks = QTextEdit()
        self.remarks.setMaximumHeight(80)
        self.remarks.setPlaceholderText("Optional remarks...")
        if result:
            self.remarks.setPlainText(result.get("remarks", ""))
        layout.addWidget(self.remarks)

        # Load data
        self._all_students = state.load_records()
        self._populate_students(self._all_students)

        if result:
            self.student.setCurrentIndex(
                self.student.findData(result["student_record_id"])
            )
            # When editing, populate all examinations first so the existing one is available
            self._populate_examinations()
            self.examination.setCurrentIndex(
                self.examination.findData(result["examination_record_id"])
            )
            self.student.setEnabled(False)
            self.student_search.setEnabled(False)
            self.examination.setEnabled(False)
        else:
            # For new results, populate examinations after student selection
            self._populate_examinations()
        self._on_student_changed()
        self._on_examination_changed()
        self._update_grade_preview()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate_students(self, students):
        current_data = self.student.currentData()
        self.student.blockSignals(True)
        self.student.clear()
        for item in students:
            self.student.addItem(
                f"{item['student_id']} - {item['name']}", item["id"]
            )
        if current_data:
            idx = self.student.findData(current_data)
            if idx >= 0:
                self.student.setCurrentIndex(idx)
        self.student.blockSignals(False)

    def _filter_students(self):
        text = self.student_search.text().strip().lower()
        if not text:
            self._populate_students(self._all_students)
            return
        filtered = [
            s for s in self._all_students
            if text in s["student_id"].lower() or text in s["name"].lower()
        ]
        self._populate_students(filtered)

    def _get_student_programme_modules(self, student):
        """Get module IDs for the student's programme."""
        programme_id = student.get("programme_id")
        if not programme_id:
            return set()
        programme = next((p for p in self.state.programmes if p.id == programme_id), None)
        if not programme:
            return set()
        return {m.id for m in programme._modules}

    def _populate_examinations(self, programme_module_ids=None):
        """Populate examination combo box, optionally filtered by programme modules."""
        current_data = self.examination.currentData()
        self.examination.blockSignals(True)
        self.examination.clear()
        
        if programme_module_ids is None:
            # No filter - show all examinations (for editing existing results)
            examinations = self.state.examinations
        else:
            # Filter by programme modules
            examinations = [
                e for e in self.state.examinations
                if e.module_id in programme_module_ids
            ]
        
        for examination in examinations:
            self.examination.addItem(
                f"{examination.exam_id} - {examination.title}",
                examination.id,
            )
        
        if current_data:
            idx = self.examination.findData(current_data)
            if idx >= 0:
                self.examination.setCurrentIndex(idx)
        self.examination.blockSignals(False)

    def _on_student_changed(self):
        student_id = self.student.currentData()
        student = next((s for s in self._all_students if s["id"] == student_id), None)
        if student:
            self.student_admission.setText(student["student_id"])
            self.student_name.setText(student["name"])
            self.student_programme.setText(student.get("programme", "-"))
            
            # Filter examinations by student's programme (only for new results)
            if self.result is None:
                programme_module_ids = self._get_student_programme_modules(student)
                self._populate_examinations(programme_module_ids)
        else:
            self.student_admission.setText("-")
            self.student_name.setText("-")
            self.student_programme.setText("-")
            if self.result is None:
                self._populate_examinations(set())  # No student selected, show no examinations

    def _on_examination_changed(self):
        examination_id = self.examination.currentData()
        examination = next(
            (item for item in self.state.examinations if item.id == examination_id),
            None,
        )
        if examination:
            self.exam_max_score.setText(str(examination.total_marks))
            self.exam_module.setText(examination.module_code)
            self.exam_type.setText(examination.exam_type)
            self.score.setMaximum(examination.total_marks)
        else:
            self.exam_max_score.setText("-")
            self.exam_module.setText("-")
            self.exam_type.setText("-")
            self.score.setMaximum(1000)

    def _update_grade_preview(self):
        examination_id = self.examination.currentData()
        examination = next(
            (item for item in self.state.examinations if item.id == examination_id),
            None,
        )
        if examination:
            max_score = examination.total_marks
            score = self.score.value()
            grade = calculate_grade_preview(score, max_score)
            percentage = (Decimal(str(score)) * 100 / Decimal(str(max_score))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ) if max_score > 0 else 0
            self.grade_preview.setText(f"{grade} ({percentage}%)")
        else:
            self.grade_preview.setText("-")

    def _validate_and_accept(self):
        if self.student.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select a student.")
            return
        if self.examination.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select an examination.")
            return
        score = self.score.value()
        if score < 0:
            QMessageBox.warning(self, "Validation Error", "Score cannot be negative.")
            return
        examination_id = self.examination.currentData()
        examination = next(
            (item for item in self.state.examinations if item.id == examination_id),
            None,
        )
        if examination and score > examination.total_marks:
            QMessageBox.warning(
                self,
                "Validation Error",
                f"Score cannot exceed the examination's maximum score of {examination.total_marks}.",
            )
            return
        self.accept()


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
