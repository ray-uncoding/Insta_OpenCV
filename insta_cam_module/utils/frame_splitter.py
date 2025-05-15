# utils/frame_splitter.py

import numpy as np

def split_frame_six_regions(frame: np.ndarray) -> list[np.ndarray]:
    """將全景影像橫向等分為六區塊"""
    height, width = frame.shape[:2]
    slice_width = width // 6
    return [frame[:, i * slice_width : (i + 1) * slice_width] for i in range(6)]
