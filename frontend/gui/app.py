import sys

from PyQt6.QtWidgets import QApplication

from gui.styles.theme import THEME_QSS
from gui.windows.login_window import LoginWindow


def run():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("SDG 4 Quality Education")
    app.setStyleSheet(THEME_QSS)

    login = LoginWindow()
    login.show()
    sys.exit(app.exec())
