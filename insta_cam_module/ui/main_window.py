# ui/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget,
    QGridLayout, QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
from utils.frame_splitter import split_frame_six_regions
from utils.config_loader import get_setting
import asyncio
from controller.insta_worker import InstaWorker

# OpenCV 影像轉 QPixmap
def cvimg_to_qpixmap(cv_img):
    if cv_img is None:
        return QPixmap()
    rgb_img = cv_img[..., ::-1]  # BGR to RGB
    h, w, ch = rgb_img.shape
    bytes_per_line = ch * w
    # 修正：QImage 需傳 bytes，不可用 memoryview
    qimg = QImage(rgb_img.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insta360 分頁顯示系統")
        self.resize(1000, 600)
        self.worker = None  # 用 InstaWorker 取代 controller/heartbeat/frame_receiver
        self.split_labels = []
        self.timer = None
        self.log_widget = None
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_split_view_tab(), "分頁一")
        self.tabs.addTab(self.create_full_view_tab(), "分頁二")
        # 連線按鈕
        self.connect_btn = QPushButton("開始連線")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        # 新增訊息區
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setFixedHeight(80)
        vbox = QVBoxLayout()
        vbox.addWidget(self.connect_btn)
        vbox.addWidget(self.log_widget)
        vbox.addWidget(self.tabs)
        container = QWidget()
        container.setLayout(vbox)
        self.setCentralWidget(container)

    def create_split_view_tab(self) -> QWidget:
        """
        分頁一：六個畫面分區顯示
        """
        tab = QWidget()
        layout = QGridLayout()
        self.split_labels = []
        for i in range(6):
            label = self.create_camera_label(f"畫面{i+1}")
            self.split_labels.append(label)
            row = i // 3
            col = i % 3
            layout.addWidget(label, row, col)
        tab.setLayout(layout)
        return tab

    def create_full_view_tab(self) -> QWidget:
        """
        分頁二：全景畫面顯示
        """
        tab = QWidget()
        layout = QVBoxLayout()
        self.full_view_label = self.create_camera_label("全景\n0~360")
        layout.addWidget(self.full_view_label, alignment=Qt.AlignCenter)
        tab.setLayout(layout)
        return tab

    def create_camera_label(self, text: str) -> QLabel:
        """
        建立預設相機畫面框，未來可替換為 QPixmap 更新畫面
        """
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        # 放大預設尺寸，讓畫面顯示更大
        label.setFixedSize(320, 180)
        label.setStyleSheet("border: 1px solid gray; font-size: 16px;")
        return label

    def log_message(self, msg):
        # 同時顯示在 UI 與終端
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        if isinstance(msg, dict):
            import json
            msg = json.dumps(msg, indent=2, ensure_ascii=False)
        self.log_widget.append(f"[{now}] {msg}")
        print(f"[{now}] {msg}")

    def update_split_view(self):
        """
        只在分頁一啟用時才刷新六分割畫面，並自動調整 QLabel 尺寸與畫質。
        """
        # 只在分頁一時才刷新
        if self.tabs.currentIndex() != 0:
            return
        if self.worker is None:
            self.log_message("[UI] Worker not started.")
            return
        frame = self.worker.get_latest_frame()
        if frame is not None:
            try:
                slices = split_frame_six_regions(frame)
                # 動態調整 QLabel 尺寸（大一點）
                label_w, label_h = 320, 180
                for i, img in enumerate(slices):
                    pix = cvimg_to_qpixmap(img)
                    self.split_labels[i].setText("")
                    self.split_labels[i].setPixmap(pix.scaled(label_w, label_h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.full_view_label.setText("")
            except Exception as e:
                self.log_message(f"[UI] Frame process error: {e}")
        else:
            self.log_message("[UI] No frame received yet.")

    def update_full_view(self):
        """
        只在分頁二啟用時才刷新全景畫面。
        """
        if self.tabs.currentIndex() != 1:
            return
        if self.worker is None:
            return
        frame = self.worker.get_latest_frame()
        if frame is not None:
            pix = cvimg_to_qpixmap(frame)
            self.full_view_label.setText("")
            self.full_view_label.setPixmap(pix.scaled(900, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_connect_clicked(self):
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("連線中...")
        import threading
        threading.Thread(target=self._do_connect, daemon=True).start()

    def _do_connect(self):
        try:
            self.worker = InstaWorker()
            ready_event = self.worker.start_all()
            print("[UI] Waiting for worker to be ready...")
            ready_event.wait()
            print("[UI] Worker ready, request UI timer start.")
            from PyQt5.QtCore import QTimer
            # 用 singleShot 讓 QTimer 在主 thread 啟動
            QTimer.singleShot(0, self._start_timer)
            self.connect_btn.setText("連線成功")
            self.connect_btn.setEnabled(False)
        except Exception as e:
            self.show_message(f"連線失敗: {e}")
            self.connect_btn.setEnabled(True)
            self.connect_btn.setText("開始連線")

    def _start_timer(self):
        from PyQt5.QtCore import QTimer
        print("[UI] QTimer started in main thread.")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_current_tab)
        self.timer.start(1000 // 30)  # 30fps，提升流暢度

    def _refresh_current_tab(self):
        # 根據目前分頁只刷新對應畫面，減少負擔
        if self.tabs.currentIndex() == 0:
            self.update_split_view()
        elif self.tabs.currentIndex() == 1:
            self.update_full_view()

    def on_stream_error(self, msg):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, "串流異常", msg)
        self.log_message(f"[UI] 串流異常: {msg}")

    def show_message(self, msg):
        QMessageBox.information(self, "訊息", msg)
