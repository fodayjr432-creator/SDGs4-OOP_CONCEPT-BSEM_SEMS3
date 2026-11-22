from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QMessageBox,
)

from api_client import ApiError
from gui.components.sidebar import Sidebar
from gui.components.header import Header


class MainWindow(QMainWindow):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.setWindowTitle("SDG 4 Quality Education")
        self.resize(1280, 760)
        self.setObjectName("root")

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar()
        root_layout.addWidget(self.sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.header = Header(
            state.username,
            state.account.get("institution"),
        )
        content_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        root_layout.addWidget(content)
        self.setCentralWidget(root)

        self.sidebar.page_requested.connect(self.navigate)
        self.sidebar.logout_requested.connect(self.logout)

        from gui.pages.dashboard_page import DashboardPage
        from gui.pages.students_page import StudentsPage
        from gui.pages.programmes_page import ProgrammesPage
        from gui.pages.modules_page import ModulesPage
        from gui.pages.examinations_page import ExaminationsPage
        from gui.pages.results_page import ResultsPage
        from gui.pages.reports_page import ReportsPage

        self.pages = {
            "Dashboard": DashboardPage(state),
            "Students": StudentsPage(state),
            "Programmes": ProgrammesPage(state),
            "Modules": ModulesPage(state),
            "Examinations": ExaminationsPage(state),
            "Results": ResultsPage(state),
            "Reports": ReportsPage(state),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)
        self.pages["Dashboard"].action_requested.connect(self.navigate)
        self.pages["Dashboard"].institution_name_changed.connect(
            self.header.set_institution
        )

        self.navigate("Dashboard")

    def navigate(self, name):
        page = self.pages[name]
        self.stack.setCurrentWidget(page)
        self.header.set_title(name)
        if hasattr(page, "refresh"):
            page.refresh()


    def logout(self):
        from gui.windows.login_window import LoginWindow

        logout_error = None
        try:
            self.state.api.logout()
        except ApiError as error:
            logout_error = error
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()
        if logout_error:
            QMessageBox.warning(
                self.login_window, "Logout", f"Could not revoke the server session: {logout_error}"
            )
