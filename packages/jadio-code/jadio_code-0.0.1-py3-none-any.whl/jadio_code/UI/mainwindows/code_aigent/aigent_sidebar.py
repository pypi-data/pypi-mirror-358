from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from styles import Styles


class AigentSidebar(QWidget):
    """
    VS Code Activity Bar style sidebar - vertical buttons on far right
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply centralized sidebar styles
        self.setStyleSheet(Styles.get_sidebar_style())

        # Fixed width like VS Code activity bar
        self.setFixedWidth(48)

        # Vertical layout for buttons
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        # AIGent activity buttons
        buttons_config = [
            ("🔍", "Search"),
            ("🤖", "AI Chat"),
            ("⚙️", "Settings"),
            ("🔌", "Plugins"),
            ("📊", "Analytics")
        ]

        self.buttons = []
        for icon, tooltip in buttons_config:
            btn = QPushButton(icon)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, t=tooltip: self.handle_button_click(t))
            layout.addWidget(btn)
            self.buttons.append(btn)

        # Stretch to push buttons to top
        layout.addStretch()

        self.setLayout(layout)

        # Default: first button selected
        if self.buttons:
            self.buttons[0].setChecked(True)

    def handle_button_click(self, button_name):
        """Handle button clicks - switch AIGent modes"""
        print(f"AIGent mode switched to: {button_name}")
        
        # Update button states (only one can be checked)
        sender = self.sender()
        for btn in self.buttons:
            btn.setChecked(btn == sender)