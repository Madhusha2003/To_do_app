from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QWidget, QListWidget,
    QListWidgetItem, QCheckBox,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor


class TaskCard(QFrame):
    def __init__(self, task_name, category, date_info="", time_info=""):
        super().__init__()

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
        self.expanded = False

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

        self.cat_label = QLabel(self.category)
        self.cat_label.setObjectName("TaskCategory")
        self.cat_label.setStyleSheet(
            f"background-color: {self.get_color(self.category)};"
        )
        self.header_layout.addWidget(self.cat_label)

        self.main_layout.addWidget(self.header)

        self.header.mousePressEvent = self.toggle_expand

        # ================= EXPAND AREA =================
        self.extra_container = QWidget()
        self.extra_layout = QVBoxLayout(self.extra_container)
        self.extra_layout.setContentsMargins(0, 0, 0, 0)
        self.extra_layout.setSpacing(1)

        self.extra_container.setVisible(False)
        self.main_layout.addWidget(self.extra_container)

        # route system (ONLY 2 TYPES)
        self.build_ui()

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

    def clear_checked_shopping_items(self):
        for i in reversed(range(self.item_list.count())):
            widget = self.item_list.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                self.item_list.removeWidget(widget)
                widget.deleteLater()
        self._recalculate_size()

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

        self.add_btn = QPushButton("Save")
        self.add_btn.setObjectName("SaveBtn")
        self.add_btn.clicked.connect(self.add_general_item)

        row.addWidget(self.input)
        row.addWidget(self.add_btn)

        self.extra_layout.addWidget(self.list_container)
        self.extra_layout.addWidget(self.input_row)

    def add_general_item(self):
        text = self.input.text().strip()
        if text:
            label = QLabel(f"• {text}")
            label.setObjectName("GeneralItem")

            self.general_list.addWidget(label)

            self.input.clear()
            self._recalculate_size()


    # --------------------------------------------------
    # COLOR
    # --------------------------------------------------
    def get_color(self, cat):
        colors = {
            "WORK": "#0984e3",
            "PERSONAL": "#00b894",
            "HEALTH": "#d63031",
            "SOCIAL": "#6c5ce7",
            "GROCERY": "#f39c12",
            "SHOPPING": "#f39c12"
        }
        return colors.get(cat, "#b2bec3")