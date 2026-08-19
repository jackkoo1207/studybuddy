# 教學計畫範本（Lesson Plan Template）

> **類型**: topic
> **建立時間**: 2026-08-19
> **最後更新**: 2026-08-19
> **來源**: [[raw/Task]] §Lesson；[[raw/personality]] §9；[[topics/teaching-playbook]]

## 摘要
SmartBuddy 須為每位寶寶產出**家長易懂的教學計畫**，並可視為圖結構（節點=活動/概念，邊=先後/依賴）。本頁給 agent 一個產出範本：個人化課程聚焦「概念性錯誤」，並附家長執行提示與進度追蹤。

## 計畫結構（建議）

```
# 寶寶教學計畫 — {姓名} {月齡}
## 1. 當前定位
- 英語等級：L{n}（{英文名}）  ［[concepts/english-tutor-levels]］
- Doman 階段：第{n}階（{腦部期}）
- 城市線級：{F1} ｜ 性格原型：{archetype}
- 薄弱項：{通路} ｜ 優勢項：{通路}

## 2. 本週焦點（conceptual mistake / 目標）
- 聚焦概念性錯誤：{例如 混淆 b/p 首音}
- 優先提升：{G1 選項}

## 3. 每週課表（圖結構可視化）
- 頻次：{frequency} 次/週 ｜ 每次：{session_min} 分鐘
- Day1: {活動} → Day2: {活動} → ...（節點間標「先後/依賴」）

## 4. 活動清單（依等級取 [topics/english-content-by-level]）
- 活動 A：{名稱} ｜ 方法：{TPR/Phonics/繪本} ｜ 目標詞：{...}
- 活動 B：{名稱} ｜ 性格配對：{persona} ｜ 提示：{...}

## 5. 家長執行提示（parent_tip）
- {一句話，依性格與線級調語氣 [concepts/city-tier-adaptation]}

## 6. 進度追蹤
- 已掌握：{topics} ｜ 常錯：{mistakes} ｜ 下一步：{next}
```

## 設計原則（[[raw/Task]] §Lesson）
1. **個人化**：依年齡區間與評估，不給通用模板。
2. **聚焦概念性錯誤**：課程圍繞寶寶具體迷思（如首音混淆、中英混用），而非泛泛而教。
3. **家長易懂**：語氣依城市線級分化（見 [[concepts/city-tier-adaptation]]）；低線全白話、零成本。
4. **圖結構**：活動間標「先後/依賴」，便於排課與 Google Calendar 匯入（[[entities/agent-smartbuddy]]）。

## 與 AvatarPlan 的關係
教學計畫的「活動清單 + 分量」來自 AvatarPlan（[[topics/avatar-plan-schema]]）；本範本是其**家長可讀版**。

## 安全
- 分量不得超 [[concepts/dosage-screen-safety]] 三重夾緊。
- 不診斷；建議專業評估時明確提示。

## 關聯
- 參見: [[topics/teaching-playbook]]、[[topics/avatar-plan-schema]]、[[topics/stage-activities]]
- 依賴: [[concepts/english-tutor-levels]]、[[concepts/child-personality-archetypes]]、[[concepts/dosage-screen-safety]]

## 引用來源
- [1] [[raw/Task]] §Lesson
- [2] [[raw/personality]] §9 AvatarPlan

## 變更記錄
- 2026-08-19: 初始建立。
