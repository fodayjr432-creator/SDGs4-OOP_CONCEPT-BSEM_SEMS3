from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from gui.styles.theme import palette, theme_signal
from gui.components.stat_card import StatCard
from gui.components.data_table import DataTable
from api_client import ApiError


ICONS = {
    "Total Students": "users",
    "Total Programmes": "school",
    "Total Modules": "books",
    "Total Examinations": "file-text",
    "Results Recorded": "checklist",
}

TITLES = (
    "Total Students",
    "Total Programmes",
    "Total Modules",
    "Total Examinations",
    "Results Recorded",
)

COUNT_KEYS = {
    "Total Students": "students",
    "Total Programmes": "programmes",
    "Total Modules": "modules",
    "Total Examinations": "examinations",
    "Results Recorded": "results",
}

FALLBACK_COUNTS = {
    "Total Students": 8,
    "Total Programmes": 3,
    "Total Modules": 14,
    "Total Examinations": 3,
    "Results Recorded": 7,
}

FALLBACK_RESULTS = [
    ("Foday Kamara Jr", "BSE", "90.0", "A"),
    ("Alice Mensah", "CE", "82.5", "B"),
    ("Kwame Osei", "BICT", "74.0", "B"),
    ("Zainab Kamara", "BSE", "68.0", "C"),
    ("David Conteh", "CE", "91.5", "A"),
]


class GradeDelegate(QStyledItemDelegate):
    """Renders the Overall Grade column as a themed pill."""

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        p = palette()
        rect = option.rect.adjusted(6, 6, -6, -6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["tint_bg"]))
        painter.drawRoundedRect(rect, 10, 10)
        pen = painter.pen()
        pen.setColor(QColor(p["tint_text"]))
        painter.setPen(pen)
        font = painter.font()
        font.setPointSize(11)
        font.setWeight(700)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(index.data() or ""))
        painter.restore()


class DashboardPage(QWidget):
    action_requested = pyqtSignal(str)
    institution_name_changed = pyqtSignal(str)

    def __init__(self, state):
        super().__init__()
        self.state = state
        theme_signal.changed.connect(self._refresh_styles)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        self._build_welcome_banner(layout)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        self.card_labels = {}
        for title in TITLES:
            card = StatCard(title, "0", ICONS[title])
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            cards_layout.addWidget(card)
            self.card_labels[title] = card
        layout.addLayout(cards_layout)

        self._build_quick_actions(layout)
        self._build_results_table(layout)

        layout.addStretch()
        self._refresh_styles()
        self.refresh()

    # ------------------------------------------------------------------ UI

    def _build_welcome_banner(self, layout):
        welcome = QFrame()
        welcome.setObjectName("card")
        welcome_layout = QHBoxLayout(welcome)
        welcome_layout.setContentsMargins(20, 14, 20, 14)
        welcome_layout.setSpacing(12)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        institution_name = getattr(self.state, "institution_name", "Limkokwing University")
        self.welcome_title = QLabel(f"Welcome to {institution_name}")
        self.welcome_title.setObjectName("dashboardWelcome")
        self.welcome_title.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        welcome_subtitle = QLabel(
            "Here's an overview of your academic activities."
        )
        welcome_subtitle.setObjectName("muted")
        text_layout.addWidget(self.welcome_title)
        text_layout.addWidget(welcome_subtitle)
        welcome_layout.addLayout(text_layout, 1)

        if self.state.is_admin:
            edit_button = QPushButton("Edit Institution Name")
            edit_button.setObjectName("secondary")
            edit_button.setMinimumHeight(36)
            edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_button.clicked.connect(self.edit_institution_name)
            welcome_layout.addWidget(edit_button)

        layout.addWidget(welcome)

    def _build_quick_actions(self, layout):
        quick = QFrame()
        quick.setObjectName("card")
        quick_layout = QVBoxLayout(quick)
        quick_layout.setContentsMargins(16, 12, 16, 12)
        quick_layout.setSpacing(10)

        quick_heading = QLabel("Quick Actions")
        quick_heading.setStyleSheet(
            f"font-size: 16px; font-weight: 800; color: {palette()['text']};"
        )
        quick_layout.addWidget(quick_heading)

        quick_buttons = QHBoxLayout()
        quick_buttons.setSpacing(10)
        targets = {
            "Add Student": "Students",
            "Record Result": "Results",
            "View Reports": "Reports",
        }
        for title in targets:
            button = QPushButton(title)
            button.setObjectName("secondary")
            button.setMinimumHeight(42)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _, page=targets[title]: self.action_requested.emit(page)
            )
            quick_buttons.addWidget(button, 1)
        quick_layout.addLayout(quick_buttons)
        layout.addWidget(quick)

    def _build_results_table(self, layout):
        recent = QFrame()
        recent.setObjectName("card")
        recent_layout = QVBoxLayout(recent)
        recent_layout.setContentsMargins(16, 12, 16, 12)
        recent_layout.setSpacing(8)

        label = QLabel("Recent Examination Results")
        label.setStyleSheet(
            f"font-size: 16px; font-weight: 800; color: {palette()['text']};"
        )
        recent_layout.addWidget(label)

        self.table = DataTable(("Student", "Programme", "Average", "Overall Grade"))
        self.table.setMinimumHeight(180)
        self.table.setMaximumHeight(220)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.table.setItemDelegateForColumn(3, GradeDelegate(self.table))
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        recent_layout.addWidget(self.table)
        layout.addWidget(recent)

    # ------------------------------------------------------------------ themes

    def _refresh_styles(self):
        p = palette()
        self.welcome_title.setStyleSheet(
            f"font-size: 20px; font-weight: 800; color: {p['text']};"
        )
        self.table.viewport().update()

    # ------------------------------------------------------------------ data

    def refresh(self):
        try:
            data = self.state.load_dashboard() or {}
            counts = data.get("counts") or {}
            values = {
                title: counts.get(key, 0)
                for title, key in COUNT_KEYS.items()
            }
            rows = [
                (
                    str(result.get("name", "")),
                    str(result.get("programme", "")),
                    str(result.get("average_score", "")),
                    str(result.get("overall_grade", "")),
                )
                for result in (data.get("recent_results") or [])
            ]
        except Exception:
            values = dict(FALLBACK_COUNTS)
            rows = [tuple(row) for row in FALLBACK_RESULTS]

        for title, value in values.items():
            self.card_labels[title].set_value(value)

        for row_index in range(self.table.rowCount()):
            self.table.setCellWidget(row_index, 3, None)

        self.table.clearSpans()
        self.table.populate(rows)
        if not rows:
            self.table.setRowCount(1)
            p = palette()
            empty = QTableWidgetItem("No recent examination results")
            empty.setForeground(QColor(p["muted"]))
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

    # ------------------------------------------------------------------ actions

    def edit_institution_name(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Institution Name")
        dialog.setMinimumWidth(420)
        p = palette()
        dialog.setStyleSheet(f"""
            QDialog {{ background: {p['bg']}; color: {p['text']}; }}
            QLabel {{ color: {p['text']}; }}
            QLineEdit {{
                background: {p['card']};
                border: 1px solid {p['border']};
                border-radius: 8px;
                padding: 8px;
                color: {p['text']};
                min-height: 36px;
            }}
            QLineEdit:focus {{ border: 2px solid {p['primary']}; }}
            QPushButton {{
                background: {p['primary']};
                color: {p['sidebar_active_text']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                min-height: 36px;
            }}
            QPushButton:hover {{ background: {p['primary_hover']}; }}
        """)

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(24, 20, 24, 20)
        d_layout.setSpacing(12)
        d_layout.addWidget(QLabel("Institution name"))

        name_input = QLineEdit(getattr(self.state, "institution_name", ""))
        name_input.setAccessibleName("Institution name")
        name_input.selectAll()
        d_layout.addWidget(name_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        d_layout.addWidget(buttons)

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
