from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QWidget, QListWidget,
    QListWidgetItem, QCheckBox,
    QGraphicsDropShadowEffect, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor


class TaskCard(QFrame):
    deleted = Signal(object)
    file_attached = Signal(str, str) # (file_path, task_name)
    changed = Signal() # Signal to trigger auto-save
    
    def __init__(self, task_name, category, date_info="", time_info="", sub_items=None, expanded=False, priority="MEDIUM"):
        super().__init__()

        self.task_name = task_name
        self.date_info = date_info
        self.time_info = time_info
        self.priority = priority.upper()

        self.setObjectName("TaskCard")

        # Modern floating shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self.list_item = None

        self.category = (category or "INBOX").upper()
        self.expanded = expanded

        # ================= MAIN LAYOUT =================
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 10, 12, 10)

        self.main_layout.setSpacing(1)
        #self.extra_layout.setSpacing(8)

        # ================= HEADER =================
        self.header = QWidget()
        self.header.setCursor(Qt.PointingHandCursor)

        self.header_layout = QHBoxLayout(self.header)
        self.header.setObjectName("TaskHeader")
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel(task_name)
        self.name_label.setObjectName("TaskName")
        self.header_layout.addWidget(self.name_label, stretch=1)

        dt_text = " ".join([t for t in [date_info, time_info] if t]).strip()
        if dt_text:
            self.dt_label = QLabel(dt_text)
            self.dt_label.setObjectName("TaskDate")
            self.header_layout.addWidget(self.dt_label)

        # Priority Badge
        self.priority_badge = QLabel(self.priority)
        self.priority_badge.setStyleSheet(f"""
            background-color: {self.get_priority_color(self.priority)};
            color: white;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: bold;
        """)
        self.header_layout.addWidget(self.priority_badge)

        self.cat_label = QLabel(self.category)
        self.cat_label.setObjectName("TaskCategory")
        self.cat_label.setStyleSheet(
            f"background-color: {self.get_color(self.category)};"
        )
        self.header_layout.addWidget(self.cat_label)

        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setObjectName("DeleteBtn")
        self.delete_btn.setToolTip("Delete Task")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background: #ff7675;
                border-radius: 4px;
            }
        """)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.clicked.connect(self._on_delete)
        self.header_layout.addWidget(self.delete_btn)

        self.main_layout.addWidget(self.header)

        self.header.mousePressEvent = self.toggle_expand

        # ================= EXPAND AREA =================
        self.extra_container = QWidget()
        self.extra_layout = QVBoxLayout(self.extra_container)
        self.extra_layout.setContentsMargins(10, 5, 10, 10)
        self.extra_layout.setSpacing(5)

        self.extra_container.setVisible(self.expanded)
        self.main_layout.addWidget(self.extra_container)

        # Knowledge Base Section (Files)
        self.knowledge_container = QWidget()
        self.knowledge_layout = QVBoxLayout(self.knowledge_container)
        self.knowledge_layout.setContentsMargins(0, 5, 0, 0)
        self.knowledge_layout.setSpacing(2)
        
        self.knowledge_header = QLabel("<b>📚 Knowledge Base</b>")
        self.knowledge_header.setStyleSheet("color: #b2bec3; font-size: 11px; margin-top: 5px;")
        self.knowledge_layout.addWidget(self.knowledge_header)
        
        self.file_list_layout = QVBoxLayout()
        self.knowledge_layout.addLayout(self.file_list_layout)
        
        self.extra_layout.addWidget(self.knowledge_container)
        self.knowledge_container.setVisible(False)

        # route system (ONLY 2 TYPES)
        self.current_attached_file = None
        self.build_ui()
        
        # Load saved data if exists
        if sub_items:
            self.load_sub_items(sub_items)

    def _on_delete(self):
        self.deleted.emit(self)

    def load_sub_items(self, sub_items):
        if self.category == "GROCERY":
            for item in sub_items:
                check = QCheckBox(item.get("text", ""))
                if item.get("checked"):
                    check.setChecked(True)
                self.item_list.addWidget(check)
        else:
            for item in sub_items:
                self.add_general_item_to_ui(item.get("text", ""), item.get("file_path"))
        
        self.refresh_knowledge_base()
        self._update_size()

    def to_dict(self):
        data = {
            "task_name": self.task_name,
            "category": self.category,
            "date_info": self.date_info,
            "time_info": self.time_info,
            "priority": self.priority,
            "expanded": self.expanded,
            "sub_items": []
        }
        if self.category == "GROCERY":
            for i in range(self.item_list.count()):
                widget = self.item_list.itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    data["sub_items"].append({
                        "text": widget.text(),
                        "checked": widget.isChecked()
                    })
        else:
            for i in range(self.general_list.count()):
                item_widget = self.general_list.itemAt(i).widget()
                if item_widget:
                    label = item_widget.findChild(QLabel, "GeneralItemLabel")
                    if label:
                        file_path = label.property("file_path")
                        data["sub_items"].append({
                            "text": label.text().lstrip("• ").rstrip(" 📎"),
                            "file_path": file_path
                        })
        return data

    # --------------------------------------------------
    # EXPAND / COLLAPSE
    # --------------------------------------------------
    def _update_size(self):
        self.adjustSize()
        if self.list_item:
            self.list_item.setSizeHint(self.sizeHint())
        self.updateGeometry()

    def _recalculate_size(self):
        QTimer.singleShot(10, self._update_size)

    def toggle_expand(self, event=None):
        self.expanded = not self.expanded
        self.extra_container.setVisible(self.expanded)
        self._update_size()

    # --------------------------------------------------
    # UI ROUTER (IMPORTANT)
    # --------------------------------------------------
    def build_ui(self):
        if self.category == "GROCERY":
            self.build_shopping_ui()
        else:
            self.build_general_ui()

    # --------------------------------------------------
    # 🛒 SHOPPING UI (CHECKBOX LIST)
    # --------------------------------------------------
    def build_shopping_ui(self):
        self.item_list = QVBoxLayout()

        self.list_container = QWidget()
        self.list_container.setObjectName("ShoppingList")
        self.list_container.setLayout(self.item_list)

        # input row
        self.input_row = QWidget()
        row = QHBoxLayout(self.input_row)
        row.setContentsMargins(0, 0, 0, 0)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Add item...")

        self.add_btn = QPushButton("Add")
        self.add_btn.setObjectName("AddItemBtn")
        self.add_btn.clicked.connect(self.add_shopping_item)

        self.clear_btn = QPushButton("Clear Done")
        self.clear_btn.setObjectName("ClearBtn")
        self.clear_btn.clicked.connect(self.clear_checked_shopping_items)

        row.addWidget(self.input)
        row.addWidget(self.add_btn)
        row.addWidget(self.clear_btn)

        self.extra_layout.addWidget(self.list_container)
        self.extra_layout.addWidget(self.input_row)

    def add_shopping_item(self):
        text = self.input.text().strip()
        if text:
            item = QCheckBox(text)
            self.item_list.addWidget(item)

            self.input.clear()
            self._recalculate_size()
            self.changed.emit()

    def clear_checked_shopping_items(self):
        for i in reversed(range(self.item_list.count())):
            widget = self.item_list.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                self.item_list.removeWidget(widget)
                widget.deleteLater()
        self._recalculate_size()
        self.changed.emit()

    # --------------------------------------------------
    # 📄 GENERAL UI (default)
    # --------------------------------------------------
    def build_general_ui(self):
        self.general_list = QVBoxLayout()

        self.list_container = QWidget()
        self.list_container.setLayout(self.general_list)

        self.input_row = QWidget()
        row = QHBoxLayout(self.input_row)
        row.setContentsMargins(0, 0, 0, 0)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Add note...")

        self.attach_btn = QPushButton("📎")
        self.attach_btn.setToolTip("Attach Document for Nova (PDF/TXT)")
        self.attach_btn.setFixedWidth(30)
        self.attach_btn.clicked.connect(self.pick_file)

        self.add_btn = QPushButton("Save")
        self.add_btn.setObjectName("SaveBtn")
        self.add_btn.clicked.connect(self.add_general_item)

        row.addWidget(self.input)
        row.addWidget(self.attach_btn)
        row.addWidget(self.add_btn)

        self.extra_layout.insertWidget(0, self.list_container) # Put list above input
        self.extra_layout.addWidget(self.input_row)

    def add_general_item(self):
        text = self.input.text().strip()
        if text:
            self.add_general_item_to_ui(text, self.current_attached_file)
            self.input.clear()
            self.input.setPlaceholderText("Add note...")
            self.current_attached_file = None
            self.refresh_knowledge_base()
            self._recalculate_size()
            self.changed.emit()

    def add_general_item_to_ui(self, text, file_path=None):
        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(0, 2, 0, 2)
        
        file_text = " 📎" if file_path else ""
        label = QLabel(f"• {text}{file_text}")
        label.setObjectName("GeneralItemLabel")
        if file_path:
            label.setProperty("file_path", file_path)
            label.setToolTip(f"File: {file_path}")
        
        del_btn = QPushButton("×")
        del_btn.setFixedSize(20, 20)
        del_btn.setStyleSheet("background: transparent; color: #ff7675; border: none; font-weight: bold;")
        del_btn.clicked.connect(lambda: self.remove_general_item(item_widget))
        
        layout.addWidget(label, stretch=1)
        layout.addWidget(del_btn)
        self.general_list.addWidget(item_widget)

    def remove_general_item(self, widget):
        self.general_list.removeWidget(widget)
        widget.deleteLater()
        QTimer.singleShot(100, self.refresh_knowledge_base)
        QTimer.singleShot(110, self._recalculate_size)
        QTimer.singleShot(120, self.changed.emit)

    def refresh_knowledge_base(self):
        import os
        # Clear current list
        for i in reversed(range(self.file_list_layout.count())):
            item = self.file_list_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        files = []
        if hasattr(self, "general_list"):
            for i in range(self.general_list.count()):
                item_widget = self.general_list.itemAt(i).widget()
                if item_widget:
                    label = item_widget.findChild(QLabel, "GeneralItemLabel")
                    if label and label.property("file_path"):
                        files.append(label.property("file_path"))
        
        if not files:
            self.knowledge_container.setVisible(False)
            return

        self.knowledge_container.setVisible(True)
        for f in sorted(list(set(files))):
            file_row = QWidget()
            row_layout = QHBoxLayout(file_row)
            row_layout.setContentsMargins(5, 2, 5, 2)
            row_layout.setSpacing(10)
            
            fname = os.path.basename(f)
            name_label = QLabel(f"📄 {fname}")
            name_label.setStyleSheet("color: #74b9ff; font-size: 11px;")
            name_label.setToolTip(f)
            
            open_btn = QPushButton("Open")
            open_btn.setFixedWidth(50)
            open_btn.setCursor(Qt.PointingHandCursor)
            open_btn.setStyleSheet("""
                QPushButton { background: #2d3436; color: #dfe6e9; border-radius: 4px; font-size: 10px; padding: 2px; }
                QPushButton:hover { background: #636e72; }
            """)
            open_btn.clicked.connect(lambda checked=False, path=f: os.startfile(path))
            
            row_layout.addWidget(name_label, stretch=1)
            row_layout.addWidget(open_btn)
            self.file_list_layout.addWidget(file_row)

    def pick_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document", "", "Documents (*.pdf *.txt)")
        if file_path:
            import os
            self.current_attached_file = file_path
            self.input.setPlaceholderText(f"Attached: {os.path.basename(file_path)}")
            self.file_attached.emit(file_path, self.task_name)

    def get_priority_color(self, priority):
        if priority == "HIGH": return "#e74c3c"
        if priority == "MEDIUM": return "#f39c12"
        return "#2ecc71"


    # --------------------------------------------------
    # COLOR
    # --------------------------------------------------
    def get_color(self, cat):
        colors = {
            "WORK": "#0984e3",       # Blue
            "PERSONAL": "#00b894",   # Green
            "HEALTH": "#d63031",     # Red
            "TRAVEL": "#e17055",     # Orange-ish
            "SHOPPING": "#f1c40f",   # Yellow
            "GROCERY": "#f39c12",    # Dark Yellow
            "FINANCE": "#27ae60",    # Emerald
            "STUDY": "#6c5ce7",      # Purple
            "REMINDER": "#fab1a0"    # Peach
        }
        return colors.get(cat.upper(), "#b2bec3")