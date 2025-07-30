from PyQt6.QtWidgets import QPlainTextEdit

class TerminalWindow(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Placeholder initial text
        self.setPlainText(
            "Welcome to JADIO Terminal\n\n> _"
        )

        # Disable line wrap for real terminal feel
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        # Later you can hook this up to read/write subprocess output
