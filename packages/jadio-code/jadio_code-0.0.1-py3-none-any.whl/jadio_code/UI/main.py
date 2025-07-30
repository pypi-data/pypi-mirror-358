import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt

# Add the current directory to Python path to fix imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# IMPORT YOUR MODULES
from mainwindows.explorer.explorer_controller import ExplorerController
from mainwindows.editor.editor_controller import EditorController
from mainwindows.terminal.terminal_controller import TerminalController
from mainwindows.code_aigent.aigent_controller import AigentController
from menubar import MenuBar
from styles import Styles

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JADIO CODE")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 700)

        # Apply centralized styles
        self.setStyleSheet(Styles.get_complete_stylesheet())

        # Set the menu bar
        self.setMenuBar(MenuBar(self))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # ================================================
        # LEFT SIDE: Main Content Area
        # ================================================
        left_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Explorer (narrow sidebar)
        explorer = ExplorerController()
        explorer.setMinimumWidth(200)
        explorer.setMaximumWidth(400)
        left_splitter.addWidget(explorer)

        # 2. Editor + Terminal Area (main content)
        editor_terminal_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Editor (STRETCHES VERTICALLY)
        editor = EditorController()
        editor_terminal_splitter.addWidget(editor)
        
        # Terminal (fixed height)
        terminal = TerminalController()
        terminal.setMinimumHeight(150)
        terminal.setMaximumHeight(300)
        editor_terminal_splitter.addWidget(terminal)
        
        # Set proportions: Editor gets most space, Terminal fixed
        editor_terminal_splitter.setSizes([700, 200])
        editor_terminal_splitter.setStretchFactor(0, 1)  # Editor stretches
        editor_terminal_splitter.setStretchFactor(1, 0)  # Terminal fixed
        
        left_splitter.addWidget(editor_terminal_splitter)
        
        # Set Explorer vs Editor+Terminal proportions
        left_splitter.setSizes([250, 900])
        left_splitter.setStretchFactor(0, 0)  # Explorer fixed
        left_splitter.setStretchFactor(1, 1)  # Editor area stretches

        # ================================================
        # RIGHT SIDE: AIGent Panel (STRETCHES)
        # ================================================
        aigent_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # AIGent Panel (can stretch)
        agent_panel = AigentController()
        agent_panel.setMinimumWidth(300)
        
        # Add both to the horizontal splitter
        aigent_splitter.addWidget(left_splitter)
        aigent_splitter.addWidget(agent_panel)
        
        # Set proportions: Main content 70%, AIGent 30%
        aigent_splitter.setSizes([1000, 400])
        aigent_splitter.setStretchFactor(0, 1)  # Main content stretches
        aigent_splitter.setStretchFactor(1, 1)  # AIGent ALSO stretches

        # Add to main layout
        main_layout.addWidget(aigent_splitter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())