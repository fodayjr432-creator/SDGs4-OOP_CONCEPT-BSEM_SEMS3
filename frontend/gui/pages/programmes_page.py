from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QDialog, QLabel, QTextEdit, QDialogButtonBox, QMessageBox,
)

from gui.components.data_table import DataTable
from programme import Programme
from api_client import ApiError


class ProgrammeDialog(QDialog):
    def __init__(self, programme=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Programme" if programme is None else "Edit Programme")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Programme Code"))
        self.code = QLineEdit(programme.code if programme else "")
        layout.addWidget(self.code)
        layout.addWidget(QLabel("Programme Name"))
        self.name = QLineEdit(programme.name if programme else "")
        layout.addWidget(self.name)
        layout.addWidget(QLabel("Description"))
        self.description = QTextEdit()
        if programme:
            self.description.setPlainText(getattr(programme, "description", ""))
        layout.addWidget(self.description)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ProgrammesPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search programmes")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)
        self.add_button = QPushButton("Add Programme")
        self.add_button.clicked.connect(self.add_programme)
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("secondary")
        self.edit_button.clicked.connect(self.edit_programme)
        for button in (self.add_button, self.edit_button):
            button.setVisible(state.is_admin)
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        self.table = DataTable(("Code", "Name", "Modules", "Status"))
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        query = self.search.text().lower() if hasattr(self, "search") else ""
        rows = []
        try:
            self.state.refresh_reference_data()
        except ApiError as error:
            QMessageBox.critical(self, "Programmes", str(error))
            return
        for programme in self.state.programmes:
            if query in programme.code.lower() or query in programme.name.lower():
                rows.append((
                    programme.code,
                    programme.name,
                    len(programme.get_modules()),
                    "Active" if programme.active else "Inactive",
                ))
        self.table.populate(rows)

    def selected_programme(self):
        row = self.table.selected_row()
        if row < 0:
            QMessageBox.warning(self, "Programme", "Select a programme.")
            return None
        code = self.table.item(row, 0).text()
        return next(p for p in self.state.programmes if p.code == code)

    def add_programme(self):
        dialog = ProgrammeDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            if any(p.code == dialog.code.text().strip().upper()
                   for p in self.state.programmes):
                raise ValueError("Programme code already exists.")
            programme = Programme(dialog.code.text(), dialog.name.text())
            programme.description = dialog.description.toPlainText()
            self.state.add_programme(programme)
            QMessageBox.information(self, "Programme", "Programme added.")
            self.refresh()
        except (ValueError, ApiError) as error:
            QMessageBox.critical(self, "Programme", str(error))

    def edit_programme(self):
        programme = self.selected_programme()
        if programme is None:
            return
        dialog = ProgrammeDialog(programme, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            new_code = dialog.code.text().strip().upper()
            if any(p is not programme and p.code == new_code
                   for p in self.state.programmes):
                raise ValueError("Programme code already exists.")
            programme.code = new_code
            programme.name = dialog.name.text().strip()
            programme.description = dialog.description.toPlainText()
            self.state.save_programmes()
            QMessageBox.information(self, "Programme", "Programme updated.")
            self.refresh()
        except (ValueError, ApiError) as error:
            QMessageBox.critical(self, "Programme", str(error))
