from pathlib import Path
import sys
import re
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
        
        # find date info if exists
        date_info = None
        time_info = None

        # Look for date keywords in the full text
        date_match = re.search(r'\b(today|tomorrow|next\s+\w+|in\s+\d+\s+\w+|by\s+\w+)\b', text, re.IGNORECASE)
        
        # Matches "at 5", "at 5:30", "5pm", but ignores random digits without "at" or "am/pm"
        time_match = re.search(r'\b(?:at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?|\d{1,2}(?::\d{2})?\s*(?:am|pm))\b', text, re.IGNORECASE)
        
        if time_match:
            time_str = time_match.group(0)
            parsed_time = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})
            if parsed_time:
                time_info = parsed_time.strftime('%I:%M %p') # E.g., 05:00 PM
            
            # Remove the extracted time string from the text and clean up spaces
            text = text.replace(time_str, "").strip()
            text = re.sub(r'\s+', ' ', text)

        if date_match:
            date_str = date_match.group(0)
            parsed_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})
            if parsed_date:
                date_info = parsed_date.strftime('%b %d, %Y')
            
            # Remove the extracted date string from the text and clean up spaces
            text = text.replace(date_str, "").strip()
            text = re.sub(r'\s+', ' ', text)
        
        # Capitalize the first letter for a cleaner look
        formatedText = text[0].upper() + text[1:] if text else ""

        # Safely format the tag based on whether date, time, or both were provided
        tags = [info for info in (date_info, time_info) if info]
        info_tag = f"[{' | '.join(tags)}] " if tags else ""
        
        # Create Item
        display_text = f"{info_tag}{formatedText}"
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