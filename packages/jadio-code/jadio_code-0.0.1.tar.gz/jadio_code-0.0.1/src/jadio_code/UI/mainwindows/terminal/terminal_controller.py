from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from .terminal_menu import TerminalMenu
from .terminal_window import TerminalWindow
from .terminal_shells import TerminalShells

class TerminalController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # FUTURISTIC BLACK & RED TERMINAL STYLING
        self.setStyleSheet("""
            QWidget {
                background-color: #050505;
                color: #e0e0e0;
            }
            QSplitter::handle {
                background-color: #ff0040;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #ff3366;
                box-shadow: 0 0 6px rgba(255, 0, 64, 0.5);
            }
        """)

        # Overall vertical layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar - FIXED 40px HEIGHT
        self.menu = TerminalMenu()
        self.menu.setFixedHeight(40)
        layout.addWidget(self.menu)

        # Splitter for CLI and shell list
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #ff0040;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #ff3366;
                box-shadow: 0 0 6px rgba(255, 0, 64, 0.5);
            }
        """)

        # Terminal window (main area)
        self.window = TerminalWindow()
        self.window.setStyleSheet("""
            QWidget {
                background-color: #080808;
                border: 1px solid #333333;
            }
        """)

        # Shell list (right sidebar)
        self.shells = TerminalShells()
        self.shells.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                border-left: 1px solid #333333;
            }
        """)

        splitter.addWidget(self.window)
        splitter.addWidget(self.shells)
        splitter.setSizes([800, 200])

        layout.addWidget(splitter)
        self.setLayout(layout)