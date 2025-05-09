import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from .camera_widget import CameraWidget
from .status_bar import StatusBar

class MainWindow(QMainWindow):
    def __init__(self, signal_manager):
        super().__init__()
        self.signal_manager = signal_manager
        self.init_ui()

    def init_ui(self):
        """Initialize the main window UI."""
        self.setWindowTitle("Insta OpenCV")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Add camera widget
        self.camera_widget = CameraWidget()
        layout.addWidget(self.camera_widget)

        # Add status bar
        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def update_ui(self, signal):
        """Update the UI based on signals."""
        if signal == "Face recognized":
            self.status_bar.update_status("Face recognized!")