#!/usr/bin/env python3
"""ntfy.sh 推送脚本 — 从命令行参数读取，避免编码问题"""
import sys
import os
import requests

title = sys.argv[1] if len(sys.argv) > 1 else "ACE"
message = sys.argv[2] if len(sys.argv) > 2 else "notification"
priority = sys.argv[3] if len(sys.argv) > 3 else "default"

server = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
topic = os.environ.get("NTFY_TOPIC", "ace-stock-advisor")

try:
    r = requests.post(
        f"{server}/{topic}",
        data=message.encode("utf-8"),
        headers={
            "Title": title.encode("utf-8"),
            "Priority": priority,
            "Tags": "robot",
        },
        timeout=15
    )
    print(f"[NTFY] {r.status_code}")
except Exception as e:
    print(f"[NTFY] Error: {e}")
