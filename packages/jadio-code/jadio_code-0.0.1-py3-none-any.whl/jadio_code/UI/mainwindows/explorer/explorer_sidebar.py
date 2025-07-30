from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from styles import Styles

class ExplorerSidebar(QWidget):
    """
    Vertical button sidebar for Explorer - left side
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply centralized sidebar styles
        self.setStyleSheet(Styles.get_sidebar_style())

        # Fixed width like AIGent sidebar
        self.setFixedWidth(48)

        # Vertical layout for buttons
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)

        # Vertical buttons
        buttons_config = [
            ("📁", "Files"),
            ("🔍", "Search"), 
            ("🌿", "Git"),
            ("🐛", "Debug"),
            ("📦", "Extensions")
        ]

        self.buttons = []
        for icon, tooltip in buttons_config:
            btn = QPushButton(icon)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, t=tooltip: self.handle_button_click(t))
            layout.addWidget(btn)
            self.buttons.append(btn)

        # Stretch to keep them top-aligned
        layout.addStretch()

        self.setLayout(layout)

        # Default: first button selected
        if self.buttons:
            self.buttons[0].setChecked(True)

    def handle_button_click(self, button_name):
        """Handle button clicks"""
        print(f"Explorer sidebar: {button_name} clicked")
        
        # Update button states (only one can be checked)
        sender = self.sender()
        for btn in self.buttons:
            btn.setChecked(btn == sender)