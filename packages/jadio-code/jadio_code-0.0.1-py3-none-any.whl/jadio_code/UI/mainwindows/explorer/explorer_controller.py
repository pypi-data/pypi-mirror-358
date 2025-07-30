import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTreeView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QModelIndex, Qt
from .explorer_sidebar import ExplorerSidebar
from .explorer_menu import ExplorerMenu
from styles import Styles

class ExplorerController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main horizontal layout: sidebar + content
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # LEFT: Vertical button sidebar
        self.sidebar = ExplorerSidebar()
        main_layout.addWidget(self.sidebar)

        # RIGHT: Menu + Explorer
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # TOP: Horizontal menu
        self.menu = ExplorerMenu()
        content_layout.addWidget(self.menu)

        # BOTTOM: File tree with centralized styles
        self.file_tree = QTreeView()
        # Apply centralized tree and scrollbar styles
        self.file_tree.setStyleSheet(f"""
            {Styles.TREE_STYLE}
            {Styles.SCROLLBAR_STYLE}
        """)

        # File system model
        self.model = QFileSystemModel()
        self.model.setRootPath(os.path.expanduser("~"))
        self.file_tree.setModel(self.model)
        self.file_tree.setRootIndex(self.model.index(os.path.expanduser("~")))
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setAnimated(True)
        self.file_tree.setIndentation(16)
        self.file_tree.setSortingEnabled(True)
        
        # DISABLE HORIZONTAL SCROLLBAR - only show filenames
        self.file_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.file_tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Hide all columns except the first (Name column)
        for i in range(1, self.model.columnCount()):
            self.file_tree.hideColumn(i)

        content_layout.addWidget(self.file_tree, stretch=1)
        content.setLayout(content_layout)
        main_layout.addWidget(content, stretch=1)

        self.setLayout(main_layout)