from pathlib import Path
import sys
import dateparser
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QListWidget, 
                             QListWidgetItem, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class ModernSmartTodo(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ToDo Buddy Pro")
        self.resize(500, 700)

        # Main Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(25, 30, 25, 30)
        self.main_layout.setSpacing(15)

        # --- Input Section (Horizontal) ---
        self.input_container = QHBoxLayout()
        self.input_container.setSpacing(0) # Join the input and button

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Try: Finish report by Friday 5pm")
        
        self.add_button = QPushButton("ADD")
        self.add_button.setObjectName("AddBtn") # Used for specific QSS styling
        self.add_button.setCursor(Qt.PointingHandCursor)

        self.input_container.addWidget(self.input_field)
        self.input_container.addWidget(self.add_button)
        
        self.main_layout.addLayout(self.input_container)

        # --- Task List ---
        self.task_list = QListWidget()
        self.main_layout.addWidget(self.task_list)

        # --- Logic Connections ---
        # Both "Enter" and "Click" trigger the same method
        self.input_field.returnPressed.connect(self.add_task_logic)
        self.add_button.clicked.connect(self.add_task_logic)

        # Subtle Shadow for the input bar
        shadow = QGraphicsDropShadowEffect(blurRadius=10, xOffset=0, yOffset=3)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.input_field.setGraphicsEffect(shadow)

    def add_task_logic(self):
        text = self.input_field.text().strip()
        if not text:
            return

        # Smart Parsing (The Logic part)
        parsed = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
        
        info_tag = "[Today]"
        if parsed:
            # Check if user specified a time or just a date
            has_time = any(word in text.lower() for word in [':', 'am', 'pm', 'at'])
            if has_time:
                info_tag = f"[{parsed.strftime('%b %d @ %I:%M %p')}]"
            else:
                info_tag = f"[{parsed.strftime('%b %d')}]"

        # Create Item
        display_text = f"{info_tag} {text}"
        item = QListWidgetItem(display_text)
        
        # Add to list and clear
        self.task_list.insertItem(0, item)
        self.input_field.clear()

    def styleSheet(self):
        return super().styleSheet()
    
def load_stylesheet(path):
    style_file = Path(path)
    if style_file.exists():
        return style_file.read_text()
    print(f"Warning: {path} not found!")
    return ""    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Force a modern font if available
    app.setFont(QFont("Segoe UI", 10))
    style = load_stylesheet("app\\style.qss")
    app.setStyleSheet(style)

    window = ModernSmartTodo()
    window.show()
    sys.exit(app.exec())