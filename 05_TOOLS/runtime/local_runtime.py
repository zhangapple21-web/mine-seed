#!/usr/bin/env python3
"""
ACE Runtime — 本地 Living OS

职责：
  1. 持续运行（while alive）
  2. 从 GitHub 拉取云端 Worker 产出
  3. 推送到 Telegram Bot
  4. 归档到本地记忆
  5. 监听用户消息（可选）

运行环境：Windows 本地（或任何能连 TG API 的环境）

用法:
  python3 local_runtime.py              # 启动主循环
  python3 local_runtime.py --once       # 只跑一轮
  python3 local_runtime.py --test-tg    # 测试 TG 推送
"""

import os
import sys
import json
import time
import signal
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# ============================================================
# 配置
# ============================================================

# GitHub 仓库（本地 clone 路径）
REPO_DIR = Path(os.environ.get("MINE_SEED", Path.home() / "mine-seed"))
CLOUD_DIR = REPO_DIR / "cloud" / "advisor"
PUSHED_LOG = REPO_DIR / "02_MEMORY" / "runtime_pushed.json"

# Telegram Bot
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8384310757:AAEhfTTMaYrV_n9hXFjBUMh2LdeeWkB-Czo")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "")

# 心跳间隔（秒）
HEARTBEAT = int(os.environ.get("RUNTIME_HEARTBEAT", "60"))

# 日志
LOG_DIR = REPO_DIR / "02_MEMORY" / "runtime_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "runtime.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("ACE.Runtime")

_alive = True


def signal_handler(sig, frame):
    global _alive
    log.info(f"[SIGNAL] {sig} received, shutting down...")
    _alive = False


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


# ============================================================
# Git 同步
# ============================================================

def git_pull() -> bool:
    """从 GitHub 拉取最新代码"""
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            changed = "Already up to date" not in result.stdout
            if changed:
                log.info(f"[GIT] Repository updated")
            return changed
        else:
            log.warning(f"[GIT] Pull failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        log.error(f"[GIT] Error: {e}")
        return False


# ============================================================
# TG 推送
# ============================================================

def load_pushed() -> set:
    """加载已推送的文件列表"""
    if PUSHED_LOG.exists():
        try:
            with open(PUSHED_LOG) as f:
                data = json.load(f)
                return set(data.get("advisor", []))
        except:
            pass
    return set()


def save_pushed(pushed: set):
    """保存已推送的文件列表"""
    PUSHED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PUSHED_LOG, "w") as f:
        json.dump({"advisor": sorted(pushed)}, f, ensure_ascii=False, indent=2)


def send_tg_message(text: str) -> bool:
    """发送 TG 文本消息"""
    import urllib.request
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
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
                log.info(f"[TG] Message sent")
                return True
            else:
                log.warning(f"[TG] Failed: {result}")
                return False
    except Exception as e:
        log.error(f"[TG] Send error: {e}")
        return False


def send_tg_file(file_path: Path, caption: str = "") -> bool:
    """发送 TG 文件"""
    import urllib.request
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendDocument"
    boundary = "----WebKitFormBoundary"
    
    try:
        body = []
        body.append(f"--{boundary}\r\n".encode())
        body.append(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'.encode())
        body.append(f"{TG_CHAT_ID}\r\n".encode())
        
        if caption:
            body.append(f"--{boundary}\r\n".encode())
            body.append(f'Content-Disposition: form-data; name="caption"\r\n\r\n'.encode())
            body.append(f"{caption}\r\n".encode())
        
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        body.append(f"--{boundary}\r\n".encode())
        body.append(f'Content-Disposition: form-data; name="document"; filename="{file_path.name}"\r\n'.encode())
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
                log.info(f"[TG] File sent: {file_path.name}")
                return True
            else:
                log.warning(f"[TG] File send failed: {result}")
                return False
    except Exception as e:
        log.error(f"[TG] File send error: {e}")
        return False


def push_advisor_report(report_path: Path) -> bool:
    """推送 Stock Advisor 报告到 TG"""
    if not report_path.exists():
        log.warning(f"[PUSH] Report not found: {report_path}")
        return False
    
    if not TG_CHAT_ID:
        log.error("[PUSH] TG_CHAT_ID not set")
        return False
    
    with open(report_path, "r", encoding="utf-8") as f:
        report = f.read()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 提取 TOP2
    top_lines = []
    for line in report.split("\n"):
        if any(k in line for k in ["TOP", "推荐", "🎯", "⭐", "**"]):
            top_lines.append(line.strip())
    
    # 构造摘要消息
    summary = f"📊 *A股每日荐股* — {today}\n\n"
    if top_lines:
        summary += "🎯 *今日推荐:*\n"
        for line in top_lines[:3]:
            # 转义 Markdown
            line = line.replace("*", "").replace("_", "")
            summary += f"  {line}\n"
    else:
        summary += report[:400] + "...\n"
    
    summary += f"\n📄 完整报告见附件"
    
    # 发送摘要
    if not send_tg_message(summary):
        return False
    
    # 发送文件
    time.sleep(1)
    if not send_tg_file(report_path, caption=f"Stock Advisor Report - {today}"):
        return False
    
    log.info(f"[PUSH] Report pushed: {report_path.name}")
    return True


# ============================================================
# 检测新产出
# ============================================================

def check_new_advisor_reports(pushed: set) -> list:
    """检查 cloud/advisor/ 目录是否有新报告"""
    if not CLOUD_DIR.exists():
        return []
    
    new_reports = []
    for f in sorted(CLOUD_DIR.glob("advisor_*.md")):
        if f.name not in pushed:
            new_reports.append(f)
    
    return new_reports


# ============================================================
# 主循环
# ============================================================

def run_once():
    """运行一轮"""
    log.info("=" * 50)
    log.info("[LOOP] ACE Runtime — Local Living OS")
    log.info("=" * 50)
    
    # 1. 拉取 GitHub
    changed = git_pull()
    
    # 2. 检查新报告
    pushed = load_pushed()
    new_reports = check_new_advisor_reports(pushed)
    
    if new_reports:
        log.info(f"[LOOP] Found {len(new_reports)} new advisor reports")
        for report in new_reports:
            log.info(f"[LOOP] Pushing: {report.name}")
            if push_advisor_report(report):
                pushed.add(report.name)
                save_pushed(pushed)
                log.info(f"[LOOP] Pushed: {report.name}")
            else:
                log.error(f"[LOOP] Push failed: {report.name}")
                break  # 失败就停一轮，下次重试
    else:
        if changed:
            log.info("[LOOP] Repository changed, no new advisor reports")
        else:
            log.info("[LOOP] No changes")
    
    # 3. 归档日志
    log.info("[LOOP] Cycle complete")


def test_tg():
    """测试 TG 连接"""
    log.info("[TEST] Testing Telegram Bot connection...")
    
    if not TG_CHAT_ID:
        log.error("[TEST] TG_CHAT_ID not set. Please set it first.")
        log.info("[TEST] How to get chat_id:")
        log.info("  1. Send a message to your bot")
        log.info("  2. Visit: https://api.telegram.org/bot<TOKEN>/getUpdates")
        log.info("  3. Find 'chat' -> 'id'")
        return False
    
    # 发送测试消息
    test_msg = "🤖 ACE Runtime — Local Living OS 已连接\n\n推票系统就绪。"
    if send_tg_message(test_msg):
        log.info("[TEST] TG connection OK")
        return True
    else:
        log.error("[TEST] TG connection failed")
        return False


def run_loop():
    """主循环：while alive"""
    log.info("ACE Runtime — Local Living OS 启动")
    log.info(f"Repo: {REPO_DIR}")
    log.info(f"Cloud: {CLOUD_DIR}")
    log.info(f"Heartbeat: {HEARTBEAT}s")
    log.info("=" * 50)
    
    while _alive:
        try:
            run_once()
        except Exception as e:
            log.error(f"[LOOP] Error: {e}")
            import traceback
            traceback.print_exc()
        
        if not _alive:
            break
        
        # 分段睡眠
        for _ in range(HEARTBEAT):
            if not _alive:
                break
            time.sleep(1)
    
    log.info("[LOOP] ACE Runtime stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ACE Runtime — Local Living OS")
    parser.add_argument("--once", action="store_true", help="Run one cycle")
    parser.add_argument("--test-tg", action="store_true", help="Test TG connection")
    parser.add_argument("--chat-id", help="Set TG chat ID")
    args = parser.parse_args()
    
    if args.chat_id:
        TG_CHAT_ID = args.chat_id
        log.info(f"[INIT] Chat ID set: {TG_CHAT_ID}")
    
    if args.test_tg:
        sys.exit(0 if test_tg() else 1)
    elif args.once:
        run_once()
    else:
        run_loop()
