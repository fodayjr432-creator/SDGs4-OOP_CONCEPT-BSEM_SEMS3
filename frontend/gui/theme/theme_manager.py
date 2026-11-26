import json
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

SETTINGS = Path.home() / ".sdg4_theme.json"

DARK = {
    "bg": "#101319",
    "sidebar": "#151A23",
    "card": "#1C2330",
    "surface": "#222B39",
    "text": "#F8FAFC",
    "muted": "#A3AEC0",
    "accent": "#3B82F6",
    "accent_hover": "#2563EB",
    "border": "#303B4B",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
}

LIGHT = {
    "bg": "#F4F7FB",
    "sidebar": "#FFFFFF",
    "card": "#FFFFFF",
    "surface": "#F8FAFC",
    "text": "#172033",
    "muted": "#687386",
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "border": "#E5EAF2",
    "success": "#16A34A",
    "warning": "#D97706",
    "error": "#DC2626",
}


class ThemeManager(QObject):
    _instance = None
    style_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.mode = "light"
        try:
            data = json.loads(SETTINGS.read_text())
            self.mode = data.get("mode", "light")
        except Exception:
            pass

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def palette(self):
        return DARK if self.mode == "dark" else LIGHT

    def toggle(self):
        self.mode = "light" if self.mode == "dark" else "dark"
        try:
            SETTINGS.write_text(json.dumps({"mode": self.mode}))
        except Exception:
            pass
        self.apply(QApplication.instance())
        self.style_changed.emit()

    def apply(self, app):
        if app is None:
            return
        p = self.palette()
        app.setStyleSheet(f"""
            QWidget {{ background: {p['bg']}; color: {p['text']}; font-family: Segoe UI; font-size: 13px; }}
            QMainWindow, QStackedWidget {{ background: {p['bg']}; }}
            QFrame, .Card {{ background: {p['card']}; border: 1px solid {p['border']}; border-radius: 12px; }}
            QPushButton {{ background: {p['accent']}; color: white; border: none; border-radius: 8px; padding: 8px 14px; font-weight: 600; }}
            QPushButton:hover {{ background: {p['accent_hover']}; }}
            QLineEdit, QComboBox, QDateEdit {{ background: {p['surface']}; border: 1px solid {p['border']}; border-radius: 8px; padding: 6px; color: {p['text']}; }}
            QTableWidget {{ background: {p['card']}; gridline-color: {p['border']}; border: 1px solid {p['border']}; border-radius: 8px; }}
            QHeaderView::section {{ background: {p['surface']}; color: {p['text']}; padding: 8px; border: none; border-bottom: 1px solid {p['border']}; font-weight: 700; }}
            QScrollBar:vertical {{ background: {p['bg']}; width: 10px; }}
            QScrollBar::handle:vertical {{ background: {p['border']}; border-radius: 5px; }}
        """)
        self.style_changed.emit()
