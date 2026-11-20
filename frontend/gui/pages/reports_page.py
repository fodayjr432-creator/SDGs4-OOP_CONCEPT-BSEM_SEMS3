import csv

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QComboBox, QFileDialog, QMessageBox,
)

from gui.components.data_table import DataTable
from api_client import ApiError


class ReportsPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search student performance")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search)
        self.programme_filter = QComboBox()
        self.programme_filter.addItem("All programmes", "")
        for programme in state.programmes:
            self.programme_filter.addItem(programme.name, programme.code)
        self.programme_filter.currentTextChanged.connect(self.refresh)
        toolbar.addWidget(self.programme_filter)
        export = QPushButton("Export CSV")
        export.clicked.connect(self.export_csv)
        toolbar.addWidget(export)
        layout.addLayout(toolbar)

        self.table = DataTable((
            "Student ID", "Student", "Programme", "Total Score",
            "Average", "Overall Grade",
        ))
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        query = self.search.text().strip() if hasattr(self, "search") else ""
        programme_code = (
            self.programme_filter.currentData()
            if hasattr(self, "programme_filter") else ""
        )
        try:
            reports = self.state.load_reports(query, programme_code)
            self._rows = [
                (
                    record["student_id"],
                    record["name"],
                    record["programme"],
                    record["total_score"],
                    record["average_score"],
                    record["overall_grade"],
                )
                for record in reports
            ]
            self.table.populate(self._rows)
        except ApiError as error:
            QMessageBox.critical(self, "Reports", str(error))

    def export_csv(self):
        if not getattr(self, "_rows", None):
            QMessageBox.information(self, "Reports", "There are no report rows to export.")
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "student_performance.csv",
            "CSV Files (*.csv)",
        )
        if not filepath:
            return
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow((
                    "Student ID", "Student", "Programme", "Total Score",
                    "Average", "Overall Grade",
                ))
                writer.writerows(self._rows)
            QMessageBox.information(self, "Reports", "Report exported successfully.")
        except OSError as error:
            QMessageBox.critical(self, "Reports", f"Could not export report: {error}")
