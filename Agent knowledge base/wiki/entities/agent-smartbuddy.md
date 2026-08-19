# SmartBuddy — 學前英語陪練 Agent

> **類型**: entity（agent）
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/Task]]

## 摘要
SmartBuddy 是專注 **0–6 歲** 學齡前兒童的英語陪練 agent。假設寶寶母語為**普通話或粵語**，目標是學英語。接收家長問卷答案（見 [[raw/questionnaires]]）以個人化教學，並與數字人（Avatar）協作產出對話腳本。

## 工作流（[[raw/Task]]）
1. 家長經登入頁註冊。
2. 填寫問卷（參 [[raw/questionnaires]]、personality 模組）以了解寶寶發展。
3. 寶寶與 agent 互動。

## 關鍵要解決的問題
- 缺乏個人化、反饋延遲、隱性迷思、教師頻寬有限、學習動機低、學習歷史碎片化。

## 期望能力
學習診斷、個人化學習計畫、自適應講解、互動練習、進度記憶、家長支援、負責任陪練（引導而非代答、保護隱私、適時升級）。

## 課程產出（[[raw/Task]] §Lesson）
1. 依兒童年齡區間產出**個人化課程**，聚焦其概念性錯誤（conceptual mistake）。
2. 產出**家長易懂的教學計畫**（可考慮圖結構）。

## 網站與軟體
- 頁面：登入頁、問卷頁、用戶頁（教學計畫/進度、Chatbot、常見概念錯誤、時間表/日曆）。
- 技術：Firebase 前後端；Google Calendar 匯入/匯出寶寶行程以排課。
- 外部 AI：ElevenLabs（聽說）、Simli（數字人）、Qwen-Image-Plus / Seedance（圖/影片，暫不接）。

## 關聯
- 相關實體: [[entities/agent-avatar-personality]]、[[entities/product-elevenlabs]]、[[entities/product-simli]]
- 參見: [[topics/decision-flow]]、[[topics/teaching-playbook]]、[[topics/lesson-plan]]

## 引用來源
- [1] [[raw/Task]] — Agent.md 規格

## 變更記錄
- 2026-08-19: 初始建立。
