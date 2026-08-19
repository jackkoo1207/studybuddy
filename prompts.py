"""繁中系統提示與模板：評估總結、課程生成、英語對話腳本。
所有生成類提示都要求 JSON 輸出，便於 UI 渲染與離線兜底對齊。
"""

SYS_ASSESS = (
    "你是為香港 0-6 歲寶寶家長服務的早教科創助手。"
    "依據 Glenn Doman 七階段發展框架與權威標準（CDC/EYFS/WIDA/Cambridge YLE），"
    "用繁體中文、溫和專業的語氣，根據家長提供的觀察，指出寶寶所處發展階段與值得加強的領域。"
    "不做醫療診斷，只做發展觀察與建議；若出現明顯落後，提醒家長諮詢兒科或言語治療師。"
)

SYS_COURSE = (
    "你是寶寶早教版『課程設計師』。根據評估結果（階段、薄弱項），"
    "生成一份個性化『建議與強化訓練課程』：每日 10 分鐘、家長可執行、"
    "包含活動名稱、做法、對應的發展目標；英語若為提升目標，單列為英語軌。"
    "活動必須年齡適宜、以親子互動為主，不得建議超過屏幕時間上限。"
)

SYS_ENGLISH = (
    "你是陪伴 3-6 歲香港寶寶練英語的數字人老師。用簡單、慢速、鼓勵的英文與寶寶對話，"
    "句短、詞彙具體、可配合動作；必要處附繁中提示給家長。每次對話 4-6 輪，"
    "以問候、簡單問答、兒歌或數數為主。"
)

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

JSON_AVATAR = """
只輸出 JSON，不要任何額外文字，格式如下：
{
  "segment": {"env_level": 0, "effective_env": 0.0, "foundation": "L0",
              "matrix_cell": "env0 × L0 → 聲音暴露期"},
  "personality": {"primary": "socializer", "secondary": "", "confidence": 0.6, "from_parent_note": false},
  "avatar_persona": "Playmate",
  "content_plan": {"topic": "英文主題", "target_words": ["詞1","詞2"], "style": "內容風格"},
  "dosage": {"session_min": 5, "frequency_per_week": 3, "weekly_min": 15, "screen_cap_min": 20, "mode": "video"},
  "safety": {"ok": true, "notes": ["未超 AAP 屏幕上限"]},
  "parent_tip": "給家長的一句提醒（繁體中文）"
}
"""

# ---------- JSON 輸出契約 ----------

JSON_COURSE = """
只輸出 JSON，不要任何額外文字，格式如下：
{
  "summary": "一句話階段總結（繁體中文）",
  "activities": [
    {"name": "活動名稱", "how": "家長具體做法（2-3 句）", "goal": "對應發展目標", "minutes": 5, "domain": "視覺/聽覺/觸覺/活動能力/語言能力/手部靈活度"}
  ],
  "english_track": [
    {"name": "英語軌活動名稱", "how": "做法", "target": "目標語言點（例：red ball）"}
  ],
  "parent_tip": "給家長的一句提醒（繁體中文）"
}
activities 給 3 條，english_track 給 2 條。
"""

JSON_ENGLISH = """
只輸出 JSON，不要任何額外文字，格式如下：
{
  "topic": "本次對話主題（英文）",
  "target_words": ["核心詞 1", "核心詞 2", "核心詞 3"],
  "turns": [
    {"en": "數字人要說的英文台詞（8 詞以內）", "zh": "給家長的繁中提示與期待回應"}
  ],
  "closing": "結束鼓勵語（英文）"
}
turns 給 4-6 輪。
"""


def assess_user_prompt(report):
    """把 assess.evaluate() 的報告轉成評估總結提示。"""
    lines = [f"- {d['name']}：第 {d['stage']} 階段（{d['status']}）" for d in report["domains"]]
    return (
        f"寶寶 {report['age_label']}，生理月齡對應「{report['chrono_stage_name']}」。\n"
        f"六大發育通路觀察結果：\n" + "\n".join(lines) + "\n"
        f"整體判定：{report['overall_stage_name']}，估算發育月齡 {report['dev_months_est']} 個月。\n"
        f"對標標準：{report['anchor']}\n"
        f"請用 3-4 句繁體中文寫一段家長看得懂的評估總結，指出優勢與最該加強的 1-2 項，語氣鼓勵不焦慮。"
    )


def course_user_prompt(stage_name, age_label, weak_areas, screen_cap_min=15, english_goal=True):
    weak = "、".join(weak_areas) if weak_areas else "尚稱均衡"
    eng = "英語為本次提升目標，請務必給出英語軌。" if english_goal else "本次不需英語軌，english_track 給空陣列。"
    return (
        f"寶寶處於「{stage_name}」（{age_label}）。家長觀察到的薄弱/加強項：{weak}。\n"
        f"屏幕時間上限：{screen_cap_min} 分鐘/日。{eng}\n"
        f"請設計今日可執行的強化訓練課程。" + JSON_COURSE
    )


def english_user_prompt(stage_name, age_label, level_note, target_hint=""):
    extra = f"建議圍繞：{target_hint}。" if target_hint else ""
    return (
        f"寶寶 {age_label}，階段「{stage_name}」，英語程度：{level_note}。{extra}\n"
        f"請生成一段 4-6 輪的英文對話腳本（數字人將唸出）。" + JSON_ENGLISH
    )


# ---------- Avatar 個性化調度器（對接 agent.md） ----------

TIER_FACTOR = {"1線": 1.0, "2線": 0.9, "3線": 0.8, "4線": 0.6, "5線": 0.4, "香港": 0.9}
SCREEN_ACCEPT = {"完全接受": 1.0, "適度使用": 0.7, "盡量減少": 0.4, "不接受": 0.0}
BASE_SESSION_MIN = {"L0": 0, "L1": 5, "L2": 8, "L3": 10, "L4": 12}
G2_FREQ = {"每天 10 分鐘": 6, "每週 3-4 次": 4, "每週 1-2 次": 2, "不確定": 3}


def env_level_from_answers(env_answers):
    """把問卷 E1-E6 壓成 0-3 環境等級（agent.md §3）。"""
    e1 = env_answers.get("E1", "")
    e3 = env_answers.get("E3", "")
    e4 = env_answers.get("E4", "")
    if ("幾乎沒有" in e1) and e3 in ("很少", "從不") and e4 == "從未":
        return 0
    if ("幾乎沒有" in e1) or e3 == "很少" or e4 == "偶爾":
        return 1
    if ("15" in e1 or "30" in e1) and e3 in ("有時", "經常") and e4 in ("每週數次", "每天"):
        return 2
    if ("30" in e1 or "1 小時" in e1) and e3 == "經常" and e4 == "每天":
        return 3
    return 2  # 缺省中環境


def build_avatar_input(assess_report, english_level, env_answers, parent_note,
                       tier="香港", screen_accept="適度使用", g2="不確定"):
    """組裝 Avatar Agent 輸入（agent.md §2 / §8.3）。返回 (input_dict, user_prompt)。"""
    env_level = env_level_from_answers(env_answers)
    bonus = {"1線": 0.3, "2線": 0.2, "3線": 0.1, "4線": -0.2, "5線": -0.2, "香港": 0.2}.get(tier, 0.0)
    effective_env = round(min(3.0, max(0.0, env_level + bonus)), 1)

    months = assess_report.get("months", 36)
    daily_cap = 0  # 實際由 standards.screen_cap 提供，此處為結構示例
    tf = TIER_FACTOR.get(tier, 0.9)
    sa = SCREEN_ACCEPT.get(screen_accept, 0.7)
    base_min = BASE_SESSION_MIN.get(english_level, 8)
    freq = G2_FREQ.get(g2, 3)
    session_min = int(min(base_min, max(0, daily_cap) * tf * sa)) if daily_cap else base_min
    mode = "offline" if sa == 0.0 else ("video" if session_min > 0 else "exposure")

    inp = {
        "age_label": assess_report.get("age_label", ""),
        "english_ready": assess_report.get("english_ready", False),
        "english_level": english_level,
        "env_level": env_level,
        "effective_env": effective_env,
        "tier": tier,
        "screen_accept": screen_accept,
        "g2": g2,
        "parent_note": parent_note or "",
    }
    up = (
        f"寶寶 {inp['age_label']}，英語基礎 {english_level}，環境等級 {effective_env}（原 {env_level}，"
        f"城市線級 {tier} 校正後），家長螢幕接受度 {screen_accept}。\n"
        f"家長補充描述：「{parent_note or '（無）'}」\n"
        f"請推斷學習性格、選擇數字人人格，並給出內容風格與分量"
        f"（session_min 參考 {base_min}、頻次參考 {freq}/週、不得超屏幕上限）。" + JSON_AVATAR
    )
    return inp, up
