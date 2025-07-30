from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class BottomBoxChat(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("BottomBox Chat View")
        layout.addWidget(label)
        self.setLayout(layout)
