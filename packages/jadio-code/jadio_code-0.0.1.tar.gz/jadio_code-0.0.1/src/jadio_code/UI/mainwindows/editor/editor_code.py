from PyQt6.QtWidgets import QPlainTextEdit

class EditorCode(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Example placeholder text
        self.setPlainText("# Welcome to JADIO CODE Editor\n\nStart coding here...")

        # Monospaced font can be added later
        # self.setFont(QFont("Courier New", 10))

        # Enable line wrap / off
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
