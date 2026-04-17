from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QMainWindow, QMenu, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction

# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.

class MainWindow(QMainWindow):
    TaskBtnEnabled = True

    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("ToDo Buddy")
        # set windows size
        self.resize(1280, 720)
        self.setMinimumSize(QSize(640, 480))
        self.setMaximumSize(QSize(1920, 1080))

        # label
        self.label = QLabel()

        # input
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter your task here")
        self.input.textChanged.connect(self.label.setText)
        
        # button
        self.button = QPushButton("Add Task")
        self.button.clicked.connect(self.button_clicked)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        # widget
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)



    def button_clicked(self, checked):
        print("Button clicked, checked =", checked)
        self.button.setEnabled(self.TaskBtnEnabled)


    # Mouse events
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.TaskBtnEnabled = False

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.TaskBtnEnabled = True

    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())



app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()

# Your application won't reach here until you exit and the event
# loop has stopped.