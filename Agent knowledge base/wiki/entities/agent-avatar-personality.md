# Avatar Agent — 兒童英語陪練個性化調度器

> **類型**: entity（agent）
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/personality]]

## 摘要
Avatar Agent 是 SmartBuddy 的「個性化調度器」子模組（對接 `digital_human.py`）。它**不直接產生每句台詞**（那是 `tutor.generate_english_script` 的活），而是在對話前完成三件事：**分類（環境等級）→ 性格推斷（原型）→ 配對（人格/內容/分量）**，輸出 `AvatarPlan` JSON 供數字人渲染。

## 輸入（三類信號，[[raw/personality]] §2）
1. **英語環境** E1–E6（[[raw/questionnaires]] §2.1）
2. **英語基礎** Level 0–4（[[raw/questionnaires]] §2.4）
3. **家長補充描述**（G 開放題 + 評估備註）

## 三大職責
- **§3 環境分類**：E1–E6 → `env_level`（0–3），並以城市線級校準為 `effective_env`（見 [[concepts/city-tier-adaptation]]）。
- **§5 性格推斷**：家長文字 + 評估 → 6 原型（見 [[concepts/child-personality-archetypes]]）。
- **§4/§6/§7 配對**：環境×基礎矩陣定起點內容；性格定人格與內容風格。

## 輸出：AvatarPlan JSON（§9，詳 [[topics/avatar-plan-schema]]）
包含 segment / personality / avatar_persona / content_plan / dosage / safety / parent_tip。

## 安全欄（§1、§11）
- < 3 歲不開數字人對話，只給聲音暴露（[[concepts/english-tutor-levels]] L0）。
- 螢幕分量不得超 `standards.screen_cap(months)`（見 [[concepts/dosage-screen-safety]]）。
- 性格推斷**不作醫療/診斷標籤**。
- 無 LLM key / API 掛時走規則庫降級，輸出同一份 AvatarPlan。

## 系統提示詞
建議加入 `prompts.py` 作為 `SYS_AVATAR`（§10），由 Avatar Agent 推斷性格與配對時使用。

## 關聯
- 相關實體: [[entities/agent-smartbuddy]]
- 相關概念: [[concepts/english-tutor-levels]]、[[concepts/city-tier-adaptation]]、[[concepts/child-personality-archetypes]]、[[concepts/dosage-screen-safety]]
- 參見: [[topics/avatar-plan-schema]]、[[topics/decision-flow]]

## 引用來源
- [1] [[raw/personality]] — Personality 全文

## 變更記錄
- 2026-08-19: 初始建立。
