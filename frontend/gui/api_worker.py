import logging

from PyQt6.QtCore import QThread, pyqtSignal

from api_client import ApiError


logger = logging.getLogger(__name__)


class ApiWorker(QThread):
    succeeded = pyqtSignal(object)
    failed = pyqtSignal(object)

    def __init__(self, operation, parent=None):
        super().__init__(parent)
        self.operation = operation

    def run(self):
        try:
            result = self.operation()
        except ApiError as error:
            self.failed.emit(error)
        except Exception:
            logger.exception("Unexpected backend request failure.")
            self.failed.emit("The backend request failed unexpectedly.")
        else:
            self.succeeded.emit(result)
