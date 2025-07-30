from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class BottomBoxContext(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("BottomBox Context View")
        layout.addWidget(label)
        self.setLayout(layout)
