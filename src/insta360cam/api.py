# insta_cam_module/api.py
"""
API 封裝：讓外部專案可 import 並取得即時影像、啟動/關閉 UI、進行分割等。
"""
from src.insta360cam.controller.insta_worker import InstaWorker
from src.insta360cam.ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

__all__ = ["InstaWorker", "launch_ui"]

def launch_ui():
    """啟動 Insta360 UI（阻塞主執行緒）"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
