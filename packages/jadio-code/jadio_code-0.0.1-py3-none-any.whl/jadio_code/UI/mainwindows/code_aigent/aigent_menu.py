from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from styles import Styles

class AigentMenu(QWidget):
    """
    Collapsible AIGent menu - starts collapsed, expands to show all buttons
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set fixed height and apply centralized styles
        self.setFixedHeight(40)
        self.setStyleSheet(Styles.get_menu_bar_style())

        # Initially collapsed state
        self.expanded = False
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        self.create_collapsed_layout(layout)
        self.setLayout(layout)

    def create_collapsed_layout(self, layout):
        """Create the collapsed state with just the main toggle button"""
        self.clear_layout(layout)
        
        # Main toggle button
        self.toggle_button = QPushButton("🤖 ▼")
        self.toggle_button.clicked.connect(self.toggle_menu)
        layout.addWidget(self.toggle_button)
        layout.addStretch()

    def create_expanded_layout(self, layout):
        """Create the expanded state with all AIGent buttons"""
        self.clear_layout(layout)

        # Toggle button (now shows up arrow)
        self.toggle_button = QPushButton("🤖 ▲")
        self.toggle_button.clicked.connect(self.toggle_menu)
        layout.addWidget(self.toggle_button)

        # All the AIGent action buttons
        buttons_config = [
            ("🔄", self.handle_refresh),
            ("💬", self.handle_new_chat),
            ("📚", self.handle_old_chats),
            ("⚙️", self.handle_settings),
            ("❓", self.handle_help)
        ]

        for label, handler in buttons_config:
            btn = QPushButton(label)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        layout.addStretch()

    def toggle_menu(self):
        """Toggle between collapsed and expanded states"""
        self.expanded = not self.expanded
        layout = self.layout()
        
        if self.expanded:
            self.create_expanded_layout(layout)
        else:
            self.create_collapsed_layout(layout)

    def clear_layout(self, layout):
        """Clear all widgets from layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # Button handlers
    def handle_refresh(self):
        print("Refresh button clicked.")

    def handle_new_chat(self):
        print("New Chat button clicked.")

    def handle_old_chats(self):
        print("Old Chats button clicked.")

    def handle_settings(self):
        print("Settings button clicked.")

    def handle_help(self):
        print("Help button clicked.")