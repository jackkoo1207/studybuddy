# Simli Studio — 數字人（Talking Head Avatar）

> **類型**: entity（product）
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/Task]] §Talking head avatar

## 摘要
Simli Studio 提供 SmartBuddy 的**數字人（會說話的頭像）**渲染層。對話腳本由 `tutor.generate_english_script` 產出，經 `digital_human.speak()` 驅動 Simli 數字人演出，並套用 Avatar Agent 配對的人格（見 [[entities/agent-avatar-personality]]、[[concepts/child-personality-archetypes]]）。

## 配置（[[raw/Task]]）
- 模組：`digital_human.py`（P2 負責）。
- 人格由 AvatarPlan.avatar_persona 決定（Guide / Companion / Playmate / Host / Captain / Sensory）。
- 三級降級：L1 預渲染影片 → L2 預渲染 → L3 TTS → L4 文字（見 [[concepts/dosage-screen-safety]] §11）。

## 螢幕約束
數字人影片是否啟用，受家長螢幕接受度 G3 與城市線級夾緊（[[concepts/dosage-screen-safety]]）。`screen_accept=0` 時關閉影片，改純語音或離線實物活動。

## 關聯
- 相關實體: [[entities/product-elevenlabs]]、[[entities/agent-smartbuddy]]
- 參見: [[topics/avatar-plan-schema]]

## 引用來源
- [1] [[raw/Task]] §Talking head avatar、§Software

## 變更記錄
- 2026-08-19: 初始建立。
