# ui/ui_worker.py
"""
UIWorker: 專為 UI 管理高階功能（RTMP 啟動、心跳、FrameReceiver、異常處理）
讓 main_window.py 只需專注於 UI 顯示與互動。
"""
from src.insta360cam.controller.insta_worker import InstaWorker
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
from src.insta360cam.utils.frame_splitter import split_frame_six_regions
import cv2

# OpenCV 影像轉 QPixmap
# 這裡複製 main_window.py 的轉換函式，避免循環 import
def cvimg_to_qpixmap(cv_img):
    if cv_img is None:
        return QPixmap()
    rgb_img = cv_img[..., ::-1]  # BGR to RGB
    h, w, ch = rgb_img.shape
    bytes_per_line = ch * w
    qimg = QImage(rgb_img.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)

class FrameProcessWorker(QThread):
    # 傳遞 (split_np_arrays, full_np_array)
    frame_ready = pyqtSignal(object, object)
    def __init__(self, get_frame_func, parent=None):
        super().__init__(parent)
        self.get_frame_func = get_frame_func
        self.running = False
        self.split_mode = 'six'  # 預設六分割

    def set_split_mode(self, mode):
        self.split_mode = mode

    def run(self):
        print("[DEBUG] FrameProcessWorker started")
        self.running = True
        def resize_and_pad(img, target_w=320, target_h=240):
            h, w = img.shape[:2]
            scale = min(target_w / w, target_h / h)
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(img, (new_w, new_h))
            result = np.zeros((target_h, target_w, 3), dtype=img.dtype)
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            return result
        from src.insta360cam.utils.frame_splitter import split_frame_by_centers
        while self.running:
            frame = self.get_frame_func()
            if frame is not None:
                if self.split_mode == 'six':
                    centers = [0, 60, 120, 180, 240, 300]
                    fov = 120
                elif self.split_mode == 'three':
                    centers = [0, 120, 240]
                    fov = 120
                elif self.split_mode == 'two':
                    centers = [0, 180]
                    fov = 180
                else:
                    centers = [0, 60, 120, 180, 240, 300]
                    fov = 120
                slices = split_frame_by_centers(frame, centers, fov)
                split_np_arrays = []
                for img in slices:
                    # 防呆：若 shape 不正確，補黑圖
                    if img is None or img.shape[0] == 0 or img.shape[1] == 0:
                        img = np.zeros((240, 320, 3), dtype=np.uint8)
                    try:
                        padded = resize_and_pad(img, 320, 240)
                    except Exception:
                        padded = np.zeros((240, 320, 3), dtype=np.uint8)
                    split_np_arrays.append(padded)
                full_np_array = cv2.resize(frame, (900, 400))
                self.frame_ready.emit(split_np_arrays, full_np_array)
            self.msleep(33)  # 約 30FPS

    def stop(self):
        self.running = False
        self.wait()

class UIWorker(QObject):
    frame_ready = pyqtSignal(object, object)
    def __init__(self, on_stream_error=None, parent=None):
        super().__init__(parent)
        self.worker = None
        self.on_stream_error = on_stream_error
        self.frame_thread = None

    def start_all(self, split_mode='six'):
        self.worker = InstaWorker()
        ready_event = self.worker.start_all(on_stream_error=self.on_stream_error)
        self.frame_thread = FrameProcessWorker(self.worker.get_latest_frame, parent=self)
        self.frame_thread.set_split_mode(split_mode)
        self.frame_thread.frame_ready.connect(self._emit_frame_ready)
        print("[DEBUG] frame_ready signal connected")
        self.frame_thread.start()
        return ready_event

    def _emit_frame_ready(self, split_np_arrays, full_np_array):
        print("[DEBUG] _emit_frame_ready called")
        self.frame_ready.emit(split_np_arrays, full_np_array)

    def get_latest_frame(self):
        if self.worker:
            return self.worker.get_latest_frame()
        return None

    def stop_all(self):
        if self.frame_thread:
            self.frame_thread.stop()
            self.frame_thread = None
        if self.worker:
            self.worker.stop_all()
            self.worker = None
