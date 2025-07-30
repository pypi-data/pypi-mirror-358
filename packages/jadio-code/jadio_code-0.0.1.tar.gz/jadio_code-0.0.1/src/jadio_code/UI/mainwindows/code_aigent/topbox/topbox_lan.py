from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class TopboxLan(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("LAN Settings Panel")
        layout.addWidget(label)
        self.setLayout(layout)
