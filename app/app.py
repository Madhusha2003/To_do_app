from pathlib import Path
import sys
import re
import requests
import dateparser
from utils import DateTimeExtractor
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QSplashScreen, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QListWidget, 
                             QListWidgetItem, QGraphicsDropShadowEffect, QDialog, QRadioButton, QButtonGroup, QFormLayout, QComboBox, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont

# CATEGORIES
categories = {"GROCERY", "PERSONAL", "WORK", "HEALTH", "TRAVEL", "SHOPPING", "FINANCE", "STUDY", "REMINDER"}

class AILoaderThread(QThread):
    # Signals to send messages and the actual models back to the main app
    progress_update = Signal(str)
    loading_finished = Signal(object)  # (task_classifier)

    def run(self):
        # 1. Load Logistic Regression Categorizer
        self.progress_update.emit("Loading Logistic Brain...")
        from categorizer import task_classifier
        
        # 2. Finish
        self.progress_update.emit("All systems ready!")
        self.loading_finished.emit(task_classifier)

# import custom widgets
from task_card import TaskCard
from data_manager import load_ai_config, save_ai_config
from ai_service import AIService, build_prompt
from ai_settings_window import AIPanelDialog
from nova_window import NovaResponseDialog


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
        self.main_layout.setSpacing(10)

        # --- Task List ---
        self.task_list_label = QLabel("Your Tasks")
        self.task_list_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        self.task_list = QListWidget()
        self.task_list.setSpacing(10) # Space between tasks
        self.main_layout.addWidget(self.task_list_label)
        self.main_layout.addWidget(self.task_list, stretch=1)

        # --- Input Section (Horizontal) ---
        self.input_container = QHBoxLayout()
        self.input_container.setContentsMargins(0, 0, 0, 0)
        self.input_container.setSpacing(0) # Join the input and button

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Try: Finish report by Friday 5pm")
        
        self.add_button = QPushButton("ADD")
        self.add_button.setObjectName("AddBtn") # Used for specific QSS styling
        self.add_button.setCursor(Qt.PointingHandCursor)

        self.input_container.addWidget(self.input_field)
        self.input_container.addWidget(self.add_button)
        
        self.main_layout.addLayout(self.input_container)

        # --- Assistant Section ---
        self.assistant_layout = QHBoxLayout()
        self.assistant_layout.setContentsMargins(0, 0, 0, 0)
        self.assistant_layout.setSpacing(10)
        
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Ask Nova about your tasks...")
        
        self.ask_nova_btn = QPushButton("✨ Ask")
        self.ask_nova_btn.setCursor(Qt.PointingHandCursor)
        self.ask_nova_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                border-radius: 15px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a29bfe;
            }
        """)

        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setToolTip("AI Settings")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 20px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
        """)
        
        self.assistant_layout.addWidget(self.ai_input, stretch=1)
        self.assistant_layout.addWidget(self.ask_nova_btn)
        self.assistant_layout.addWidget(self.settings_btn)
        self.main_layout.addLayout(self.assistant_layout)

        # --- Logic Connections ---
        self.input_field.returnPressed.connect(self.add_task_logic)
        self.add_button.clicked.connect(self.add_task_logic)
        self.ai_input.returnPressed.connect(self.ask_nova)
        self.ask_nova_btn.clicked.connect(self.ask_nova)
        self.settings_btn.clicked.connect(self.open_settings)

        # Subtle Shadow for the input bar
        shadow = QGraphicsDropShadowEffect(blurRadius=10, xOffset=0, yOffset=3)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.input_field.setGraphicsEffect(shadow)

    def open_settings(self):
        dialog = AIPanelDialog(self)
        dialog.exec()

    def ask_nova(self):
        user_prompt = self.ai_input.text().strip()
        if not user_prompt:
            user_prompt = "Tell me what to do today and why in a short, encouraging message."
            
        from data_manager import load_ai_config
        config = load_ai_config()
        
        # Read current tasks from the UI
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            card = self.task_list.itemWidget(item)
            if card and hasattr(card, "to_dict"):
                tasks.append(card.to_dict())
                
        prompt = build_prompt(tasks, user_prompt)
        service = AIService(config)
        
        # Simple synchronous call for now as requested
        self.statusBar().showMessage("Nova is thinking...")
        QApplication.processEvents() # Force UI update
        
        response = service.ask(prompt)
        
        self.statusBar().showMessage("AI Engine: Online | ToDo version 1.0")
        
        # Display the response in the new Nova window
        dialog = NovaResponseDialog(self, response_text=response)
        dialog.exec()
        
        self.ai_input.clear()

    def add_task_logic(self):
        text = self.input_field.text().strip()
        if not text:
            return
        
        # find category info if classifier exists
        category = "PERSONAL"
        if hasattr(self, "task_classifier"):
            category = self.text_category_classifier() or "PERSONAL"

        # Extract date and time information using utility function
        text, date_info, time_info = DateTimeExtractor.extract(text)
        
        # Capitalize the first letter for a cleaner look
        formatedText = text[0].upper() + text[1:] if text else ""

        # Safely format the tag based on whether date, time, or both were provided
        tags = [info for info in (date_info, time_info) if info]
        info_tag = f"[{' | '.join(tags)}] " if tags else ""

        # Create TaskCard
        self.card = TaskCard(formatedText, category, date_info, time_info)
        self.card.deleted.connect(self.delete_task) # Connect delete signal
        self.item = QListWidgetItem()
        self.item.setSizeHint(self.card.sizeHint())
        self.task_list.insertItem(0, self.item)
        self.task_list.setItemWidget(self.item, self.card)
        self.input_field.clear()
        self.card.list_item = self.item 
        self.save_current_tasks() # Auto-save
        
    def delete_task(self, card):
        # Find item in list
        row = self.task_list.row(card.list_item)
        if row != -1:
            self.task_list.takeItem(row)
            self.save_current_tasks() # Auto-save
            
    def save_current_tasks(self):
        try:
            from data_manager import save_tasks
            tasks_data = []
            for i in range(self.task_list.count()):
                item = self.task_list.item(i)
                card = self.task_list.itemWidget(item)
                if card and hasattr(card, "to_dict"):
                    tasks_data.append(card.to_dict())
            save_tasks(tasks_data)
        except Exception as e:
            print(f"Failed to save tasks: {e}")
        
    def text_category_classifier(self):
        text = self.input_field.text().strip()
        lower_text = text.lower()
        category = self.task_classifier.classify(lower_text) or "PERSONAL"
        if category.upper() in categories:
            print("Found category from classifier", category)
            return category.upper()
        else:
            return "PERSONAL"
            
    def add_task_from_dict(self, data):
        card = TaskCard(
            task_name=data.get("task_name", ""),
            category=data.get("category", ""),
            date_info=data.get("date_info", ""),
            time_info=data.get("time_info", ""),
            sub_items=data.get("sub_items", []),
            expanded=data.get("expanded", False)
        )
        card.deleted.connect(self.delete_task) # Connect delete signal
        item = QListWidgetItem()
        item.setSizeHint(card.sizeHint())
        # To maintain the correct visual order from top-to-bottom after a reversed load
        self.task_list.insertItem(0, item)
        self.task_list.setItemWidget(item, card)
        card.list_item = item

    def closeEvent(self, event):
        self.save_current_tasks()
        super().closeEvent(event)

    def styleSheet(self):
        return super().styleSheet()
    
def load_stylesheet():
    style_file = Path(__file__).parent / "style.qss"
    if style_file.exists():
        return style_file.read_text()
    print(f"Warning: {style_file} not found!")
    return ""    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    # --- Setup Splash Screen ---
    from PySide6.QtGui import QPixmap, QPainter
    pixmap = QPixmap(400, 250)
    pixmap.fill(QColor("#2d3436")) # Dark slate background
    
    splash = QSplashScreen(pixmap)
    splash.show()

    # ---Initialize Main Window ---
    window = ModernSmartTodo()

    # --- Setup and Start Loader Thread ---
    loader = AILoaderThread()

    def update_splash(message):
        splash.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)

    def on_finished(classifier):
        # Assign the loaded model
        window.task_classifier = classifier
        
        # Load style and transition to main window
        style = load_stylesheet()
        app.setStyleSheet(style)
        
        # Load Tasks
        from data_manager import load_tasks
        saved_tasks = load_tasks()
        # the list populates via insert(0, ...), so load in reverse so the original top item is inserted last and physically remains on top!
        for task_data in reversed(saved_tasks):
            window.add_task_from_dict(task_data)

        splash.finish(window)
        window.show()
        window.statusBar().showMessage("AI Engine: Online | ToDo version 1.0")

    loader.progress_update.connect(update_splash)
    loader.loading_finished.connect(on_finished)
    
    # Start the "heavy lifting" in the background
    loader.start()

    sys.exit(app.exec())