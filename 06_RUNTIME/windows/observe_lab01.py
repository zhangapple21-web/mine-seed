#!/usr/bin/env python3
"""
ACE Local Observer — Windows 本地观测台
通过 zrok 公网桥观测 lab_01 生产环境的健康状态
不执行矿场任务，仅观测 + 心跳
"""
import os, json, time, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

# Load env
env_path = Path(__file__).parent.parent.parent / "05_TOOLS" / "miner" / "miner_env.sh"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("export ") and "=" in line:
                k, v = line[7:].split("=", 1)
                os.environ[k] = v.strip().strip('"').strip("'")

# Public endpoints
ENDPOINTS = {
    "oneapi": "https://oneapi-v1.shares.zrok.io/v1/models",
    "data":   "https://data-r1-v5.shares.zrok.io/dashboard/",
}

def http_get(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ACE-Observer/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="ignore")[:500]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="ignore")[:500]
    except Exception as e:
        return None, str(e)

def tg_send(text):
    token = os.environ.get("TG_BOT_TOKEN_2", "")
    if not token:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        data = json.dumps({"chat_id": "@ACE_OBSERVER_BOT", "text": text}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[TG] send failed: {e}")
        return False

def observe():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=== ACE Observer @ {ts} ===")
    report = [f"ACE Observer @ {ts}"]
    healthy = 0
    for name, url in ENDPOINTS.items():
        status, body = http_get(url)
        if status == 200 or status == 401:
            print(f"  [OK]   {name:8s} {url} -> {status}")
            report.append(f"[OK] {name} {status}")
            healthy += 1
        else:
            print(f"  [FAIL] {name:8s} {url} -> {status} {body[:100]}")
            report.append(f"[FAIL] {name} {status} {body[:80]}")
    return healthy == len(ENDPOINTS), "\n".join(report)

if __name__ == "__main__":
    ok, report = observe()
    print(f"\nOverall: {'HEALTHY' if ok else 'DEGRADED'}")
    # Save report
    out = Path(__file__).parent / "observer_reports"
    out.mkdir(exist_ok=True)
    log = out / f"{datetime.now().strftime('%Y%m%d')}.log"
    with open(log, "a", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"Report saved: {log}")
