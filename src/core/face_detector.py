import cv2

class FaceDetector:
    def __init__(self, model_path="haarcascade_frontalface_default.xml"):
        """
        初始化人臉偵測器
        :param model_path: Haar Cascade 模型路徑
        """
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + model_path)

    def detect_faces(self, frame):
        """
        偵測影像中的人臉
        :param frame: 輸入影像
        :return: 偵測到的人臉座標列表
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces