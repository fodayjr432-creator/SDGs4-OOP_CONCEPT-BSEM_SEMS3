"""Centralized dashboard theme tokens and QSS.

Defines LIGHT_THEME and DARK_THEME palettes used exclusively by the
dashboard workspace. The login window and the shared ThemeManager are
left untouched, so the login page keeps its existing design, colors,
and behavior.

Accent colors:
    Light theme: #2563EB (electric royal blue)
    Dark theme:  #1D63ED (electric royal blue)
"""

from __future__ import annotations

ACCENT_LIGHT = "#2563EB"
ACCENT_DARK = "#1D63ED"
ACCENT_HOVER = "#1D4ED8"

LIGHT_THEME: dict[str, str] = {
    "bg": "#F4F7FB",
    "sidebar": "#FFFFFF",
    "card": "#FFFFFF",
    "surface": "#F8FAFC",
    "text": "#172033",
    "muted": "#687386",
    "accent": ACCENT_LIGHT,
    "accent_hover": ACCENT_HOVER,
    "border": "#E5EAF2",
    "success": "#16A34A",
    "warning": "#D97706",
    "error": "#DC2626",
}

DARK_THEME: dict[str, str] = {
    "bg": "#101319",
    "sidebar": "#151A23",
    "card": "#1C2330",
    "surface": "#222B39",
    "text": "#F8FAFC",
    "muted": "#A3AEC0",
    "accent": ACCENT_DARK,
    "accent_hover": ACCENT_HOVER,
    "border": "#303B4B",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
}

THEMES = {"light": LIGHT_THEME, "dark": DARK_THEME}


def palette_for_mode(mode: str) -> dict[str, str]:
    return DARK_THEME if mode == "dark" else LIGHT_THEME


def _pill_tokens(p: dict[str, str]) -> tuple[str, str]:
    if p["accent"] == ACCENT_DARK:
        return "#1B2434", "#303B4B"
    return "#EFF6FF", "#BFDBFE"


def dashboard_qss(p: dict[str, str]) -> str:
    """Full QSS for the dashboard workspace built from a theme palette."""
    pill_bg, pill_border = _pill_tokens(p)
    return f"""
    QWidget {{
        background: {p['bg']};
        color: {p['text']};
        font-family: "Segoe UI";
        font-size: 13px;
    }}
    QFrame#card {{
        background: {p['card']};
        border: 1px solid {p['border']};
        border-radius: 12px;
    }}
    QLabel#pageTitle {{
        color: {p['text']};
        font-size: 18px;
        font-weight: 700;
    }}
    QLabel#muted {{
        color: {p['muted']};
        font-size: 13px;
    }}
    QLabel#dashboardWelcome {{
        color: {p['text']};
        font-size: 20px;
        font-weight: 800;
    }}
    QLabel#pagePill {{
        color: {p['accent']};
        background: {pill_bg};
        border: 1px solid {pill_border};
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 13px;
        font-weight: 700;
    }}
    QPushButton#secondary {{
        background: {p['surface']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 8px;
        padding: 6px 14px;
        font-weight: 600;
        min-height: 36px;
    }}
    QPushButton#secondary:hover {{
        background: {p['accent_hover']};
        color: #FFFFFF;
        border: 1px solid {p['accent_hover']};
    }}
    QPushButton#secondary:pressed {{
        background: {p['accent']};
    }}
    QPushButton#primaryButton {{
        background: {p['accent']};
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        min-height: 42px;
    }}
    QPushButton#primaryButton:hover {{
        background: {p['accent_hover']};
    }}
    QPushButton#primaryButton:pressed {{
        background: {ACCENT_DARK if p['accent'] == ACCENT_DARK else '#1D4ED8'};
    }}
    QTableWidget {{
        background: {p['card']};
        border: 1px solid {p['border']};
        border-radius: 8px;
        gridline-color: {p['border']};
    }}
    QHeaderView::section {{
        background: {p['surface']};
        color: {p['text']};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {p['border']};
        font-weight: 700;
        font-size: 13px;
    }}
    QTableWidget::item {{
        padding: 7px;
        border: none;
    }}
    QTableWidget::item:selected {{
        background: {p['accent']};
        color: #FFFFFF;
    }}
    """
