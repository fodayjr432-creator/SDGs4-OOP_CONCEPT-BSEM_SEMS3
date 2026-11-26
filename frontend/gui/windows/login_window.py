from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.api_worker import ApiWorker
from gui.app_state import AppState
from gui.styles.theme import PALETTES
from gui.windows.registration_window import RegistrationWindow
from api_client import ApiClient, ApiError


_LIGHT = PALETTES["Light"]
BG_LEFT = _LIGHT["brand_panel_bg"]
BG_RIGHT = _LIGHT["card"]
CARD_SURFACE = _LIGHT["card"]
BORDER = _LIGHT["border"]
DIVIDER = _LIGHT["border"]
INPUT_BORDER = _LIGHT["border"]
PRIMARY = _LIGHT["primary"]
PRIMARY_HOVER = _LIGHT["primary_hover"]
PRIMARY_PRESSED = _LIGHT["primary_pressed"]
TEXT_DARK = _LIGHT["text"]
TEXT_DARK2 = _LIGHT["text"]
MUTED = _LIGHT["muted"]
MUTED2 = _LIGHT["muted"]
LABEL_COLOR = _LIGHT["text"]
ILLUSTRATION_BG = _LIGHT["tint_bg"]
GREEN = _LIGHT["success"]
ERROR = _LIGHT["danger"]


class BrandMark(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 46)
        self.setAccessibleName("Academic results system logo")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(PRIMARY))
        painter.drawRoundedRect(QRectF(0, 0, 46, 46), 13, 13)

        pen = QPen(QColor("#FFFFFF"), 2.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        book = QPainterPath()
        book.moveTo(12, 14)
        book.lineTo(21, 17)
        book.lineTo(21, 30)
        book.lineTo(12, 27)
        book.closeSubpath()
        book.moveTo(32, 14)
        book.lineTo(23, 17)
        book.lineTo(23, 30)
        book.lineTo(32, 27)
        book.closeSubpath()
        book.moveTo(22, 17)
        book.lineTo(22, 31)
        painter.drawPath(book)
        event.accept()


class AcademicIllustration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(190)
        self.setMaximumHeight(270)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAccessibleName("Illustration of academic results and performance charts")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale = min(self.width() / 480, self.height() / 270)
        painter.translate(
            (self.width() - 480 * scale) / 2,
            (self.height() - 270 * scale) / 2,
        )
        painter.scale(scale, scale)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(ILLUSTRATION_BG))
        painter.drawRoundedRect(QRectF(0, 0, 480, 270), 22, 22)
        painter.setBrush(QColor("#DCE9FC"))
        painter.drawEllipse(QRectF(24, 25, 10, 10))
        painter.drawEllipse(QRectF(438, 225, 7, 7))
        painter.setBrush(QColor("#D5E4FB"))
        painter.drawEllipse(QRectF(390, 24, 42, 42))

        # Report card with a soft offset shadow.
        painter.setBrush(QColor("#D4E1F5"))
        painter.drawRoundedRect(QRectF(153, 32, 180, 214), 13, 13)
        painter.setBrush(QColor(CARD_SURFACE))
        painter.drawRoundedRect(QRectF(146, 25, 180, 214), 13, 13)

        painter.setBrush(QColor("#EFF5FF"))
        painter.drawRoundedRect(QRectF(163, 42, 34, 34), 10, 10)
        painter.setPen(QPen(QColor(PRIMARY), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(QPointF(170, 61), QPointF(177, 54))
        painter.drawLine(QPointF(177, 54), QPointF(182, 59))
        painter.drawLine(QPointF(182, 59), QPointF(191, 49))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#CBD5E1"))
        painter.drawRoundedRect(QRectF(207, 48, 100, 7), 3, 3)
        painter.setBrush(QColor("#E2E8F0"))
        painter.drawRoundedRect(QRectF(207, 62, 70, 5), 2, 2)

        painter.setPen(QPen(QColor("#E2E8F0"), 1))
        painter.drawLine(QPointF(164, 91), QPointF(308, 91))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#94A3B8"))
        for y, width in ((104, 49), (135, 62), (166, 42)):
            painter.drawRoundedRect(QRectF(164, y, width, 5), 2, 2)
        painter.setBrush(QColor("#E2E8F0"))
        for y in (104, 135, 166):
            painter.drawRoundedRect(QRectF(224, y, 83, 5), 2, 2)

        # Floating performance summary.
        painter.setBrush(QColor("#D4E1F5"))
        painter.drawRoundedRect(QRectF(326, 115, 124, 97), 12, 12)
        painter.setBrush(QColor(CARD_SURFACE))
        painter.drawRoundedRect(QRectF(321, 110, 124, 97), 12, 12)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#64748B"))
        painter.drawRoundedRect(QRectF(335, 124, 53, 5), 2, 2)
        painter.setBrush(QColor("#F0FDF4"))
        painter.drawEllipse(QRectF(399, 121, 30, 30))
        painter.setPen(QPen(QColor(GREEN), 2.5))
        painter.drawLine(QPointF(407, 136), QPointF(412, 141))
        painter.drawLine(QPointF(412, 141), QPointF(422, 130))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#E2E8F0"))
        painter.drawRoundedRect(QRectF(335, 142, 64, 5), 2, 2)

        # Graduation cap accent.
        cap = QPolygonF([
            QPointF(39, 133), QPointF(88, 112),
            QPointF(137, 133), QPointF(88, 153),
        ])
        painter.setBrush(QColor(PRIMARY))
        painter.drawPolygon(cap)
        painter.setBrush(QColor("#1D4ED8"))
        painter.drawRoundedRect(QRectF(55, 134, 66, 23), 0, 0)
        painter.drawRect(QRectF(62, 149, 52, 5))
        painter.setPen(QPen(QColor(PRIMARY), 2))
        painter.drawLine(QPointF(128, 132), QPointF(128, 158))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#60A5FA"))
        painter.drawEllipse(QRectF(124, 156, 8, 8))

        # Smaller result card with green checkmark badge and vertical bars.
        painter.setBrush(QColor("#D4E1F5"))
        painter.drawRoundedRect(QRectF(260, 160, 100, 74), 8, 8)
        painter.setBrush(QColor(CARD_SURFACE))
        painter.drawRoundedRect(QRectF(255, 155, 100, 74), 8, 8)
        painter.setBrush(QColor("#F0FDF4"))
        painter.drawEllipse(QRectF(332, 164, 20, 20))
        painter.setPen(QPen(QColor(GREEN), 2))
        painter.drawLine(QPointF(336, 175), QPointF(341, 180))
        painter.drawLine(QPointF(341, 180), QPointF(346, 170))
        painter.setBrush(QColor("#60A5FA"))
        painter.drawRoundedRect(QRectF(272, 176, 10, 22), 3, 3)
        painter.setBrush(QColor("#93C5FD"))
        painter.drawRoundedRect(QRectF(286, 170, 10, 28), 3, 3)
        painter.setBrush(QColor("#BFDBFE"))
        painter.drawRoundedRect(QRectF(300, 164, 10, 34), 3, 3)
        event.accept()


class FocusAwareLineEdit(QLineEdit):
    focus_changed = pyqtSignal(bool)

    def focusInEvent(self, _event):
        super().focusInEvent(_event)
        self.focus_changed.emit(True)

    def focusOutEvent(self, _event):
        super().focusOutEvent(_event)
        self.focus_changed.emit(False)


_LOGIN_QSS = f"""
QWidget#loginWindow {{
    background: {BG_LEFT};
    color: {TEXT_DARK};
}}
QWidget#loginBrand {{
    background: {BG_LEFT};
}}
QWidget#loginSurface {{
    background: {BG_RIGHT};
    border-left: 1px solid {BORDER};
}}
QLabel#brandName {{
    color: {TEXT_DARK};
    font-size: 15px;
    font-weight: 700;
}}
QLabel#brandCaption {{
    color: {MUTED};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
}}
QLabel#loginHeadline {{
    color: {TEXT_DARK2};
    font-size: 34px;
    font-weight: 700;
}}
QLabel#supportingCopy {{
    color: {MUTED};
    font-size: 15px;
}}
QLabel#brandFooter {{
    color: {MUTED};
    font-size: 12px;
}}
QFrame#loginCard {{
    background: {CARD_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 16px;
}}
QLabel#cardHeading {{
    color: {TEXT_DARK2};
    font-size: 26px;
    font-weight: 700;
}}
QLabel#cardSubtitle {{
    color: {MUTED};
    font-size: 14px;
}}
QLabel#fieldLabel {{
    color: {LABEL_COLOR};
    font-size: 13px;
    font-weight: 600;
}}
QLineEdit#usernameInput {{
    background: {CARD_SURFACE};
    border: 1px solid {INPUT_BORDER};
    border-radius: 9px;
    color: {TEXT_DARK2};
    padding: 0 13px;
    min-height: 46px;
    selection-background-color: {PRIMARY};
}}
QLineEdit#usernameInput:focus {{
    border: 2px solid {PRIMARY};
}}
QLineEdit#usernameInput[invalid="true"] {{
    border: 1px solid {ERROR};
}}
QLineEdit#usernameInput::placeholder {{
    color: {MUTED};
}}
QFrame#passwordWrapper {{
    background: {CARD_SURFACE};
    border: 1px solid {INPUT_BORDER};
    border-radius: 9px;
}}
QFrame#passwordWrapper[focused="true"] {{
    border: 2px solid {PRIMARY};
}}
QFrame#passwordWrapper[invalid="true"] {{
    border: 1px solid {ERROR};
}}
QLineEdit#passwordInput {{
    background: transparent;
    border: none;
    color: {TEXT_DARK2};
    padding: 0;
    min-height: 46px;
    selection-background-color: {PRIMARY};
}}
QLineEdit#passwordInput::placeholder {{
    color: {MUTED};
}}
QPushButton#passwordToggle {{
    background: transparent;
    border: none;
    color: {PRIMARY};
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#passwordToggle:hover {{
    color: {PRIMARY_HOVER};
}}
QPushButton#passwordToggle:focus {{
    outline: none;
    color: {PRIMARY_HOVER};
}}
QPushButton#loginSubmit {{
    background: {PRIMARY};
    border: none;
    border-radius: 9px;
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 600;
    min-height: 48px;
}}
QPushButton#loginSubmit:hover {{ background: {PRIMARY_HOVER}; }}
QPushButton#loginSubmit:pressed {{ background: {PRIMARY_PRESSED}; }}
QPushButton#loginSubmit:disabled {{
    background: #94A3B8;
    color: #FFFFFF;
}}
QPushButton#registrationLink {{
    background: transparent;
    border: none;
    color: {PRIMARY};
    font-size: 13px;
    font-weight: 600;
    padding: 8px;
}}
QPushButton#registrationLink:hover {{ color: {PRIMARY_HOVER}; }}
QLabel#loginStatus {{
    color: {MUTED};
    font-size: 13px;
}}
QLabel#loginStatus[feedback="error"] {{ color: {ERROR}; }}
QLabel#loginStatus[feedback="success"] {{ color: {GREEN}; }}
QLabel#versionFooter {{
    color: {MUTED};
    font-size: 12px;
}}
"""


class LoginWindow(QWidget):
    login_successful = pyqtSignal(object)
    setup_requested = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setObjectName("loginWindow")
        self.setWindowTitle("SDG 4 Quality Education")
        self.resize(1180, 760)
        self.setMinimumSize(900, 640)
        self._processing = False
        self.main_window = None
        self.api = ApiClient()
        self.account = None
        self._worker = None
        self._authentication_available = False
        self._apply_styles()
        self._build_ui()

    def _apply_styles(self):
        self.setStyleSheet(_LOGIN_QSS)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ------------------------------------------------------------------ left panel (brand)
        brand = QWidget()
        brand.setObjectName("loginBrand")
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(52, 38, 48, 30)
        brand_layout.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(13)
        brand_row.addWidget(BrandMark())
        brand_text = QVBoxLayout()
        brand_text.setSpacing(3)
        brand_name = QLabel("Digital Examination Results\nManagement System")
        brand_name.setObjectName("brandName")
        brand_text.addWidget(brand_name)
        brand_caption = QLabel("ACADEMIC OPERATIONS")
        brand_caption.setObjectName("brandCaption")
        brand_text.addWidget(brand_caption)
        brand_row.addLayout(brand_text, 1)
        brand_layout.addLayout(brand_row)

        brand_layout.addSpacing(36)
        headline = QLabel("Manage Academic Results with Confidence.")
        headline.setObjectName("loginHeadline")
        headline.setWordWrap(True)
        brand_layout.addWidget(headline)
        brand_layout.addSpacing(15)

        description = QLabel(
            "A clear, reliable workspace for managing students, examinations, "
            "academic results, and performance reports."
        )
        description.setObjectName("supportingCopy")
        description.setWordWrap(True)
        description.setMaximumWidth(540)
        brand_layout.addWidget(description)
        brand_layout.addStretch(1)

        brand_layout.addWidget(AcademicIllustration())
        brand_layout.addStretch(1)

        brand_footer = QLabel("Supporting better decisions through clear academic data.")
        brand_footer.setObjectName("brandFooter")
        brand_footer.setWordWrap(True)
        brand_layout.addWidget(brand_footer)

        # ------------------------------------------------------------------ right panel (sign-in)
        surface = QWidget()
        surface.setObjectName("loginSurface")
        surface_layout = QVBoxLayout(surface)
        surface_layout.setContentsMargins(36, 36, 36, 28)
        surface_layout.addStretch(1)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setMinimumWidth(360)
        card.setMaximumWidth(440)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(23, 32, 51, 22))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 30, 32, 28)
        card_layout.setSpacing(0)

        welcome = QLabel("Welcome Back")
        welcome.setObjectName("cardHeading")
        card_layout.addWidget(welcome)
        card_layout.addSpacing(7)
        instruction = QLabel("Sign in to access your examination workspace.")
        instruction.setObjectName("cardSubtitle")
        instruction.setWordWrap(True)
        card_layout.addWidget(instruction)
        card_layout.addSpacing(25)

        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")
        card_layout.addWidget(username_label)
        card_layout.addSpacing(7)
        self.username = QLineEdit()
        self.username.setObjectName("usernameInput")
        self.username.setPlaceholderText("Enter your username")
        self.username.setClearButtonEnabled(True)
        self.username.setAccessibleName("Username")
        self.username.returnPressed.connect(lambda: self.password.setFocus())
        self.username.textChanged.connect(self._clear_username_error)
        card_layout.addWidget(self.username)
        card_layout.addSpacing(17)

        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        card_layout.addWidget(password_label)
        card_layout.addSpacing(7)

        self.password_wrapper = QFrame()
        self.password_wrapper.setObjectName("passwordWrapper")
        password_layout = QHBoxLayout(self.password_wrapper)
        password_layout.setContentsMargins(12, 0, 7, 0)
        password_layout.setSpacing(4)

        self.password = FocusAwareLineEdit()
        self.password.setObjectName("passwordInput")
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setAccessibleName("Password")
        self.password.returnPressed.connect(self.login)
        self.password.textChanged.connect(self._clear_password_error)
        self.password.focus_changed.connect(self._set_password_focus)
        password_layout.addWidget(self.password, 1)

        self.password_toggle = QPushButton("Show")
        self.password_toggle.setObjectName("passwordToggle")
        self.password_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.password_toggle.setAccessibleName("Show password")
        self.password_toggle.setCheckable(True)
        self.password_toggle.toggled.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.password_toggle)
        card_layout.addWidget(self.password_wrapper)
        card_layout.addSpacing(14)

        self.status = QLabel("")
        self.status.setObjectName("loginStatus")
        self.status.setMinimumHeight(20)
        self.status.setWordWrap(True)
        self.status.setProperty("feedback", "neutral")
        card_layout.addWidget(self.status)
        card_layout.addSpacing(9)

        self.login_button = QPushButton("Sign In")
        self.login_button.setObjectName("loginSubmit")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.login)
        card_layout.addWidget(self.login_button)
        card_layout.addSpacing(8)

        self.registration_button = QPushButton("First-time institution setup")
        self.registration_button.setObjectName("registrationLink")
        self.registration_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.registration_button.clicked.connect(self.open_registration)
        self.registration_button.setEnabled(False)
        card_layout.addWidget(
            self.registration_button,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )

        surface_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)
        surface_layout.addStretch(1)
        version_footer = QLabel("Digital Examination Results Management System  ·  v1.0")
        version_footer.setObjectName("versionFooter")
        version_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_footer.setWordWrap(True)
        surface_layout.addWidget(version_footer)

        root.addWidget(brand, 1)
        root.addWidget(surface, 1)

        self.login_button.setEnabled(False)
        self._set_status("Checking backend availability…")
        self._start_worker(
            self.api.status,
            self._backend_status_received,
            self._backend_status_failed,
        )

    # ------------------------------------------------------------------ backend / auth flow

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

    def _backend_status_received(self, status):
        if not status.get("authentication_configured", False):
            self._set_status(
                "The PostgreSQL backend is reachable, but authentication "
                "is not configured. Sign-in is unavailable.",
                "error",
            )
            self.login_button.setEnabled(False)
            return
        self._authentication_available = True
        self.login_button.setEnabled(True)
        self._set_status("")
        self._start_worker(
            self.api.registration_status,
            self._registration_status_received,
            self._registration_status_failed,
        )

    def _backend_status_failed(self, message):
        self._authentication_available = True
        self._set_status(str(message), "error")
        self.login_button.setEnabled(True)
        self.registration_button.setEnabled(True)

    def _registration_status_received(self, result):
        registration_open = (
            isinstance(result, dict) and result.get("registration_open") is True
        )
        self.registration_button.setVisible(registration_open)
        self.registration_button.setEnabled(registration_open)

    def _registration_status_failed(self, _message):
        self.registration_button.setVisible(True)
        self.registration_button.setEnabled(True)

    def open_registration(self):
        if self._processing:
            return
        dialog = RegistrationWindow(self.api, self)
        dialog.registration_succeeded.connect(self._registration_completed)
        if dialog.exec():
            self.username.setFocus()
        self.setup_requested.emit(self.api)

    def _registration_completed(self):
        self.registration_button.setVisible(False)
        self._set_status(
            "Institution administrator created. Sign in with the new account.",
            "success",
        )

    def _set_status(self, message, feedback="neutral"):
        self.status.setText(message)
        self.status.setProperty("feedback", feedback)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def _set_invalid(self, widget, invalid):
        widget.setProperty("invalid", "true" if invalid else "false")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _clear_username_error(self):
        if self.username.property("invalid") == "true":
            self._set_invalid(self.username, False)
            self._set_status("")

    def _clear_password_error(self):
        if self.password_wrapper.property("invalid") == "true":
            self._set_invalid(self.password_wrapper, False)
            self._set_status("")

    def _set_password_focus(self, focused):
        self.password_wrapper.setProperty("focused", "true" if focused else "false")
        self.password_wrapper.style().unpolish(self.password_wrapper)
        self.password_wrapper.style().polish(self.password_wrapper)

    def _toggle_password_visibility(self, visible):
        self.password.setEchoMode(
            QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        )
        self.password_toggle.setText("Hide" if visible else "Show")
        self.password_toggle.setAccessibleName(
            "Hide password" if visible else "Show password"
        )

    def login(self):
        if self._processing:
            return
        if not self._authentication_available:
            self._set_status(
                "The backend does not have authentication available.",
                "error",
            )
            return

        username = self.username.text().strip()
        password = self.password.text()
        missing_username = not username
        missing_password = not password
        self._set_invalid(self.username, missing_username)
        self._set_invalid(self.password_wrapper, missing_password)

        if missing_username or missing_password:
            self._set_status("Enter both username and password.", "error")
            (self.username if missing_username else self.password).setFocus()
            return

        self._processing = True
        self.login_button.setEnabled(False)
        self.login_button.setText("Signing in…")
        self.username.setEnabled(False)
        self.password.setEnabled(False)
        self.password_toggle.setEnabled(False)
        self._set_status("Checking your sign-in details…")
        username = self.username.text().strip()
        password = self.password.text()
        self._start_worker(
            lambda: self._authenticate_and_load(username, password),
            self._login_succeeded,
            self._login_failed,
        )

    def _authenticate_and_load(self, username, password):
        account = self.api.login(username, password)
        state = AppState(
            username=account["username"],
            api_client=self.api,
            account=account,
        )
        return account, state

    def _login_succeeded(self, result):
        self.account, state = result
        self._set_status("Sign-in successful. Opening your workspace…", "success")
        self.password.clear()
        from gui.windows.main_window import MainWindow

        self.main_window = MainWindow(state)
        self.main_window.show()
        self.close()
        self.login_successful.emit(state)

    def _login_failed(self, message):
        self._set_status(str(message), "error")
        self._processing = False
        self.login_button.setEnabled(True)
        self.login_button.setText("Sign In")
        self.username.setEnabled(True)
        self.password.setEnabled(True)
        self.password_toggle.setEnabled(True)
        self._set_invalid(self.username, True)
        self._set_invalid(self.password_wrapper, True)
        self.password.selectAll()
        self.password.setFocus()
