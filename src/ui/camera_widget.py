from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np

class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.image_label = QLabel("Camera Feed")
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)

        # 初始化上一幀為空白影像
        self.last_frame = np.zeros((480, 640, 3), dtype=np.uint8)  # 默認大小為 640x480 的黑色影像

    def update_frame(self, frame):
        if frame is None or frame.size == 0:
            # 如果幀無效，直接顯示上一幀
            self._display_frame(self.last_frame)
            return

        # 保存當前幀為上一幀
        self.last_frame = frame
        self._display_frame(frame)

    def _display_frame(self, frame):
        """將影像幀顯示在 QLabel 上"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))