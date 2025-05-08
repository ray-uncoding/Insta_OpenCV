from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from src.ui.status_bar import StatusBar
from src.core import CameraManager, StreamWorker, FaceDetector
from src.utils import setup_logger
from src.utils.data_processor import FPSCounter
from src.core.insta_api import InstaAPI
from src.ui.camera_widget import CameraWidget
import datetime
import os
import queue
from src.core.stream_controller import StreamController
from src.utils.config_loader import load_config

class MainWindow(QMainWindow):
    def __init__(self, stream_controller):
        super().__init__()
        self.setWindowTitle("Insta_OpenCV")
        self.resize(800, 600)

        # 使用傳入的 StreamController
        self.stream_controller = stream_controller
        self.stream_controller.new_frame.connect(self.camera_widget.update_frame)
        self.stream_controller.fps_updated.connect(self.status_bar.update_fps)

        # 從配置檔案中載入 URL
        config = load_config("insta_api.json")
        urls = config.get("urls", {})
        command_url = urls.get("command_url", "")
        state_url = urls.get("state_url", "")

        # 初始化 InstaAPI
        self.api = InstaAPI(
            config_path=os.path.join(os.path.dirname(__file__), "../config/insta_api.json"),
            command_url=command_url,
            state_url=state_url
        )

        # 設置主視窗佈局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # 初始化 CameraWidget
        self.camera_widget = CameraWidget(self)
        self.layout.addWidget(self.camera_widget)

        # 狀態列
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        # 啟動控制器
        try:
            self.stream_controller.start()
        except Exception as e:
            self.status_bar.update_connection_status("Disconnected", str(e))
            print(f"Error starting StreamController: {e}")