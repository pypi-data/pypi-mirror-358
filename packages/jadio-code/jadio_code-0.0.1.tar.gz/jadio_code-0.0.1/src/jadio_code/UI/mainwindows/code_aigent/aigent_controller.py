from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit
from .aigent_menu import AigentMenu
from .topbox.topbox_controller import TopBox
from .chatwindow.aigent_chat_controller import ChatWindow
from .bottombox.bottombox_controller import BottomBox
from .aigent_sidebar import AigentSidebar


class AigentController(QWidget):
    """
    VS Code style AIGent panel - with flexible chat and expandable terminal
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set background color to distinguish the panel
        self.setStyleSheet("""
            AigentController {
                background-color: #1e1e1e;
                border-left: 1px solid #333;
            }
        """)

        # Track terminal state
        self.terminal_expanded = False

        # Main horizontal layout: Content + Sidebar
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =============================================
        # LEFT: Main AIGent Content Area
        # =============================================
        content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # 1. AIGent Menu (top bar) - Fixed height
        self.menu = AigentMenu()
        self.menu.setFixedHeight(40)
        self.content_layout.addWidget(self.menu)

        # 2. TopBox (compact) - Fixed height  
        self.topbox = TopBox()
        self.topbox.setFixedHeight(120)
        self.content_layout.addWidget(self.topbox)

        # 3. ChatWindow (FLEXIBLE) - Gets remaining space
        self.chatwindow = ChatWindow()
        self.content_layout.addWidget(self.chatwindow, stretch=1)  # FLEXIBLE!

        # 4. Expandable Terminal (hidden by default)
        self.expanded_terminal = QTextEdit()
        self.expanded_terminal.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)
        self.expanded_terminal.setPlaceholderText("Expanded AIGent Terminal...")
        self.expanded_terminal.hide()  # Hidden by default
        self.content_layout.addWidget(self.expanded_terminal)

        # 5. BottomBox (FIXED height) - Input area
        self.bottombox = BottomBox()
        self.bottombox.setFixedHeight(200)  # Fixed height
        self.content_layout.addWidget(self.bottombox)

        content_widget.setLayout(self.content_layout)

        # =============================================
        # RIGHT: AIGent Sidebar
        # =============================================
        self.sidebar = AigentSidebar()
        self.sidebar.setFixedWidth(48)

        # Add both to main layout
        main_layout.addWidget(content_widget, stretch=1)
        main_layout.addWidget(self.sidebar)

        self.setLayout(main_layout)

        # Connect expand terminal button
        self.connect_expand_button()

    def connect_expand_button(self):
        """Connect the expand terminal button from BottomBox"""
        # We'll connect this after BottomBox is created
        if hasattr(self.bottombox, 'expand_button'):
            self.bottombox.expand_button.clicked.disconnect()  # Remove old connection
            self.bottombox.expand_button.clicked.connect(self.toggle_terminal)

    def toggle_terminal(self):
        """Toggle the expanded terminal"""
        if self.terminal_expanded:
            # Close terminal
            self.expanded_terminal.hide()
            self.expanded_terminal.setFixedHeight(0)
            self.bottombox.expand_button.setText("↗\nExpand\nTerminal")
            self.terminal_expanded = False
        else:
            # Open terminal
            self.expanded_terminal.show()
            self.expanded_terminal.setFixedHeight(250)  # 250px as requested
            self.bottombox.expand_button.setText("↙\nClose\nTerminal")
            self.terminal_expanded = True