from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.camera.camera_thread import CameraThread
from src.face_recognition.face_detection_thread import FaceDetectionThread
from src.signal_processing.signal_processing_thread import SignalProcessingThread
from src.camera.camera_manager import CameraManager
from src.camera.live_stream import LiveStream
from src.ui.live_preview import LivePreview
import sys

def main():
    app = QApplication(sys.argv)

    # 初始化 UI
    window = MainWindow()

    # 初始化相機管理與直播模組
    camera_manager = CameraManager(
        command_url="http://192.168.1.188:20000/osc/commands/execute",
        state_url="http://192.168.1.188:20000/osc/state"
    )
    live_stream = LiveStream(stream_url="rtmp://192.168.1.188:1935/live/preview")

    # 初始化直播預覽 UI
    live_preview = LivePreview()
    live_preview.startStreamSignal.connect(live_stream.start_preview)
    live_preview.stopStreamSignal.connect(live_stream.stop_preview)

    # 初始化執行緒
    camera_thread = CameraThread()
    face_detection_thread = FaceDetectionThread()
    signal_processing_thread = SignalProcessingThread()

    # 訊號連接
    camera_thread.signal.connect(window.update_camera_view)
    face_detection_thread.signal.connect(window.update_face_detection)
    signal_processing_thread.signal.connect(window.update_signal_status)

    # 啟動執行緒
    camera_thread.start()
    face_detection_thread.start()
    signal_processing_thread.start()

    # 顯示 UI
    window.show()

    # 顯示直播預覽 UI
    live_preview.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()