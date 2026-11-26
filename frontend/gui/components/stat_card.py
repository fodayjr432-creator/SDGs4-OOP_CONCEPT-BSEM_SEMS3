from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from gui.styles.theme import palette, theme_signal
from gui.components.icons import tinted_pixmap


def _stat_card_qss(p):
    return f"""
QFrame#card {{
    background: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 12px;
}}
QLabel#muted {{
    color: {p['muted']};
    font-size: 13px;
    font-weight: 600;
}}
QLabel#statValue {{
    color: {p['text']};
    font-size: 26px;
    font-weight: 800;
}}
"""


class StatCard(QFrame):
    def __init__(self, title, value="0", icon="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(108)
        self._icon = icon
        theme_signal.changed.connect(self._refresh_styles)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(7)

        heading_layout = QHBoxLayout()
        heading_layout.setContentsMargins(0, 0, 0, 0)
        heading_layout.setSpacing(8)

        self.badge = None
        if icon:
            self.badge = QLabel()
            self.badge.setFixedSize(32, 32)
            self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            heading_layout.addWidget(
                self.badge,
                0,
                Qt.AlignmentFlag.AlignVCenter,
            )

        title_label = QLabel(title)
        title_label.setObjectName("muted")
        title_label.setWordWrap(True)
        heading_layout.addWidget(
            title_label,
            1,
            Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addLayout(heading_layout)

        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("statValue")
        layout.addWidget(self.value_label)

        self._refresh_styles()

    def _refresh_styles(self):
        self.setStyleSheet(_stat_card_qss(palette()))
        if self.badge is not None and self._icon:
            p = palette()
            self.badge.setStyleSheet(
                f"background: {p['tint_bg']}; border-radius: 16px;"
            )
            self.badge.setPixmap(
                tinted_pixmap(
                    self._icon,
                    p["tint_text"],
                    18,
                )
            )

    def set_value(self, value):
        self.value_label.setText(str(value))
