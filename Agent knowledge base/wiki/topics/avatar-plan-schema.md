# AvatarPlan 輸出結構（Schema）

> **類型**: topic
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/personality]] §9、§12

## 摘要
Avatar Agent 最終輸出一份 **AvatarPlan JSON**，供 `digital_human.speak()` 與前端渲染。本頁定義欄位契約——LLM 路徑與規則庫降級路徑（[[concepts/dosage-screen-safety]] §11）**必須輸出同一結構**。

## 欄位定義

```json
{
  "segment": {
    "env_level": 2,            // 0–3 英語環境等級 [concepts/city-tier-adaptation]
    "effective_env": 2.2,      // env_level + tier_bonus
    "foundation": "L2",        // 英語基礎 L0–4 [concepts/english-tutor-levels]
    "matrix_cell": "env2 × L2 → 簡單問答"
  },
  "personality": {
    "primary": "explorer",     // 主原型 [concepts/child-personality-archetypes]
    "secondary": "performer",  // 次原型（可無）
    "confidence": 0.7,
    "from_parent_note": true
  },
  "avatar_persona": "Guide",   // Guide/Companion/Playmate/Host/Captain/Sensory
  "content_plan": {
    "topic": "Animals at the park",
    "target_words": ["run", "dog", "ball", "go"],
    "style": "TPR + 動作命名"   // 來自性格×基礎配對
  },
  "dosage": {
    "session_min": 8,           // 每次時長（受三重夾緊）
    "frequency_per_week": 4,    // 頻次
    "weekly_min": 32,
    "screen_cap_min": 20,       // AAP 上限
    "mode": "video"             // video / tts / offline / exposure
  },
  "safety": {
    "ok": true,
    "notes": ["未超 AAP 螢幕上限", "3 歲以上已開啟對話"]
  },
  "parent_tip": "寶寶好動，建議讓他邊跑邊跟數字人說 'run'。"
}
```

## 欄位說明
- `segment`：環境×基礎定位，決定起點內容（[[raw/personality]] §4）。
- `personality`：性格推斷結果（[[raw/personality]] §5）。
- `avatar_persona`：人格（[[concepts/child-personality-archetypes]] §6）。
- `content_plan`：內容由 `tutor.generate_english_script` 產出（topic/target_words/turns/closing），Avatar 只注入性格提示與分量。
- `dosage`：計算見 [[concepts/dosage-screen-safety]]。
- `safety.ok=false` 時：標註原因（如 <3 歲、螢幕拒絕、超上限），並降級 mode。
- `parent_tip`：依線級與性格調語氣（[[concepts/city-tier-adaptation]]）。

## mode 取值邏輯
- `exposure`：<3 歲或 L0，只聲音暴露。
- `video`：數字人影片（家長接受且未超上限）。
- `tts`：純語音（螢幕接受低或部分降級）。
- `offline`：離線實物活動（家長拒螢幕）。

## 對接點（[[raw/personality]] §12）
`tutor.generate_english_script`(level) → `digital_human.speak`；`standards.screen_cap(months)`、`standards.safety_check`；前端數字人 tab 先取 AvatarPlan 再渲染。

## 關聯
- 參見: [[topics/teaching-playbook]]、[[topics/lesson-plan]]、[[topics/decision-flow]]
- 依賴: [[concepts/english-tutor-levels]]、[[concepts/child-personality-archetypes]]、[[concepts/dosage-screen-safety]]、[[entities/agent-avatar-personality]]

## 引用來源
- [1] [[raw/personality]] §9 AvatarPlan、§12 對接清單

## 變更記錄
- 2026-08-19: 初始建立。
