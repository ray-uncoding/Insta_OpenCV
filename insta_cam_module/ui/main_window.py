# ui/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget,
    QGridLayout, QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
from utils.frame_splitter import split_frame_six_regions
from utils.config_loader import get_setting
import asyncio
from controller.insta_worker import InstaWorker
import cv2
from controller.insta_controller import InstaController
from ui.ui_worker import UIWorker

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
        self.ui_worker = None  # 用 UIWorker 管理高階功能
        self.split_labels = []
        self.log_widget = None
        self.init_ui()
        self._last_slices = None
        self._last_full = None

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_split_view_tab('six'), "六分割")
        self.tabs.addTab(self.create_split_view_tab('three'), "三分割")
        self.tabs.addTab(self.create_split_view_tab('two'), "二分割")
        self.tabs.addTab(self.create_full_view_tab(), "全景")
        self.tabs.currentChanged.connect(self.on_tab_changed)  # 分頁切換時同步分割模式
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

    def create_split_view_tab(self, mode: str) -> QWidget:
        """
        分割畫面顯示，mode: 'six'/'three'/'two'
        """
        tab = QWidget()
        layout = QGridLayout()
        n = 6 if mode == 'six' else 3 if mode == 'three' else 2 if mode == 'two' else 6
        labels = []
        for i in range(n):
            label = self.create_camera_label(f"畫面{i+1}")
            labels.append(label)
            row = i // 3 if n > 3 else 0
            col = i % 3 if n > 3 else i
            layout.addWidget(label, row, col)
        tab.setLayout(layout)
        if not hasattr(self, 'split_labels_dict'):
            self.split_labels_dict = {}
        self.split_labels_dict[mode] = labels
        return tab

    def create_full_view_tab(self) -> QWidget:
        """
        分頁二：全景畫面顯示
        """
        tab = QWidget()
        layout = QVBoxLayout()
        # 將全景畫面label尺寸調大，假設900x400
        self.full_view_label = self.create_camera_label("全景\n0~360", w=900, h=400)
        layout.addWidget(self.full_view_label, alignment=Qt.AlignCenter)
        tab.setLayout(layout)
        # 新增：將全景label存入split_labels_dict，key為'full'
        if not hasattr(self, 'split_labels_dict'):
            self.split_labels_dict = {}
        self.split_labels_dict['full'] = [self.full_view_label]
        return tab

    def create_camera_label(self, text: str, w=320, h=240) -> QLabel:
        """
        建立預設相機畫面框，未來可替換為 QPixmap 更新畫面
        """
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(w, h)
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

    def update_split_view(self, mode: str):
        if self.tabs.currentIndex() not in [0, 1, 2]:
            return
        if not self._last_slices:
            self.log_message("[UI] No frame received yet.")
            return
        label_w, label_h = 320, 240
        labels = self.split_labels_dict.get(mode, [])
        for i, pix in enumerate(self._last_slices):
            if i >= len(labels):
                break
            labels[i].setText("")
            if pix is None or pix.isNull():
                black = QPixmap(label_w, label_h)
                black.fill(Qt.black)
                labels[i].setPixmap(black)
            else:
                labels[i].setPixmap(pix.scaled(label_w, label_h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.full_view_label.setText("")

    def update_full_view(self):
        if self.tabs.currentIndex() != 3:
            return
        if not self._last_full:
            self.log_message("[UI] No frame received yet.")
            return
        self.full_view_label.setText("")
        label_w, label_h = 900, 400
        if self._last_full is None or self._last_full.isNull():
            black = QPixmap(label_w, label_h)
            black.fill(Qt.black)
            self.full_view_label.setPixmap(black)
        else:
            self.full_view_label.setPixmap(self._last_full.scaled(label_w, label_h, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_connect_clicked(self):
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("連線中...")
        self._do_connect()  # 直接呼叫，不要用 threading.Thread

    def _do_connect(self):
        try:
            # 根據分頁決定分割模式
            idx = self.tabs.currentIndex()
            if idx == 0:
                split_mode = 'six'
            elif idx == 1:
                split_mode = 'three'
            elif idx == 2:
                split_mode = 'two'
            else:
                split_mode = 'six'
            self.ui_worker = UIWorker(on_stream_error=self.on_stream_error, parent=self)
            self.ui_worker.frame_ready.connect(self.on_frame_ready)
            ready_event = self.ui_worker.start_all(split_mode=split_mode)
            self.log_message("[UI] Waiting for worker to be ready...")
            from PyQt5.QtCore import QTimer
            def check_ready():
                if ready_event.is_set():
                    self.log_message("[UI] Worker ready, UI will update on frame_ready signal.")
                    self.connect_btn.setText("連線成功")
                    self.connect_btn.setEnabled(False)
                else:
                    QTimer.singleShot(100, check_ready)
            check_ready()
        except Exception as e:
            self.show_message(f"連線失敗: {e}")
            self.connect_btn.setEnabled(True)
            self.connect_btn.setText("開始連線")

    @pyqtSlot(object, object)
    def on_frame_ready(self, split_np_arrays, full_np_array):
        print("[DEBUG] on_frame_ready called")
        self._last_slices = [cvimg_to_qpixmap(img) for img in split_np_arrays]
        self._last_full = cvimg_to_qpixmap(full_np_array)
        idx = self.tabs.currentIndex()
        if idx == 0:
            self.update_split_view('six')
        elif idx == 1:
            self.update_split_view('three')
        elif idx == 2:
            self.update_split_view('two')
        elif idx == 3:
            self.update_full_view()

    def get_latest_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def on_stream_error(self, msg):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, "串流異常", msg)
        self.log_message(f"[UI] 串流異常: {msg}")
        # 啟用重新連線按鈕
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("重新連線")

    def show_message(self, msg):
        QMessageBox.information(self, "訊息", msg)

    def closeEvent(self, event):
        if self.ui_worker:
            self.ui_worker.stop_all()
        event.accept()

    def on_tab_changed(self, idx):
        if not self.ui_worker or not hasattr(self.ui_worker, 'frame_thread') or not self.ui_worker.frame_thread:
            return
        if idx == 0:
            mode = 'six'
        elif idx == 1:
            mode = 'three'
        elif idx == 2:
            mode = 'two'
        else:
            mode = 'six'
        self.ui_worker.frame_thread.set_split_mode(mode)
        # 強制觸發一次畫面更新（下次 frame_ready 會自動更新）
