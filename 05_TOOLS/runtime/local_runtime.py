#!/usr/bin/env python3
"""
ACE Runtime — 本地 Living OS

职责：
  1. 持续运行（while alive）
  2. 从 GitHub 拉取云端 Worker 产出
  3. 推送到 Telegram Bot
  4. 归档到本地记忆
  5. 兜底荐股（工作日9点后，如果云端没生成报告就本地补跑）

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

REPO_DIR = Path(os.environ.get("MINE_SEED", Path.home() / "mine-seed"))
CLOUD_DIR = REPO_DIR / "cloud" / "advisor"
PUSHED_LOG = REPO_DIR / "02_MEMORY" / "runtime_pushed.json"

# Telegram Bot — 从环境变量读取，不硬编码
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "")

HEARTBEAT = int(os.environ.get("RUNTIME_HEARTBEAT", "60"))

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
    if PUSHED_LOG.exists():
        try:
            with open(PUSHED_LOG) as f:
                data = json.load(f)
                return set(data.get("advisor", []))
        except:
            pass
    return set()


def save_pushed(pushed: set):
    PUSHED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PUSHED_LOG, "w") as f:
        json.dump({"advisor": sorted(pushed)}, f, ensure_ascii=False, indent=2)


def send_tg_message(text: str) -> bool:
    import urllib.request
    if not TG_BOT_TOKEN:
        log.error("[TG] TG_BOT_TOKEN not set")
        return False
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
    import urllib.request
    if not TG_BOT_TOKEN:
        log.error("[TG] TG_BOT_TOKEN not set")
        return False
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
    if not report_path.exists():
        log.warning(f"[PUSH] Report not found: {report_path}")
        return False
    if not TG_CHAT_ID:
        log.error("[PUSH] TG_CHAT_ID not set")
        return False
    with open(report_path, "r", encoding="utf-8") as f:
        report = f.read()
    today = datetime.now().strftime("%Y-%m-%d")
    top_lines = []
    for line in report.split("\n"):
        if any(k in line for k in ["TOP", "推荐", "🎯", "⭐", "**"]):
            top_lines.append(line.strip())
    summary = f"📊 *A股每日荐股* — {today}\n\n"
    if top_lines:
        summary += "🎯 *今日推荐:*\n"
        for line in top_lines[:3]:
            line = line.replace("*", "").replace("_", "")
            summary += f"  {line}\n"
    else:
        summary += report[:400] + "...\n"
    summary += f"\n📄 完整报告见附件"
    if not send_tg_message(summary):
        return False
    time.sleep(1)
    if not send_tg_file(report_path, caption=f"Stock Advisor Report - {today}"):
        return False
    log.info(f"[PUSH] Report pushed: {report_path.name}")
    return True


# ============================================================
# 检测新产出
# ============================================================

def check_new_advisor_reports(pushed: set) -> list:
    if not CLOUD_DIR.exists():
        return []
    new_reports = []
    for f in sorted(CLOUD_DIR.glob("advisor_*.md")):
        if f.name not in pushed:
            new_reports.append(f)
    return new_reports


# ============================================================
# 兜底荐股
# ============================================================

def check_advisor_fallback():
    """兜底荐股：工作日9点后，如果云端没生成报告就本地补跑。
    
    双层保险：
    - 云端 cron 8:15 生成（主力）
    - 本地 Runtime 9:00+ 检查，缺了就补（兜底）
    """
    now = datetime.now()
    today = now.strftime("%Y%m%d")
    today_dash = now.strftime("%Y-%m-%d")
    
    if now.weekday() >= 5:
        return
    if now.hour < 9:
        return
    
    today_report = CLOUD_DIR / f"advisor_{today}.md"
    if today_report.exists():
        return
    
    fallback_flag = REPO_DIR / "02_MEMORY" / f".advisor_fallback_{today}"
    if fallback_flag.exists():
        return
    
    log.warning(f"[FALLBACK] 今日荐股报告缺失，本地兜底补跑...")
    
    fallback_flag.parent.mkdir(parents=True, exist_ok=True)
    fallback_flag.write_text(now.isoformat())
    
    advisor_script = REPO_DIR / "05_TOOLS" / "advisor" / "stock_advisor.py"
    advisor_env = REPO_DIR / "05_TOOLS" / "miner" / "free_api.env"
    
    if not advisor_script.exists():
        log.error(f"[FALLBACK] stock_advisor.py not found: {advisor_script}")
        return
    
    try:
        env = os.environ.copy()
        if advisor_env.exists():
            with open(advisor_env) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("export "):
                        parts = line[7:].split("=", 1)
                        if len(parts) == 2:
                            val = parts[1].strip().strip('"').strip("'")
                            env[parts[0]] = val
        
        env["ONE_API_URL"] = ""
        env["FREE_LLM_MODE"] = "1"
        
        result = subprocess.run(
            [sys.executable, str(advisor_script)],
            cwd=str(advisor_script.parent),
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            advisor_out = REPO_DIR / "05_TOOLS" / "mine_output" / "advisor"
            latest = None
            if advisor_out.exists():
                reports = sorted(advisor_out.glob("advisor_*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
                for r in reports:
                    if today in r.name or today_dash in r.name:
                        latest = r
                        break
                if not latest and reports:
                    latest = reports[0]
            
            if latest and latest.exists():
                CLOUD_DIR.mkdir(parents=True, exist_ok=True)
                dest = CLOUD_DIR / f"advisor_{today}.md"
                import shutil
                shutil.copy(latest, dest)
                log.info(f"[FALLBACK] 兜底荐股成功: {dest}")
                push_advisor_report(dest)
            else:
                log.warning("[FALLBACK] stock_advisor.py 执行完但未找到报告文件")
        else:
            log.error(f"[FALLBACK] stock_advisor.py 失败: {result.stderr[:200]}")
            
            log.warning("[FALLBACK] 启动终极降级：free_llm 直接生成")
            try:
                sys.path.insert(0, str(REPO_DIR / "05_TOOLS" / "miner"))
                from free_llm import call
                
                result_llm = call(
                    f"你是A股市场分析师。生成今日({today_dash})的简短荐股报告，推荐2只股票，包含股票代码、名称、推荐理由。格式：Markdown。",
                    system="你是专业的A股投资顾问。",
                    max_tokens=1000,
                    prefer="glm"
                )
                
                report = f"# A股每日荐股 — {today_dash}\n\n{result_llm['content']}\n\n---\n渠道: {result_llm['channel']}/{result_llm['model']} | 耗时: {result_llm['elapsed']:.1f}s | 本地兜底\n"
                
                CLOUD_DIR.mkdir(parents=True, exist_ok=True)
                dest = CLOUD_DIR / f"advisor_{today}.md"
                dest.write_text(report, encoding="utf-8")
                log.info(f"[FALLBACK] 终极降级成功: {dest}")
                push_advisor_report(dest)
            except Exception as e:
                log.error(f"[FALLBACK] 终极降级也失败: {e}")
                
    except subprocess.TimeoutExpired:
        log.error("[FALLBACK] stock_advisor.py 超时(120s)")
    except Exception as e:
        log.error(f"[FALLBACK] 错误: {e}")


# ============================================================
# 主循环
# ============================================================

def check_advisor_fallback():
    """兜底荐股：如果今天是工作日、时间 >= 09:00、cloud/advisor/ 下没有今天的报告，本地补跑。
    
    双层保险：
    - 云端 cron 8:15 生成（主力）
    - 本地 Runtime 9:00+ 检查，缺了就补（兜底）
    """
    now = datetime.now()
    today = now.strftime("%Y%m%d")
    today_dash = now.strftime("%Y-%m-%d")
    
    # 周末不跑
    if now.weekday() >= 5:
        return
    
    # 9 点前不跑（给云端 8:15 留时间）
    if now.hour < 9:
        return
    
    # 检查今天是否已有报告
    today_report = CLOUD_DIR / f"advisor_{today}.md"
    if today_report.exists():
        return  # 云端已生成，不需要兜底
    
    # 检查今天是否已经尝试过兜底（避免反复重试）
    fallback_flag = REPO_DIR / "02_MEMORY" / f".advisor_fallback_{today}"
    if fallback_flag.exists():
        return  # 今天已尝试过
    
    log.warning(f"[FALLBACK] 今日荐股报告缺失，本地兜底补跑...")
    
    # 标记今天已尝试
    fallback_flag.parent.mkdir(parents=True, exist_ok=True)
    fallback_flag.write_text(now.isoformat())
    
    # 运行 stock_advisor.py
    advisor_script = REPO_DIR / "05_TOOLS" / "advisor" / "stock_advisor.py"
    advisor_env = REPO_DIR / "05_TOOLS" / "miner" / "free_api.env"
    
    if not advisor_script.exists():
        log.error(f"[FALLBACK] stock_advisor.py not found: {advisor_script}")
        return
    
    try:
        # 加载免费 API 环境
        env = os.environ.copy()
        if advisor_env.exists():
            # source free_api.env 的 Python 等价
            with open(advisor_env) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("export "):
                        parts = line[7:].split("=", 1)
                        if len(parts) == 2:
                            val = parts[1].strip().strip('"').strip("'")
                            env[parts[0]] = val
        
        # 设置 API（优先用 free_llm，不依赖 Gateway）
        env["ONE_API_URL"] = ""
        env["FREE_LLM_MODE"] = "1"
        
        result = subprocess.run(
            [sys.executable, str(advisor_script)],
            cwd=str(advisor_script.parent),
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            # 查找生成的报告
            advisor_out = REPO_DIR / "05_TOOLS" / "mine_output" / "advisor"
            latest = None
            if advisor_out.exists():
                reports = sorted(advisor_out.glob("advisor_*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
                for r in reports:
                    if today in r.name or today_dash in r.name:
                        latest = r
                        break
                if not latest and reports:
                    latest = reports[0]  # 取最新的
            
            if latest and latest.exists():
                # 复制到 cloud/
                CLOUD_DIR.mkdir(parents=True, exist_ok=True)
                dest = CLOUD_DIR / f"advisor_{today}.md"
                import shutil
                shutil.copy(latest, dest)
                log.info(f"[FALLBACK] 兜底荐股成功: {dest}")
                
                # 推 TG
                push_advisor_report(dest)
            else:
                log.warning("[FALLBACK] stock_advisor.py 执行完但未找到报告文件")
        else:
            log.error(f"[FALLBACK] stock_advisor.py 失败: {result.stderr[:200]}")
            
            # 终极降级：用 free_llm 直接生成
            log.warning("[FALLBACK] 启动终极降级：free_llm 直接生成")
            try:
                sys.path.insert(0, str(REPO_DIR / "05_TOOLS" / "miner"))
                from free_llm import call
                
                result_llm = call(
                    f"你是A股市场分析师。生成今日({today_dash})的简短荐股报告，推荐2只股票，包含股票代码、名称、推荐理由。格式：Markdown。",
                    system="你是专业的A股投资顾问。",
                    max_tokens=1000,
                    prefer="glm"
                )
                
                report = f"# A股每日荐股 — {today_dash}\n\n{result_llm['content']}\n\n---\n渠道: {result_llm['channel']}/{result_llm['model']} | 耗时: {result_llm['elapsed']:.1f}s | 本地兜底\n"
                
                CLOUD_DIR.mkdir(parents=True, exist_ok=True)
                dest = CLOUD_DIR / f"advisor_{today}.md"
                dest.write_text(report, encoding="utf-8")
                log.info(f"[FALLBACK] 终极降级成功: {dest}")
                
                push_advisor_report(dest)
            except Exception as e:
                log.error(f"[FALLBACK] 终极降级也失败: {e}")
                
    except subprocess.TimeoutExpired:
        log.error("[FALLBACK] stock_advisor.py 超时(120s)")
    except Exception as e:
        log.error(f"[FALLBACK] 错误: {e}")


def run_once():
    """运行一轮"""
    log.info("=" * 50)
    log.info("[LOOP] ACE Runtime — Local Living OS")
    log.info("=" * 50)
    
    # 0. 兜底荐股检查（工作日 9 点后，如果云端没生成报告就补跑）
    check_advisor_fallback()
    
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
                break
    else:
        if changed:
            log.info("[LOOP] Repository changed, no new advisor reports")
        else:
            log.info("[LOOP] No changes")
    
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
