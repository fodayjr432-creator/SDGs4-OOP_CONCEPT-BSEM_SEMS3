from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QDialog, QLabel, QComboBox, QSpinBox, QDateEdit, QDialogButtonBox,
    QMessageBox, QTextEdit,
)
from PyQt6.QtCore import QDate

from gui.components.data_table import DataTable
from examination import Examination, Question
from api_client import ApiError


class QuestionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Examination Question")
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Question Type"))
        self.question_type = QComboBox()
        self.question_type.addItems(("mcq", "true_false", "short_answer"))
        layout.addWidget(self.question_type)
        layout.addWidget(QLabel("Question Text"))
        self.text = QTextEdit()
        self.text.setMaximumHeight(100)
        layout.addWidget(self.text)
        layout.addWidget(QLabel("Correct Answer"))
        self.answer = QLineEdit()
        layout.addWidget(self.answer)
        layout.addWidget(QLabel("Marks"))
        self.marks = QSpinBox()
        self.marks.setRange(1, 100)
        self.marks.setValue(1)
        layout.addWidget(self.marks)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ExaminationDialog(QDialog):
    def __init__(self, state, examination=None, parent=None):
        super().__init__(parent)
        self.state = state
        self.setWindowTitle("Create Examination" if examination is None else "Edit Examination")
        self.setMinimumWidth(470)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Examination ID"))
        self.exam_id = QLineEdit(examination.exam_id if examination else "")
        layout.addWidget(self.exam_id)
        layout.addWidget(QLabel("Title"))
        self.title = QLineEdit(examination.title if examination else "")
        layout.addWidget(self.title)
        layout.addWidget(QLabel("Module"))
        self.module = QComboBox()
        for module in state.modules:
            programme = next(
                item for item in state.programmes
                if item.id == module.programme_id
            )
            self.module.addItem(
                f"{programme.code} - {module.code} - {module.name}",
                module.id,
            )
        if examination:
            index = self.module.findData(examination.module_id)
            if index >= 0:
                self.module.setCurrentIndex(index)
        layout.addWidget(self.module)
        layout.addWidget(QLabel("Examination Type"))
        self.exam_type = QComboBox()
        self.exam_type.addItems(("Quiz", "Midterm", "Final", "Practical", "Assignment"))
        if examination:
            index = self.exam_type.findText(getattr(examination, "exam_type", "Final"))
            if index >= 0:
                self.exam_type.setCurrentIndex(index)
        layout.addWidget(self.exam_type)
        layout.addWidget(QLabel("Maximum Marks"))
        self.max_marks = QSpinBox()
        self.max_marks.setRange(1, 1000)
        self.max_marks.setValue(examination.total_marks if examination else 100)
        layout.addWidget(self.max_marks)
        layout.addWidget(QLabel("Duration (minutes)"))
        self.duration = QSpinBox()
        self.duration.setRange(1, 600)
        self.duration.setValue(examination.duration_minutes if examination else 60)
        layout.addWidget(self.duration)
        layout.addWidget(QLabel("Examination Date"))
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        if examination and getattr(examination, "exam_date", ""):
            self.date.setDate(QDate.fromString(examination.exam_date, "yyyy-MM-dd"))
        layout.addWidget(self.date)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ExaminationsPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search examinations")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)
        self.add_button = QPushButton("Create Examination")
        self.add_button.clicked.connect(self.create_examination)
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("secondary")
        self.edit_button.clicked.connect(self.edit_examination)
        self.questions_button = QPushButton("Add Question")
        self.questions_button.setObjectName("secondary")
        self.questions_button.clicked.connect(self.add_question)
        for button in (self.add_button, self.edit_button, self.questions_button):
            button.setVisible(state.is_admin)
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        self.table = DataTable(("ID", "Title", "Module", "Type", "Max Marks",
                                "Duration", "Status"))
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        query = self.search.text().lower() if hasattr(self, "search") else ""
        rows = []
        try:
            self.state.refresh_reference_data()
        except ApiError as error:
            QMessageBox.critical(self, "Examinations", str(error))
            return
        for examination in self.state.examinations:
            searchable = f"{examination.exam_id} {examination.title} {examination.module_code}".lower()
            if query in searchable:
                rows.append((
                    examination.exam_id,
                    examination.title,
                    examination.module_code,
                    getattr(examination, "exam_type", "Final"),
                    examination.total_marks,
                    examination.duration_minutes,
                    examination.status,
                ))
        self.table.populate(rows)

    def selected_examination(self):
        row = self.table.selected_row()
        if row < 0:
            QMessageBox.warning(self, "Examination", "Select an examination.")
            return None
        exam_id = self.table.item(row, 0).text()
        return next(e for e in self.state.examinations if e.exam_id == exam_id)

    def create_examination(self):
        dialog = ExaminationDialog(self.state, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if not self.state.modules:
            QMessageBox.warning(self, "Examination", "Create a module first.")
            return
        if not dialog.exam_id.text().strip() or not dialog.title.text().strip():
            QMessageBox.warning(self, "Examination", "Exam ID and title are required.")
            return
        try:
            module_id = dialog.module.currentData()
            module = next(item for item in self.state.modules if item.id == module_id)
            examination = Examination(
                dialog.exam_id.text().strip(),
                dialog.title.text().strip(),
                module.code,
                dialog.max_marks.value(),
                dialog.duration.value(),
                module_id=module_id,
            )
            examination.exam_type = dialog.exam_type.currentText()
            examination.exam_date = dialog.date.date().toString("yyyy-MM-dd")
            examination.status = "draft"
            self.state.add_examination(examination)
            QMessageBox.information(self, "Examination", "Examination created.")
            self.refresh()
        except (ApiError, StopIteration, ValueError) as error:
            QMessageBox.critical(self, "Examination", str(error))

    def edit_examination(self):
        examination = self.selected_examination()
        if examination is None:
            return
        dialog = ExaminationDialog(self.state, examination, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            module_id = dialog.module.currentData()
            module = next(item for item in self.state.modules if item.id == module_id)
            examination.title = dialog.title.text().strip()
            examination.module_code = module.code
            examination.module_id = module_id
            examination.exam_type = dialog.exam_type.currentText()
            examination.total_marks = dialog.max_marks.value()
            examination.duration_minutes = dialog.duration.value()
            examination.exam_date = dialog.date.date().toString("yyyy-MM-dd")
            self.state.save_examinations()
            QMessageBox.information(self, "Examination", "Examination updated.")
            self.refresh()
        except (ApiError, StopIteration, ValueError) as error:
            QMessageBox.critical(self, "Examination", str(error))

    def add_question(self):
        examination = self.selected_examination()
        if examination is None:
            return
        dialog = QuestionDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        text = dialog.text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Question", "Question text is required.")
            return
        question = Question(
            question_id=f"Q{len(examination.questions) + 1}",
            text=text,
            question_type=dialog.question_type.currentText(),
            correct_answer=dialog.answer.text().strip(),
            marks=dialog.marks.value(),
        )
        examination.add_question(question)
        try:
            self.state.save_examinations()
            QMessageBox.information(
                self, "Question",
                f"Question added. {len(examination.questions)} question(s) now exist.",
            )
        except (ApiError, ValueError) as error:
            QMessageBox.critical(self, "Question", str(error))
