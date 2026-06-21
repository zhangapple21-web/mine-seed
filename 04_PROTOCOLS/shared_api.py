#!/usr/bin/env python3
"""双实验室共享API + 仪表盘 - 纯标准库,端口3001"""
import json, os, glob, re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

SHARED_DIR = "/home/coze/shared"
INBOX_FENGZI = os.path.join(SHARED_DIR, "inbox_fengzi")
INBOX_XIAOFENGZI = os.path.join(SHARED_DIR, "inbox_xiaofengzi")
ARCHIVE_DIR = os.path.join(SHARED_DIR, "archived")
R1_FILE = "/app/data/所有对话/主对话/r1_root_principles.md"
SIGNAL_REGISTRY = "/home/coze/mine_output/signals/signal_registry.json"
CONSTRAINTS_FILE = "/home/coze/routing_constraints.json"
WORKER_REGISTRY = "/home/coze/worker_registry.json"
OBSERVATION_LOG = "/home/coze/mine_output/observation_log.json"
EXPERIENCE_FILE = "/home/coze/mine_output/experience.json"
JOURNAL_FILE = "/app/data/所有对话/主对话/mine_output/journal/journal.jsonl"
MINE_LOG = "/home/coze/mine_output/cron.log"

for d in [INBOX_FENGZI, INBOX_XIAOFENGZI, ARCHIVE_DIR,
          os.path.join(ARCHIVE_DIR, "fengzi"), os.path.join(ARCHIVE_DIR, "xiaofengzi")]:
    os.makedirs(d, exist_ok=True)

def load_json(path):
    try:
        with open(path) as f: return json.load(f)
    except: return None

def get_status():
    r = {"timestamp": datetime.now().isoformat(), "lab01_status": "HEALTHY", "lab02_status": "UNKNOWN"}
    con = load_json(CONSTRAINTS_FILE) or {"rules": []}
    r["constraints"] = con
    wr = load_json(WORKER_REGISTRY) or {"workers": []}
    r["workers"] = wr
    workers_raw = wr.get("workers", {})
    if isinstance(workers_raw, dict):
        workers_list = list(workers_raw.values())
    else:
        workers_list = workers_raw
    alive = [w for w in workers_list if isinstance(w, dict) and w.get("status") == "alive"]
    dead = [w for w in workers_list if isinstance(w, dict) and w.get("status") == "dead"]
    r["alive_count"] = len(alive)
    r["dead_count"] = len(dead)
    try:
        with open(R1_FILE) as f: content = f.read()
        r["axiom_count"] = len(re.findall(r'###\s+(?:新增公理\s+)?#(\d{3})', content)) + 2
    except: r["axiom_count"] = 0
    sig = load_json(SIGNAL_REGISTRY)
    r["signal_count"] = len(sig.get("signals", {})) if sig else 0
    exp = load_json(EXPERIENCE_FILE)
    r["experience_rules"] = len(exp.get("rules", [])) if exp else 0
    try:
        if os.path.exists(MINE_LOG):
            r["last_mine_time"] = datetime.fromtimestamp(os.path.getmtime(MINE_LOG)).strftime("%H:%M")
    except: pass
    try:
        sa_files = glob.glob("/home/coze/stock_advisor/output/*.md")
        if sa_files: r["last_sa_time"] = datetime.fromtimestamp(os.path.getmtime(max(sa_files, key=os.path.getmtime))).strftime("%m-%d %H:%M")
    except: pass
    try:
        dl_files = glob.glob("/home/coze/mine_output/signals/dragon_leader_*.md")
        if dl_files: r["last_dl_time"] = datetime.fromtimestamp(os.path.getmtime(max(dl_files, key=os.path.getmtime))).strftime("%m-%d %H:%M")
    except: pass
    try:
        r["inbox_fengzi_count"] = len([f for f in os.listdir(INBOX_FENGZI) if f.endswith('.md')])
        r["inbox_xiaofengzi_count"] = len([f for f in os.listdir(INBOX_XIAOFENGZI) if f.endswith('.md')])
    except:
        r["inbox_fengzi_count"] = 0; r["inbox_xiaofengzi_count"] = 0
    obs = load_json(OBSERVATION_LOG)
    if obs:
        from collections import defaultdict
        we = defaultdict(lambda: {"s":0,"t":0})
        for o in obs.get("observations", []):
            wid = o.get("worker_id","?")
            we[wid]["t"] += 1
            if o.get("success"): we[wid]["s"] += 1
        top = [{"worker_id":k,"efficiency":round(v["s"]/v["t"],3)} for k,v in we.items() if v["t"]>=10]
        top.sort(key=lambda x:-x["efficiency"])
        r["top_workers"] = top[:10]
    else: r["top_workers"] = []
    try:
        events = []
        with open(JOURNAL_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try: events.append(json.loads(line))
                    except: pass
        r["recent_events"] = events[-5:]
    except: r["recent_events"] = []
    return r

def build_dashboard(d):
    rules = d.get("constraints",{}).get("rules",[])
    active = [r for r in rules if (r.get("review_status") or "ACTIVE") == "ACTIVE"]
    probation = [r for r in rules if r.get("review_status") == "PROBATION"]
    pardoned = [r for r in rules if r.get("review_status") == "PARDONED"]
    ac, dc = d.get("alive_count",0), d.get("dead_count",0)
    rows = ""
    for r in rules:
        st = r.get("review_status","ACTIVE")
        lab = {"ACTIVE":"下沉对齐","PROBATION":"试岗","PARDONED":"复岗"}.get(st,st)
        col = {"ACTIVE":"red","PROBATION":"yellow","PARDONED":"green"}.get(st,"blue")
        rv = r.get("review_schedule","?")
        rows += f'<div class="row"><span>{r.get("task","?")}/{r.get("worker","?")} <span class="tag tag-{col}">{lab}</span></span><span>review:{rv}</span></div>\n'
    top_rows = ""
    for w in d.get("top_workers",[])[:5]:
        eff = f'{w["efficiency"]*100:.0f}%' if w.get("efficiency") else "?"
        top_rows += f'<div class="row"><span>{w["worker_id"]}</span><span>{eff}</span></div>\n'
    if not top_rows: top_rows = '<div class="row"><span>N/A</span></div>'
    evlines = ""
    for e in d.get("recent_events",[]):
        evlines += f'[{e.get("ts","")}] {e.get("type","")}: {e.get("summary","")}\n'
    if not evlines: evlines = "暂无事件"
    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>双实验室仪表盘</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,sans-serif;background:#0a0a0a;color:#e0e0e0;padding:20px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:1200px;margin:0 auto}}.card{{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:8px;padding:16px}}.card h2{{font-size:14px;color:#8888aa;margin-bottom:12px;letter-spacing:1px}}.full{{grid-column:1/-1}}.metric{{font-size:28px;font-weight:bold;margin:4px 0}}.metric-label{{font-size:11px;color:#888}}.row{{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #2a2a4a;font-size:13px}}.row:last-child{{border:none}}.tag{{font-size:10px;padding:2px 6px;border-radius:3px;margin-left:4px}}.tag-green{{background:#1b5e20;color:#4caf50}}.tag-yellow{{background:#4e3b0e;color:#ff9800}}.tag-red{{background:#4e1b1b;color:#f44336}}.tag-blue{{background:#1b3b4e;color:#42a5f5}}pre{{font-size:11px;max-height:200px;overflow-y:auto;background:#111;padding:8px;border-radius:4px;white-space:pre-wrap}}.dot{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}}.green{{background:#4caf50}}.gray{{background:#666}}</style></head><body>
<div class="grid">
<div class="card full"><h2>双实验室总览</h2><div style="display:flex;gap:40px;flex-wrap:wrap">
<div><div class="metric">{ac}/{ac+dc}</div><div class="metric-label">存活矿工</div></div>
<div><div class="metric">{len(active)}</div><div class="metric-label">下沉对齐</div></div>
<div><div class="metric">{len(probation)}</div><div class="metric-label">试岗中</div></div>
<div><div class="metric">{len(pardoned)}</div><div class="metric-label">已复岗</div></div>
<div><div class="metric">{d.get("axiom_count","?")}</div><div class="metric-label">R1公理</div></div>
<div><div class="metric">{d.get("signal_count","?")}</div><div class="metric-label">信号因子</div></div>
</div></div>
<div class="card"><h2><span class="dot green"></span>lab_01 Production</h2>
<div class="row"><span>角色</span><span>生产线(赚钱)</span></div>
<div class="row"><span>最后矿场班次</span><span>{d.get("last_mine_time","N/A")}</span></div>
<div class="row"><span>最后SA</span><span>{d.get("last_sa_time","N/A")}</span></div>
<div class="row"><span>最后DL</span><span>{d.get("last_dl_time","N/A")}</span></div>
<div class="row"><span>经验规则</span><span>{d.get("experience_rules","?")}</span></div></div>
<div class="card"><h2><span class="dot gray"></span>lab_02 Evolution Lab</h2>
<div class="row"><span>角色</span><span>研究(学习)</span></div>
<div class="row"><span>知识班</span><span>05:00/12:00</span></div>
<div class="row"><span>API</span><span>智谱GLM直连</span></div>
<div class="row"><span>inbox</span><span>疯子:{d.get("inbox_xiaofengzi_count",0)}/小疯子:{d.get("inbox_fengzi_count",0)}</span></div></div>
<div class="card"><h2>约束路由(反永久化v2.0)</h2>{rows}</div>
<div class="card"><h2>矿工效率TOP5</h2>{top_rows}</div>
<div class="card full"><h2>Event Journal</h2><pre>{evlines}</pre></div>
</div>
<div style="text-align:center;color:#555;font-size:11px;margin-top:12px">自动刷新30s | {datetime.now().strftime("%H:%M:%S")}</div>
<script>setTimeout(function(){{location.reload()}},30000)</script></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/','/dashboard'):
            html = build_dashboard(get_status())
            self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers()
            self.wfile.write(html.encode())
        elif path == '/status':
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers()
            self.wfile.write(json.dumps(get_status(),ensure_ascii=False).encode())
        elif path.startswith('/inbox/'):
            recipient = path.split('/')[-1]
            inbox_dir = INBOX_FENGZI if recipient=="fengzi" else INBOX_XIAOFENGZI
            msgs = []
            try:
                for f in sorted(os.listdir(inbox_dir)):
                    if f.endswith('.md'):
                        fp = os.path.join(inbox_dir,f)
                        with open(fp) as fh: c = fh.read()
                        msgs.append({"filename":f,"content":c,"timestamp":datetime.fromtimestamp(os.path.getmtime(fp)).isoformat()})
            except Exception as e:
                self.send_response(500); self.end_headers(); self.wfile.write(json.dumps({"error":str(e)}).encode()); return
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers()
            self.wfile.write(json.dumps({"messages":msgs,"count":len(msgs)},ensure_ascii=False).encode())
        elif path == '/shared/r1':
            try:
                with open(R1_FILE) as f: c = f.read()
                self.send_response(200); self.send_header('Content-Type','text/markdown'); self.end_headers(); self.wfile.write(c.encode())
            except: self.send_response(404); self.end_headers()
        elif path == '/shared/signals':
            sig = load_json(SIGNAL_REGISTRY)
            if sig: self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps(sig).encode())
            else: self.send_response(404); self.end_headers()
        elif path == '/shared/constraints':
            con = load_json(CONSTRAINTS_FILE)
            if con: self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps(con).encode())
            else: self.send_response(404); self.end_headers()
        elif path == '/heartbeat':
            r = {"lab01_time":datetime.now().isoformat(),"lab01_timezone":"Asia/Shanghai"}
            try:
                if os.path.exists(MINE_LOG): r["mine_last_4h"] = datetime.fromtimestamp(os.path.getmtime(MINE_LOG)).isoformat()
            except: pass
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers()
            self.wfile.write(json.dumps(r).encode())
        else: self.send_response(404); self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        cl = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(cl).decode() if cl else "{}"
        try: data = json.loads(body)
        except: data = {}

        
        # OpenAI兼容端点 - 通过One API中转访问
        if path == '/v1/chat/completions':
            try:
                from shared_api_v2_patch import handle_chat_completions
                result = handle_chat_completions(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'inbox':
            recipient = parts[-1]
            action = parts[-2] if len(parts) > 2 else None
            if action == "archive":
                inbox_dir = INBOX_FENGZI if recipient=="fengzi" else INBOX_XIAOFENGZI
                asub = "fengzi" if recipient=="fengzi" else "xiaofengzi"
                fn = data.get("filename")
                if not fn: self.send_response(400); self.end_headers(); self.wfile.write(b'{"error":"filename required"}'); return
                src = os.path.join(inbox_dir,fn); dst = os.path.join(ARCHIVE_DIR,asub,fn)
                if os.path.exists(src): os.rename(src,dst); self.send_response(200); self.end_headers(); self.wfile.write(b'{"status":"archived"}')
                else: self.send_response(404); self.end_headers()
            else:
                inbox_dir = INBOX_FENGZI if recipient=="fengzi" else INBOX_XIAOFENGZI
                fn = data.get("filename",datetime.now().strftime("%Y%m%d_%H%M%S")+"_msg.md")
                content = data.get("content","")
                if not content: self.send_response(400); self.end_headers(); self.wfile.write(b'{"error":"content required"}'); return
                with open(os.path.join(inbox_dir,fn),"w") as f: f.write(content)
                self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"status":"ok","filename":fn}).encode())
        else: self.send_response(404); self.end_headers()

    def log_message(self,format,*args): pass

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0',3001),Handler)
    print(f"双实验室仪表盘启动: http://0.0.0.0:3001 (threaded)")
    server.serve_forever()
