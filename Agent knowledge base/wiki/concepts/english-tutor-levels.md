# 英語陪練等級（English Tutor Levels 0–4）

> **類型**: concept
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/questionnaires]] §2.4；[[raw/personality]] §3–§4；[[raw/Task]]

## 摘要
根據「家庭英語環境 + 寶寶能力表現」，SmartBuddy 把寶寶歸入 **Level 0–4** 五個英語等級，並推薦對應內容。這是英語教學的「基礎坐標」，與 Doman 月齡、城市線級、性格原型共同決定教學腳本。

## 五個等級定義（[[raw/questionnaires]] §2.4）

| 等級 | 英文名稱 | 年齡參考 | 能力描述 | 推薦內容 |
|---|---|---|---|---|
| Level 0 | Sound Exposure | 0–18 個月 | 英語聲音暴露期 | 英文兒歌、節奏律動、媽媽聲音朗讀 |
| Level 1 | Word Awareness | 18–30 個月 | 單字意識萌芽 | 實物命名、TPR 指令、簡單繪本 |
| Level 2 | Phrase Builder | 30–42 個月 | 兩詞短句、跟讀 | 圖卡配對、兒歌跟唱、簡單問答 |
| Level 3 | Early Talker | 42–54 個月 | 簡單對話、語音意識 | AI 數字人對話、Phonics 遊戲、主題詞彙 |
| Level 4 | Pre-A1 Starters | 54–72 個月 | 接近 Cambridge Pre-A1 | 數字人角色扮演、故事複述、基礎書寫預備 |

## 等級如何判定
- **輸入**：家庭環境題 E1–E6（[[raw/questionnaires]] §2.1）+ 能力題（0–36 月 EA1–5；36–72 月 EB1–7，§2.2）。
- **0–2 歲**：以「聲音暴露 + 親子互動」為主（EA 題）。
- **3–6 歲**：加入對話、詞彙、語音意識評估（EB 題）。
- **環境等級 env_level 0–3**：由 E1–E6 壓縮（見 [[entities/agent-avatar-personality]] §3），作為「起點資源」維度。

## 等級 × 環境 起點矩陣（參考 [[raw/personality]] §4）
| | L0(0–18m) | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| env3 強 | 沉浸暴露 | 早起步對話 | 主動對話 | 角色扮演 | 故事複述+書寫預備 |
| env2 中 | 穩定暴露 | 跟讀啟蒙 | 簡單問答 | 數字人對話 | 主題詞彙+Phonics |
| env1 弱 | 喚醒興趣 | 實物命名 | TPR 指令 | 短對話 | 圖卡配對 |
| env0 零 | 聲音暴露 | 親子兒歌 | 兒歌跟唱 | 基礎問答 | 日常對話 |

> 矩陣只定「起點內容類型」，最終怎麼講、講多少由性格與分量決定（[[concepts/child-personality-archetypes]]、[[concepts/dosage-screen-safety]]）。

## 對接國際標準
- 依據 WIDA E-ELD、Cambridge YLE Pre-A1 Starters、UK EYFS、CDC 語言里程碑。
- Level 4 對標 **Cambridge YLE Pre-A1 Starters**；是否對接由家長意願 G4 決定（[[raw/questionnaires]] §2.3）。

## 關聯
- 相關概念: [[concepts/doman-seven-stage-framework]]、[[concepts/city-tier-adaptation]]、[[concepts/child-personality-archetypes]]
- 參見: [[topics/english-content-by-level]]、[[topics/teaching-playbook]]

## 引用來源
- [1] [[raw/questionnaires]] §2.1–2.4
- [2] [[raw/personality]] §3–§4 環境等級與起點矩陣
- [3] [[raw/Task]] — SmartBuddy 規格

## 變更記錄
- 2026-08-19: 初始建立。
