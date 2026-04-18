from pathlib import Path
import sys
import re
import dateparser
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QSplashScreen, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QListWidget, 
                             QListWidgetItem, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont

class AILoaderThread(QThread):
    # Signals to send messages and the actual models back to the main app
    progress_update = Signal(str)
    loading_finished = Signal(object, object)  # (task_classifier, nlp)

    def run(self):
        # 1. Load TextBlob Classifier
        self.progress_update.emit("Training the brain...")
        from categorizer import task_classifier
        
        # 2. Load spaCy NLP
        self.progress_update.emit("Waking up spaCy AI...")
        from item_finder import nlp
        
        # 3. Finish
        self.progress_update.emit("All systems ready!")
        self.loading_finished.emit(task_classifier, nlp)

# import custom widgets
from task_card import TaskCard

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
        self.task_list_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d3436;")
        self.task_list = QListWidget()
        self.task_list.setSpacing(10) # Space between tasks
        self.main_layout.addWidget(self.task_list_label)
        self.main_layout.addWidget(self.task_list, stretch=1)

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
        date_info = ""
        time_info = ""
        category = self.task_classifier.classify(text.lower()) or ""

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

        # widget select
        self.smart_widget_select()
        
        # Create TaskCard
        card = TaskCard(formatedText, category, date_info, time_info)
        item = QListWidgetItem()
        item.setSizeHint(card.sizeHint())
        self.task_list.insertItem(0, item)
        self.task_list.setItemWidget(item, card)
        self.input_field.clear()

    def smart_widget_select(self):
        text = self.input_field.text().strip()
        if not text: return

        # Let spaCy analyze the sentence
        doc = self.nlp(text)
        
        # 1. Check for Grocery Entities
        # spaCy can find 'NOUNS' that are objects/products
        is_grocery = False
        items_found = []

        for ent in doc.ents:
            if ent.label_ == "GROCERY" or ent.label_ == "PRODUCT":
                is_grocery = True
                items_found.append(ent.text)

        # Even if no specific entity is found, we can check for the verb "buy" 
        # and the presence of a "noun" (object)
        if not is_grocery:
            has_buy_verb = any(token.lemma_ == "buy" for token in doc)
            if has_buy_verb:
                is_grocery = True

        # 2. Trigger the correct UI
        if is_grocery:
            print(f"Triggering Grocery Widget for: {items_found}")
            # self.open_grocery_widget(items_found) 
        else:
            # Fall back to your TextBlob classifier for general categories
            category = self.task_classifier.classify(text)
            print(f"Adding normal task to {category}")

        

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

    def on_finished(classifier, nlp_model):
        # Assign the loaded models
        window.task_classifier = classifier
        window.nlp = nlp_model
        
        # Load style and transition to main window
        style = load_stylesheet("app\\style.qss")
        app.setStyleSheet(style)
        
        splash.finish(window)
        window.show()
        window.statusBar().showMessage("AI Engine: Online | ToDo version 1.0")

    loader.progress_update.connect(update_splash)
    loader.loading_finished.connect(on_finished)
    
    # Start the "heavy lifting" in the background
    loader.start()

    sys.exit(app.exec())