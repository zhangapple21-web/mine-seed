#!/usr/bin/env python3
"""
双实验室消息总线 - GitHub Gist中继
零端口、零安全组、纯HTTPS出站
用法：
  python3 lab_bus.py push xiaofengzi "消息内容"
  python3 lab_bus.py pull xiaofengzi
  python3 lab_bus.py heartbeat lab01
  python3 lab_bus.py status
  python3 lab_bus.py push_file xiaofengzi /path/to/file.md
"""
import sys, json, os, time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError

GH_PAT = os.environ.get("GH_PAT", "{{GH_PAT}}")
GIST_ID = os.environ.get("LAB_BUS_GIST_ID", "03c87ff7f013daef66970a21ff2c428d")
API_BASE = "https://api.github.com/gists"

def gh_req(url, method="GET", data=None, retries=2):
    headers = {"Authorization": f"token {GH_PAT}", "Content-Type": "application/json", "Accept": "application/vnd.github.v3+json"}
    body = json.dumps(data).encode() if data else None
    for i in range(retries + 1):
        try:
            req = Request(url, data=body, headers=headers, method=method)
            with urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            if e.code == 403 and i < retries:
                wait = min(int(e.headers.get("X-RateLimit-Reset", time.time()+60)) - int(time.time()), 30)
                if wait > 0: time.sleep(wait)
                continue
            return {"error": f"HTTP {e.code}"}
        except Exception as e:
            if i < retries: time.sleep(3); continue
            return {"error": str(e)}

def read_gist(): return gh_req(f"{API_BASE}/{GIST_ID}")
def update_gist(files_data):
    files = {k: {"content": json.dumps(v, ensure_ascii=False) if isinstance(v, (dict,list)) else v} for k,v in files_data.items()}
    return gh_req(f"{API_BASE}/{GIST_ID}", "PATCH", {"files": files})

def push(recipient, content):
    inbox = f"inbox_{recipient}.json"
    gist = read_gist()
    cur = json.loads(gist["files"][inbox]["content"]) if inbox in gist.get("files",{}) else {"messages":[]}
    sender = "fengzi" if recipient == "xiaofengzi" else "xiaofengzi"
    cur["messages"].append({"from": sender, "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "content": content})
    if len(cur["messages"]) > 50: cur["messages"] = cur["messages"][-50:]
    r = update_gist({inbox: cur})
    ok = "error" not in r
    print(f"{'OK' if ok else 'FAIL'} -> {recipient}: {content[:60]}")
    return ok

def pull(recipient, clear=True):
    inbox = f"inbox_{recipient}.json"
    gist = read_gist()
    cur = json.loads(gist["files"][inbox]["content"]) if inbox in gist.get("files",{}) else {"messages":[]}
    msgs = cur.get("messages", [])
    if not msgs: print("EMPTY"); return []
    for i, m in enumerate(msgs):
        print(f"[{i+1}] {m.get('from','?')} @ {m.get('time','?')}")
        print(f"    {m.get('content','')[:120]}")
    if clear:
        cur["messages"] = []
        update_gist({inbox: cur})
        print(f"READ {len(msgs)}, cleared")
    return msgs

def push_file(recipient, filepath):
    with open(filepath) as f: content = f.read()
    return push(recipient, f"## {os.path.basename(filepath)}\n{content}")

def heartbeat(lab_id):
    gist = read_gist()
    hb = json.loads(gist["files"]["heartbeat.json"]["content"]) if "heartbeat.json" in gist.get("files",{}) else {}
    hb[f"{lab_id}_time"] = datetime.now().isoformat()
    update_gist({"heartbeat.json": hb})
    print(f"HB {lab_id}: {hb}")

def status():
    gist = read_gist()
    print(f"LAB-BUS Updated: {gist.get('updated_at','?')}")
    for fn, fd in gist.get("files",{}).items():
        try:
            c = json.loads(fd["content"])
            print(f"  {fn}: {len(c.get('messages',[]))} msgs" if "messages" in c else f"  {fn}: {json.dumps(c,ensure_ascii=False)[:80]}")
        except: print(f"  {fn}: parse error")

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "push" and len(sys.argv) >= 4: push(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "pull" and len(sys.argv) >= 3: pull(sys.argv[2])
    elif cmd == "heartbeat" and len(sys.argv) >= 3: heartbeat(sys.argv[2])
    elif cmd == "status": status()
    elif cmd == "push_file" and len(sys.argv) >= 4: push_file(sys.argv[2], sys.argv[3])
    else: print(__doc__)
