from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QSizePolicy, QHeaderView, QTableWidgetItem,
    QDialog, QLineEdit, QDialogButtonBox, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from api_client import ApiError
from PyQt6.QtWidgets import QMessageBox


class DashboardPage(QWidget):
    action_requested = pyqtSignal(str)
    institution_name_changed = pyqtSignal(str)

    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        welcome = QFrame()
        welcome.setObjectName("card")
        welcome_layout = QHBoxLayout(welcome)
        welcome_layout.setContentsMargins(20, 14, 20, 14)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        institution_name = getattr(
            state,
            "institution_name",
            state.account.get("institution")
            if hasattr(state, "account")
            else "Scaling Grammar School",
        )
        self.welcome_title = QLabel(
            f"Welcome to {institution_name}"
        )
        welcome_title = self.welcome_title
        welcome_title.setStyleSheet("font-size: 20px; font-weight: 800;")
        welcome_title.setObjectName("dashboardWelcome")
        welcome_title.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        welcome_subtitle = QLabel(
            "Here's an overview of your academic activities."
        )
        welcome_subtitle.setObjectName("muted")
        text_layout.addWidget(welcome_title)
        text_layout.addWidget(welcome_subtitle)
        welcome_layout.addLayout(text_layout, 1)

        if state.is_admin:
            edit_button = QPushButton("Edit Institution Name")
            edit_button.setObjectName("secondary")
            edit_button.setMinimumHeight(36)
            edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_button.clicked.connect(self.edit_institution_name)
            welcome_layout.addWidget(edit_button)

        heading = QLabel("Dashboard")
        heading.setObjectName("pageTitle")
        heading.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        welcome_layout.addWidget(heading)
        layout.addWidget(welcome)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        self.card_labels = {}
        markers = {
            "Total Students": "ST",
            "Total Programmes": "PR",
            "Total Modules": "MO",
            "Total Examinations": "EX",
            "Results Recorded": "RS",
        }
        titles = (
            "Total Students",
            "Total Programmes",
            "Total Modules",
            "Total Examinations",
            "Results Recorded",
        )
        for title in titles:
            card = StatCard(title, "0", markers[title])
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            cards_layout.addWidget(card)
            self.card_labels[title] = card
        layout.addLayout(cards_layout)

        overview = QFrame()
        overview.setObjectName("card")
        overview_layout = QHBoxLayout(overview)
        overview_layout.setContentsMargins(16, 12, 16, 12)
        overview_layout.setSpacing(18)

        overview_title = QLabel("Academic Overview")
        overview_title.setStyleSheet("font-size: 16px; font-weight: 800;")
        overview_layout.addWidget(overview_title)

        self.examination_summary = QLabel("Examinations: 0")
        self.examination_summary.setObjectName("muted")
        overview_layout.addWidget(self.examination_summary)
        overview_layout.addWidget(self._divider())

        self.results_summary = QLabel("Results recorded: 0")
        self.results_summary.setObjectName("muted")
        overview_layout.addWidget(self.results_summary)
        overview_layout.addWidget(self._divider())
        self.gender_summary = QLabel(
            "Gender distribution: Not available from the dashboard data"
        )
        self.gender_summary.setObjectName("muted")
        overview_layout.addWidget(self.gender_summary)
        overview_layout.addStretch()
        layout.addWidget(overview)

        quick = QFrame()
        quick.setObjectName("card")
        quick_layout = QVBoxLayout(quick)
        quick_layout.setContentsMargins(16, 12, 16, 16)
        quick_layout.setSpacing(10)

        quick_heading = QLabel("Quick Actions")
        quick_heading.setStyleSheet("font-size: 16px; font-weight: 800;")
        quick_layout.addWidget(quick_heading)

        quick_buttons = QHBoxLayout()
        quick_buttons.setSpacing(10)
        for title in ("Add Student", "Record Result", "View Reports"):
            button = QPushButton(title)
            button.setObjectName("secondary")
            button.setMinimumHeight(42)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            target = {
                "Add Student": "Students",
                "Record Result": "Results",
                "View Reports": "Reports",
            }[title]
            button.clicked.connect(
                lambda _, page=target: self.action_requested.emit(page)
            )
            quick_buttons.addWidget(button)
        quick_layout.addLayout(quick_buttons)
        layout.addWidget(quick)

        recent = QFrame()
        recent.setObjectName("card")
        recent_layout = QVBoxLayout(recent)
        recent_layout.setContentsMargins(16, 12, 16, 16)
        recent_layout.setSpacing(8)

        label = QLabel("Recent Examination Results")
        label.setStyleSheet("font-size: 16px; font-weight: 800;")
        recent_layout.addWidget(label)
        self.table = DataTable(("Student", "Programme", "Average", "Overall Grade"))
        self.table.setMinimumHeight(180)
        self.table.setMaximumHeight(220)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        recent_layout.addWidget(self.table)
        layout.addWidget(recent)
        layout.addStretch()
        self.refresh()

    def edit_institution_name(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Institution Name")
        dialog.setMinimumWidth(420)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(QLabel("Institution name"))

        name_input = QLineEdit(self.state.institution_name)
        name_input.setAccessibleName("Institution name")
        name_input.selectAll()
        layout.addWidget(name_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        institution_name = name_input.text().strip()
        if not institution_name:
            QMessageBox.warning(
                self,
                "Institution",
                "Institution name cannot be empty.",
            )
            return

        try:
            updated_name = self.state.update_institution_name(
                institution_name
            )
            self.welcome_title.setText(f"Welcome to {updated_name}")
            self.institution_name_changed.emit(updated_name)
        except (ApiError, OSError, ValueError) as error:
            QMessageBox.critical(self, "Institution", str(error))

    @staticmethod
    def _divider():
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFrameShadow(QFrame.Shadow.Plain)
        divider.setFixedWidth(1)
        divider.setStyleSheet("background: #E5EAF2;")
        return divider

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

            self.examination_summary.setText(
                f"Examinations: {counts['examinations']}"
            )
            self.results_summary.setText(
                f"Results recorded: {counts['results']}"
            )

            rows = [
                (
                    result["name"],
                    result["programme"],
                    result["average_score"],
                    result["overall_grade"],
                )
                for result in data["recent_results"]
            ]
            self.table.clearSpans()
            self.table.populate(rows)
            if not rows:
                self.table.setRowCount(1)
                empty = QTableWidgetItem("No recent examination results")
                empty.setForeground(QColor("#64748B"))
                empty.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.table.setItem(0, 0, empty)
                self.table.setSpan(0, 0, 1, 4)
            else:
                for row_index in range(len(rows)):
                    for column_index in (2, 3):
                        item = self.table.item(row_index, column_index)
                        if item:
                            item.setTextAlignment(
                                Qt.AlignmentFlag.AlignCenter
                                | Qt.AlignmentFlag.AlignVCenter
                            )
        except ApiError as error:
            QMessageBox.critical(self, "Dashboard", str(error))
