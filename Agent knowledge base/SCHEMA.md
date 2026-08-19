# SCHEMA.md — BabyStep AI 英語陪練知識庫規範

> 版本：2026-08-19 ｜ 維護者：LLM Wiki 專家 ｜ 適用 agent：`SmartBuddy` / `Avatar Agent`

## 0. 這份知識庫的用途

本知識庫是 **0–6 歲、母語為普通話／粵語的寶寶之 AI 英語陪練**（SmartBuddy）的「編譯型」知識層。
它的唯一目的：**讓 agent 在每次教學決策時，能快速檢索到「該教什麼、怎麼教、教多少、用什麼語氣」**。

原始資料（raw/）只讀，永不改動。本檔（wiki/）是 AI 編譯後的結構化知識，可被 agent 直接檢索。

## 1. 三層架構

```
Agent knowledge base/
├── raw/                 ← 第一層：原始資料（只讀，家長/作者投放）
│   ├── how_smart_is_your_baby.md        （Glenn Doman《How Smart Is Your Baby?》）
│   ├── 如何使寶寶身強體健.md            （Doman 體能計畫書）
│   └── 成長階段建議.md                  （Doman 七階段×六通路 + 家長協助 + 城市線級對比）
├── wiki/                ← 第二層：AI 編譯知識層（本層）
│   ├── index.md          ← 內容目錄（檢索入口）
│   ├── log.md            ← 變更時間線
│   ├── entities/         ← 人物 / 產品 / agent
│   ├── concepts/         ← 框架 / 方法 / 標準
│   └── topics/           ← 主題綜述 / 檢索決策頁
└── SCHEMA.md            ← 第三層：本規範
```

## 2. 頁面類型與命名

| 類型 | 目錄 | 命名規則 | 說明 |
|---|---|---|---|
| entity | `entities/` | `person-*` / `agent-*` / `product-*` | 人物、產品、agent 實體 |
| concept | `concepts/` | `concept-*` / `method-*` | 框架、標準、教學法 |
| topic | `topics/` | `topic-*` | 綜述與檢索決策頁（agent 主要讀這層） |

- 頁面檔名一律 `kebab-case`（小寫、dash 分隔）。
- Wiki 連結用 `[[相对路径，不含副檔名]]`，例如 `[[concepts/english-tutor-levels]]`。
- 所有知識點必須標註來源 `[[raw/xxx]]` 或明確標註「AI 推理」。

## 3. Agent 檢索「API」（黃金路徑）

agent 在任何教學回合，依序檢索：

1. **決策輸入** → 讀家長問卷答案（`[[raw/questionnaires]]`，結構見 `[[topics/decision-flow]]`）。
2. **定位分段** → 由月齡+評估得 Doman 階段（`[[concepts/doman-seven-stage-framework]]`）、英語等級（`[[concepts/english-tutor-levels]]`）、城市線級（`[[concepts/city-tier-adaptation]]`）、性格原型（`[[concepts/child-personality-archetypes]]`）。
3. **取教學腳本** → 讀 `[[topics/teaching-playbook]]`（主檢索頁）與 `[[topics/english-content-by-level]]`、`[[topics/stage-activities]]`。
4. **定分量與安全** → 讀 `[[concepts/dosage-screen-safety]]`，不得超過 AAP 螢幕上限。
5. **產出** → 依 `[[topics/lesson-plan]]` 與 `[[topics/avatar-plan-schema]]` 輸出給前端。

> 若任一步驟資訊不足，先給最穩健的通用起點（預設性格 `socializer`、env 中、Level 依月齡），並在回覆中標註「待家長補充」。

## 4. 內容品質紅線

- **不臆測**：所有發展/教學結論須有 `[[raw/]]` 依據；AI 綜合推理須標 `> 🧠 AI 推理`。
- **標矛盾**：來源間衝突用 `> ⚠️ 矛盾標註` 引用塊。
- **不診斷**：本庫僅供家庭早期發展參考，明確標注「不替代專業醫療／教育評估」。
- **增量更新**：更新頁面保留歷史，追加新內容並記入變更記錄。

## 5. 引用來源一覽

- `[[raw/questionnaires]]` — 家長問卷（決策輸入）
- `[[raw/成長階段建議]]` — Doman 七階段發展 + 家長協助建議 + 城市線級對比
- `[[raw/how_smart_is_your_baby]]` — Doman 感官／動作評估與神經計畫
- `[[raw/如何使寶寶身強體健]]` — Doman 體能計畫（動作／操作／平衡）
- 外部依據（原始問卷聲明）：WIDA E-ELD、Cambridge YLE Pre-A1 Starters、UK EYFS、CDC 語言里程碑、香港衞生署兒童健康資訊。
