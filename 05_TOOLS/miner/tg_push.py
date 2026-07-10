#!/usr/bin/env python3
"""
Telegram Bot 推送模块
用于将 Stock Advisor 荐股报告推送到 Telegram

用法:
  python3 tg_push.py --file /path/to/advisor_YYYYMMDD.md
  python3 tg_push.py --message "今日荐股: xxx"
  python3 tg_push.py --test
"""

import os
import sys
import argparse
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

# TG Bot Token（从环境变量或 miner_env.sh 加载）
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN_1", "")
if not TG_BOT_TOKEN:
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN_2", "")

# 默认聊天 ID（需要先获取）
DEFAULT_CHAT_ID = os.environ.get("TG_CHAT_ID", "")


def get_bot_info():
    """获取 Bot 信息"""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getMe"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_updates():
    """获取最近的更新，从中提取 chat_id"""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getUpdates?limit=10"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("ok"):
                for update in data.get("result", []):
                    # 从消息中提取 chat_id
                    if "message" in update:
                        chat = update["message"].get("chat", {})
                        return chat.get("id")
                    if "channel_post" in update:
                        chat = update["channel_post"].get("chat", {})
                        return chat.get("id")
            return None
    except Exception as e:
        print(f"[TG] getUpdates error: {e}")
        return None


def send_message(chat_id: str, text: str, parse_mode: str = "Markdown"):
    """发送文本消息"""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": str(chat_id),
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                print(f"[TG] Message sent to {chat_id}")
                return True
            else:
                print(f"[TG] Failed: {result}")
                return False
    except Exception as e:
        print(f"[TG] Send error: {e}")
        return False


def send_file(chat_id: str, file_path: str, caption: str = ""):
    """发送文件"""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendDocument"
    
    try:
        boundary = "----WebKitFormBoundary"
        body = []
        
        # chat_id
        body.append(f"--{boundary}\r\n".encode())
        body.append(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'.encode())
        body.append(f"{chat_id}\r\n".encode())
        
        # caption
        if caption:
            body.append(f"--{boundary}\r\n".encode())
            body.append(f'Content-Disposition: form-data; name="caption"\r\n\r\n'.encode())
            body.append(f"{caption}\r\n".encode())
        
        # file
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        filename = Path(file_path).name
        body.append(f"--{boundary}\r\n".encode())
        body.append(f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'.encode())
        body.append(b"Content-Type: text/markdown\r\n\r\n")
        body.append(file_data)
        body.append(f"\r\n--{boundary}--\r\n".encode())
        
        req = urllib.request.Request(
            url,
            data=b"".join(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                print(f"[TG] File sent: {filename}")
                return True
            else:
                print(f"[TG] File send failed: {result}")
                return False
    except Exception as e:
        print(f"[TG] File send error: {e}")
        return False


def push_advisor_report(report_path: str, chat_id: str = None):
    """推送 Stock Advisor 报告到 TG"""
    if not chat_id:
        chat_id = DEFAULT_CHAT_ID
    if not chat_id:
        chat_id = get_updates()
    if not chat_id:
        print("[TG] ERROR: No chat_id found. Please set TG_CHAT_ID env var or send a message to the bot first.")
        return False
    
    if not Path(report_path).exists():
        print(f"[TG] Report not found: {report_path}")
        return False
    
    # 读取报告内容
    with open(report_path, "r", encoding="utf-8") as f:
        report = f.read()
    
    # 提取 TOP2 股票摘要
    top_stocks = []
    for line in report.split("\n"):
        if "**TOP" in line or "## TOP" in line:
            top_stocks.append(line.strip())
    
    # 构造推送消息
    today = datetime.now().strftime("%Y-%m-%d")
    summary = f"📊 *A股每日荐股* — {today}\n\n"
    
    if top_stocks:
        summary += "🎯 *今日推荐:*\n"
        for s in top_stocks[:2]:
            summary += f"  {s}\n"
    else:
        # 提取报告前300字作为摘要
        summary += report[:300] + "...\n"
    
    summary += f"\n📄 完整报告见附件"
    
    # 发送摘要消息
    send_message(chat_id, summary)
    
    # 发送完整报告文件
    send_file(chat_id, report_path, caption=f"Stock Advisor Report - {today}")
    
    return True


def test_connection():
    """测试 TG Bot 连接"""
    print("[TG] Testing bot connection...")
    
    if not TG_BOT_TOKEN:
        print("[TG] ERROR: TG_BOT_TOKEN not set")
        return False
    
    info = get_bot_info()
    if info.get("ok"):
        bot = info["result"]
        print(f"[TG] Bot: @{bot['username']} ({bot['first_name']})")
    else:
        print(f"[TG] Bot info failed: {info}")
        return False
    
    chat_id = get_updates()
    if chat_id:
        print(f"[TG] Chat ID found: {chat_id}")
        # 发送测试消息
        send_message(chat_id, "🤖 ACE Runtime Bot 已连接\n\n世界存活自检系统运行中。")
        return True
    else:
        print("[TG] No chat found. Please send a message to the bot first.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TG Bot Push")
    parser.add_argument("--file", help="Path to advisor report file")
    parser.add_argument("--message", help="Send a text message")
    parser.add_argument("--test", action="store_true", help="Test bot connection")
    parser.add_argument("--chat-id", help="Target chat ID")
    args = parser.parse_args()
    
    if args.test:
        sys.exit(0 if test_connection() else 1)
    elif args.file:
        sys.exit(0 if push_advisor_report(args.file, args.chat_id) else 1)
    elif args.message:
        chat_id = args.chat_id or DEFAULT_CHAT_ID or get_updates()
        if chat_id:
            sys.exit(0 if send_message(chat_id, args.message) else 1)
        else:
            print("[TG] No chat_id found")
            sys.exit(1)
    else:
        parser.print_help()
