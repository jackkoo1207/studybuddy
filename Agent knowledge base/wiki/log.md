# 變更日誌（Change Log）

## 2026-08-19 — 知識庫初建（Ingest）
- ✨ 新增 `SCHEMA.md`：定義三層架構、頁面類型、agent 檢索黃金路徑、品質紅線。
- ✨ 新增 `wiki/index.md`：23 頁索引 + 檢索黃金路徑。
- 📝 新增 11 個概念頁：doman-seven-stage-framework、six-pathways、developmental-profile-scoring、english-tutor-levels、city-tier-adaptation、child-personality-archetypes、dosage-screen-safety、method-tpr、method-phonics、method-early-reading、method-physical-program。
- 📝 新增 6 個實體頁：person-glenn-doman、agent-smartbuddy、agent-avatar-personality、product-elevenlabs、product-simli、product-qwen-seedance。
- 📝 新增 6 個主題頁：teaching-playbook（主檢索頁）、decision-flow、avatar-plan-schema、english-content-by-level、stage-activities、lesson-plan。
- 🔗 建立頁間雙向 `[[wiki link]]` 交叉引用（框架↔教學↔實體）。
- ⚠️ 矛盾/缺口標註：raw/ 中《如何教寶寶閱讀》《如何教寶寶數學》《如何教寶寶百科知識》全本未收錄，早期閱讀/數學/百科僅原則級摘要，待補 raw 來源後擴充。
- 📝 更新 `concepts/method-early-reading`：明定「還不會讀的寶寶」首補書為 Doman《How to Teach Your Baby to Read》；新增 🧠 AI 推理操作綱要與 ⚠️ 整字法 vs 拼音法矛盾標註 + 普通話/粵語跨語系提醒。
- ✨ **ingest `raw/How To Teach Your Baby to Read` 全本（317KB）**：將 `method-early-reading` 由原則級擴寫為完整教案——字卡規格（6×22″/3″紅字/印刷體小寫）、五步路徑（單字→雙詞→片語→句子→書）、字級漸進梯（3″紅→7/8″黑）、0 起點起步法、與 Level 0–4 框架對接；index.md 補 raw 連結。
- 📝 **新增 `concepts/method-teach-baby-to-talk`**：「教寶寶說話」方法頁。來源 = `raw/how_smart_is_your_baby` 的語言發展計畫章（line ~2189–2545，六大規則 2545，Stage IV 聽覺/語言 3481/3567，最佳詞彙/禁 baby talk 3789）。**不需再補 raw 書**——Doman 語言計畫已含於《How Smart Is Your Baby?》專章。內容含七核心理念、六大規則、五項並行活動（對話/詩歌填充/選擇板/指派意義/Stage IV 錨點）、最佳詞彙原則、與英語陪練 agent 對接綱要（L0–L4 映射 + 普通話/粵語跨語系提醒）；index.md 補連結、總頁數 23→24。
- 📝 **新增 `concepts/method-spelling`**：拼寫方法頁。來源 = `raw/How To Teach Your Baby to Read` 拼寫專段（line 557–563：閱讀是腦功能、拼寫是規則型學校科目、嚴格在閱讀之後；line 663 字母延後；line 1031 拼字比賽見證；line 619 print 絕不用 cursive；line 675 早教字母致混淆）。**Doman 無教寶寶拼寫的方法/年齡**——本頁誠實框定為「拼寫 = 閱讀下游的學校科目」，並映射至 L3–L4（標為 AI 推理）；含整字法 vs 拼音法在拼寫上的最大分歧標註、普通話/粵語跨語系提醒；index.md 補連結、總頁數 24→25。

## 來源清單（本次 ingest）
- `raw/questionnaires.md`（家長問卷）
- `raw/成長階段建議.md`（七階段發展 + 家長協助 + 城市線級對比）
- `raw/how_smart_is_your_baby.md`（Doman 感官/動作評估與神經計畫）
- `raw/如何使寶寶身強體健.md`（Doman 體能計畫）
- `personality.md`（Avatar Agent）、`Task.md`（SmartBuddy 規格）

## 下一步建議
- [x] 《如何教寶寶閱讀》已補 raw 並 ingest（method-early-reading 完成）。
- [x] 「教寶寶說話」已 ingest（method-teach-baby-to-talk，來源在 `raw/how_smart_is_your_baby`，無需補書）。
- [x] 「拼寫」已 ingest（method-spelling，來源 `raw/How To Teach Your Baby to Read` line 557–563；Doman 無寶寶教法/年齡）。
- [ ] 若需要：新增 `method-early-writing`（誠實框定：Doman 無寫字年齡/方法，寫字 = 閱讀後續 + 手部皮質對立門檻；用戶已確認 Gentle Revolution 無寫字專書）。
- [ ] 補齊《如何教寶寶數學》《如何教寶寶百科知識》raw 來源 → 新增 method-early-math / method-encyclopedic-knowledge（對應問卷數學/百科學習窗口）。
- [ ] 增加「常見概念性錯誤（conceptual mistakes）」專頁，供 lesson-plan 聚焦。
- [ ] 增 `comparison-` 頁：中英母語寶寶英語啟蒙差異、Doman vs 傳統年齡里程碑對照。
- [ ] 定期 lint：檢查孤立頁、過時結論、缺失引用。
