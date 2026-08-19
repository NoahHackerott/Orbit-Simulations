# import PySide6 classes that we need for application
import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton


# Subclass QMainWindow to customize application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Click me")

        # Set the central widget of the window
        self.setCentralWidget(button)


# pass command line arguments to the application
# if not passing command line arguments can replace with []
app = QApplication(sys.argv)

# create an instance of QWidget
window = MainWindow()
window.show()

# Start up the event loop
app.exec()

