from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidgetItem

from gui.components.data_table import DataTable


class AuditLogsPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        title = QLabel("Audit Logs")
        layout.addWidget(title)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_btn)
        self.table = DataTable(["Timestamp", "Username", "Role", "Event", "Action", "Status", "IP"])
        layout.addWidget(self.table)
        self.error_label = QLabel()
        self.error_label.setObjectName("muted")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

    def refresh(self):
        try:
            data = self.state.api.get("/api/audit-logs/")
            items = data.get("results", data) if isinstance(data, dict) else data
            self.error_label.clear()
            self.table.setRowCount(0)
            for row in items or []:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(row.get("timestamp", ""))))
                self.table.setItem(r, 1, QTableWidgetItem(str(row.get("username", ""))))
                self.table.setItem(r, 2, QTableWidgetItem(str(row.get("user_role", ""))))
                self.table.setItem(r, 3, QTableWidgetItem(str(row.get("event_type", ""))))
                self.table.setItem(r, 4, QTableWidgetItem(str(row.get("action", ""))))
                success = bool(row.get("success"))
                self.table.setItem(r, 5, QTableWidgetItem("Yes" if success else "No"))
                self.table.setItem(r, 6, QTableWidgetItem(str(row.get("ip_address", ""))))
        except Exception as exc:
            self.table.setRowCount(0)
            self.error_label.setText(str(exc))
