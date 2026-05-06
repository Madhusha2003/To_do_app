from pathlib import Path
import os
import sys
import re
import requests
import dateparser
from datetime import datetime
from core.utils import DateTimeExtractor
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QSplashScreen, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QListWidget, QFrame,
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
        from core.categorizer import task_classifier
        
        # 2. Finish
        self.progress_update.emit("All systems ready!")
        self.loading_finished.emit(task_classifier)

from ui.task_card import TaskCard
from core.data_manager import load_ai_config, save_ai_config
from core.ai_service import AIService, build_chat_prompt, build_task_prompt
from core.rag_service import RAGService
from ui.ai_settings_window import AIPanelDialog
from ui.nova_window import NovaResponseDialog


class ModernSmartTodo(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ToDo Buddy Pro")
        self.resize(500, 700)
        
        # Initialize Services
        from core.data_manager import load_ai_config
        config = load_ai_config()
        self.rag_service = RAGService(config)

        # Main Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(25, 30, 25, 30)
        self.main_layout.setSpacing(10)

        # --- Header ---
        self.header_layout = QHBoxLayout()
        self.task_list_label = QLabel("Your Tasks")
        self.task_list_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setToolTip("App Settings")
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
        
        self.kb_btn = QPushButton("📚")
        self.kb_btn.setToolTip("Open Knowledge Base Folder")
        self.kb_btn.setCursor(Qt.PointingHandCursor)
        self.kb_btn.setStyleSheet("""
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
        self.kb_btn.clicked.connect(self.open_knowledge_base)
        
        self.header_layout.addWidget(self.task_list_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.kb_btn)
        self.header_layout.addWidget(self.settings_btn)
        
        self.main_layout.addLayout(self.header_layout)

        # --- Task List ---
        self.task_list = QListWidget()
        self.task_list.setSpacing(10) # Space between tasks
        self.main_layout.addWidget(self.task_list, stretch=1)

        # --- Modern Input Bar ---
        self.input_frame = QFrame()
        self.input_frame.setObjectName("ModernInputBar")
        self.input_frame.setStyleSheet("""
            QFrame#ModernInputBar {
                background-color: #2d3436;
                border-radius: 25px;
                border: 1px solid #636e72;
            }
        """)
        
        # Shadow for the input frame
        shadow = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=5)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.input_frame.setGraphicsEffect(shadow)

        self.input_container = QHBoxLayout(self.input_frame)
        self.input_container.setContentsMargins(15, 5, 5, 5) # Left padding for combobox, small margins elsewhere
        self.input_container.setSpacing(10)

        # Mode Selector
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["General Chat", "Add Task"])
        self.mode_selector.setCursor(Qt.PointingHandCursor)
        self.mode_selector.setStyleSheet("""
            QComboBox {
                background: transparent;
                color: #dfe6e9;
                border: none;
                font-weight: bold;
                padding-right: 15px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d3436;
                color: white;
                selection-background-color: #636e72;
                border-radius: 5px;
            }
        """)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
            }
        """)

        self.add_button = QPushButton("⬆️")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setFixedSize(40, 40)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #0984e3;
                color: white;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #74b9ff;
            }
        """)

        self.input_container.addWidget(self.mode_selector)
        self.input_container.addWidget(self.input_field)
        self.input_container.addWidget(self.add_button)
        
        self.main_layout.addWidget(self.input_frame)

        self.update_ui_for_mode()

        # --- Logic Connections ---
        self.input_field.returnPressed.connect(self.process_input)
        self.add_button.clicked.connect(self.process_input)
        self.settings_btn.clicked.connect(self.open_settings)

        # Subtle Shadow for the input bar
        shadow = QGraphicsDropShadowEffect(blurRadius=10, xOffset=0, yOffset=3)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.input_field.setGraphicsEffect(shadow)

    def update_ui_for_mode(self):
        from core.data_manager import load_ai_config
        config = load_ai_config()
        self.cat_mode = config.get("categorizer_mode", "ML")
        
        if self.cat_mode == "Nova":
            self.input_field.setPlaceholderText("Message Nova...")
            self.mode_selector.show()
        else:
            self.input_field.setPlaceholderText("Try: Finish report by Friday 5pm")
            self.mode_selector.hide()

    def open_settings(self):
        dialog = AIPanelDialog(self)
        dialog.exec()
        self.update_ui_for_mode()

    def process_input(self, checked=False):
        text = self.input_field.text().strip()
        if not text:
            return
            
        if self.cat_mode == "Nova":
            if self.mode_selector.currentText() == "General Chat":
                self.process_nova_chat(text)
            else:
                self.process_nova_task(text)
        else:
            self.add_task_logic(text)

    def process_nova_chat(self, text):
        from core.data_manager import load_ai_config
        config = load_ai_config()
        service = AIService(config)

        # Collect current tasks for context
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            card = self.task_list.itemWidget(item)
            if card and hasattr(card, "to_dict"):
                tasks.append(card.to_dict())

        mode = config.get("mode", "online")

        # --- RAG: query BEFORE building prompt ---
        rag_context = self.rag_service.query(text)
        if rag_context:
            print(f"[RAG] Context injected ({len(rag_context)} chars): {rag_context[:120]}...")
        else:
            print("[RAG] No context retrieved for this query.")

        prompt = build_chat_prompt(tasks, mode=mode, user_prompt=text, rag_context=rag_context)

        self.statusBar().showMessage("Nova is thinking...")
        QApplication.processEvents()

        response = service.ask(prompt)
        self.statusBar().showMessage(f"AI Engine: {mode.capitalize()} | ToDo version 1.0")

        dialog = NovaResponseDialog(self, response_text=response)
        dialog.exec()
        self.input_field.clear()

    def process_nova_task(self, text):
        from core.data_manager import load_ai_config
        import json
        import re

        config = load_ai_config()
        mode = config.get("mode", "online")
        service = AIService(config)

        extracted_date = ""
        extracted_time = ""
        ai_input_text = text

        if mode == "local":
            ai_input_text, extracted_date, extracted_time = DateTimeExtractor.extract(text)
            self.statusBar().showMessage("Nova (Local) is classifying...")
        else:
            self.statusBar().showMessage("Nova (Online) is classifying...")

        # RAG context for task classification (helps with custom category rules)
        rag_context = self.rag_service.query(ai_input_text)
        if rag_context:
            print(f"[RAG] Task context injected ({len(rag_context)} chars)")

        prompt = build_task_prompt(ai_input_text, mode=mode, rag_context=rag_context)
        QApplication.processEvents()

        response = service.ask(prompt)
        self.statusBar().showMessage(f"AI Engine: {mode.capitalize()} | ToDo version 1.0")
        
        try:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                response = match.group(0)
            data = json.loads(response)
            
            category = data.get("category", "PERSONAL")
            task_name = data.get("task_name", ai_input_text)
            priority = data.get("priority", "MEDIUM")
            
            # For online mode, use AI parsed dates. For local, use our extractor's dates.
            if mode == "online":
                date_info = data.get("date_info", "")
                time_info = data.get("time_info", "")
            else:
                date_info = extracted_date
                time_info = extracted_time
                
            self.add_task_logic(task_name, override_category=category, override_date=date_info, override_time=time_info, override_priority=priority)
        except Exception as e:
            print("Failed to parse JSON:", e, "Response:", response)
            self.add_task_logic(text, override_category="PERSONAL")

    def add_task_logic(self, text=None, override_category=None, override_date=None, override_time=None, override_priority=None):
        if text is None:
            text = self.input_field.text().strip()
        if not text:
            return
        
        # find category info if classifier exists
        category = override_category or "PERSONAL"
        if not override_category and hasattr(self, "task_classifier"):
            category = self.text_category_classifier(text) or "PERSONAL"

        # Extract date and time information using utility function or use overrides
        if override_date is not None or override_time is not None:
            date_info = override_date or ""
            time_info = override_time or ""
        else:
            text, date_info, time_info = DateTimeExtractor.extract(text)
        
        # Ensure date_info always has a value (defaulting to today)
        if not date_info:
            date_info = datetime.now().strftime('%b %d, %Y')
        
        priority = override_priority or "MEDIUM"
        
        # Capitalize the first letter for a cleaner look
        formatedText = text[0].upper() + text[1:] if text else ""

        # Safely format the tag based on whether date, time, or both were provided
        tags = [info for info in (date_info, time_info) if info]
        info_tag = f"[{' | '.join(tags)}] " if tags else ""

        self.card = TaskCard(formatedText, category, date_info, time_info, priority=priority)
        self.card.deleted.connect(self.delete_task) # Connect delete signal
        self.card.file_attached.connect(self.index_file) # Connect RAG signal
        self.card.changed.connect(self.save_current_tasks) # Connect auto-save
        self.item = QListWidgetItem()
        self.item.setSizeHint(self.card.sizeHint())
        self.task_list.insertItem(0, self.item)
        self.task_list.setItemWidget(self.item, self.card)
        self.input_field.clear()
        self.card.list_item = self.item 
        
        # Index the task itself for better RAG results
        self.rag_service.index_task(formatedText, category)
        
        self.save_current_tasks() # Auto-save

    def index_file(self, file_path, task_name=None):
        display_name = os.path.basename(file_path)
        self.statusBar().showMessage(f"Nova is indexing: {display_name}...")
        QApplication.processEvents()
        
        # If task_name is provided, use it as context for the file
        success = self.rag_service.add_document(file_path, task_context=task_name)
        
        if success:
            self.statusBar().showMessage(f"'{display_name}' indexed successfully! ✓", 3000)
        else:
            self.statusBar().showMessage(f"Failed to index {display_name}.", 3000)

    def open_knowledge_base(self):
        """Open the knowledge_base folder and refresh index."""
        kb_path = str(self.rag_service.knowledge_base_path)
        os.startfile(kb_path)
        self.statusBar().showMessage("Syncing knowledge base...", 2000)
        self.rag_service.refresh_knowledge_base()
        self.statusBar().showMessage("Knowledge Base synced! ✓", 3000)

    def delete_task(self, card):
        # Find item in list
        row = self.task_list.row(card.list_item)
        if row != -1:
            self.task_list.takeItem(row)
            self.save_current_tasks() # Auto-save
            
    def save_current_tasks(self):
        try:
            from core.data_manager import save_tasks
            tasks_data = []
            for i in range(self.task_list.count()):
                item = self.task_list.item(i)
                card = self.task_list.itemWidget(item)
                if card and hasattr(card, "to_dict"):
                    tasks_data.append(card.to_dict())
            save_tasks(tasks_data)
        except Exception as e:
            print(f"Failed to save tasks: {e}")
        
    def text_category_classifier(self, text):
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
            priority=data.get("priority", "MEDIUM"),
            sub_items=data.get("sub_items", []),
            expanded=data.get("expanded", False)
        )
        card.deleted.connect(self.delete_task)
        card.file_attached.connect(self.index_file)
        card.changed.connect(self.save_current_tasks)
        item = QListWidgetItem()
        item.setSizeHint(card.sizeHint())
        self.task_list.insertItem(0, item)
        self.task_list.setItemWidget(item, card)
        card.list_item = item

        # Re-index any attached files that aren't yet in the vector DB
        for sub in data.get("sub_items", []):
            fp = sub.get("file_path")
            if fp and os.path.exists(fp):
                print(f"[RAG System] Re-syncing task attachment: {os.path.basename(fp)}")
                self.rag_service.add_document(fp, task_context=data.get("task_name"))
        
        # Also ensure the task itself is indexed
        self.rag_service.index_task(data.get("task_name", ""), data.get("category", ""))

    def closeEvent(self, event):
        self.save_current_tasks()
        super().closeEvent(event)

    def styleSheet(self):
        return super().styleSheet()
    
def load_stylesheet():
    style_file = Path(__file__).parent / "ui" / "style.qss"
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
        from core.data_manager import load_tasks
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