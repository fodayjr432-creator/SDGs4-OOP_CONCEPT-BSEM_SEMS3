from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton,
)
from PyQt6.QtCore import pyqtSignal

from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from api_client import ApiError
from PyQt6.QtWidgets import QMessageBox


class DashboardPage(QWidget):
    action_requested = pyqtSignal(str)

    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)
        self.card_labels = {}
        titles = ("Total Students", "Total Programmes", "Total Modules",
                  "Total Examinations", "Results Recorded")
        for title in titles:
            card = StatCard(title, "0")
            cards_layout.addWidget(card)
            self.card_labels[title] = card
        layout.addLayout(cards_layout)

        quick = QHBoxLayout()
        quick.addWidget(QLabel("Quick Actions"))
        quick.addStretch()
        for title in ("Add Student", "Record Result", "View Reports"):
            button = QPushButton(title)
            button.setObjectName("secondary")
            target = {
                "Add Student": "Students",
                "Record Result": "Results",
                "View Reports": "Reports",
            }[title]
            button.clicked.connect(
                lambda _, page=target: self.action_requested.emit(page)
            )
            quick.addWidget(button)
        layout.addLayout(quick)

        label = QLabel("Recent Examination Results")
        label.setStyleSheet("font-size: 17px; font-weight: 700;")
        layout.addWidget(label)
        self.table = DataTable(("Student", "Programme", "Average", "Overall Grade"))
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        try:
            data = self.state.load_dashboard()
            counts = data["counts"]
            values = {
                "Total Students": counts["students"],
                "Total Programmes": counts["programmes"],
                "Total Modules": counts["modules"],
                "Total Examinations": counts["examinations"],
                "Results Recorded": counts["results"],
            }
            for title, value in values.items():
                self.card_labels[title].set_value(value)

            rows = [
                (
                    result["name"],
                    result["programme"],
                    result["average_score"],
                    result["overall_grade"],
                )
                for result in data["recent_results"]
            ]
            self.table.populate(rows)
        except ApiError as error:
            QMessageBox.critical(self, "Dashboard", str(error))
