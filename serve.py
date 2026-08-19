# StudyBuddy 本地／Railway 伺服器：自動從環境變數（或 .env 檔）讀取 ElEVENLABS_TOKEN 注入前端，
# 瀏覽器不需貼 API key、不會彈出任何輸入框。
# 用法：
#   本地:    python serve.py                然後開 http://localhost:8123（讀 D:\OPC\.env）
#   Railway: 設環境變數 ElEVENLABS_TOKEN，啟動指令 python serve.py（PORT 由 Railway 注入）
import http.server, os, json, socketserver, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
AGENT_ID = 'agent_0801m0c2cy4sftabmmjhd9bn02vp'
PORT = int(os.environ.get('PORT') or os.environ.get('SB_PORT') or 8123)

def _env_api_key():
    # 精確名稱優先
    for name in ('ELEVENLABS_API_KEY', 'ElEVENLABS_TOKEN', 'ELEVENLABS_TOKEN', 'ELEVANLABS_API_KEY'):
        v = os.environ.get(name, '').strip()
        if v:
            return v
    # 容錯：任何含 ELEVENLABS／ELEVANLABS 且含 KEY／TOKEN 的變數（大小寫不拘）
    for k, v in os.environ.items():
        ku = k.upper()
        if ('ELEVENLABS' in ku or 'ELEVANLABS' in ku) and ('KEY' in ku or 'TOKEN' in ku):
            v = v.strip()
            if v:
                return v
    return ''

def load_config():
    # Railway：從環境變數讀（伺服器端，不下載、不入 git）；支援多種命名
    key = _env_api_key()
    # 本地：從 .env 檔讀
    if not key:
        env_path = os.path.join(ROOT, '.env')
        try:
            for line in open(env_path, encoding='utf-8'):
                line = line.strip()
                if line.startswith('ElEVENLABS_TOKEN='):
                    key = line.split('=', 1)[1].strip().strip('"').strip("'")
        except FileNotFoundError:
            pass
    if not key:
        return 'window.ELEVENLABS_CONFIG = null; // 未設定 ElEVENLABS_TOKEN'
    cfg = {'agentId': AGENT_ID, 'apiKey': key}
    return 'window.ELEVENLABS_CONFIG = %s;' % json.dumps(cfg)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_GET(self):
        if self.path.split('?')[0] == '/elevenlabs_config.js':
            body = load_config().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        sys.stderr.write('[serve.py] %s\n' % (fmt % args))

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print('StudyBuddy: http://localhost:%d  (config auto-injected from .env)' % PORT)
        httpd.serve_forever()
