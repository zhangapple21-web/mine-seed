#!/usr/bin/env python3
"""
ntfy.sh 推送模块 — 沙箱内即时推送（绕过 TG API 网络限制）

用法:
  python3 ntfy_push.py --topic ace-stock-advisor --title "今日荐股" --message "xxx"
  python3 ntfy_push.py --file /path/to/advisor_report.md --topic ace-stock-advisor
"""

import os
import sys
import argparse
import json
import requests
from pathlib import Path
from datetime import datetime

NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
DEFAULT_TOPIC = os.environ.get("NTFY_TOPIC", "ace-stock-advisor")


def send_notification(topic: str, message: str, title: str = "", priority: str = "default",
                      tags: str = ""):
    """发送 ntfy 通知"""
    url = f"{NTFY_SERVER}/{topic}"
    
    headers = {
        "Content-Type": "text/plain; charset=utf-8",
    }
    if title:
        headers["Title"] = title.encode("utf-8").decode("latin-1")
    if priority in ("min", "low", "default", "high", "urgent"):
        headers["Priority"] = priority
    if tags:
        headers["Tags"] = tags
    
    try:
        r = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=15)
        if r.status_code == 200:
            result = r.json()
            print(f"[NTFY] Sent to {topic}: {result.get('message', 'ok')[:50]}")
            return True
        else:
            print(f"[NTFY] HTTP {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"[NTFY] Send error: {e}")
        return False


def push_advisor_report(report_path: str, topic: str = None):
    """推送 Stock Advisor 报告到 ntfy"""
    if not topic:
        topic = DEFAULT_TOPIC
    
    if not Path(report_path).exists():
        print(f"[NTFY] Report not found: {report_path}")
        return False
    
    with open(report_path, "r", encoding="utf-8") as f:
        report = f.read()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 提取 TOP2
    top_lines = []
    for line in report.split("\n"):
        if any(k in line for k in ["TOP", "推荐", "🎯", "⭐"]):
            top_lines.append(line.strip())
    
    # 构造消息
    summary = f"A股每日荐股 — {today}\n\n"
    if top_lines:
        summary += "今日推荐:\n"
        for line in top_lines[:3]:
            summary += f"  {line}\n"
    else:
        summary += report[:500] + "...\n"
    
    # 发送高优先级通知
    send_notification(
        topic=topic,
        message=summary,
        title=f"每日荐股 {today}",
        priority="high",
        tags="chart_with_upwards_trend,money_with_wings",
    )
    
    # 发送完整报告作为第二条
    send_notification(
        topic=topic,
        message=report[:4000],
        title=f"完整报告 {today}",
        priority="default",
        tags="page_with_curl",
    )
    
    return True


def test_connection():
    """测试 ntfy 连接"""
    print("[NTFY] Testing connection...")
    return send_notification(
        topic=DEFAULT_TOPIC,
        message="ACE Runtime 已连接\n\nStock Advisor 推送系统就绪。",
        title="ACE Runtime 测试",
        priority="default",
        tags="robot",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ntfy.sh Push")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="ntfy topic")
    parser.add_argument("--title", default="", help="Notification title")
    parser.add_argument("--message", help="Message text")
    parser.add_argument("--file", help="Path to advisor report file")
    parser.add_argument("--priority", default="default", help="Priority: min/low/default/high/urgent")
    parser.add_argument("--tags", default="", help="Tags emoji")
    parser.add_argument("--test", action="store_true", help="Test connection")
    args = parser.parse_args()
    
    if args.test:
        sys.exit(0 if test_connection() else 1)
    elif args.file:
        sys.exit(0 if push_advisor_report(args.file, args.topic) else 1)
    elif args.message:
        sys.exit(0 if send_notification(args.topic, args.message, args.title, args.priority, args.tags) else 1)
    else:
        parser.print_help()
