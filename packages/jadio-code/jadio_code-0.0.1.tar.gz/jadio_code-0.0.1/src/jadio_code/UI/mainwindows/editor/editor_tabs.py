from PyQt6.QtWidgets import QTabBar

class EditorTabs(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initial tab for demonstration
        self.addTab("Welcome")
        self.addTab("Untitled 1")

        # Set movable tabs
        self.setMovable(True)

        # Close buttons on tabs
        self.setTabsClosable(True)

        # Signals can be connected later in controller
