# InstaCam Module

本專案負責 Insta360 Pro 相機的串流控制、畫面切割、心跳維持與 PyQt5 UI 顯示。
支援 async 架構、模組化設計，可單獨啟動或整合進其他系統。

---

## 🏗️ 專案結構

```
insta_cam_module/
├── main.py                  # 啟動 UI 主程式
├── insta_api_test.py        # 單獨測試串流與 frame 取得效能
├── controller/
│   ├── insta_controller.py  # 相機 HTTP API 控制主模組（asyncio + aiohttp）
│   └── insta_worker.py      # 高階協調器，整合 controller、心跳、FrameReceiver
├── services/
│   └── heartbeat.py         # 心跳維持服務（asyncio）
├── ui/
│   ├── main_window.py       # PyQt5 UI 主視窗，分頁顯示六分割/全景
│   └── ui_worker.py         # UI 與背景 frame 處理協調（QThread）
├── utils/
│   ├── config_loader.py     # 設定檔管理
│   ├── frame_receiver.py    # RTMP 串流 frame 擷取（OpenCV + Thread）
│   └── frame_splitter.py    # 全景畫面切割六區
├── config/
│   └── settings.json        # 參數設定
├── README.md                # 專案說明（本檔案）
├── 非同步設計說明.md        # 架構與非同步設計細節
└── controller/insta_controller說明.md # 控制器 API 詳細說明
```

---

## 🧩 架構邏輯與訊號流


### 1. UI 架構（2025/05 最新重構）

- **main.py** 啟動 PyQt5 UI。
- **main_window.py** 管理 UI 顯示、分頁、訊息區、連線按鈕。
- **ui_worker.py** 用 QThread 處理 frame 分割、resize，主執行緒只 setPixmap。
- **訊號流**：FrameReceiver（Thread）→ InstaWorker → UIWorker（QThread）→ MainWindow（slot）
- **所有 PyQt 物件與 QThread 必須在主執行緒建立與啟動，signal/slot 也要在主執行緒註冊**。


### 2. 非同步與多執行緒協作

- **controller/insta_controller.py** 用 asyncio + aiohttp 控制相機 HTTP API。
- **services/heartbeat.py** 用 asyncio 定時送心跳。
- **utils/frame_receiver.py** 用 Thread 持續抓 RTMP frame，避免阻塞 event loop。
- **utils/frame_splitter.py** 負責 frame 分割。

---

## 🛠️ 重大開發歷程與困難點


### 1. UI 嚴重卡頓問題

- **現象**：PyQt5 UI 顯示 frame 時非常卡頓，效能遠低於單純 OpenCV 測試。
- **原因**：原本在 UI 執行緒做 frame 分割、resize、QPixmap 轉換，導致主執行緒負擔過重。
- **解法**：重構為 QThread 處理所有影像運算，UI 只 setPixmap，效能大幅提升。


### 2. PyQt 多執行緒訊號流丟失

- **現象**：QThread run() 沒執行、signal/slot 沒有任何 debug print，UI 無畫面。
- **原因**：PyQt 物件與 QThread 在非主執行緒建立與啟動，PyQt 事件機制直接失效。
- **解法**：所有 PyQt 物件與 QThread 必須在主執行緒建立與啟動，signal/slot 也要在主執行緒註冊。用 QTimer 輪詢 ready_event，避免阻塞主執行緒。


### 3. OpenCV frame 顯示驗證

- **現象**：UI 沒畫面時，OpenCV 測試檔能正常顯示。
- **解法**：在 UI slot 內用 cv2.imshow 顯示 debug 畫面，快速定位問題在 PyQt 訊號流。


### 4. Windows + asyncio + OpenCV 陷阱

- **現象**：Windows 下 asyncio + OpenCV + RTMP 容易出現 socket reset。
- **解法**：將 OpenCV frame 擷取完全移到 Thread，asyncio event loop 只跑 HTTP API 與心跳。

---

## 🧠 重要設計原則

- **UI 執行緒只做 setPixmap，所有重運算都在 QThread 處理**。
- **PyQt QThread 必須在主執行緒建立與啟動，parent 關係要正確**。
- **訊號流設計要有 debug print，方便追蹤訊號流向**。
- **OpenCV frame 處理與 PyQt UI 顯示完全分離，互不阻塞**。

---

## 🚩 目前已解決問題

- UI 卡頓、訊號流丟失、QThread 啟動失敗、OpenCV frame 顯示驗證。

---

## 🏁 待優化項目

- 畫面比例自動調整（避免被擠壓）。
- UI 分頁切換時的效能優化。
- 增加更多控制按鈕（拍照、重連、停止預覽等）。

---

## 📦 InstaCam Module - 快速模組化用法

本專案可被其他 Python 專案 import，支援即時影像串流、分割、UI 啟動等功能。

### 1. 取得即時影像（不啟動 UI）

```python
from insta_cam_module.api import InstaWorker

worker = InstaWorker()
ready_event = worker.start_all()
ready_event.wait()  # 等待串流與心跳啟動
frame = worker.get_latest_frame()
# frame 為 numpy.ndarray，可進行影像辨識、分割等
```

### 2. 啟動 Insta360 UI

```python
from insta_cam_module.api import launch_ui
launch_ui()  # 會阻塞主執行緒，直到 UI 關閉
```

### 3. 進行全景影像分割

```python
from insta_cam_module.utils.frame_splitter import split_frame_by_centers
# 假設 frame 為 360 相機輸出
centers = [0, 120, 240]
fov = 120
slices = split_frame_by_centers(frame, centers, fov)
# slices 為分割後的多個 numpy.ndarray
```

---

## 🧩 典型應用場景
- 影像辨識/AI 專案：import InstaWorker 取得即時 frame，直接送入 AI 模型。
- 監控/串流 UI：import launch_ui 啟動多分割 UI。
- 影像後處理：import frame_splitter 進行自訂分割。

---

## 🧑‍💻 參考文件

- [非同步設計說明.md](./非同步設計說明.md)
- [controller/insta_controller說明.md](./controller/insta_controller說明.md)

---

如需協助，請參考本 README 與設計說明，或聯絡專案負責人。
