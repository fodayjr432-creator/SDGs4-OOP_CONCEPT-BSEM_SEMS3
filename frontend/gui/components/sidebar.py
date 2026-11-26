from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.styles.theme import palette, theme_signal
from gui.components.icons import tinted_pixmap

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
    background: {p['sidebar_hover_bg']};
    color: {p['sidebar_hover_text']};
}}
QWidget#sidebar QPushButton[active="true"] {{
    background: {p['sidebar_active_bg']};
    color: {p['sidebar_active_text']};
}}
QWidget#sidebar QPushButton[active="true"]:hover {{
    background: {p['sidebar_active_bg']};
}}
"""


class NavButton(QPushButton):
    def __init__(self, label, icon_name, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self._state = "normal"
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(label)
        self.setToolTip(label)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(12)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self.text_label = QLabel(label)
        self.text_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.text_label.setStyleSheet(
            "background: transparent; border: none; "
            "font-size: 13px; font-weight: 600;"
        )
        self.text_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label, 1)
        self.set_state("normal")

    def set_state(self, state):
        if state not in {"normal", "hover", "active"}:
            state = "normal"
        self._state = state
        p = palette()
        if state == "active":
            icon_color = p["sidebar_active_text"]
            text_color = p["sidebar_active_text"]
        elif state == "hover":
            icon_color = p["sidebar_hover_text"]
            text_color = p["sidebar_hover_text"]
        else:
            icon_color = p["sidebar_text"]
            text_color = p["sidebar_text"]
        self.icon_label.setPixmap(tinted_pixmap(self.icon_name, icon_color, 20))
        self.text_label.setStyleSheet(
            "background: transparent; border: none; "
            f"color: {text_color}; font-size: 13px; font-weight: 600;"
        )

    def enterEvent(self, event):
        if self.property("active") != "true":
            self.set_state("hover")
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.property("active") == "true":
            self.set_state("active")
        else:
            self.set_state("normal")
        super().leaveEvent(event)


class Sidebar(QWidget):
    page_requested = pyqtSignal(str)
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
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
            button = NavButton(label, ICON_MAP[label])
            button.clicked.connect(lambda _, name=label: self.select(name))
            layout.addWidget(button)
            self.buttons[label] = button

        layout.addStretch()
        self.logout_button = NavButton("Logout", "logout")
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
            button.set_state("active" if label == active else "normal")
        logout_active = self.logout_button.property("active") == "true"
        self.logout_button.set_state("active" if logout_active else "normal")

    def select(self, name):
        for label, button in self.buttons.items():
            active = label == name
            button.setProperty("active", "true" if active else "false")
            button.set_state("active" if active else "normal")
            button.style().unpolish(button)
            button.style().polish(button)
        self.page_requested.emit(name)
