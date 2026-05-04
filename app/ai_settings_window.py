import requests
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QLabel, QFormLayout, QComboBox, QLineEdit, QPushButton, QMessageBox, QApplication)
from data_manager import load_ai_config, save_ai_config

class AIPanelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Assistant Settings")
        self.setMinimumWidth(300)
        self.config = load_ai_config()

        layout = QVBoxLayout(self)

        self.mode_group = QButtonGroup(self)
        self.local_radio = QRadioButton("Local (Ollama)")
        self.online_radio = QRadioButton("Online (Gemini)")
        self.mode_group.addButton(self.local_radio)
        self.mode_group.addButton(self.online_radio)

        if self.config.get("mode") == "local":
            self.local_radio.setChecked(True)
            self.info_label = QLabel("""
            Local Mode:
            - Uses Ollama on your PC
            - Requires installed model
            """)
            self.info_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.insertWidget(0, self.info_label)
        else:
            self.online_radio.setChecked(True)
            self.info_label = QLabel("""
            Online Mode:
            - Uses Gemini API
            - Requires API key
            """)
            self.info_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.insertWidget(0, self.info_label)
            
        layout.addWidget(QLabel("Mode:"))
        layout.addWidget(self.local_radio)
        layout.addWidget(self.online_radio)
        layout.addWidget(self.info_label)

        self.form_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        
        # Fetch models from Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            models = [m["name"] for m in response.json().get("models", [])]
            if not models:
                models = ["No models found."]
        except Exception:
            models = ["No models found."]
            
        self.model_combo.addItems(models)
        
        saved_model = self.config.get("model", "")
        if self.config.get("mode") == "local":
            if saved_model in models:
                self.model_combo.setCurrentText(saved_model)
            elif models and models[0] != "No models found.":
                self.model_combo.setCurrentText(models[0])

        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.config.get("api_key", ""))
        self.api_key_input.setEchoMode(QLineEdit.Password)
        
        self.fetch_btn = QPushButton("Fetch Models")
        self.fetch_btn.setFixedWidth(100)
        self.fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)

        self.api_key_layout = QHBoxLayout()
        self.api_key_layout.addWidget(self.api_key_input)
        self.api_key_layout.addWidget(self.fetch_btn)
        
        self.online_model_combo = QComboBox()
        self.online_model_combo.setPlaceholderText("Click 'Fetch Models' to load...")
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["gemini"])
        self.provider_combo.setCurrentText(self.config.get("provider", "gemini"))

        self.form_layout.addRow("Model (Local):", self.model_combo)
        self.form_layout.addRow("Provider (Online):", self.provider_combo)
        self.form_layout.addRow("API Key (Online):", self.api_key_layout)
        self.form_layout.addRow("Model (Online):", self.online_model_combo)
        
        layout.addLayout(self.form_layout)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        # Connections
        self.save_btn.clicked.connect(self.save_settings)
        self.fetch_btn.clicked.connect(self.fetch_gemini_models)

    def fetch_gemini_models(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            return

        self.online_model_combo.clear()
        self.online_model_combo.addItem("Fetching models...")
        QApplication.processEvents()

        try:
            url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            response = requests.get(url, timeout=5)
            data = response.json()

            if "models" in data:
                # Filter for models that support generateContent
                gemini_models = [
                    m["name"].split("/")[-1] 
                    for m in data["models"] 
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                ]
                
                self.online_model_combo.clear()
                self.online_model_combo.addItems(gemini_models)
                
                # Select saved model if it exists in the list
                saved_model = self.config.get("model", "")
                index = self.online_model_combo.findText(saved_model)
                if index >= 0:
                    self.online_model_combo.setCurrentIndex(index)
            else:
                error = data.get("error", {}).get("message", "Unknown error")
                self.online_model_combo.clear()
                self.online_model_combo.addItem(f"Error: {error[:30]}...")
        except Exception as e:
            self.online_model_combo.clear()
            self.online_model_combo.addItem(f"Network Error")

    def save_settings(self):
        self.config["mode"] = "local" if self.local_radio.isChecked() else "online"
        
        if self.config["mode"] == "local":
            self.config["model"] = self.model_combo.currentText()
        else:
            self.config["model"] = self.online_model_combo.currentText()
            
        self.config["api_key"] = self.api_key_input.text()
        self.config["provider"] = self.provider_combo.currentText()
        save_ai_config(self.config)
        QMessageBox.information(self, "Saved", "Settings saved successfully!")
        self.accept()
