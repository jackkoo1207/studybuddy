# Wiki 索引（BabyStep AI 英語陪練知識庫）

> 總頁數: 25 ｜ 最後更新: 2026-08-19 ｜ 維護: LLM Wiki 專家
> 架構規範見 [[../SCHEMA]] ｜ 原始資料見 `raw/`（只讀）

## 檢索黃金路徑
1. 決策輸入 → [[topics/decision-flow]]
2. 定位分段 → [[concepts/doman-seven-stage-framework]] / [[concepts/english-tutor-levels]] / [[concepts/city-tier-adaptation]] / [[concepts/child-personality-archetypes]]
3. 取教學腳本 → **[[topics/teaching-playbook]]**（主頁） / [[topics/english-content-by-level]] / [[topics/stage-activities]]
4. 定分量安全 → [[concepts/dosage-screen-safety]]
5. 產出 → [[topics/lesson-plan]] / [[topics/avatar-plan-schema]]

---

## 主題（Topics）— agent 主要讀這層

### 檢索決策頁
- [[topics/teaching-playbook]] — **主檢索頁**：問卷答案 → 教什麼/怎麼教/教多少/語氣
- [[topics/decision-flow]] — 問卷答案 → 教學決策的六步流程
- [[topics/avatar-plan-schema]] — AvatarPlan JSON 欄位契約（輸出結構）

### 教學內容頁
- [[topics/english-content-by-level]] — 英語內容推薦（Level 0–4）+ 主題詞彙庫
- [[topics/stage-activities]] — 分階段家長協助活動（Doman 1–7 階，六通路分項）
- [[topics/lesson-plan]] — 家長易懂的教學計畫範本

> 📌 總頁數: 25 ｜ 最後更新: 2026-08-19（ingest 拼寫方法頁）

## 概念（Concepts）— 框架 / 標準 / 教學法

### 發展框架
- [[concepts/doman-seven-stage-framework]] — Doman 七階段 × 腦部區域 × 年齡窗口
- [[concepts/six-pathways]] — 六通路（視/聽/觸/活動/語言/手部）
- [[concepts/developmental-profile-scoring]] — 物理評分與報告輸出邏輯

### 英語教學坐標
- [[concepts/english-tutor-levels]] — 英語等級 L0–4（定義/判定/矩陣）
- [[concepts/city-tier-adaptation]] — 城市線級 1–5+港 適配矩陣與校準係數
- [[concepts/child-personality-archetypes]] — 6 性格原型 → 人格/內容配對

### 安全與方法
- [[concepts/dosage-screen-safety]] — 分量計算 + AAP 螢幕上限 + 降級
- [[concepts/method-tpr]] — TPR 全身反應法
- [[concepts/method-phonics]] — Phonics 語音意識
- [[concepts/method-early-reading]] — Doman 早期閱讀（已 ingest 全本，完整教案）
- [[concepts/method-teach-baby-to-talk]] — Doman 語言發展計畫（說話啟蒙，raw 已含，已 ingest）
- [[concepts/method-spelling]] — 拼寫（Doman：規則型學校科目，在閱讀之後，無寶寶教法/年齡）
- [[concepts/method-physical-program]] — Doman 體能計畫

## 實體（Entities）— 人物 / Agent / 產品
- [[entities/person-glenn-doman]] — Glenn Doman / IAHP（框架源頭）
- [[entities/agent-smartbuddy]] — SmartBuddy 學前英語陪練 agent（規格）
- [[entities/agent-avatar-personality]] — Avatar Agent 個性化調度器
- [[entities/product-elevenlabs]] — ElevenLabs 聽說語音（Voice ID）
- [[entities/product-simli]] — Simli Studio 數字人
- [[entities/product-qwen-seedance]] — Qwen-Image-Plus / Seedance（暫不接）

## 原始資料（raw/，只讀）
- [[raw/questionnaires]] — 家長問卷（決策輸入）
- [[raw/成長階段建議]] — Doman 七階段 + 家長協助 + 城市線級對比
- [[raw/how_smart_is_your_baby]] — Glenn Doman《How Smart Is Your Baby?》
- [[raw/如何使寶寶身強體健]] — Doman 體能計畫書
- [[raw/How To Teach Your Baby to Read]] — Glenn Doman《How to Teach Your Baby to Read》（識字法全本，已 ingest）
