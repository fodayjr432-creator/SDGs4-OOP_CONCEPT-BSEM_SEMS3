from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel


class Header(QWidget):
    def __init__(self, username="Administrator", parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        self.title = QLabel("Dashboard")
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)
        layout.addStretch()
        welcome = QLabel(f"Welcome, {username}")
        welcome.setObjectName("muted")
        layout.addWidget(welcome)

    def set_title(self, title):
        self.title.setText(title)
