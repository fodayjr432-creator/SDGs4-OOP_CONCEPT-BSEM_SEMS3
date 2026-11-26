from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem


class AuditLogsPage(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Audit Logs"))
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_btn)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Username", "Role", "Event", "Action", "Status", "IP"])
        layout.addWidget(self.table)

    def refresh(self):
        try:
            data = self.state.api.get("/api/audit-logs/")
            items = data.get("results", data) if isinstance(data, dict) else data
            self.table.setRowCount(0)
            for row in items or []:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(row.get("timestamp", ""))))
                self.table.setItem(r, 1, QTableWidgetItem(str(row.get("username", ""))))
                self.table.setItem(r, 2, QTableWidgetItem(str(row.get("user_role", ""))))
                self.table.setItem(r, 3, QTableWidgetItem(str(row.get("event_type", ""))))
                self.table.setItem(r, 4, QTableWidgetItem(str(row.get("action", ""))))
                self.table.setItem(r, 5, QTableWidgetItem(str(row.get("success", ""))))
                self.table.setItem(r, 6, QTableWidgetItem(str(row.get("ip_address", ""))))
        except Exception as exc:
            self.table.setRowCount(0)
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem(str(exc)))
