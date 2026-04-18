from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

class TaskCard(QFrame):
    def __init__(self, task_name, category, date_info, time_info):
        super().__init__()
        self.setObjectName("TaskCard")
        self.setMinimumHeight(60)
        
        # Combined layout
        self.layout = QHBoxLayout(self)
        self.layout.setObjectName("TaskLayout")
        #self.layout.setContentsMargins(15, 12, 15, 12)
        self.layout.setSpacing(10)

        # 1. Task Name
        self.name_label = QLabel(task_name)
        self.name_label.setStyleSheet("font-weight: 600; color: #2d3436; font-size: 14px;")
        self.layout.addWidget(self.name_label, stretch=1)

        # 2. Date/Time Info (if available)
        dt_text = f"{date_info} {time_info}".strip()
        if dt_text:
            self.dt_label = QLabel(dt_text)
            self.dt_label.setStyleSheet("color: #636e72; font-size: 11px; font-style: italic;")
            self.layout.addWidget(self.dt_label)

        # 3. Category Pill
        display_cat = category.upper() if category else "INBOX"
        self.cat_label = QLabel(display_cat)
        bg_color = self.get_color(display_cat)
        self.cat_label.setStyleSheet(f"""
            background-color: {bg_color};
            color: white;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        self.layout.addWidget(self.cat_label)

    def get_color(self, cat):
        colors = {
            "WORK": "#0984e3", "PERSONAL": "#00b894", 
            "HEALTH": "#d63031", "SOCIAL": "#6c5ce7", "GROCERY": "#f39c12"
        }
        return colors.get(cat, "#b2bec3")