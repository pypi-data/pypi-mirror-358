from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from styles import Styles

class EditorTopMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply centralized menu bar styles
        self.setStyleSheet(Styles.get_menu_bar_style())

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Emoji buttons instead of text
        buttons_config = [
            ("❌", "Close Tab"),
            ("⚡", "Split View"),
            ("▶️", "Run"),
            ("✨", "Format")
        ]

        for emoji, tooltip in buttons_config:
            btn = QPushButton(emoji)
            btn.setToolTip(tooltip)
            layout.addWidget(btn)

        # Stretch to fill right side
        layout.addStretch()
        self.setLayout(layout)