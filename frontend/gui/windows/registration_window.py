from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from api_client import ApiClient, ApiError
from gui.api_worker import ApiWorker
from gui.styles.theme import palette, theme_signal


def _registration_qss(p):
    """Generate the registration window stylesheet from the given theme palette."""
    return f"""
QDialog {{
    background: {p['bg']};
    color: {p['text']};
    font-family: "Segoe UI";
}}
QLabel#registrationTitle {{
    color: {p['text']};
    font-size: 25px;
    font-weight: 700;
}}
QLabel#registrationDescription, QLabel#registrationStatus {{
    color: {p['muted']};
    font-size: 13px;
}}
QLabel#registrationStatus[feedback="error"] {{ color: {p['danger']}; }}
QLabel#registrationStatus[feedback="success"] {{ color: {p['success']}; }}
QLineEdit {{
    background: {p['bg']};
    border: 1px solid {p['border']};
    border-radius: 7px;
    color: {p['text']};
    min-height: 36px;
    padding: 0 9px;
}}
QLineEdit:focus {{ border: 2px solid {p['primary']}; }}
QPushButton#registerSubmit {{
    background: {p['primary']};
    border: none;
    border-radius: 7px;
    color: #FFFFFF;
    font-weight: 600;
    min-height: 42px;
}}
QPushButton#registerSubmit:hover {{ background: {p['primary_hover']}; }}
QPushButton#registerSubmit:disabled {{ background: {p['muted']}; }}
QPushButton#registerCancel {{
    background: {p['bg']};
    border: 1px solid {p['border']};
    border-radius: 7px;
    color: {p['text']};
    min-height: 40px;
}}
QPushButton#registerCancel:hover {{ background: {p['primary_hover']}; color: #FFFFFF; }}
"""


class RegistrationWindow(QDialog):
    registration_succeeded = pyqtSignal()

    def __init__(self, api_client=None, parent=None):
        super().__init__(parent)
        self.api = api_client or ApiClient()
        self._worker = None
        self._processing = False
        self._registered = False
        self.setWindowTitle("First-time institution setup")
        self.setMinimumWidth(480)
        self._refresh_styles()
        theme_signal.changed.connect(self._refresh_styles)
        self._build_ui()

    def _refresh_styles(self):
        self.setStyleSheet(_registration_qss(palette()))

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 24)
        layout.setSpacing(12)

        title = QLabel("Register your institution")
        title.setObjectName("registrationTitle")
        layout.addWidget(title)

        description = QLabel(
            "Create the first institution administrator account. "
            "Public registration closes after this account is created."
        )
        description.setObjectName("registrationDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        form = QFormLayout()
        form.setVerticalSpacing(10)
        self.institution_name = self._add_field(form, "Institution name")
        self.administrator_name = self._add_field(form, "Administrator full name")
        self.username = self._add_field(form, "Username")
        self.email = self._add_field(form, "Email")
        self.password = self._add_field(form, "Password", password=True)
        self.confirm_password = self._add_field(
            form,
            "Confirm password",
            password=True,
        )
        layout.addLayout(form)

        password_hint = QLabel(
            "Use at least 12 characters, including a letter, a number, "
            "and a special character."
        )
        password_hint.setObjectName("registrationDescription")
        password_hint.setWordWrap(True)
        layout.addWidget(password_hint)

        self.status = QLabel("")
        self.status.setObjectName("registrationStatus")
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(20)
        layout.addWidget(self.status)

        self.submit_button = QPushButton("Create administrator account")
        self.submit_button.setObjectName("registerSubmit")
        self.submit_button.clicked.connect(self.submit)
        layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("registerCancel")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

    @staticmethod
    def _add_field(form, label, password=False):
        field = QLineEdit()
        field.setAccessibleName(label)
        field.setPlaceholderText(label)
        if password:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow(label, field)
        return field

    def _set_status(self, message, feedback="neutral"):
        self.status.setText(message)
        self.status.setProperty("feedback", feedback)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def submit(self):
        if self._registered:
            self.accept()
            return
        if self._processing:
            return

        institution_name = self.institution_name.text().strip()
        administrator_name = self.administrator_name.text().strip()
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text()
        confirm_password = self.confirm_password.text()
        if not all((institution_name, administrator_name, username, email, password)):
            self._set_status("Complete all fields before continuing.", "error")
            return
        if password != confirm_password:
            self._set_status("The passwords do not match.", "error")
            return

        self._processing = True
        self._set_enabled(False)
        self.submit_button.setText("Creating account…")
        self._set_status("Validating account details…")
        self._start_worker(
            lambda: self.api.register_institution_administrator(
                institution_name,
                administrator_name,
                username,
                email,
                password,
                confirm_password,
            ),
            self._registration_succeeded,
            self._registration_failed,
        )

    def _start_worker(self, operation, succeeded, failed):
        worker = ApiWorker(operation, self)
        worker.succeeded.connect(succeeded)
        worker.failed.connect(failed)
        worker.finished.connect(lambda: self._worker_finished(worker))
        self._worker = worker
        worker.start()

    def _worker_finished(self, worker):
        if self._worker is worker:
            self._worker = None
        worker.deleteLater()

    def _registration_succeeded(self, _response):
        self._registered = True
        self._processing = False
        self.password.clear()
        self.confirm_password.clear()
        self.registration_succeeded.emit()
        self._set_status(
            "Administrator account created. Close this window and sign in.",
            "success",
        )
        self.submit_button.setText("Done")
        self._set_enabled(False)
        self.submit_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Close")

    def _registration_failed(self, message):
        self._processing = False
        self._set_status(str(message), "error")
        self.submit_button.setText("Create administrator account")
        self._set_enabled(True)

    def _set_enabled(self, enabled):
        for field in (
            self.institution_name,
            self.administrator_name,
            self.username,
            self.email,
            self.password,
            self.confirm_password,
        ):
            field.setEnabled(enabled)
        self.submit_button.setEnabled(enabled)
        self.cancel_button.setEnabled(enabled)

    def reject(self):
        if not self._processing:
            super().reject()
