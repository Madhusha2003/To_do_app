from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

class NovaResponseDialog(QDialog):
    def __init__(self, parent=None, response_text=""):
        super().__init__(parent)
        self.setWindowTitle("✨ Nova Response")
        self.setMinimumSize(450, 550)
        
        # Make it look like a modern frameless window or at least nicely styled
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Markdown Viewer
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #282a36;
                color: #f8f8f2;
                border: 1px solid #44475a;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                selection-background-color: #6272a4;
            }
        """)
        # Set markdown text
        self.text_browser.setMarkdown(response_text)
        
        # Add a subtle shadow to the text area
        shadow = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=5)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.text_browser.setGraphicsEffect(shadow)

        layout.addWidget(self.text_browser)

        # Button Layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.close_btn = QPushButton("Got it!")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #bd93f9;
                color: #282a36;
                border-radius: 15px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff79c6;
            }
            QPushButton:pressed {
                background-color: #ff92d0;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
