import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.signal_processing.signal_manager import SignalManager
from src.camera.camera_controller import CameraController
from src.camera.heartbeat import Heartbeat
from src.face_recognition.recognition_worker import RecognitionWorker

def main():
    # Initialize signal manager
    signal_manager = SignalManager()

    # Initialize camera controller and heartbeat
    camera_controller = CameraController()
    heartbeat = Heartbeat()

    # Initialize recognition worker
    recognition_worker = RecognitionWorker(signal_manager)

    # Start all threads
    signal_manager.start()
    heartbeat.start()
    recognition_worker.start()

    # Start the application
    app = QApplication(sys.argv)
    main_window = MainWindow(signal_manager)
    main_window.show()

    # Run the application
    exit_code = app.exec_()

    # Stop all threads
    recognition_worker.stop()
    heartbeat.stop()
    signal_manager.stop()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()