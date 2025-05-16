# Insta360 OpenCV UI 重構與非同步效能最佳化紀錄

## 2025/05 重構開發歷程

本文件記錄 Insta360 OpenCV UI 專案在 2025/05 進行的重大重構過程，聚焦於解決 PyQt5 UI 嚴重卡頓、訊號流丟失、非同步與多執行緒協作等問題，並總結最佳實踐與設計原則，方便團隊與 AI 夥伴快速理解與維護。

---

## 問題背景

- 原本 UI 架構將 frame 分割、resize、QPixmap 轉換等重運算全部放在 PyQt5 主執行緒，導致 UI 嚴重卡頓。
- 單純用 OpenCV 測試（insta_api_test.py）時，畫面流暢，效能極佳。
- 將 UI 重運算移到 QThread 後，訊號流卻丟失，UI 無法顯示畫面。

---

## 主要困難與踩坑紀錄

1. **PyQt QThread run() 未執行、signal/slot 無法觸發**
   - 問題：QThread、QObject 在非主執行緒建立與啟動，PyQt 事件機制直接失效。
   - 解法：所有 PyQt 物件與 QThread 必須在主執行緒建立與啟動，signal/slot 也要在主執行緒註冊。

2. **UI 執行緒負擔過重導致卡頓**
   - 問題：frame 分割、resize、QPixmap 轉換都在 UI 執行緒，導致畫面更新緩慢。
   - 解法：重構為 QThread 處理所有影像運算，UI 只 setPixmap，效能大幅提升。

3. **訊號流 debug 與驗證**
   - 問題：UI 無畫面時難以定位問題。
   - 解法：在 slot 內用 print 與 cv2.imshow 顯示 debug 畫面，快速定位問題在 PyQt 訊號流。

4. **Windows + asyncio + OpenCV 陷阱**
   - 問題：Windows 下 asyncio + OpenCV + RTMP 容易出現 socket reset。
   - 解法：將 OpenCV frame 擷取完全移到 Thread，asyncio event loop 只跑 HTTP API 與心跳。

---

## 重構後的非同步 API 架構

- **FrameReceiver**：用 Thread 持續抓 RTMP frame，避免阻塞 asyncio event loop。
- **InstaWorker**：協調 controller、心跳、FrameReceiver。
- **UIWorker (QThread)**：負責 frame 分割、resize，主執行緒只 setPixmap。
- **MainWindow**：PyQt5 UI 主視窗，slot 只負責顯示 QPixmap。
- **訊號流**：FrameReceiver（Thread）→ InstaWorker → UIWorker（QThread）→ MainWindow（slot）
- **所有 PyQt 物件與 QThread 必須在主執行緒建立與啟動，signal/slot 也要在主執行緒註冊。**
- **用 QTimer 輪詢 ready_event，避免阻塞主執行緒。**

---

## 設計原則與最佳實踐

- UI 執行緒只做 setPixmap，所有重運算都在 QThread 處理。
- PyQt QThread 必須在主執行緒建立與啟動，parent 關係要正確。
- 訊號流設計要有 debug print，方便追蹤訊號流向。
- OpenCV frame 處理與 PyQt UI 顯示完全分離，互不阻塞。

---

## 目前已解決問題

- UI 卡頓、訊號流丟失、QThread 啟動失敗、OpenCV frame 顯示驗證。

---

## 參考

- 詳細訊號流與協作流程請見 [README.md](./README.md) 與 [非同步設計說明.md](./非同步設計說明.md)
- 控制器 API 詳細說明請見 [controller/insta_controller說明.md](./controller/insta_controller說明.md)

---

如需協助，請參考本說明與專案 README。
