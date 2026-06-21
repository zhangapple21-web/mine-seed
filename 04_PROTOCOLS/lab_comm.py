#!/usr/bin/env python3
"""
双通道通信客户端 - lab_02用
通道1（主）: One API反向代理 → lab_01:3000 → localhost:3001
通道2（备）: GitHub Gist中继

用法：
  python3 lab_comm.py pull          # 拉取疯子给小疯子的消息
  python3 lab_comm.py push "内容"   # 推送产出给疯子
  python3 lab_comm.py ping          # 心跳测试
  python3 lab_comm.py status        # 查看状态
"""
import sys, json, os
from datetime import datetime
from urllib.request import Request, urlopen

# 通道1: One API
ONEAPI_URL = "http://140.143.124.211:3000/v1/chat/completions"
ONEAPI_KEY = "{{ONE_API_KEY}}"

# 通道2: GitHub Gist
GH_PAT = os.environ.get("GH_PAT", "{{GH_PAT}}")
GIST_ID = "03c87ff7f013daef66970a21ff2c428d"

def oneapi_cmd(cmd, content=""):
    """通过One API发命令"""
    data = {
        "model": cmd,
        "messages": [{"role": "user", "content": f"[CMD:{cmd}] {content}".strip()}]
    }
    req = Request(ONEAPI_URL,
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"Bearer {ONEAPI_KEY}",
            "Content-Type": "application/json"
        },
        method="POST")
    try:
        with urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        return f"ONEAPI_ERROR: {e}"

def gist_cmd(cmd, content=""):
    """通过GitHub Gist通信"""
    from urllib.error import HTTPError
    API_BASE = "https://api.github.com/gists"
    headers = {"Authorization": f"token {GH_PAT}", "Content-Type": "application/json", "Accept": "application/vnd.github.v3+json"}
    
    if cmd == "pull":
        url = f"{API_BASE}/{GIST_ID}"
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=20) as resp:
                gist = json.loads(resp.read().decode())
            inbox = "inbox_xiaofengzi.json"
            cur = json.loads(gist["files"][inbox]["content"]) if inbox in gist.get("files",{}) else {"messages":[]}
            msgs = cur.get("messages", [])
            if not msgs: return "暂无新消息"
            result = []
            for m in msgs:
                result.append(f"## {m.get('from','?')} @ {m.get('time','?')}\n{m.get('content','')}")
            # 清空
            cur["messages"] = []
            patch_data = {"files": {inbox: {"content": json.dumps(cur, ensure_ascii=False)}}}
            req2 = Request(f"{API_BASE}/{GIST_ID}", data=json.dumps(patch_data).encode(), headers=headers, method="PATCH")
            urlopen(req2, timeout=15)
            return "\n---\n".join(result)
        except Exception as e:
            return f"GIST_ERROR: {e}"
    
    elif cmd == "push":
        inbox = "inbox_fengzi.json"
        # 先读
        url = f"{API_BASE}/{GIST_ID}"
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=20) as resp:
                gist = json.loads(resp.read().decode())
            cur = json.loads(gist["files"][inbox]["content"]) if inbox in gist.get("files",{}) else {"messages":[]}
            cur["messages"].append({"from": "xiaofengzi", "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "content": content})
            if len(cur["messages"]) > 50: cur["messages"] = cur["messages"][-50:]
            patch_data = {"files": {inbox: {"content": json.dumps(cur, ensure_ascii=False)}}}
            req2 = Request(f"{API_BASE}/{GIST_ID}", data=json.dumps(patch_data).encode(), headers=headers, method="PATCH")
            urlopen(req2, timeout=15)
            return "OK"
        except Exception as e:
            return f"GIST_ERROR: {e}"

def pull():
    """拉取消息，先走One API，失败走Gist"""
    result = oneapi_cmd("inbox-xiaofengzi")
    if "ERROR" in result:
        print("One API failed, falling back to Gist")
        result = gist_cmd("pull")
    print(result)

def push(content):
    """推送产出，先走One API，失败走Gist"""
    result = oneapi_cmd("outbox-xiaofengzi", content)
    if "ERROR" in result:
        print("One API failed, falling back to Gist")
        result = gist_cmd("push", content)
    print(result)

def ping():
    result = oneapi_cmd("ping")
    print(result)

def status():
    print("=== One API ===")
    print(oneapi_cmd("ping"))
    print("\n=== Gist ===")
    print(gist_cmd("pull"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "pull": pull()
    elif cmd == "push" and len(sys.argv) >= 3: push(" ".join(sys.argv[2:]))
    elif cmd == "ping": ping()
    elif cmd == "status": status()
    else: print(__doc__)
