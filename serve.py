# StudyBuddy 伺服器（本地／Railway）：靜態網站 + 多用戶 API（PostgreSQL）
# - 靜態檔：index.html、asserts/…、/elevenlabs_config.js（ElevenLabs key 由環境變數注入）
# - 用戶：註冊／登入（pbkdf2 雜湊 + session token）、答案、評估快照、教學計畫
# 環境變數：
#   ELEVENLABS_API_KEY / ElEVENLABS_TOKEN / ELEVENLABS_TOKEN   ElevenLabs key（擇一）
#   DATABASE_PRIVATE_URL 或 DATABASE_URL                        Postgres 連線（Railway: ${{ Postgres.DATABASE_PRIVATE_URL }}）
#   PORT / SB_PORT                                             監聽埠（Railway 注入 PORT）
import http.server, os, json, socketserver, sys, re, hashlib, hmac, secrets, urllib.parse, urllib.request, threading
from contextlib import contextmanager
from datetime import datetime, timezone

@contextmanager
def _cur(c):  # pg8000 cursor 不支援 with，自訂 context manager
    cur = c.cursor()
    try:
        yield cur
    finally:
        try:
            cur.close()
        except Exception:
            pass

ROOT = os.path.dirname(os.path.abspath(__file__))
AGENT_ID = 'agent_0801m0c2cy4sftabmmjhd9bn02vp'
PORT = int(os.environ.get('PORT') or os.environ.get('SB_PORT') or 8123)
PBKDF2_ITER = 100_000
DB_URL = os.environ.get('DATABASE_PRIVATE_URL') or os.environ.get('DATABASE_URL') or ''

SCHEMA = [
"""CREATE TABLE IF NOT EXISTS users(
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  pass_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now())""",
"""CREATE TABLE IF NOT EXISTS sessions(
  token TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now())""",
"""CREATE TABLE IF NOT EXISTS answers(
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  q_key TEXT NOT NULL,
  q_value TEXT NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY(user_id, q_key))""",
"""CREATE TABLE IF NOT EXISTS snapshots(
  user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  snapshot JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now())""",
"""CREATE TABLE IF NOT EXISTS plans(
  user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  plan_json JSONB NOT NULL,
  schedule_json JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now())""",
]

# ---------- ElevenLabs 簽名 URL（key 只留在伺服器端，瀏覽器永不接觸 key） ----------
def _env_api_key():
    for name in ('ELEVENLABS_API_KEY', 'ElEVENLABS_TOKEN', 'ELEVENLABS_TOKEN', 'ELEVANLABS_API_KEY'):
        v = os.environ.get(name, '').strip()
        if v:
            return v
    for k, v in os.environ.items():
        ku = k.upper()
        if ('ELEVENLABS' in ku or 'ELEVANLABS' in ku) and ('KEY' in ku or 'TOKEN' in ku):
            v = v.strip()
            if v:
                return v
    # 本地開發：從 .env 檔讀
    try:
        for line in open(os.path.join(ROOT, '.env'), encoding='utf-8'):
            line = line.strip()
            if line.startswith('ElEVENLABS_TOKEN='):
                v = line.split('=', 1)[1].strip().strip('"').strip("'")
                if v:
                    return v
    except FileNotFoundError:
        pass
    return ''

def _voice_id():
    for name in ('VOICE_ID', 'ELEVENLABS_VOICE_ID', 'ELEVENLABS_DEFAULT_VOICE_ID'):
        v = os.environ.get(name, '').strip()
        if v:
            return v
    try:
        for line in open(os.path.join(ROOT, '.env'), encoding='utf-8'):
            line = line.strip()
            for prefix in ('VOICE_ID=', 'ELEVENLABS_VOICE_ID='):
                if line.startswith(prefix):
                    v = line.split('=', 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
    except FileNotFoundError:
        pass
    return ''

def _deepseek_key():
    v = os.environ.get('DEEPSEEK_API_KEY', '').strip()
    if v:
        return v
    for k, val in os.environ.items():  # 容錯：任何含 DEEPSEEK 的變數（大小寫不拘）
        ku = k.upper()
        if 'DEEPSEEK' in ku and ('KEY' in ku or 'TOKEN' in ku or ku.endswith('DEEPSEEK')):
            val = val.strip()
            if val:
                return val
    try:
        for line in open(os.path.join(ROOT, '.env'), encoding='utf-8'):
            if line.strip().startswith('DEEPSEEK_API_KEY='):
                v = line.split('=', 1)[1].strip().strip('"').strip("'")
                if v:
                    return v
    except FileNotFoundError:
        pass
    return ''

DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-v4-flash')

_KB_DIR = os.path.join(ROOT, 'Agent knowledge base')


def _lesson_planner_prompt():
    """課程設計師系統提示：優先讀 Agent knowledge base/lesson-planner-agent.md，
    缺失或空白時退回內建精簡版（保持 /api/generate-plan 永不因 KB 問題中斷）。"""
    try:
        with open(os.path.join(_KB_DIR, 'lesson-planner-agent.md'), encoding='utf-8') as f:
            t = f.read().strip()
        if t:
            return t
    except Exception:
        pass
    return DEEPSEEK_SYSTEM_PROMPT


PACKY_BASE_URL = os.environ.get('PACKY_BASE_URL', 'https://www.packyapi.ai')
PACKY_IMAGE_MODEL = os.environ.get('PACKY_IMAGE_MODEL', 'gemini-2.5-flash-image')


def _packy_key():
    """PackyAPI key：GEMINI_API_KEY（gemini 官渠令牌）優先，其次 PACKY_CODE_API_KEY /
    PACKY_CODE_TOKEN（env 或 .env）。"""
    for k in ('GEMINI_API_KEY', 'PACKY_CODE_API_KEY', 'PACKY_CODE_TOKEN'):
        v = os.environ.get(k, '').strip()
        if v:
            return v
    try:
        for line in open(os.path.join(ROOT, '.env'), encoding='utf-8'):
            for k in ('GEMINI_API_KEY=', 'PACKY_CODE_API_KEY=', 'PACKY_CODE_TOKEN='):
                if line.strip().startswith(k):
                    v = line.split('=', 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
    except FileNotFoundError:
        pass
    return ''


def generate_image(prompt, model=None):
    """PackyAPI 出圖：Gemini 系（gemini/banana/nano）走 /v1/chat/completions（回傳 markdown
    ![image](data:...)），其餘（gpt-image-2 等）走 /v1/images/generations（OpenAI 相容）。
    回傳 (url_or_dataurl, err)。"""
    key = _packy_key()
    if not key:
        return None, '未設定 PACKY_CODE_API_KEY（Railway 環境變數）'
    model = model or PACKY_IMAGE_MODEL
    base = PACKY_BASE_URL.rstrip('/')
    if any(k in model.lower() for k in ('gemini', 'banana', 'nano')):
        body = {'model': model, 'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}], 'max_tokens': 4096}
        req = urllib.request.Request(base + '/v1/chat/completions', data=json.dumps(body).encode(),
                                     headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
                                     method='POST')
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=120).read().decode())
            c = r['choices'][0]['message'].get('content')
            text = c if isinstance(c, str) else ''.join(p.get('text', '') for p in c if isinstance(p, dict))
            m = re.search(r'!\[[^\]]*\]\((data:image/[^)]+|https?://[^)]+)\)', text or '')
            if m:
                return m.group(1), None
            return None, 'Gemini 回傳未含圖片'
        except urllib.error.HTTPError as e:
            msg = (e.read().decode() or str(e))[:200] if e.fp else str(e)[:200]
            return None, 'PackyAPI %s: %s' % (e.code, msg)
        except Exception as e:
            return None, 'PackyAPI 失敗：%s' % str(e)[:160]
    body = {'model': model, 'prompt': prompt, 'n': 1, 'size': '1024x1024'}
    req = urllib.request.Request(base + '/v1/images/generations', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
                                 method='POST')
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=90).read().decode())
        data = r.get('data') or []
        if not data:
            return None, 'PackyAPI 回傳無圖片資料'
        item = data[0]
        if item.get('b64_json'):
            return 'data:image/png;base64,' + item['b64_json'], None
        if item.get('url'):
            return item['url'], None
        return None, 'PackyAPI 回傳格式不符'
    except urllib.error.HTTPError as e:
        msg = (e.read().decode() or str(e))[:200] if e.fp else str(e)[:200]
        return None, 'PackyAPI %s: %s' % (e.code, msg)
    except Exception as e:
        return None, 'PackyAPI 失敗：%s' % str(e)[:160]


def packy_models():
    """PackyAPI 模型目錄（用 Railway 的 key）。回傳 (ids, err)。"""
    key = _packy_key()
    if not key:
        return None, '未設定 PACKY_CODE_API_KEY（Railway 環境變數）'
    req = urllib.request.Request(PACKY_BASE_URL.rstrip('/') + '/v1beta/models',
                                 headers={'Authorization': 'Bearer ' + key})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        ids = [m.get('id') for m in (r.get('data') or []) if m.get('id')]
        return ids, None
    except urllib.error.HTTPError as e:
        msg = (e.read().decode() or str(e))[:200] if e.fp else str(e)[:200]
        return None, 'PackyAPI %s: %s' % (e.code, msg)
    except Exception as e:
        return None, 'PackyAPI 失敗：%s' % str(e)[:160]


DEEPSEEK_SYSTEM_PROMPT = """You are the curriculum designer of StudyBuddy, an early-English tutor for children aged 0-6 whose mother tongue is Cantonese or Mandarin. You generate a personalized 4-week English lesson plan from the child's assessment profile.

STRICT OUTPUT: reply with ONLY a JSON object (no markdown fences, no commentary) in exactly this shape:
{
  "weeks": [
    {
      "week": 1,
      "focus": "Chinese weekly topic title",
      "lessons": [
        {
          "day": "Day 1",
          "pillar": "Hear",
          "activity": "short Chinese activity name",
          "how": "short Chinese parent instructions, ending with （每次 X 分）",
          "words": "English target words joined by 、, or — when none",
          "goal": "short Chinese goal"
        }
      ]
    }
  ]
}

RULES:
1. Exactly 4 weeks. Each week has exactly frequency_per_week lessons (Day 1..N from the profile's dosage.frequency_per_week, clamped 2-6).
2. Pillars: Vision = 視覺通路刺激 (visual tracking / card gazing — the input channel that feeds reading), Hear = listening exposure, Read = word/picture recognition, Spell = oral output / phonics. Choose by English level:
   - L0 (exposure mode): Vision + Hear only — high-contrast static card gazing & parent-led tracking, spoken exposure & clapping rhythm; no Spell, minimal or no words, no screen.
   - L1: Vision + Hear + light Read; TPR commands and naming real objects, slow card sweeps.
   - L2: Hear + Read + first Spell (echoing, letter sounds, clapping syllables); Vision continues via letter shapes.
   - L3: all four; "What is this?" Q&A; phonics first sounds (b-b-ball).
   - L4: all four; role-play dialogue, story retelling, spelling aloud (c-a-t).
3. Emphasis — weak points and parent interest decide the pillar mix:
   - Weak pathways (profile.phys.weak = the TWO LOWEST-scoring dimensions of Vision/Hear/Read/Spell): 視覺->Vision, 聽覺->Hear, 閱讀->Read, 拼寫->Spell. The weak pillars get the MAJORITY of lessons across all 4 weeks (e.g. weak 聽覺 -> most lessons are Hear: listening games, TPR, echo games; weak 視覺 -> Vision games every week: static card gazing / parent-led tracking). The FIRST lesson of week 1 is a targeted reinforcement game for the weakest pathway; week 1 focus must include the text 針對薄弱項 and list the weak pathways (e.g. 針對薄弱項：視覺、拼寫).
   - Parent interest (profile.goal): 視覺->Vision-heavy; 聽覺->Hear-heavy; 閱讀->Read-heavy; 拼寫->Spell-heavy.
   - Weak points outrank the goal when they conflict. No weak pathways -> follow the goal; no goal (or legacy value) -> balanced rotation of all four pillars.
4. APP CAPABILITIES: the app can show static text + static image cards, speak English via TTS, and LISTEN to the child's speech (mic). It CANNOT animate/move on-screen elements, play songs/music, or SEE the child (no camera). PARENT ROLE: the app is the tutor — never assign teaching tasks to the parent (no 媽媽持字卡/朗讀/問答); the parent only sets up, sits with the child, and may play along as a peer. MOVEMENT: physical actions (run/jump/point) are only ENCOURAGED by the tutor's voice ("Run! 跑起來!") — never required, observed or verified; the lesson continues regardless. Write how as what the APP shows/says + what the child is invited to do. Short, slow, encouraging English (max 8 words per sentence). Respect dosage: each session <= session_min minutes, screens <= screen_cap_min minutes per day.
5. Target words MUST come from these 6 categories: pet 寵物 (cat, dog, bird, fish, duck, rabbit, hamster, turtle, pig, cow), home device 家居電器 (tv, phone, lamp, clock, bed, bath, door), family 家庭 (mama, daddy, baby, grandma, grandpa, brother, sister), cloth 衣物 (hat, shirt, dress, socks, shoes, coat, trousers), food 食物 (apple, banana, milk, water, egg, bread, rice, cake, cookie, orange, grapes), park 公園 (park, tree, ball, flower, sun, run, slide). Prefer words the app has picture cards for (cat, dog, ball, banana, apple, milk, water, park, tree, bird, pig, star, twinkle, red, blue, nose, clap, hands, car, story, book, run, touch, this, what, moon, sun, cow, duck, fish, bear, lion, monkey, house, baby, mama, daddy, tv, phone, lamp, clock, bed, bath, door, hat, shirt, dress, socks, shoes, coat, trousers, cake, egg, bread, rice, orange, grapes, cookie, candy, flower, hamster, rabbit, turtle). 2-4 words per lesson, English, joined by 、; use — when the activity has no words (physical play / L0 exposure).
6. Pace by personality (profile.personality.primary): cautious/sensitive children get more repetition, praise and slower steps; active/explorer children get movement and games.
7. Follow the content_plan topic and style from the profile (e.g. topic 動物與日常用品, style 韻律拍手 + TPR) — 兒歌 styles become spoken chants / clap-along rhythm (no music).
8. Week focuses must be distinct and progressive: weeks 1-3 build skills toward the goal, week 4 is 綜合複習＋升級預覽 (review + upgrade preview).
9. Write focus/activity/how/goal in Traditional Chinese; words in English.
10. The child's mistakes list may be empty — never invent mistakes. If mistakes exist, weave one corrective mini-step into week 1.
11. Never output anything outside the JSON object.
12. BE CONCISE (parents are busy): focus <= 25 chars, activity <= 18 chars, how <= 30 chars, goal <= 16 chars, words <= 4 items. Whole response under 1400 Chinese characters. No filler, no bullets inside fields."""

def generate_plan_with_deepseek(profile):
    key = _deepseek_key()
    if not key:
        return None, '未設定 DEEPSEEK_API_KEY（Railway 環境變數）'
    body = {
        'model': DEEPSEEK_MODEL,
        'messages': [
            {'role': 'system', 'content': _lesson_planner_prompt()},
            {'role': 'user', 'content': json.dumps(profile, ensure_ascii=False)},
        ],
        'temperature': 0.7,
        'response_format': {'type': 'json_object'},
    }
    last_err = None
    for attempt in range(2):          # DeepSeek 高負載時常慢而非掛：重試一次
        req = urllib.request.Request(
            'https://api.deepseek.com/chat/completions',
            data=json.dumps(body).encode(),
            headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
            method='POST')
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=200).read().decode())
            content = r['choices'][0]['message']['content']
            content = re.sub(r'^```(?:json)?\s*|\s*```$', '', (content or '').strip(), flags=re.S)  # 容錯：剝離 markdown 圍欄
            plan = json.loads(content)
            if not plan.get('weeks') or len(plan['weeks']) != 4:
                return None, 'DeepSeek 回傳格式不符（weeks 需 4 週）'
            return plan, None
        except Exception as e:
            last_err = e
    return None, 'DeepSeek 失敗：%s' % str(last_err)[:160]

_ds_ping = {'t': 0.0, 'ok': False}

def deepseek_ping():
    """輕量 1-token 探測：DeepSeek 在 Railway 路徑是否可用（60s 快取）。"""
    import time as _t
    if _t.time() - _ds_ping['t'] < 60:
        return _ds_ping['ok']
    key = _deepseek_key()
    ok = False
    if key:
        body = {'model': DEEPSEEK_MODEL, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 1}
        req = urllib.request.Request(
            'https://api.deepseek.com/chat/completions',
            data=json.dumps(body).encode(),
            headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
            method='POST')
        try:
            urllib.request.urlopen(req, timeout=15)
            ok = True
        except Exception:
            ok = False
    _ds_ping['t'] = _t.time(); _ds_ping['ok'] = ok
    return ok

def apply_voice_id():
    vid = _voice_id()
    if not vid:
        return None
    key = _env_api_key()
    if not key:
        return None
    req = urllib.request.Request(
        'https://api.elevenlabs.io/v1/convai/agents/' + AGENT_ID,
        data=json.dumps({'conversation_config': {'tts': {'voice_id': vid}}}).encode(),
        headers={'xi-api-key': key, 'Content-Type': 'application/json'},
        method='PATCH')
    try:
        urllib.request.urlopen(req, timeout=25)
        return vid
    except Exception as e:
        sys.stderr.write('[serve.py] voice PATCH failed: %s\n' % e)
        return None

def make_convai_signed_url():
    key = _env_api_key()
    if not key:
        return None, '未設定 ElevenLabs key'
    qs = urllib.parse.urlencode({'agent_id': AGENT_ID, 'include_conversation_id': 'true'})
    req = urllib.request.Request(
        'https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?' + qs,
        headers={'xi-api-key': key},
        method='GET')
    try:
        r = urllib.request.urlopen(req, timeout=20)
        return json.loads(r.read().decode())['signed_url'], None
    except Exception as e:
        return None, str(e)[:200]

# ---------- Postgres ----------
_db = None
_db_err = ''
DB_LOCK = threading.RLock()  # pg8000 連線非 thread-safe；所有 DB 操作需持鎖（DeepSeek 呼叫不持鎖）

def db():
    global _db, _db_err
    if _db is not None:
        return _db
    if not DB_URL:
        return None
    try:
        import pg8000.dbapi
        u = urllib.parse.urlparse(DB_URL)
        _db = pg8000.dbapi.connect(
            user=u.username or 'postgres',
            password=u.password or '',
            host=u.hostname or 'localhost',
            port=u.port or 5432,
            database=(u.path or '/postgres').lstrip('/'))
        with _cur(_db) as cur:
            for stmt in SCHEMA:  # pg8000 不支援單一 execute 多條 SQL，逐句執行
                cur.execute(stmt)
        _db.commit()
        return _db
    except Exception as e:
        _db_err = str(e)[:200]
        sys.stderr.write('[serve.py] DB connect failed: %s\n' % e)
        try:
            if _db is not None:
                _db.rollback()
        except Exception:
            pass
        _db = None  # 下次重試
        return None

# ---------- 密碼雜湊（pbkdf2，stdlib only） ----------
def hash_pw(pw):
    salt = secrets.token_hex(16)
    d = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), PBKDF2_ITER).hex()
    return 'pbkdf2_sha256$%d$%s$%s' % (PBKDF2_ITER, salt, d)

def verify_pw(pw, stored):
    try:
        _, it, salt, d = stored.split('$')
        nd = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), int(it)).hex()
        return hmac.compare_digest(nd, d)
    except Exception:
        return False

def new_session(cur, user_id):
    token = secrets.token_hex(32)
    cur.execute('INSERT INTO sessions(token,user_id) VALUES(%s,%s)', (token, user_id))
    return token

def user_by_token(c, token):
    if not token:
        return None
    with _cur(c) as cur:
        cur.execute('SELECT user_id FROM sessions WHERE token=%s', (token,))
        row = cur.fetchone()
        return row[0] if row else None

# ---------- HTTP ----------
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        # 全站 no-cache（應用很小）：部署後用戶不會拿到舊版 HTML/JS
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    # --- helpers ---
    def _send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            n = int(self.headers.get('Content-Length') or 0)
            return json.loads(self.rfile.read(n).decode('utf-8') or '{}') if n else {}
        except Exception:
            return None

    def _bearer(self):
        h = self.headers.get('Authorization') or ''
        return h[7:].strip() if h.startswith('Bearer ') else ''

    def _require_db(self):
        c = db()
        if c is None:
            self._send_json(503, {'error': 'database not configured'})
            return None
        return c

    # --- API GET ---
    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/healthz':
            host = urllib.parse.urlparse(DB_URL).hostname if DB_URL else None
            self._send_json(200, {
                'ok': True, 'db': bool(DB_URL), 'db_host': host, 'db_err': _db_err or None,
                'deepseek': bool(_deepseek_key()), 'deepseek_ok': deepseek_ping(), 'voice_id': _voice_id() or None,
                'packy_image': bool(_packy_key()), 'packy_model': PACKY_IMAGE_MODEL,
            })
            return
        if path == '/api/packy-models':
            try:
                with DB_LOCK:
                    c = self._require_db()
                    if c is None:
                        return
                    if user_by_token(c, self._bearer()) is None:
                        self._send_json(401, {'error': 'unauthorized'}); return
                ids, err = packy_models()
                if err:
                    self._send_json(502, {'error': err}); return
                self._send_json(200, {'models': ids, 'count': len(ids)})
            except Exception as e:
                sys.stderr.write('[serve.py] /api/packy-models error: %s\n' % e)
                self._send_json(500, {'error': 'server error', 'detail': str(e)[:200]})
            return
        if path == '/api/state':
            try:
                with DB_LOCK:
                    c = self._require_db()
                    if c is None:
                        return
                    uid = user_by_token(c, self._bearer())
                    if uid is None:
                        self._send_json(401, {'error': 'unauthorized'})
                        return
                    with _cur(c) as cur:
                        cur.execute('SELECT q_key,q_value FROM answers WHERE user_id=%s', (uid,))
                        answers = {k: v for k, v in cur.fetchall()}
                        cur.execute('SELECT snapshot FROM snapshots WHERE user_id=%s', (uid,))
                        row = cur.fetchone()
                        snapshot = row[0] if row else None
                        cur.execute('SELECT plan_json, schedule_json FROM plans WHERE user_id=%s', (uid,))
                        row = cur.fetchone()
                        plan = {'plan': row[0], 'schedule': row[1]} if row else None
                self._send_json(200, {'answers': answers, 'snapshot': snapshot, 'plan': plan})
            except Exception as e:
                sys.stderr.write('[serve.py] /api/state error: %s\n' % e)
                self._send_json(500, {'error': 'server error', 'detail': str(e)[:200]})
            return
        super().do_GET()

    # --- API POST ---
    def do_POST(self):
        path = self.path.split('?')[0]
        try:
            self._api_post(path)
        except Exception as e:
            sys.stderr.write('[serve.py] %s error: %s\n' % (path, e))
            try:
                self._send_json(500, {'error': 'server error', 'detail': str(e)[:200]})
            except Exception:
                pass

    def _api_post(self, path):
        if path == '/api/convai-url':
            # 需要登入（DB 未設定時放行，供本地開發）；不依賴 DB
            if DB_URL:
                with DB_LOCK:
                    c = db()
                    if c is None:
                        self._send_json(503, {'error': 'database not configured'}); return
                    if user_by_token(c, self._bearer()) is None:
                        self._send_json(401, {'error': 'unauthorized'}); return
            url, err = make_convai_signed_url()
            if err:
                self._send_json(500, {'error': err})
                return
            self._send_json(200, {'url': url, 'voice_id': _voice_id() or None})
            return
        if path == '/api/gen-image':
            # 生成圖卡（PackyAPI）；需要登入（DB 未設定時放行，供本地開發）
            if DB_URL:
                with DB_LOCK:
                    c = db()
                    if c is None:
                        self._send_json(503, {'error': 'database not configured'}); return
                    if user_by_token(c, self._bearer()) is None:
                        self._send_json(401, {'error': 'unauthorized'}); return
            body = self._read_json()
            if not isinstance(body, dict):
                self._send_json(400, {'error': 'bad request'}); return
            prompt = (body.get('prompt') or '').strip()
            if not prompt:
                self._send_json(400, {'error': '缺少 prompt'}); return
            if len(prompt) > 200:
                self._send_json(400, {'error': 'prompt 過長（≤200 字元）'}); return
            model = (body.get('model') or '').strip()
            if len(model) > 100:
                self._send_json(400, {'error': 'model 名稱過長'}); return
            url, err = generate_image(prompt, model or None)
            if err:
                self._send_json(502, {'error': err}); return
            self._send_json(200, {'ok': True, 'url': url, 'model': model or PACKY_IMAGE_MODEL})
            return
        if path == '/api/generate-plan':
            with DB_LOCK:
                c = db()
                if c is None:
                    self._send_json(503, {'error': 'database not configured'}); return
                if user_by_token(c, self._bearer()) is None:
                    self._send_json(401, {'error': 'unauthorized'}); return
            body = self._read_json()
            if not isinstance(body, dict):
                self._send_json(400, {'error': 'bad request'}); return
            plan, err = generate_plan_with_deepseek(body)  # 慢呼叫：不持鎖
            if err:
                self._send_json(502, {'error': err}); return
            plan['generated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            plan['level'] = body.get('level') or ''
            self._send_json(200, {'plan': plan, 'source': 'deepseek', 'model': DEEPSEEK_MODEL})
            return
        with DB_LOCK:
            c = self._require_db()
            if c is None:
                return
            if path == '/api/register':
                body = self._read_json()
                if not body or not isinstance(body, dict):
                    self._send_json(400, {'error': 'bad request'}); return
                u = (body.get('username') or '').strip()
                p = body.get('password') or ''
                if not re.fullmatch(r'[\w-]{2,32}', u):
                    self._send_json(400, {'error': '用戶名需 2–32 位（字母、數字、_、-）'}); return
                if len(p) < 6:
                    self._send_json(400, {'error': '密碼至少 6 位'}); return
                with _cur(c) as cur:
                    cur.execute('SELECT id FROM users WHERE username=%s', (u,))
                    if cur.fetchone():
                        self._send_json(409, {'error': '此用戶名已存在，請直接登入'}); return
                    cur.execute('INSERT INTO users(username,pass_hash) VALUES(%s,%s) RETURNING id', (u, hash_pw(p)))
                    uid = cur.fetchone()[0]
                    token = new_session(cur, uid)
                c.commit()
                self._send_json(201, {'token': token, 'username': u})
                return
            if path == '/api/login':
                body = self._read_json()
                if not body or not isinstance(body, dict):
                    self._send_json(400, {'error': 'bad request'}); return
                u = (body.get('username') or '').strip()
                p = body.get('password') or ''
                with _cur(c) as cur:
                    cur.execute('SELECT id, pass_hash FROM users WHERE username=%s', (u,))
                    row = cur.fetchone()
                    if not row or not verify_pw(p, row[1]):
                        self._send_json(401, {'error': '用戶名或密碼錯誤（若為遷移前的舊帳號，請重新註冊）'}); return
                    token = new_session(cur, row[0])
                c.commit()
                self._send_json(200, {'token': token, 'username': u})
                return
            if path == '/api/logout':
                t = self._bearer()
                with _cur(c) as cur:
                    cur.execute('DELETE FROM sessions WHERE token=%s', (t,))
                c.commit()
                self._send_json(200, {'ok': True})
                return
            self._send_json(404, {'error': 'not found'})

    # --- API PUT ---
    def do_PUT(self):
        path = self.path.split('?')[0]
        try:
            self._api_put(path)
        except Exception as e:
            sys.stderr.write('[serve.py] %s error: %s\n' % (path, e))
            try:
                self._send_json(500, {'error': 'server error', 'detail': str(e)[:200]})
            except Exception:
                pass

    def _api_put(self, path):
        with DB_LOCK:
            c = self._require_db()
            if c is None:
                return
            uid = user_by_token(c, self._bearer())
            if uid is None:
                self._send_json(401, {'error': 'unauthorized'}); return
            body = self._read_json()
            if body is None:
                self._send_json(400, {'error': 'bad request'}); return
            if path == '/api/answers':
                ans = body.get('answers') or {}
                if not isinstance(ans, dict) or len(ans) > 500:
                    self._send_json(400, {'error': 'bad answers'}); return
                with _cur(c) as cur:
                    for k, v in ans.items():
                        cur.execute(
                            'INSERT INTO answers(user_id,q_key,q_value) VALUES(%s,%s,%s) '
                            'ON CONFLICT (user_id,q_key) DO UPDATE SET q_value=EXCLUDED.q_value, updated_at=now()',
                            (uid, str(k), str(v)))
                c.commit()
                self._send_json(200, {'ok': True, 'count': len(ans)})
                return
            if path == '/api/snapshot':
                snap = body.get('snapshot')
                if not isinstance(snap, dict):
                    self._send_json(400, {'error': 'bad snapshot'}); return
                with _cur(c) as cur:
                    cur.execute(
                        'INSERT INTO snapshots(user_id,snapshot) VALUES(%s,%s::jsonb) '
                        'ON CONFLICT (user_id) DO UPDATE SET snapshot=EXCLUDED.snapshot, updated_at=now()',
                        (uid, json.dumps(snap, ensure_ascii=False)))
                c.commit()
                self._send_json(200, {'ok': True})
                return
            if path == '/api/plan':
                plan, sched = body.get('plan'), body.get('schedule')
                if not isinstance(plan, dict):
                    self._send_json(400, {'error': 'bad plan'}); return
                if not isinstance(sched, dict):
                    sched = {}
                with _cur(c) as cur:
                    cur.execute(
                        'INSERT INTO plans(user_id,plan_json,schedule_json) VALUES(%s,%s::jsonb,%s::jsonb) '
                        'ON CONFLICT (user_id) DO UPDATE SET plan_json=EXCLUDED.plan_json, schedule_json=EXCLUDED.schedule_json, updated_at=now()',
                        (uid, json.dumps(plan, ensure_ascii=False), json.dumps(sched, ensure_ascii=False)))
                c.commit()
                self._send_json(200, {'ok': True})
                return
            self._send_json(404, {'error': 'not found'})

    def log_message(self, fmt, *args):
        sys.stderr.write('[serve.py] %s\n' % (fmt % args))

if __name__ == '__main__':
    vid = apply_voice_id()
    if vid:
        print('Voice ID applied to agent:', vid)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True  # 多執行緒：DeepSeek 慢呼叫不阻塞其他請求
    with socketserver.ThreadingTCPServer(('', PORT), Handler) as httpd:
        print('StudyBuddy: http://localhost:%d  (db: %s)' % (PORT, 'configured' if DB_URL else 'NOT configured — static only'))
        httpd.serve_forever()
