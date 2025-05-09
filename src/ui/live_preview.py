from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal

class LivePreview(QWidget):
    startStreamSignal = pyqtSignal()
    stopStreamSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Preview")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.label = QLabel("Live Stream Preview")
        layout.addWidget(self.label)

        self.start_button = QPushButton("Start Live Stream")
        self.start_button.clicked.connect(self.startStreamSignal.emit)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Live Stream")
        self.stop_button.clicked.connect(self.stopStreamSignal.emit)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
