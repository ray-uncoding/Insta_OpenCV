import cv2

class CameraManager:
    def __init__(self, stream_url):
        """
        初始化 CameraManager
        :param stream_url: 相機串流的 URL
        """
        self.stream_url = stream_url
        self.cap = None

    def connect(self):
        """
        連接到相機
        """
        self.cap = cv2.VideoCapture(self.stream_url)
        if not self.cap.isOpened():
            raise ConnectionError(f"無法連接到相機: {self.stream_url}")

    def get_frame(self):
        """
        獲取影像幀
        :return: 影像幀 (numpy array) 或 None
        """
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def disconnect(self):
        """
        釋放相機資源
        """
        if self.cap:
            self.cap.release()