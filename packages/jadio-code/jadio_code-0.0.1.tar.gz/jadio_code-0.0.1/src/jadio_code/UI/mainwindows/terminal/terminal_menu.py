from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from styles import Styles

class TerminalMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply centralized menu bar styles
        self.setStyleSheet(Styles.get_menu_bar_style())

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Clean emoji buttons - NO BOXES, professional styling
        buttons_config = [
            ("➕", "New Shell"),
            ("❌", "Kill Shell"), 
            ("🧹", "Clear"),
            ("🔒", "Scroll Lock"),
            ("⚡", "Split"),
            ("⚙️", "Settings")
        ]

        for emoji, tooltip in buttons_config:
            btn = QPushButton(emoji)
            btn.setToolTip(tooltip)
            layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)