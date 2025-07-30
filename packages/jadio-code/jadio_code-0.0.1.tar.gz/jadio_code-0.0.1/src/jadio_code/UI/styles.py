"""
JADIO CODE - Centralized Style System
Black, White, and Grey Professional Theme
"""

class Styles:
    """
    Centralized styling for JADIO CODE IDE
    Professional black, white, grey theme
    """
    
    # ========================================
    # COLOR PALETTE
    # ========================================
    COLORS = {
        # Backgrounds
        'bg_primary': '#0a0a0a',      # Deep black - main backgrounds
        'bg_secondary': '#1a1a1a',    # Dark grey - panels, sidebars
        'bg_tertiary': '#2a2a2a',     # Medium grey - hover states
        'bg_input': '#141414',        # Input backgrounds
        
        # Text
        'text_primary': '#ffffff',    # Pure white - main text
        'text_secondary': '#cccccc',  # Light grey - secondary text
        'text_muted': '#888888',      # Medium grey - muted text
        'text_disabled': '#555555',   # Dark grey - disabled text
        
        # Borders & Separators
        'border_primary': '#333333',  # Main borders
        'border_secondary': '#222222', # Subtle borders
        'border_accent': '#555555',   # Accent borders
        
        # Interactive States
        'hover': '#3a3a3a',          # Light grey hover
        'pressed': '#4a4a4a',        # Pressed state
        'selected': '#404040',       # Selected items
        'focus': '#666666',          # Focus outlines
    }

    # ========================================
    # MAIN APPLICATION STYLE
    # ========================================
    MAIN_STYLE = f"""
        QMainWindow {{
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }}
        
        QWidget {{
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
            font-size: 13px;
        }}
        
        /* SPLITTERS */
        QSplitter::handle {{
            background-color: {COLORS['border_primary']};
            width: 1px;
            height: 1px;
        }}
        QSplitter::handle:hover {{
            background-color: {COLORS['focus']};
        }}
    """

    # ========================================
    # BUTTON STYLES
    # ========================================
    BUTTON_STYLE = f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: 500;
            padding: 8px;
            min-height: 24px;
            border-radius: 2px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['hover']};
            color: {COLORS['text_primary']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['pressed']};
        }}
        QPushButton:checked {{
            background-color: {COLORS['selected']};
            color: {COLORS['text_primary']};
            border-left: 2px solid {COLORS['focus']};
        }}
        QPushButton:disabled {{
            color: {COLORS['text_disabled']};
        }}
    """

    # ========================================
    # INPUT STYLES
    # ========================================
    INPUT_STYLE = f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {COLORS['bg_input']};
            border: 1px solid {COLORS['border_primary']};
            color: {COLORS['text_primary']};
            padding: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            border-radius: 2px;
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {COLORS['focus']};
            background-color: {COLORS['bg_secondary']};
        }}
        QLineEdit::placeholder, QTextEdit::placeholder {{
            color: {COLORS['text_muted']};
        }}
    """

    # ========================================
    # TREE VIEW STYLES
    # ========================================
    TREE_STYLE = f"""
        QTreeView {{
            background-color: {COLORS['bg_secondary']};
            border: none;
            outline: none;
            color: {COLORS['text_primary']};
            font-size: 13px;
            alternate-background-color: {COLORS['bg_primary']};
        }}
        QTreeView::item {{
            padding: 6px 8px;
            border: none;
            min-height: 20px;
        }}
        QTreeView::item:hover {{
            background-color: {COLORS['hover']};
            color: {COLORS['text_primary']};
        }}
        QTreeView::item:selected {{
            background-color: {COLORS['selected']};
            color: {COLORS['text_primary']};
            border-left: 2px solid {COLORS['focus']};
        }}
    """

    # ========================================
    # SCROLLBAR STYLES
    # ========================================
    SCROLLBAR_STYLE = f"""
        /* CLEAN VERTICAL SCROLLBAR */
        QScrollBar:vertical {{
            background-color: {COLORS['bg_secondary']};
            width: 8px;
            border: none;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {COLORS['border_primary']};
            border-radius: 4px;
            min-height: 20px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {COLORS['focus']};
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
            background: none;
        }}
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        /* HIDE HORIZONTAL SCROLLBAR */
        QScrollBar:horizontal {{
            height: 0px;
            background: transparent;
        }}
    """

    # ========================================
    # MENU STYLES
    # ========================================
    MENU_STYLE = f"""
        QMenuBar {{
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
            border-bottom: 1px solid {COLORS['border_primary']};
            padding: 4px;
            font-size: 14px;
            font-weight: 500;
        }}
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            margin: 2px;
            border-radius: 2px;
        }}
        QMenuBar::item:selected {{
            background-color: {COLORS['hover']};
        }}
        QMenuBar::item:pressed {{
            background-color: {COLORS['pressed']};
        }}
        
        QMenu {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_primary']};
            border: 1px solid {COLORS['border_primary']};
            padding: 6px;
            font-size: 13px;
        }}
        QMenu::item {{
            padding: 8px 16px;
            margin: 1px;
            border-radius: 2px;
            min-width: 120px;
        }}
        QMenu::item:selected {{
            background-color: {COLORS['hover']};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {COLORS['border_primary']};
            margin: 4px 8px;
        }}
    """

    # ========================================
    # COMPONENT-SPECIFIC STYLES
    # ========================================
    
    @classmethod
    def get_complete_stylesheet(cls):
        """Get the complete stylesheet for the entire application"""
        return f"""
            {cls.MAIN_STYLE}
            {cls.BUTTON_STYLE}
            {cls.INPUT_STYLE}
            {cls.TREE_STYLE}
            {cls.SCROLLBAR_STYLE}
            {cls.MENU_STYLE}
        """
    
    @classmethod
    def get_menu_bar_style(cls):
        """Get stylesheet for menu bars (40px height)"""
        return f"""
            QWidget {{
                background-color: {cls.COLORS['bg_primary']};
                border-bottom: 1px solid {cls.COLORS['border_primary']};
                max-height: 40px;
                min-height: 40px;
            }}
            {cls.BUTTON_STYLE}
        """
    
    @classmethod
    def get_sidebar_style(cls):
        """Get stylesheet for vertical sidebars (48px width)"""
        return f"""
            QWidget {{
                background-color: {cls.COLORS['bg_primary']};
                border-right: 1px solid {cls.COLORS['border_primary']};
                max-width: 48px;
                min-width: 48px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {cls.COLORS['text_primary']};
                font-size: 18px;
                font-weight: 500;
                text-align: center;
                padding: 12px 8px;
                margin: 4px 2px;
                min-height: 40px;
                max-height: 48px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS['hover']};
            }}
            QPushButton:checked {{
                background-color: {cls.COLORS['selected']};
                border-left: 3px solid {cls.COLORS['focus']};
                border-radius: 0px 4px 4px 0px;
            }}
        """
    
    @classmethod
    def get_panel_style(cls):
        """Get stylesheet for main panels"""
        return f"""
            QWidget {{
                background-color: {cls.COLORS['bg_secondary']};
                border: 1px solid {cls.COLORS['border_secondary']};
            }}
        """