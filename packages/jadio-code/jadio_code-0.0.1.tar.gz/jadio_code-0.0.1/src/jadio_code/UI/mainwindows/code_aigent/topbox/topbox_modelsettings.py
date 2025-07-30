from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class TopboxModelSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("AI Model Settings Panel")
        layout.addWidget(label)
        self.setLayout(layout)
