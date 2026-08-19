# ElevenLabs — 聽說語音 Agent

> **類型**: entity（product）
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/Task]] §AI agent involved

## 摘要
ElevenLabs 在 SmartBuddy 中負責**聆聽與說話**（Listening and talking agent），即數字人英語對話的語音輸入/輸出層。由 `digital_human.speak()` 調用（見 [[entities/agent-avatar-personality]]、[[topics/avatar-plan-schema]]）。

## 配置（[[raw/Task]]）
- **Voice ID — Standard（標準）**：`WkcRFJo38X9XEP8kGExm`
- **Voice ID — Taiwan（台灣腔）**：`fQj4gJSexpu8RDE2Ii5m`

> 🧠 AI 推理：標準音用於普通話/大陸腔家庭，台灣腔用於台灣/部分粵語家庭；選擇可依家長城市線級（[[concepts/city-tier-adaptation]]）與主要家庭語言（[[raw/questionnaires]] B5）決定。

## 降級
當數字人影片/API 不可用時，`digital_human.speak` 自動降為 TTS 純語音（見 [[concepts/dosage-screen-safety]] §11）。

## 關聯
- 相關實體: [[entities/agent-smartbuddy]]、[[entities/product-simli]]
- 參見: [[topics/avatar-plan-schema]]

## 引用來源
- [1] [[raw/Task]] §AI agent involved

## 變更記錄
- 2026-08-19: 初始建立（Voice ID 實錄自 Task.md）。
