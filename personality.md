# Personality

> 適用模組：`digital_human.py`（P2 負責）｜對接：`tutor.py` / `assess.py` / `standards.py` / `questionnaires.md`
> 版本：2026-08-18 ｜ 目標：讓數字人**不是千篇一律念稿**，而是先「看懂這個孩子」，再配對適合他性格的
> 人格、學習內容與分量（頻次 / 時長 / 屏幕上限）。

---

## 1. Agent 角色定位

Avatar Agent 是「**兒童英語陪練的個性化調度器**」。它不直接產生每句台詞（那是 `tutor.generate_english_script` 的活），
而是負責在對話開始前完成三件事：

1. **分類（Classify）**：把娃按「英語環境 × 英語基礎」落到一個起始分段。
2. **性格推斷（Profile）**：結合家長補充描述，推斷娃的「學習性格原型」。
3. **配對（Match）**：根據分段 + 性格，決定
   - 數字人該用哪種**人格（persona）**
   - 該練哪類**學習內容**
   - 每週/每次的**分量（dosage）**

輸出一份 `AvatarPlan` JSON，供 `digital_human.speak()` 與前端渲染使用。

> 設計約束（評審安全欄）：
> - 3 歲以下（`english_ready=False`）不開啟數字人對話，只給聲音暴露類內容（見 §6 降級）。
> - 所有屏幕分量不得超過 `standards.screen_cap(months)` 的 AAP 上限。
> - 性格推斷只用於「內容與語氣配對」，絕不作醫療 / 診斷標籤。

---

## 2. 輸入（三類信號）

Avatar Agent 的輸入來自問卷與評估結果：

| 信號 | 來源 | 內容 |
|---|---|---|
| **英語環境** | `questionnaires.md` §2.1（E1–E6） | 暴露時長、輸入來源、家長互動頻率、標準音接觸、共讀習慣、偏好形式 |
| **英語基礎** | `questionnaires.md` §2.4（Level 0–4） | 由能力題（EA1–5 / EB1–7）算出的英語等級 |
| **家長補充描述** | 問卷 G 區開放題 + 評估備註 | 自由文字：娃的脾氣、興趣、注意力、怕什麼、愛什麼、平時怎麼玩 |

輸入組裝函式建議：`build_avatar_input(assess_report, english_level, env_answers, parent_note)`。

---

## 3. 英語環境分類（English Environment Level）

把 E1–E6 壓縮成一個 `env_level`（0–3），作為「起點資源」維度：

| env_level | 名稱 | 觸發條件（參考 E1–E6） |
|---|---|---|
| **0** 零環境 | 幾乎無輸入 | E1=幾乎沒有 且 E3∈{很少,從不} 且 E4=從未 |
| **1** 弱環境 | 偶爾接觸 | E1≤15min 或 E3=很少 或 E4=偶爾；無固定共讀 |
| **2** 中環境 | 每日可見 | E1=15–30min 且 E3∈{有時,經常} 且 E4≥每週數次；有繪本/兒歌 |
| **3** 強環境 | 沉浸輸入 | E1≥30min 且 E3=經常 且 E4=每天；含親子英文對話 / 母語者 / 補習班 |

> 城市線級（§0.3）作為 env_level 的**校準係數**而非獨立維度：
> 同樣答「每天 30 分鐘」，一線家長的輸入質量（母語者/標準音）通常高於五線，
> 因此 `effective_env = env_level + tier_bonus`，其中 tier_bonus：一線 +0.3、二線 +0.2、三線 +0.1、四線 0、五線 −0.2、香港 +0.2（上限 3）。

---

## 4. 兒童起始分段矩陣（環境 × 基礎）

`segment = (effective_env 四檔, english_foundation 五檔)`。典型組合與默認策略：

| | Found L0 (0–18m) | L1 (18–30m) | L2 (30–42m) | L3 (42–54m) | L4 (54–72m) |
|---|---|---|---|---|---|
| **env 3 強** | 沉浸暴露期 | 早起步對話 | 主動對話 | 角色扮演 | 故事複述+書寫預備 |
| **env 2 中** | 穩定暴露 | 跟讀啟蒙 | 簡單問答 | 數字人對話 | 主題詞彙+Phonics |
| **env 1 弱** | 喚醒興趣 | 實物命名 | TPR 指令 | 短對話 | 圖卡配對 |
| **env 0 零** | 聲音暴露 | 親子兒歌 | 兒歌跟唱 | 基礎問答 | 日常對話 |

> 矩陣只定「起點內容類型」，最終**怎麼講、講多少**由 §5–§7 的性格與分量決定。

---

## 5. 學習性格推斷（Personality Archetype）

從「家長補充描述 + 評估觀察」推斷娃的學習性格原型。共 6 類，每類附**觸發線索詞**與**觀察信號**。

| 原型 | 代號 | 觸發線索詞（家長文字） | 觀察信號 |
|---|---|---|---|
| 探索者 | `explorer` | 好動、坐不住、好奇、到處爬、愛跑 | 移動能力高於語言；注意力短但換活動快 |
| 觀察者 | `observer` | 慢熱、怕生、先看後做、安靜、黏人 | 語言/社交起步慢；需長等待才回應 |
| 社交家 | `socializer` | 愛笑、愛互動、愛跟人玩、愛被注意 | 聽覺/語言佳；主動發聲 |
| 表演者 | `performer` | 愛唱跳、愛重複、愛被誇、小話癆 | 樂於跟讀、重複輸出 |
| 思考者 | `thinker` | 專注、愛拼圖、話少但準、自己玩 | 手部/視覺佳；話少但對 |
| 感官者 | `sensory` | 動手、愛摸、視覺強、要具體、怕抽象 | 觸覺/手部高；需實物 |

**推斷規則（可規則可 LLM）：**
- 優先用家長補充描述命中線索詞計分；同分時以評估通路高低做 tie-break（探索者→移動高，思考者→手部/視覺高，等）。
- 允許主原型 + 次原型（如 `explorer` 70% / `performer` 30%），用於混合內容配比。
- 無足夠資訊 → 默認 `socializer`（最穩健的通用起點）。

---

## 6. 性格 → Avatar 人格配對

數字人依性格切換「人設」，讓娃覺得「這個老師懂我」：

| 兒童性格 | Avatar 人格 | 語氣 / 節奏 | 互動重點 |
|---|---|---|---|
| `explorer` | 活力引導員（Guide） | 快、興奮、邊動邊說 | 大量 TPR、追蹤移動物體、短指令 |
| `observer` | 溫柔陪伴者（Companion） | 慢、輕、長停頓 | 低壓、重複、給足等待時間、不催 |
| `socializer` | 玩伴（Playmate） | 熱絡、輪流、回應多 | 輪替、模仿、誇獎、眼神（鏡頭）互動 |
| `performer` | 小主持（Host） | 節奏強、愛重複、誇 | 兒歌、跟讀、展示、「你真棒」 |
| `thinker` | 探險隊長（Captain） | 平靜、開放提問 | 謎題、選擇題、留白思考 |
| `sensory` | 多感官老師（Sensory） | 邊示範邊說 | 展示+觸摸+說出、具體物品命名 |

> 人格只改「語氣與互動框架」，不改 `tutor` 生成的**目標詞彙與輪數**（內容錨點保持對標標準）。

---

## 7. 性格 × 基礎 → 學習內容配對

| 性格 \ 基礎 | L0/L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| explorer | 動作兒歌、追蹤遊戲 | TPR 指令 + 跑跳命名 | 動起來的問答 | 戶外主題角色扮演 |
| observer | 安靜聆聽、慢節奏兒歌 | 低壓跟讀 | 一對一短對話 | 熟悉主題複述 |
| socializer | 親子對唱、揮手歌 | 輪流問答 | 數字人聊天 | 主題對話 + 朋友情景 |
| performer | 兒歌跟唱、動作歌 | 跟讀 + 表演 | 唱跳式對話 | 迷你表演 / 說唱 |
| thinker | 圖卡靜觀、拼圖配音 | 選擇問答 | 謎題式對話 | 故事邏輯問答 |
| sensory | 實物命名、觸覺兒歌 | 摸得到的詞彙 | 實物問答 | 多感官主題課 |

內容結構統一由 `tutor.generate_english_script` 產出（topic / target_words / turns / closing），
Avatar Agent 只在其 `user_prompt` 注入「性格提示」與「分量」，不改變 JSON 契約。

---

## 8. 分量（Dosage）計算

分量 = **每次時長 × 每週頻次**，並受三重上限夾緊：

### 8.1 基礎每次時長（依基礎等級）
| 基礎 | 每次對話時長 |
|---|---|
| L0 (0–18m) | 0 min（不開對話，僅聲音暴露） |
| L1 | 5 min |
| L2 | 8 min |
| L3 | 10 min |
| L4 | 12 min |

### 8.2 頻次（依家長意願 G2 + 性格）
- G2 選項直接映射：每天 10 分 → 5–7 次/週；每週 3–4 次 → 3–4 次；每週 1–2 次 → 1–2 次；不確定 → 默認 3 次。
- 性格微調：`observer` / `thinker` 可略減頻次、拉長單次等待；`performer` / `socializer` 可略增頻次。

### 8.3 三重夾緊上限
```
daily_cap   = standards.screen_cap(months)        # AAP 年齡上限（分/日）
tier_factor = {1線:1.0, 2線:0.9, 3線:0.8, 4線:0.6, 5線:0.4, 香港:0.9}[F1]
screen_accept = {完全接受:1.0, 適度:0.7, 盡量減少:0.4, 不接受:0.0}[G3]
session_min = min(base_min, daily_cap * tier_factor * screen_accept)
weekly_min  = session_min * frequency
```
- 若 `screen_accept == 0`（家長不接受螢幕）：關閉數字人影片，改推 `digital_human.speak(level="tts")` 純語音 或 離線實物活動（見 §10 降級）。
- 五線/四線：`tier_factor` 低，自動把「數字人對話」降為「語音 + 親子實物」，符合 §0.3 矩陣。

---

## 9. 輸出結構（AvatarPlan JSON）

```json
{
  "segment": {"env_level": 2, "effective_env": 2.2, "foundation": "L2",
              "matrix_cell": "env2 × L2 → 簡單問答"},
  "personality": {"primary": "explorer", "secondary": "performer",
                  "confidence": 0.7, "from_parent_note": true},
  "avatar_persona": "Guide",
  "content_plan": {
    "topic": "Animals at the park",
    "target_words": ["run", "dog", "ball", "go"],
    "style": "TPR + 動作命名"
  },
  "dosage": {"session_min": 8, "frequency_per_week": 4,
             "weekly_min": 32, "screen_cap_min": 20, "mode": "video"},
  "safety": {"ok": true, "notes": ["未超 AAP 屏幕上限", "3 歲以上已開啟對話"]},
  "parent_tip": "寶寶好動，建議讓他邊跑邊跟數字人說 'run'，比坐著念更有效。"
}
```

---

## 10. 系統提示詞模板（SYS_AVATAR）

> 建議加入 `prompts.py` 作為 `SYS_AVATAR`，由 Avatar Agent 在推斷性格與配對時使用。

```
SYS_AVATAR = (
  "你是為 3-6 歲香港寶寶配對數字人英語學習方案的『個性化調度器』。"
  "輸入：寶寶的英語環境等級、英語基礎等級（L0-L4）、家長補充描述。"
  "你要做三件事並只輸出 JSON："
  "1) 從家長描述推斷學習性格原型（explorer/observer/socializer/performer/thinker/sensory），"
  "   可給主+次原型與 confidence；"
  "2) 依性格選擇數字人人格（Guide/Companion/Playmate/Host/Captain/Sensory）；"
  "3) 依『環境×基礎』矩陣與性格，給出學習內容風格與分量"
  "   （session_min 依基礎、frequency 依家長意願、不得超過 screen_cap）。"
  "性格只用於內容與語氣配對，不作任何醫療或能力診斷標籤。"
  "輸出嚴格遵守 AvatarPlan JSON 契約。"
)
```

`avatar_user_prompt(assess_report, english_level, env_answers, parent_note, tier, screen_accept)` 負責把原始信號壓縮成一段 JSON 指令餵給 LLM；
無 LLM / key 時走 §11 規則庫。

---

## 11. 降級（無 LLM 時的規則庫）

對標 `tutor.ENGLISH_FALLBACK` 與 `digital_human.speak` 三級降級，Avatar Agent 也需規則兜底：

| 情形 | 行為 |
|---|---|
| 無 LLM key | 用關鍵詞計分推性格（§5 線索詞表），矩陣（§4）+ 基礎時長（§8.1）直出 AvatarPlan；UI 標「離線示範」 |
| < 3 歲 | `english_ready=False` → 關閉對話，`mode="exposure"`，只給聲音暴露內容 |
| 家長拒絕螢幕 | `mode="tts"` 或 `mode="offline"`，內容轉為親子實物活動 |
| 數字人 API 掛 | `digital_human.speak` 自動 L1→L2 預渲染→L3 TTS→L4 文字，AvatarPlan.persona 不變 |

> 規則庫必須與 LLM 路徑輸出**同一份 AvatarPlan 結構**，前端不感知走了哪條路。

---

## 12. 與現有代碼對接清單

| agent.md 概念 | 對接點 |
|---|---|
| 英語基礎 Level 0–4 | `questionnaires.md` §2.4；`tutor.generate_english_script` 的 `level` |
| 屏幕上限 | `standards.screen_cap(months)`、`standards.safety_check` |
| 環境等級 E1–E6 | `questionnaires.md` §2.1；組裝進 `build_avatar_input` |
| 城市線級係數 | `questionnaires.md` §0.3 矩陣（F1） |
| 對話腳本 | `tutor.generate_english_script` → `digital_human.speak` |
| 三級降級 | `digital_human.api_available / demo_video_path / tts / speak` |
| 提示詞 | 新增 `prompts.SYS_AVATAR` + `prompts.avatar_user_prompt` |
| 前端入口 | `app.py` 數字人對話 tab：先調 Avatar Agent 取 AvatarPlan，再渲染 |

---

*本 Agent 設計依據 Glenn Doman/IAHP 框架、WIDA E-ELD、Cambridge YLE Pre-A1、UK EYFS、CDC 語言里程碑，
及 `questionnaires.md` 之城際線級矩陣；僅作家庭英語啟蒙配對，不替代專業評估。*
