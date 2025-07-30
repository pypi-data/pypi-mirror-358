from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class TopboxTools(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("AI Tool Set Panel")
        layout.addWidget(label)
        self.setLayout(layout)
