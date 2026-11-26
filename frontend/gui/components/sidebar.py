from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from gui.styles.theme import palette, theme_signal

ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"

ICON_MAP = {
    "Dashboard": "layout-dashboard",
    "Students": "users",
    "Programmes": "school",
    "Modules": "books",
    "Examinations": "file-text",
    "Results": "checklist",
    "Reports": "chart-bar",
    "Audit Logs": "audit-logs",
    "Logout": "logout",
}

BUTTON_LABELS = (
    "Dashboard",
    "Students",
    "Programmes",
    "Modules",
    "Examinations",
    "Results",
    "Reports",
    "Audit Logs",
)


def _tint_icon(icon_name, color):
    path = ICONS_DIR / f"{icon_name}.svg"
    renderer = QSvgRenderer(str(path))
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)


def _sidebar_qss(p):
    return f"""
QWidget#sidebar {{
    background: {p['sidebar_bg']};
    border-right: 1px solid {p['border']};
}}
QWidget#sidebar QLabel {{
    background: transparent;
    border: none;
    color: {p['sidebar_text']};
}}
QWidget#sidebar QPushButton {{
    text-align: left;
    background: transparent;
    color: {p['sidebar_text']};
    border: none;
    border-radius: 8px;
    padding: 12px 14px;
    font-weight: 600;
    font-size: 13px;
}}
QWidget#sidebar QPushButton:hover {{
    background: {p['tint_bg']};
    color: {p['text']};
}}
QWidget#sidebar QPushButton[active="true"] {{
    background: {p['sidebar_active_bg']};
    color: {p['sidebar_active_text']};
}}
QWidget#sidebar QPushButton[active="true"]:hover {{
    background: {p['sidebar_active_bg']};
}}
"""


class Sidebar(QWidget):
    page_requested = pyqtSignal(str)
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self._icon_paths = {}
        theme_signal.changed.connect(self._refresh_styles)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(6)

        brand = QLabel("SDG 4 Quality Education")
        brand.setWordWrap(True)
        brand.setStyleSheet(
            "font-size: 17px; font-weight: 700; padding: 4px 8px 20px 8px;"
        )
        layout.addWidget(brand)

        self.buttons = {}
        for label in BUTTON_LABELS:
            button = QPushButton(label)
            button.setCursor(self.cursor())
            button.clicked.connect(lambda _, name=label: self.select(name))
            icon_name = ICON_MAP[label]
            self._set_button_icon(button, icon_name, False)
            layout.addWidget(button)
            self.buttons[label] = button

        layout.addStretch()
        self.logout_button = QPushButton("Logout")
        self._set_button_icon(self.logout_button, "logout", False)
        self.logout_button.setCursor(self.cursor())
        self.logout_button.clicked.connect(self.logout_requested.emit)
        layout.addWidget(self.logout_button)
        self._refresh_styles()
        self.select("Dashboard")

    def _refresh_styles(self, _name=None):
        p = palette()
        self.setStyleSheet(_sidebar_qss(p))
        active = next(
            (label for label, button in self.buttons.items()
             if button.property("active") == "true"),
            "Dashboard",
        )
        for label, button in self.buttons.items():
            self._set_button_icon(button, ICON_MAP[label], label == active)
        self._set_button_icon(
            self.logout_button, "logout", self.logout_button.property("active") == "true"
        )

    def _set_button_icon(self, button, icon_name, active):
        p = palette()
        color = p["sidebar_active_text"] if active else p["sidebar_text"]
        button.setIcon(_tint_icon(icon_name, color))
        button.setIconSize(QSize(20, 20))
        self._icon_paths[button] = icon_name

    def select(self, name):
        for label, button in self.buttons.items():
            active = label == name
            button.setProperty("active", "true" if active else "false")
            self._set_button_icon(button, ICON_MAP[label], active)
            button.style().unpolish(button)
            button.style().polish(button)
        self.page_requested.emit(name)
