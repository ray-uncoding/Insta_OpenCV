# InstaCam Module

此模組負責管理 Insta360 相機的串流控制、畫面切割、心跳維持與 UI 顯示。
支援 async 架構、模組化設計、可單獨啟動或整合進保全機器人主控系統中。

---

## 🔧 專案結構

insta_cam_module/
├── main.py # 啟動整體系統，啟動 async loop 與 UI
├── controller/
│ └── insta_controller.py # 相機控制主模組（connect / start / heartbeat）
├── services/
│ └── heartbeat.py # 背景非同步心跳管理（/osc/state 輪詢）
├── ui/
│ └── main_window.py # 分頁式視覺介面：六畫面 + 全景畫面
├── utils/
│ ├── config_loader.py # JSON 設定管理模組
│ ├── frame_receiver.py # 從 RTMP 串流擷取最新畫面（OpenCV）
│ └── frame_splitter.py # 將全景畫面水平切割成六塊
├── config/
│ └── settings.json # 基本參數設定檔



---

## ⚙️ 模組功能總覽

### ✅ InstaController (`controller/insta_controller.py`)
- `connect()`：呼叫 `camera._connect` 並取得 fingerprint
- `start_preview()`：設定並啟動 RTMP 串流（使用 `camera.setOptions` + `startPreview`）
- `send_heartbeat()`：維持連線存活
- `take_picture()`：拍照
- `reconnect()`：心跳失敗時自動重連

### ✅ HeartbeatService (`services/heartbeat.py`)
- `run()`：非同步背景 loop，每秒呼叫 `/osc/state`
- `stop()`：安全停止 loop

### ✅ FrameReceiver (`utils/frame_receiver.py`)
- 開啟 RTMP/MJPEG 串流，持續讀取 frame
- 可由 UI 或其他模組隨時取得最新一幀

### ✅ FrameSplitter (`utils/frame_splitter.py`)
- 將全景畫面切割為六個水平方向區段（每區約 60°）

### ✅ Config Loader (`utils/config_loader.py`)
- 管理 `settings.json` 的讀寫與更新
- 可在運行中儲存新 fingerprint 等資訊

---

## 🖥️ UI 模組說明

### 🔹 `main_window.py`
- 使用 `QTabWidget` 管理兩個分頁
  - 分頁一：六個小視角畫面（0°~360°，每 60° 一塊）
  - 分頁二：全景畫面（完整顯示）
- 支援動態更新：可由 `QTimer` 觸發每秒刷新畫面

---

## 📦 設定檔（`config/settings.json`）

```json
{
  "insta_ip": "192.168.1.188",
  "fingerprint": "",
  "preview_mode": "rtmp",
  "rtmp_url": "rtmp://192.168.1.188:1935/live/preview",
  "review_allowed_ip": "192.168.1.101",
  "resolution": "3840x1920",
  "bitrate": 10240000,
  "framerate": 30,
  "record_audio": true,
  "heartbeat_interval": 1
}

---
## 執行方式


python main.py



---

這樣一份 `README.md` 不但能幫你快速回顧系統設計，也能幫助 Copilot 與任何協作者**快速理解架構與工作邊界**。


接下來你可以：

為 UI main_window.py 加入 QTimer 定時更新畫面

將 FrameReceiver.get_latest_frame() 和 FrameSplitter.split_frame_six_regions() 整合入分頁一

使用 cvimg_to_qpixmap() 輔助轉換影像為 QLabel 顯示

加入按鈕控制（拍照、停止預覽、重新連線）
