from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class TerminalShells(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        # Example hard-coded shell list for now
        layout.addWidget(QPushButton("Shell 1"))
        layout.addWidget(QPushButton("Shell 2"))
        layout.addWidget(QPushButton("Shell 3"))

        layout.addStretch()

        self.setLayout(layout)
