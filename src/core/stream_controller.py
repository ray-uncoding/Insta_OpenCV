from PyQt5.QtCore import QObject, pyqtSignal
from src.core import CameraManager, StreamWorker, FaceDetector
from src.utils.data_processor import FPSCounter

class StreamController(QObject):
    new_frame = pyqtSignal(object)  # 發送處理後的影像幀
    fps_updated = pyqtSignal(float)  # 發送更新後的 FPS

    def __init__(self, camera_url):
        super().__init__()
        self.camera_manager = CameraManager(camera_url)
        self.frame_queue = queue.Queue()
        self.stream_worker = StreamWorker(self.camera_manager, self.frame_queue)
        self.face_detector = FaceDetector()
        self.fps_counter = FPSCounter()

    def start(self):
        self.stream_worker.new_frame.connect(self.process_frame)
        self.stream_worker.start()

    def process_frame(self, frame):
        if frame is None or frame.size == 0:
            return

        # 處理影像幀（例如人臉檢測）
        processed_frame = self.face_detector.detect(frame)

        # 計算 FPS
        fps = self.fps_counter.update()
        self.fps_updated.emit(fps)

        # 發送處理後的影像幀
        self.new_frame.emit(processed_frame)