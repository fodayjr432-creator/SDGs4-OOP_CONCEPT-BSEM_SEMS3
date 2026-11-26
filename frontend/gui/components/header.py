from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QWidget

from gui.styles.theme import apply_theme, palette, theme_signal


def _header_qss(p):
    return f"""
QWidget#header {{
    background: {p['card']};
    border-bottom: 1px solid {p['border']};
}}
QWidget#header QLabel {{
    background: transparent;
    border: none;
}}
QLabel#pageTitle {{
    color: {p['text']};
    font-size: 22px;
    font-weight: 700;
}}
QLabel#muted {{
    color: {p['muted']};
    font-size: 13px;
}}
QLabel#userBadge {{
    color: {p['text']};
    font-size: 13px;
    font-weight: 600;
    padding: 0 6px;
}}
QWidget#header QComboBox#themeCombo {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    min-height: 30px;
}}
QWidget#header QComboBox#themeCombo::drop-down {{
    border: none;
}}
QWidget#header QComboBox#themeCombo QAbstractItemView {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    selection-background-color: {p['primary']};
    selection-color: white;
}}
"""


class Header(QWidget):
    def __init__(
        self,
        username="Administrator",
        institution_name=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("header")
        self.setFixedHeight(72)
        theme_signal.changed.connect(self._refresh_styles)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        self.title = QLabel("Dashboard")
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)
        layout.addStretch()
        if institution_name:
            self.institution = QLabel(institution_name)
            self.institution.setObjectName("institutionLabel")
            self.institution.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.institution)
            layout.addSpacing(10)
        else:
            self.institution = None
        self.welcome = QLabel(f"Welcome, <b>{username}</b>")
        self.welcome.setObjectName("userBadge")
        self.welcome.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.welcome)
        layout.addSpacing(10)
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("themeCombo")
        self.theme_combo.addItems(["Light", "Dark Sidebar", "Emerald", "Night"])
        saved = QSettings("SDG4", "ExamResults").value("theme", "Light")
        if saved not in ("Light", "Dark Sidebar", "Emerald", "Night"):
            saved = "Light"
        self.theme_combo.setCurrentText(saved)
        self.theme_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addWidget(self.theme_combo)
        self._refresh_styles()

    def _refresh_styles(self):
        self.setStyleSheet(_header_qss(palette()))
        name = QSettings("SDG4", "ExamResults").value("theme", "Light")
        if name not in ("Light", "Dark Sidebar", "Emerald", "Night"):
            name = "Light"
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentText(name)
        self.theme_combo.blockSignals(False)
        if self.institution is not None:
            self.institution.setText(self.institution.text())

    def _on_theme_changed(self, name):
        apply_theme(QApplication.instance(), name)

    def set_title(self, title):
        self.title.setText(title)

    def set_institution(self, institution_name):
        if self.institution is not None:
            self.institution.setText(institution_name)
