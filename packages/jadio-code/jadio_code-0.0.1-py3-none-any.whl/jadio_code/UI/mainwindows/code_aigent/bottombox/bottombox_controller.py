from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import Qt

class BottomBox(QWidget):
    """
    BottomBox with cohesive dark theme styling
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make it taller for the large input area
        self.setMinimumHeight(200)
        self.setMaximumHeight(300)
        
        # Cohesive styling
        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
            }
        """)
        
        # Main vertical layout
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ==============================================
        # TOP: Mini Terminal / Current Context Strip
        # ==============================================
        self.mini_terminal = QLabel("Mini Terminal / Current Context")
        self.mini_terminal.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #cccccc;
                padding: 8px 12px;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        self.mini_terminal.setFixedHeight(32)
        layout.addWidget(self.mini_terminal)

        # ==============================================
        # MAIN: Large Input Area with Right Side Buttons
        # ==============================================
        input_main = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        # LARGE TEXT INPUT AREA (takes most space)
        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("Start typing here.....")
        self.input_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                font-size: 14px;
                padding: 12px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        self.input_area.setMinimumHeight(120)

        # RIGHT SIDE: Vertical buttons + Send
        right_side = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        # Small vertical buttons (stacked)
        self.expand_button = QPushButton("↗\nExpand\nTerminal")
        self.expand_button.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                font-size: 9px;
                text-align: center;
                padding: 4px;
                min-width: 60px;
                max-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #007acc;
            }
        """)
        self.expand_button.setFixedHeight(50)

        self.model_button = QPushButton("🔄\nChange\nModel")
        self.model_button.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                font-size: 9px;
                text-align: center;
                padding: 4px;
                min-width: 60px;
                max-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #007acc;
            }
        """)
        self.model_button.setFixedHeight(50)

        # Add some stretch space
        right_layout.addWidget(self.expand_button)
        right_layout.addWidget(self.model_button)
        right_layout.addStretch()

        # SEND BUTTON (bigger, at bottom right)
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: 60px;
                max-width: 80px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.send_button.setFixedHeight(40)
        right_layout.addWidget(self.send_button)

        right_side.setLayout(right_layout)
        right_side.setFixedWidth(90)

        # Add to main input layout
        input_layout.addWidget(self.input_area, stretch=1)  # Text area takes most space
        input_layout.addWidget(right_side)  # Right buttons fixed width

        input_main.setLayout(input_layout)
        layout.addWidget(input_main, stretch=1)

        self.setLayout(layout)

        # Connect signals
        self.send_button.clicked.connect(self.handle_send)
        self.expand_button.clicked.connect(self.handle_expand_terminal)
        self.model_button.clicked.connect(self.handle_model_swap)

    def handle_send(self):
        text = self.input_area.toPlainText().strip()
        if text:
            print(f"Sending: {text}")
            self.input_area.clear()

    def handle_expand_terminal(self):
        print("Expand Terminal clicked - should shrink chat window")

    def handle_model_swap(self):
        print("Change Model clicked - should open model selection")