# StudyBuddy 伺服器（本地／Railway）：靜態網站 + 多用戶 API（PostgreSQL）
# - 靜態檔：index.html、asserts/…、/elevenlabs_config.js（ElevenLabs key 由環境變數注入）
# - 用戶：註冊／登入（pbkdf2 雜湊 + session token）、答案、評估快照、教學計畫
# 環境變數：
#   ELEVENLABS_API_KEY / ElEVENLABS_TOKEN / ELEVENLABS_TOKEN   ElevenLabs key（擇一）
#   DATABASE_PRIVATE_URL 或 DATABASE_URL                        Postgres 連線（Railway: ${{ Postgres.DATABASE_PRIVATE_URL }}）
#   PORT / SB_PORT                                             監聽埠（Railway 注入 PORT）
import http.server, os, json, socketserver, sys, re, hashlib, hmac, secrets, urllib.parse, urllib.request
from contextlib import contextmanager

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
            self._send_json(200, {'ok': True, 'db': bool(DB_URL), 'db_host': host, 'db_err': _db_err or None})
            return
        if path == '/api/state':
            try:
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
                c = db()
                if c is None:
                    self._send_json(503, {'error': 'database not configured'}); return
                if user_by_token(c, self._bearer()) is None:
                    self._send_json(401, {'error': 'unauthorized'}); return
            url, err = make_convai_signed_url()
            if err:
                self._send_json(500, {'error': err})
                return
            self._send_json(200, {'url': url})
            return
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
                    self._send_json(401, {'error': '用戶名或密碼錯誤'}); return
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
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print('StudyBuddy: http://localhost:%d  (db: %s)' % (PORT, 'configured' if DB_URL else 'NOT configured — static only'))
        httpd.serve_forever()
