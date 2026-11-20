import sys

from PyQt6.QtWidgets import QApplication

from gui.styles.theme import THEME_QSS
from gui.windows.login_window import LoginWindow


def run():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Digital Examination Results Management System")
    app.setStyleSheet(THEME_QSS)

    login = LoginWindow()
    login.show()
    sys.exit(app.exec())
