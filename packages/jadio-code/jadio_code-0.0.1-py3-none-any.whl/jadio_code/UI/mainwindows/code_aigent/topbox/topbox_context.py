from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class TopboxContext(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("Long Context Panel")
        layout.addWidget(label)
        self.setLayout(layout)
