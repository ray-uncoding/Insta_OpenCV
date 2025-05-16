# utils/frame_splitter.py

import numpy as np

def split_frame_by_centers(frame: np.ndarray, centers_deg: list, fov_deg: float) -> list[np.ndarray]:
    """
    通用分割：依據中心角度列表與視角寬度切分全景影像。
    centers_deg: 中心角度（度）list，例如 [0, 60, 120, 180, 240, 300]
    fov_deg: 每個分割畫面的視角寬度
    """
    height, width = frame.shape[:2]
    triple = np.concatenate([frame, frame, frame], axis=1)
    fov_px = int(width * fov_deg / 360)
    half = fov_px // 2
    regions = []
    for deg in centers_deg:
        center_px = int(width * deg / 360) + width
        start = center_px - half
        end = center_px + half
        if end > triple.shape[1] or start < 0 or (end-start)<=0:
            regions.append(np.zeros((height, max(1, end-start), frame.shape[2]), dtype=frame.dtype))
        else:
            regions.append(triple[:, start:end])
    return regions

# 保留原六分割快捷函式

def split_frame_six_regions(frame: np.ndarray, fov_deg: float = 120) -> list[np.ndarray]:
    centers_deg = [0, 60, 120, 180, 240, 300]
    return split_frame_by_centers(frame, centers_deg, fov_deg)
