# utils/frame_receiver.py

import cv2
import threading

class FrameReceiver:
    """串流即時擷取畫面，背景執行緒維持最新影格"""
    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self.latest_frame = None
        self.running = False
        self.capture = None
        self.thread = None

    def start(self, on_error=None):
        self.capture = cv2.VideoCapture(self.stream_url)
        self.on_error = on_error
        if not self.capture.isOpened():
            if self.on_error:
                self.on_error("無法開啟串流來源")
            raise RuntimeError(f"無法開啟串流來源：{self.stream_url}")
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        fail_count = 0
        frame_count = 0
        import time
        last_log = time.time()
        while self.running:
            try:
                ret, frame = self.capture.read()
                if ret:
                    self.latest_frame = frame
                    fail_count = 0
                    frame_count += 1
                    # Log in English for debugging
                    if time.time() - last_log > 1:
                        print(f"[FrameReceiver] Frames grabbed: {frame_count}, latest frame shape: {frame.shape if frame is not None else None}")
                        last_log = time.time()
                else:
                    fail_count += 1
                    print(f"[FrameReceiver] cap.read() failed, fail_count={fail_count}")
                    if fail_count >= 30:
                        self.running = False
                        if self.on_error:
                            self.on_error("Stream error, stopped automatically.")
                        break
            except Exception as e:
                self.running = False
                if self.on_error:
                    self.on_error(f"Stream exception: {e}")
                print(f"[FrameReceiver] Exception: {e}")
                break

    def get_latest_frame(self):
        return self.latest_frame

    def stop(self):
        self.running = False
        if self.capture:
            self.capture.release()
        self.capture = None
