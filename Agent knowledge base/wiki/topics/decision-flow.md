# 決策流程（Decision Flow）：問卷答案 → 教學決策

> **類型**: topic
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/questionnaires]] 使用流程、§0–§2；[[raw/personality]] §2；[[raw/Task]] 工作流

## 摘要
本頁把「agent 收到家長問卷答案」到「產出教學決策」的鏈路寫成可執行步驟。agent 每個新用戶都走這條流程一次（註冊 → 問卷 → 評估 → 教學）。

## 流程總覽
```
註冊登入 → 填問卷(§0 背景) → 依月齡抽題(§1/§2) → 提交
  → 物理評估報告(階段/薄弱/強化)
  → 英語等級 + 內容推薦
  → 若 ≥3歲且達標 → 開啟數字人對話入口
```

## 步驟細解

### Step 0 — 家長背景（[[raw/questionnaires]] §0）
讀取：B1 出生日期（算月齡）、B5 主要家庭語言、F1 城市線級、F2 學歷、F4 家中能否英語、F5 是否聽過 Doman。
→ 輸出：`months`、`tier`、`mother_tongue`、`parent_edu`。

### Step 1 — 物理評估（≥0 月，[[raw/questionnaires]] §1）
- 依月齡取「生理階段 ±1」題目窗口（[[concepts/doman-seven-stage-framework]] 月齡表）。
- 六通路各題 4 點量表打分。
- 計分 → 發育階段、薄弱項、優勢項（[[concepts/developmental-profile-scoring]]）。
→ 輸出：`physical_stage`、薄弱/優勢通路。

### Step 2 — 英語環境 + 能力（[[raw/questionnaires]] §2）
- 環境題 E1–E6 恆顯（含 <18 月只顯環境題）。
- ≥18 月顯能力題：0–36 月 EA1–5；36–72 月 EB1–7。
- 環境 → `env_level`（[[entities/agent-avatar-personality]] §3）；能力 → `english_level` L0–4（[[concepts/english-tutor-levels]]）。
→ 輸出：`env_level`、`english_level`。

### Step 3 — 目標與約束（[[raw/questionnaires]] §2.3）
- G1 優先提升項、G2 每週頻率、G3 螢幕接受度、G4 是否對接國際標準。
→ 輸出：`goal`、`frequency`、`screen_accept`、`align_standard`。

### Step 4 — 性格推斷（[[entities/agent-avatar-personality]] §5）
- 由 G 開放題 + 評估觀察 → 6 原型（[[concepts/child-personality-archetypes]]）。
→ 輸出：`archetype`（主+次）。

### Step 5 — 組裝 AvatarPlan（[[topics/avatar-plan-schema]]）
- segment（env×foundation）、personality、avatar_persona、content_plan、dosage、safety、parent_tip。

### Step 6 — 取教學內容
- 依 `teaching-playbook` 主頁決定內容/方法/分量。
- 若 `english_ready=False`（<3 歲或 L0）→ `mode="exposure"`，不開對話。

## 關鍵分支
- **< 18 月**：只顯環境題 + 物理評估；英語等級鎖 L0。
- **18–36 月**：加 EA 能力題；等級 L1–L2。
- **≥ 36 月**：加 EB 能力題；等級 L2–L4；達標開數字人對話。
- **螢幕接受=0**：全部降為語音/離線實物（[[concepts/dosage-screen-safety]] §11）。

## 關聯
- 參見: [[topics/teaching-playbook]]、[[topics/avatar-plan-schema]]、[[topics/lesson-plan]]
- 依賴: [[concepts/doman-seven-stage-framework]]、[[concepts/english-tutor-levels]]、[[concepts/city-tier-adaptation]]、[[concepts/child-personality-archetypes]]

## 引用來源
- [1] [[raw/questionnaires]] 使用流程、§0–§2
- [2] [[raw/personality]] §2 輸入信號
- [3] [[raw/Task]] 工作流

## 變更記錄
- 2026-08-19: 初始建立。
