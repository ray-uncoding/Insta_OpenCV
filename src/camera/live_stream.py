import cv2

class LiveStream:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.cap = None

    def start_preview(self):
        self.cap = cv2.VideoCapture(self.stream_url)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            cv2.imshow('Live Preview', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def stop_preview(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
