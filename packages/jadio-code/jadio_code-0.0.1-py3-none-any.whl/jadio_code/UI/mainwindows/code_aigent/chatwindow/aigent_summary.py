from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class AigentSummary(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("Summary of Chat or Context here.")
        layout.addWidget(label)
        self.setLayout(layout)
