from PyQt6.QtWidgets import QWidget, QVBoxLayout
from .editor_topmenu import EditorTopMenu
from .editor_tabs import EditorTabs
from .editor_code import EditorCode

class EditorController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout manager for the whole editor
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Top menu bar FIRST (above tabs)
        self.topmenu = EditorTopMenu()
        layout.addWidget(self.topmenu)

        # 2. Tabs SECOND (below menu)
        self.tabs = EditorTabs()
        layout.addWidget(self.tabs)

        # 3. Actual code editing area
        self.code_area = EditorCode()
        layout.addWidget(self.code_area, stretch=1)  # Fills most space

        # Apply layout
        self.setLayout(layout)