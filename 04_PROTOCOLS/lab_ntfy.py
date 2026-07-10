#!/usr/bin/env python3
"""
lab_ntfy.py — ntfy.sh 通信客户端 (lab_01端)
替代 lab_comm.py / lab_bus.py，零端口零认证

功能:
  send <topic> <message>   — 发消息
  recv <topic> [since]     — 收消息
  ping                     — 测试连通性
  check_xfz               — 检查小疯子心跳
  send_cmd <cmd> [payload] — 发命令给小疯子
"""

import json, sys, time, urllib.request

NTFY_BASE = "https://ntfy.sh"
TOPIC_TO_XFZ  = "fengzi_to_xfz"
TOPIC_FROM_XFZ = "xfz_to_fengzi"
TOPIC_XFZ_HB  = "xfz_heartbeat"

def publish(topic, message, title="", priority="default"):
    url = f"{NTFY_BASE}/{topic}"
    headers = {"Content-Type": "application/json", "User-Agent": "ntfy-client"}
    if title: headers["Title"] = title
    if priority != "default": headers["Priority"] = priority
    data = message.encode("utf-8") if isinstance(message, str) else json.dumps(message).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def subscribe(topic, since="10m"):
    url = f"{NTFY_BASE}/{topic}/json?since={since}&poll=1"
    headers = {"Accept": "application/json", "User-Agent": "ntfy-client"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    messages = []
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8")
            for line in text.strip().split("\n"):
                line = line.strip()
                if not line: continue
                try:
                    msg = json.loads(line)
                    if msg.get("event") == "message":
                        messages.append(msg)
                except: pass
    except Exception as e:
        print(f"[ERROR] {e}")
    return messages

def main():
    args = sys.argv[1:]
    if not args:
        args = ["ping"]
    
    cmd = args[0]
    
    if cmd == "send":
        topic = args[1] if len(args) > 1 else "fengzi_lab_test"
        msg = " ".join(args[2:]) if len(args) > 2 else f"test@{int(time.time())}"
        ok = publish(topic, msg)
        print(f"Send to {topic}: {'OK' if ok else 'FAILED'}")
    
    elif cmd == "recv":
        topic = args[1] if len(args) > 1 else TOPIC_FROM_XFZ
        since = args[2] if len(args) > 2 else "10m"
        msgs = subscribe(topic, since)
        print(f"Messages from {topic} (since={since}): {len(msgs)}")
        for m in msgs:
            print(f"  [{m.get('time','')}] {m.get('message','')}")
    
    elif cmd == "ping":
        ok = publish("fengzi_lab_test", json.dumps({"src":"lab_01","cmd":"ping","ts":int(time.time())}), title="ping")
        print(f"Ping: {'OK' if ok else 'FAILED'}")
    
    elif cmd == "check_xfz":
        msgs = subscribe(TOPIC_XFZ_HB, since="30m")
        if msgs:
            latest = msgs[-1]
            print(f"小疯子最新心跳: {latest.get('message','')}")
        else:
            print("小疯子无心跳（30分钟内）")
    
    elif cmd == "send_cmd":
        xfz_cmd = args[1] if len(args) > 1 else "ping"
        payload = {}
        if len(args) > 2:
            try:
                payload = json.loads(" ".join(args[2:]))
            except: payload = {"raw": " ".join(args[2:])}
        msg = json.dumps({"cmd": xfz_cmd, "payload": payload, "ts": int(time.time())})
        ok = publish(TOPIC_TO_XFZ, msg, title=f"cmd:{xfz_cmd}")
        print(f"Send cmd '{xfz_cmd}' to 小疯子: {'OK' if ok else 'FAILED'}")
    
    else:
        print(f"Unknown: {cmd}")
        print("Usage: send|recv|ping|check_xfz|send_cmd")

if __name__ == "__main__":
    main()
