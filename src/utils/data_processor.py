import time

class FPSCounter:
    def __init__(self):
        self.last_time = time.time()
        self.frame_count = 0

    def update(self):
        """
        更新幀數並計算 FPS
        :return: 當前 FPS
        """
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_time

        if elapsed_time >= 1.0:  # 每秒更新一次
            fps = self.frame_count / elapsed_time
            self.last_time = current_time
            self.frame_count = 0
            return fps
        return None