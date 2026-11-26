from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView


class DataTable(QTableWidget):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setMinimumHeight(180)

    def populate(self, rows):
        self.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                self.setItem(row_index, column_index, item)

    def selected_row(self):
        indexes = self.selectedIndexes()
        return indexes[0].row() if indexes else -1
