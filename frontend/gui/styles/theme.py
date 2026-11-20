THEME_QSS = """
* {
    font-family: "Segoe UI";
    color: #172033;
    font-size: 14px;
}
QWidget#root {
    background: #F5F7FB;
}
QMainWindow {
    background: #F5F7FB;
}
QLabel#pageTitle {
    font-size: 22px;
    font-weight: 700;
    color: #172033;
}
QLabel#muted {
    color: #64748B;
}
QPushButton {
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}
QPushButton:hover { background: #1D4ED8; }
QPushButton:pressed { background: #1E40AF; }
QPushButton#secondary {
    background: #F5F7FB;
    color: #172033;
    border: 1px solid #E5EAF2;
}
QPushButton#danger {
    background: #DC2626;
    color: white;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {
    background: white;
    border: 1px solid #E5EAF2;
    border-radius: 8px;
    padding: 8px;
    color: #172033;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 2px solid #2563EB;
}
QFrame#card {
    background: white;
    border: 1px solid #E5EAF2;
    border-radius: 12px;
}
QTableWidget {
    background: white;
    border: 1px solid #E5EAF2;
    border-radius: 8px;
    gridline-color: #E5EAF2;
}
QHeaderView::section {
    background: #F5F7FB;
    border: none;
    border-bottom: 1px solid #E5EAF2;
    padding: 9px;
    font-weight: 700;
    color: #64748B;
}
QTableWidget::item { padding: 7px; }
QTableWidget::item:selected { background: #DBEAFE; color: #1E3A8A; }
"""
