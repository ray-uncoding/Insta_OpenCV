# InstaController 模組說明

本文件說明 `controller/insta_controller.py` 內 `InstaController` 類別的設計理念、主要功能與各方法用途，方便工程師與 AI 快速理解與維護。

---

## 模組定位

`InstaController` 是 Insta360 Pro 相機的非同步控制器，負責與相機進行 HTTP API 通訊，涵蓋連線、串流、拍照、心跳、重連等核心控制功能。採用 aiohttp + asyncio 架構，適合高併發、非阻塞應用場景。

---

## 主要屬性

- `self.settings`：讀取自 config/settings.json 的設定參數（如 IP、port、fingerprint 等）。
- `self.base_url`：API 請求的基礎網址。
- `self.fingerprint`：與相機 session 維持用的識別碼。
- `self.api_payloads`：API 請求的 payload 樣板，讀自 config/api_payloads.json。

---

## 主要方法與用途

### connect()

- 建立與相機的 session，取得 fingerprint。
- 必須先呼叫，後續所有操作都需依賴 fingerprint。

### start_preview()

- 啟動 RTMP 串流預覽。
- 呼叫後相機會開始推送 RTMP 視訊流。

### stop_preview()

- 停止 RTMP 串流。
- 結束預覽時呼叫，釋放相機端資源。

### take_picture()

- 拍攝靜態圖片，回傳 sequence。
- 可搭配 get_async_result 查詢拍照結果。

### get_async_result(sequence)

- 查詢 async 指令（如拍照）的執行結果。
- 需傳入 sequence。

### send_heartbeat()

- 維持 session 活性，每秒（或每2秒）呼叫一次 /osc/state。
- 若失敗，建議自動重連。

### reconnect()

- 心跳失敗時自動重連（connect → start_preview）。
- 可用於自動修復連線。

### get_stream_url()

- 動態組合 RTMP 預覽串流網址。
- 依據設定自動產生正確的 RTMP URL。

---

## 設計重點

- 每個 API 請求皆採用 aiohttp 非同步實作，適合與 asyncio 協程配合。
- 例外處理詳盡，遇到 API 回傳異常會詳細列印錯誤內容。
- 設定與 payload 皆集中管理，方便維護與擴充。

---

## 適用場景

- 需與 Insta360 Pro 相機進行自動化控制、即時串流、遠端拍照等應用。
- 適合與 UI、服務層、非同步任務等模組整合。

---

## 2025/05 架構重構與經驗補充

- **asyncio + aiohttp** 處理 HTTP API，**threading.Thread** 處理 OpenCV RTMP frame 擷取，**PyQt5 QThread** 處理 UI frame 分割與轉換。
- 若需擴充新功能，建議依照現有架構新增對應 API 方法，並於 config/api_payloads.json 補充 payload 樣板。
- 請參考 README.md 與 非同步設計說明.md 以獲得最新訊號流與協作細節。
