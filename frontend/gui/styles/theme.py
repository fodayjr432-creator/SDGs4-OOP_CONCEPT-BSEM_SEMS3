"""Application theme palettes and global stylesheet generation.

Defines four switchable themes (Light, Dark Sidebar, Emerald, Night) with a
single central palette each. ``build_qss`` renders the global QSS from a
palette, and ``apply_theme`` applies it to the QApplication and persists the
choice with QSettings. ``theme_signal`` lets components restyle live when the
theme changes.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QSettings

_SETTINGS = QSettings("SDG4", "ExamResults")
_THEME_KEY = "theme"
_DEFAULT_THEME = "Light"
_CURRENT_THEME = _DEFAULT_THEME

LIGHT = {
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "primary_pressed": "#1E40AF",
    "bg": "#F5F7FB",
    "card": "#FFFFFF",
    "text": "#172033",
    "muted": "#64748B",
    "border": "#E5EAF2",
    "sidebar_bg": "#FFFFFF",
    "sidebar_text": "#64748B",
    "sidebar_hover_bg": "#F1F5F9",
    "sidebar_hover_text": "#172033",
    "sidebar_active_bg": "#2563EB",
    "sidebar_active_text": "#FFFFFF",
    "brand_panel_bg": "#F5F7FB",
    "brand_text": "#172033",
    "brand_muted": "#64748B",
    "tint_bg": "#DBEAFE",
    "tint_text": "#1E3A8A",
    "danger": "#DC2626",
    "success": "#16A34A",
}


def _derive(base, overrides):
    merged = dict(base)
    merged.update(overrides)
    return merged


DARK_SIDEBAR = _derive(LIGHT, {
    "sidebar_bg": "#0F172A",
    "sidebar_text": "#94A3B8",
    "sidebar_hover_bg": "#1E293B",
    "sidebar_hover_text": "#F1F5F9",
    "brand_panel_bg": "#0F172A",
    "brand_text": "#F8FAFC",
    "brand_muted": "#94A3B8",
})

EMERALD = _derive(LIGHT, {
    "primary": "#0F766E",
    "primary_hover": "#115E59",
    "bg": "#F3F8F7",
    "brand_panel_bg": "#E6F4F1",
    "sidebar_hover_bg": "#E6F4F1",
    "sidebar_hover_text": "#134E4A",
    "tint_bg": "#CCFBF1",
    "tint_text": "#134E4A",
})

NIGHT = _derive(LIGHT, {
    "primary": "#3B82F6",
    "bg": "#0B1220",
    "card": "#111827",
    "text": "#E5E7EB",
    "muted": "#94A3B8",
    "border": "#1F2937",
    "sidebar_bg": "#0F172A",
    "sidebar_text": "#94A3B8",
    "sidebar_hover_bg": "#1E293B",
    "sidebar_hover_text": "#F1F5F9",
    "brand_panel_bg": "#0B1220",
    "brand_text": "#F1F5F9",
    "brand_muted": "#94A3B8",
    "tint_bg": "#1E3A8A",
    "tint_text": "#DBEAFE",
})

PALETTES: dict[str, dict[str, str]] = {
    "Light": LIGHT,
    "Dark Sidebar": DARK_SIDEBAR,
    "Emerald": EMERALD,
    "Night": NIGHT,
}

THEME_ORDER = ["Light", "Dark Sidebar", "Emerald", "Night"]


class ThemeSignal(QObject):
    changed = pyqtSignal(str)


theme_signal = ThemeSignal()


def palette(name=None):
    if name is None:
        name = _CURRENT_THEME
    return PALETTES.get(name, PALETTES[_DEFAULT_THEME])


def build_qss(name=_DEFAULT_THEME) -> str:
    """Render the global stylesheet from the given theme palette."""
    p = palette(name)
    return f"""
* {{
    font-family: "Segoe UI";
    font-size: 14px;
    color: {p['text']};
}}
QWidget#root {{
    background: {p['bg']};
}}
QMainWindow {{
    background: {p['bg']};
}}
QLabel#pageTitle {{
    font-size: 22px;
    font-weight: 700;
    color: {p['text']};
}}
QLabel#muted {{
    color: {p['muted']};
}}
QPushButton {{
    background: {p['primary']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {p['primary_hover']};
}}
QPushButton:pressed {{
    background: {p['primary_pressed']};
}}
QPushButton#secondary {{
    background: {p['bg']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}}
QPushButton#danger {{
    background: {p['danger']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {{
    background: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 8px;
    color: {p['text']};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border: 2px solid {p['primary']};
}}
QFrame#card {{
    background: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 12px;
}}
QTableWidget {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    gridline-color: {p['border']};
}}
QHeaderView::section {{
    background: {p['bg']};
    border: none;
    border-bottom: 1px solid {p['border']};
    padding: 9px;
    font-weight: 700;
    font-size: 13px;
    color: {p['muted']};
}}
QTableWidget::item {{
    padding: 7px;
    border: none;
}}
QTableWidget::item:selected {{
    background: {p['tint_bg']};
    color: {p['tint_text']};
}}
"""


THEME_QSS = build_qss(_DEFAULT_THEME)


def apply_theme(app, name=_DEFAULT_THEME):
    """Apply the theme to ``app``, persist it, and notify components."""
    if name not in PALETTES:
        name = _DEFAULT_THEME
    global _CURRENT_THEME
    _CURRENT_THEME = name
    app.setStyleSheet(build_qss(name))
    _SETTINGS.setValue(_THEME_KEY, name)
    theme_signal.changed.emit(name)
    return name


def load_theme(app):
    """Load the persisted theme (default Light) and apply it to ``app``."""
    name = _SETTINGS.value(_THEME_KEY, _DEFAULT_THEME)
    if not isinstance(name, str) or name not in PALETTES:
        name = _DEFAULT_THEME
    return apply_theme(app, name)
