from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from .topbox_modelsettings import TopboxModelSettings
from .topbox_lan import TopboxLan
from .topbox_tools import TopboxTools
from .topbox_context import TopboxContext


class TopBox(QWidget):
    """
    The TopBox with emoji buttons and proper width
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Overall vertical layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # -------------------------------
        # 1️⃣ Button bar (tab selector) with emojis
        # -------------------------------
        button_bar = QHBoxLayout()
        button_bar.setContentsMargins(4, 4, 4, 4)
        button_bar.setSpacing(4)

        self.buttons = []

        # Emoji buttons instead of text
        sections = [
            ("🤖", 0),  # AI Model Settings
            ("🌐", 1),  # LAN Settings  
            ("🔧", 2),  # Tools
            ("📄", 3)   # Context
        ]

        for emoji, index in sections:
            btn = QPushButton(emoji)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 16px;
                    min-width: 40px;
                    max-width: 50px;
                }
                QPushButton:checked {
                    background-color: #007acc;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QPushButton:checked:hover {
                    background-color: #1177bb;
                }
            """)
            btn.clicked.connect(lambda checked, i=index: self.show_panel(i))
            button_bar.addWidget(btn)
            self.buttons.append(btn)

        # Don't stretch - keep buttons compact
        button_bar.addStretch()

        # -------------------------------
        # 2️⃣ Stacked widget for panels
        # -------------------------------
        self.stack = QStackedWidget()
        self.stack.addWidget(TopboxModelSettings())
        self.stack.addWidget(TopboxLan())
        self.stack.addWidget(TopboxTools())
        self.stack.addWidget(TopboxContext())

        # Default selection
        self.buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)

        # Add to main layout
        layout.addLayout(button_bar)
        layout.addWidget(self.stack)

        self.setLayout(layout)

    def show_panel(self, index):
        # Update stacked widget
        self.stack.setCurrentIndex(index)
        # Update button states
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)