# 分量計算與螢幕安全（Dosage & Screen Safety）

> **類型**: concept
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/personality]] §8、§11；[[raw/questionnaires]] §2.3（G3）

## 摘要
分量 = **每次時長 × 每週頻次**，並受三重上限夾緊（AAP 螢幕上限 × 城市線級係數 × 家長螢幕接受度）。這是 agent 決定「教多少」的唯一安全約束，必須在產出 AvatarPlan 前計算。

## 8.1 基礎每次時長（依英語等級）

| 基礎 | 每次對話時長 |
|---|---|
| L0 (0–18m) | **0 min**（不開對話，僅聲音暴露） |
| L1 | 5 min |
| L2 | 8 min |
| L3 | 10 min |
| L4 | 12 min |

## 8.2 頻次（依家長意願 G2 + 性格）
- G2 映射：每天 10 分 → 5–7 次/週；每週 3–4 次 → 3–4 次；每週 1–2 次 → 1–2 次；不確定 → 預設 3 次。
- 性格微調：`observer`/`thinker` 可略減頻次、拉長單次等待；`performer`/`socializer` 可略增頻次。

## 8.3 三重夾緊上限
```
daily_cap   = standards.screen_cap(months)        # AAP 年齡上限（分/日）
tier_factor = {一線:1.0, 二線:0.9, 三線:0.8, 四線:0.6, 五線:0.4, 香港:0.9}[F1]
screen_accept = {完全接受:1.0, 適度:0.7, 盡量減少:0.4, 不接受:0.0}[G3]
session_min = min(base_min, daily_cap * tier_factor * screen_accept)
weekly_min  = session_min * frequency
```
- **家長拒絕螢幕（screen_accept=0）**：關閉數字人影片，改 `digital_human.speak(level="tts")` 純語音 或 離線實物活動。
- **五線/四線**：tier_factor 低，自動把「數字人對話」降為「語音 + 親子實物」（對齊 [[concepts/city-tier-adaptation]]）。

## 降級路徑（無 LLM / 無 API 時，[[raw/personality]] §11）
| 情形 | 行為 |
|---|---|
| 無 LLM key | 關鍵詞計分推性格 + 矩陣 + 基礎時長直出 AvatarPlan；UI 標「離線示範」 |
| < 3 歲 | `english_ready=False` → 關閉對話，`mode="exposure"`，只給聲音暴露內容 |
| 家長拒螢幕 | `mode="tts"` 或 `mode="offline"`，內容轉親子實物活動 |
| 數字人 API 掛 | 自動 L1→L2 預渲染→L3 TTS→L4 文字，persona 不變 |

> 規則庫必須與 LLM 路徑輸出**同一份 AvatarPlan 結構**（見 [[topics/avatar-plan-schema]]），前端不感知走了哪條路。

## 關聯
- 相關概念: [[concepts/english-tutor-levels]]、[[concepts/city-tier-adaptation]]、[[concepts/child-personality-archetypes]]
- 參見: [[topics/avatar-plan-schema]]、[[topics/lesson-plan]]

## 引用來源
- [1] [[raw/personality]] §8 分量計算、§11 降級
- [2] [[raw/questionnaires]] §2.3 G3 螢幕接受度

## 變更記錄
- 2026-08-19: 初始建立。
