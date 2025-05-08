from PyQt5.QtCore import QObject, pyqtSignal, QThread
import cv2

class StreamWorker(QObject):
    new_frame = pyqtSignal(object)  # 定義信號，傳遞影像幀

    def __init__(self, camera_manager):
        super().__init__()
        self.camera_manager = camera_manager
        self.running = False

    def start(self):
        self.running = True
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        self.thread.start()

    def run(self):
        while self.running:
            frame = self.camera_manager.get_frame()
            if frame is not None:
                self.new_frame.emit(frame)  # 發送新幀信號

    def stop(self):
        self.running = False
        self.thread.quit()
        self.thread.wait()