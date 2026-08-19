# BabyStep AI 英語陪練知識庫 — 建置總覽

> 建立日期：2026-08-19 ｜ 維護：LLM Wiki 專家 ｜ 位置：`D:\OPC\Agent knowledge base\`

## 這份知識庫是什麼
為 **0–6 歲、母語為普通話／粵語的寶寶之 AI 英語陪練（SmartBuddy）** 打造的「編譯型」知識層。把分散的原始資料（問卷、Doman 發展書、agent 規格）編譯成 **agent 可直接檢索、用來決定「教什麼／怎麼教／教多少／用什麼語氣」** 的結構化 Wiki。

## 架構（三層）
- `raw/`（只讀，未改動）：questionnaires.md、成長階段建議.md、how_smart_is_your_baby.md、如何使寶寶身強體健.md
- `wiki/`（23 頁）：index.md、log.md、concepts/(11)、entities/(6)、topics/(6)
- `SCHEMA.md`：規範與 agent 檢索「黃金路徑」

## 關鍵設計（為檢索優化）
1. **主檢索頁** `wiki/topics/teaching-playbook.md`：把問卷答案四坐標（英語等級 L0–4、Doman 階段 1–7、城市線級 1–5+港、性格原型 6 類）轉成具體教學動作。
2. **決策流程** `wiki/topics/decision-flow.md`：問卷 → 評估 → AvatarPlan 的六步可執行鏈。
3. **輸出契約** `wiki/topics/avatar-plan-schema.md`：AvatarPlan JSON 欄位（segment/personality/dosage/safety…），LLM 與降級路徑共用。
4. **安全欄** `wiki/concepts/dosage-screen-safety.md`：AAP 螢幕上限 × 線級係數 × 家長接受度的三重夾緊，<3 歲不開對話。
5. 全庫雙向 `[[wiki link]]` 交叉引用，每頁標來源 `[[raw/...]]`，不臆測。

## 已標註的缺口（待補）
- raw/ 未收錄《如何教寶寶閱讀／數學／百科》全本 → method-early-reading 僅原則級；數學/百科頁待補。
- 建議新增「常見概念性錯誤」專頁與中英母語啟蒙差異比較頁。

## 如何使用
agent 每個教學回合：先讀 `decision-flow` → 定位四坐標 → 查 `teaching-playbook` 取腳本 → 查 `dosage-screen-safety` 定分量 → 依 `lesson-plan` / `avatar-plan-schema` 輸出。
