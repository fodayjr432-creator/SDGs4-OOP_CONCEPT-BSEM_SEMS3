from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel


class StatCard(QFrame):
    def __init__(self, title, value="0", marker="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(108)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(7)

        heading_layout = QHBoxLayout()
        heading_layout.setContentsMargins(0, 0, 0, 0)
        heading_layout.setSpacing(8)

        if marker:
            marker_label = QLabel(marker)
            marker_label.setFixedSize(32, 32)
            marker_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            marker_label.setStyleSheet("""
                background: #2563EB;
                color: white;
                border-radius: 16px;
                font-size: 11px;
                font-weight: 800;
            """)
            heading_layout.addWidget(marker_label)

        title_label = QLabel(title)
        title_label.setObjectName("muted")
        title_label.setWordWrap(True)
        heading_layout.addWidget(title_label, 1)
        layout.addLayout(heading_layout)

        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("font-size: 26px; font-weight: 800; color: #172033;")
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))