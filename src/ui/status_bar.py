from PyQt5.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget

class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()

        # 連線狀態
        self.connection_status_label = QLabel("Connection: Disconnected")
        self.layout.addWidget(self.connection_status_label)

        # FPS
        self.fps_label = QLabel("FPS: 0")
        self.layout.addWidget(self.fps_label)

        # 將佈局設置到狀態列
        container = QWidget()
        container.setLayout(self.layout)
        self.addWidget(container)

    def update_fps(self, fps):
        self.fps_label.setText(f"FPS: {fps:.2f}")

    def update_connection_status(self, status, error_message=None):
        if error_message:
            self.connection_status_label.setText(f"Connection: {status} ({error_message})")
        else:
            self.connection_status_label.setText(f"Connection: {status}")

        # 如果斷開連線，重置 FPS 標籤
        if status == "Disconnected":
            self.fps_label.setText("FPS: 0")