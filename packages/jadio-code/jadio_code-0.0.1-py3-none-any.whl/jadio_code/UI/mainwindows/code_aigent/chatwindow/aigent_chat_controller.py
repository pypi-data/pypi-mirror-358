from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel

class ChatWindow(QWidget):
    """
    The YELLOW section (Chat Window).
    Scrollable conversation + summaries.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Conversation will appear here...")

        # Summary
        self.summary = QLabel("Summary: [No summary yet]")
        self.summary.setStyleSheet("background-color: #222; color: #ccc; padding: 4px;")

        layout.addWidget(self.chat_history, stretch=1)
        layout.addWidget(self.summary)

        self.setLayout(layout)
