from PyQt6.QtWidgets import QMenuBar, QMenu, QLineEdit, QWidgetAction
from PyQt6.QtGui import QAction

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # FUTURISTIC BLACK & RED MENUBAR STYLING
        self.setStyleSheet("""
            QMenuBar {
                background-color: #0a0a0a;
                color: #e0e0e0;
                border-bottom: 2px solid #ff0040;
                padding: 4px;
                font-size: 14px;
                font-weight: 500;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                margin: 2px;
                border-radius: 2px;
            }
            QMenuBar::item:selected {
                background-color: rgba(255, 0, 64, 0.15);
                color: #ff3366;
            }
            QMenuBar::item:pressed {
                background-color: rgba(255, 0, 64, 0.25);
                color: #ff6680;
            }
            
            QMenu {
                background-color: #111111;
                color: #e0e0e0;
                border: 1px solid #ff0040;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 16px;
                margin: 1px;
                border-radius: 2px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 0, 64, 0.2);
                color: #ff3366;
            }
            QMenu::separator {
                height: 1px;
                background-color: #333333;
                margin: 4px 8px;
            }
            
            QLineEdit {
                background-color: #121212;
                border: 1px solid #333333;
                color: #e0e0e0;
                padding: 6px 12px;
                border-radius: 3px;
                min-width: 200px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #ff0040;
                background-color: #1a1a1a;
                box-shadow: 0 0 6px rgba(255, 0, 64, 0.3);
            }
            QLineEdit::placeholder {
                color: #777777;
            }
        """)

        # Professional menu structure
        top_menus = [
            "File", "Edit", "Selection", "LAN", "LLM",
            "JADIONET", "Code Doctor", "Plugins", "Settings", "Help"
        ]

        for menu_name in top_menus:
            menu = QMenu(menu_name, self)
            # Add professional menu items with separators
            for i in range(1, 11):
                action = QAction(f"{menu_name} Option {i}", self)
                action.triggered.connect(lambda checked, name=menu_name, idx=i: print(f"Selected: {name} Option {idx}"))
                menu.addAction(action)
                
                # Add separators for better organization
                if i == 3 or i == 7:
                    menu.addSeparator()
                    
            self.addMenu(menu)

        # Professional search box on the far right
        search_action = QWidgetAction(self)
        search_field = QLineEdit()
        search_field.setPlaceholderText("Search commands...")
        search_action.setDefaultWidget(search_field)
        self.addAction(search_action)