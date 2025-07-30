from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class BottomBoxTerminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        terminal = QTextEdit()
        terminal.setReadOnly(True)
        terminal.setPlaceholderText("Terminal output will appear here...")
        layout.addWidget(terminal)
        self.setLayout(layout)
