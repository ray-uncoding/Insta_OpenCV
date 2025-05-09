from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QImage, QPixmap

class CameraWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Camera feed will appear here.")
        self.setScaledContents(True)

    def update_frame(self, frame):
        """Update the displayed frame."""
        if frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(q_image))