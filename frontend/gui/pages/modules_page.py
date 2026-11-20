from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QDialog, QLabel, QComboBox, QDialogButtonBox, QMessageBox,
)

from gui.components.data_table import DataTable
from programme import Module
from api_client import ApiError


class ModuleDialog(QDialog):
    def __init__(self, state, module=None, programme=None, parent=None):
        super().__init__(parent)
        self.state = state
        self.setWindowTitle("Add Module" if module is None else "Edit Module")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Programme"))
        self.programme = QComboBox()
        for item in state.programmes:
            self.programme.addItem(f"{item.code} - {item.name}", item.code)
        if programme:
            index = self.programme.findData(programme.code)
            if index >= 0:
                self.programme.setCurrentIndex(index)
        layout.addWidget(self.programme)
        layout.addWidget(QLabel("Module Code"))
        self.code = QLineEdit(module.code if module else "")
        layout.addWidget(self.code)
        layout.addWidget(QLabel("Module Name"))
        self.name = QLineEdit(module.name if module else "")
        layout.addWidget(self.name)
        layout.addWidget(QLabel("Level"))
        self.level = QComboBox()
        self.level.addItems(("1", "2", "3"))
        if module:
            self.level.setCurrentText(str(module.level))
        layout.addWidget(self.level)
        layout.addWidget(QLabel("Semester"))
        self.semester = QComboBox()
        self.semester.addItems(("1", "2"))
        if module:
            self.semester.setCurrentText(str(module.semester))
        layout.addWidget(self.semester)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ModulesPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search modules")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)
        self.add_button = QPushButton("Add Module")
        self.add_button.clicked.connect(self.add_module)
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("secondary")
        self.edit_button.clicked.connect(self.edit_module)
        for button in (self.add_button, self.edit_button):
            button.setVisible(state.is_admin)
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        self.table = DataTable(("Programme", "Code", "Name", "Level", "Semester"))
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        query = self.search.text().lower() if hasattr(self, "search") else ""
        rows = []
        self._modules = []
        try:
            self.state.refresh_reference_data()
        except ApiError as error:
            QMessageBox.critical(self, "Modules", str(error))
            return
        for programme in self.state.programmes:
            for module in programme.get_modules():
                searchable = f"{programme.code} {module.code} {module.name}".lower()
                if query in searchable:
                    rows.append((
                        programme.code, module.code, module.name,
                        module.level, module.semester,
                    ))
                    self._modules.append((programme, module))
        self.table.populate(rows)

    def selected_module(self):
        row = self.table.selected_row()
        if row < 0:
            QMessageBox.warning(self, "Module", "Select a module.")
            return None
        return self._modules[row]

    def add_module(self):
        dialog = ModuleDialog(self.state, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if not self.state.programmes:
            QMessageBox.warning(self, "Module", "Create a programme first.")
            return
        try:
            programme = next(p for p in self.state.programmes
                             if p.code == dialog.programme.currentData())
            module = Module(dialog.code.text(), dialog.name.text(),
                            dialog.level.currentText(), dialog.semester.currentText())
            programme.add_module(module)
            QMessageBox.information(self, "Module", "Module added.")
            self.state.save_programmes()
            self.refresh()
        except (ValueError, StopIteration, ApiError) as error:
            QMessageBox.critical(self, "Module", str(error))

    def edit_module(self):
        selected = self.selected_module()
        if selected is None:
            return
        programme, module = selected
        dialog = ModuleDialog(self.state, module, programme, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            module.code = dialog.code.text().strip().upper()
            module.name = dialog.name.text().strip()
            module.level = dialog.level.currentText()
            module.semester = dialog.semester.currentText()
            new_programme = next(p for p in self.state.programmes
                                 if p.code == dialog.programme.currentData())
            if new_programme is not programme:
                programme._modules.remove(module)
                new_programme.add_module(module)
            QMessageBox.information(self, "Module", "Module updated.")
            self.state.save_programmes()
            self.refresh()
        except (ValueError, StopIteration, ApiError) as error:
            QMessageBox.critical(self, "Module", str(error))
