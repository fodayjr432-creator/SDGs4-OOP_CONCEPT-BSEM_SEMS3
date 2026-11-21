from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class Sidebar(QWidget):
    page_requested = pyqtSignal(str)
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet("""
            QWidget { background: #FFFFFF; border-right: 1px solid #E5EAF2; }
            QLabel { color: #172033; }
            QPushButton {
                text-align: left;
                background: transparent;
                color: #64748B;
                border: none;
                border-radius: 8px;
                padding: 12px 14px;
                font-weight: 600;
            }
            QPushButton:hover { background: #F5F7FB; color: #172033; }
            QPushButton[active="true"] { background: #2563EB; color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(5)

        brand = QLabel("SDG 4 Quality Education")
        brand.setStyleSheet("font-size: 17px; font-weight: 800; padding: 4px 8px 20px 8px;")
        layout.addWidget(brand)

        self.buttons = {}
        for label in ("Dashboard", "Students", "Programmes", "Modules",
                      "Examinations", "Results", "Reports"):
            button = QPushButton(label)
            button.setCursor(self.cursor())
            button.clicked.connect(lambda _, name=label: self.select(name))
            layout.addWidget(button)
            self.buttons[label] = button

        layout.addStretch()
        logout = QPushButton("Logout")
        logout.setObjectName("logout")
        logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout)
        self.select("Dashboard")

    def select(self, name):
        for label, button in self.buttons.items():
            button.setProperty("active", "true" if label == name else "false")
            button.style().unpolish(button)
            button.style().polish(button)
        self.page_requested.emit(name)
