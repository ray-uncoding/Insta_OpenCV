import cv2
import threading
import requests
import time
import json
from pathlib import Path
from src.signal_processing.signal_handler import SignalHandler
from src.camera.heartbeat import Heartbeat

# Load configuration
config_path = Path(__file__).parent.parent / 'config' / 'insta_command.json'
with open(config_path, 'r') as config_file:
    CONFIG = json.load(config_file)

COMMAND_URL = CONFIG["COMMAND_URL"]
STATE_URL = CONFIG["STATE_URL"]
PREVIEW_PARAMETERS = CONFIG["PREVIEW_PARAMETERS"]

class CameraController:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.capture = None
        self.running = False
        self.lock = threading.Lock()
        self.fingerprint = None
        self.signal_handler = SignalHandler()
        self.heartbeat = Heartbeat()

    def start_camera(self):
        """Start the camera stream."""
        with self.lock:
            self.capture = cv2.VideoCapture(self.camera_index)
            self.running = True

    def stop_camera(self):
        """Stop the camera stream."""
        with self.lock:
            if self.capture:
                self.capture.release()
            self.running = False

    def get_frame(self):
        """Capture a single frame from the camera."""
        with self.lock:
            if self.capture and self.running:
                ret, frame = self.capture.read()
                if ret:
                    return frame
            return None

    def boot_camera(self):
        """Send boot command to the camera and retrieve fingerprint."""
        hw_time = time.strftime("%m%d%H%M%Y.%S")
        self.fingerprint = self.signal_handler.register_fingerprint(COMMAND_URL, hw_time)
        print(f"Fingerprint retrieved: {self.fingerprint}")

    def send_heartbeat(self):
        """Send heartbeat command to keep the camera connection alive."""
        if not self.fingerprint:
            raise Exception("Fingerprint is required to send heartbeat")
        self.heartbeat.send_heartbeat(STATE_URL, self.fingerprint)

    def start_preview(self):
        """Send command to start camera preview."""
        if not self.fingerprint:
            raise Exception("Fingerprint is required to start preview")
        payload = {
            "name": "camera._startPreview",
            "parameters": PREVIEW_PARAMETERS
        }
        headers = {
            "Fingerprint": self.fingerprint,
            "Content-Type": "application/json"
        }
        response = requests.post(COMMAND_URL, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception("Failed to start preview")