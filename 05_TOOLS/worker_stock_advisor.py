#!/usr/bin/env python3
"""
Stock Advisor Worker - Cloud Worker
====================================
Runs stock_advisor.py, saves report to cloud/advisor/, pushes to GitHub.
"""
import os, sys, json, argparse, subprocess, urllib.request, importlib.util
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

CLOUD_DIR = WORKSPACE / "cloud" / "advisor"


def import_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_stock_advisor(date=None):
    date_str = date or datetime.now().strftime("%Y%m%d")
    CLOUD_DIR.mkdir(parents=True, exist_ok=True)
    output_file = CLOUD_DIR / f"advisor_{date_str}.md"

    if output_file.exists():
        return {"status": "skipped", "reason": f"already exists: {output_file.name}"}

    try:
        # Import stock_advisor.py from 05_TOOLS/advisor/
        advisor_path = WORKSPACE / "05_TOOLS" / "advisor" / "stock_advisor.py"
        if not advisor_path.exists():
            return {"status": "error", "error": f"stock_advisor.py not found at {advisor_path}"}

        advisor_module = import_module(advisor_path)
        advisor = advisor_module.StockAdvisor()
        success, report = advisor.run()

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        return {
            "status": "ok" if success else "warning",
            "output": str(output_file),
            "date": date_str,
            "size": len(report)
        }
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "trace": traceback.format_exc()}


def git_push():
    try:
        subprocess.run(["git", "add", "cloud/"], cwd=str(WORKSPACE), capture_output=True)
        subprocess.run(["git", "commit", "-m", f"cloud: advisor {datetime.now().strftime('%Y%m%d')}"],
                       cwd=str(WORKSPACE), capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=str(WORKSPACE), capture_output=True)
        return True
    except Exception as e:
        print(f"[GIT] Push failed: {e}")
        return False


def notify_ntfy(message):
    topic = os.environ.get("NTPY_TOPIC", "ace-cloud-worker")
    if not topic:
        return
    try:
        req = urllib.request.Request(
            f"https://ntfy.sh/{topic}",
            data=message.encode(),
            headers={"Title": "ACE Stock Advisor"},
        )
        urllib.request.urlopen(req, timeout=10)
    except:
        pass


def notify_tg(report_file: Path):
    """推送荐股报告到 Telegram"""
    try:
        tg_push_path = WORKSPACE / "05_TOOLS" / "miner" / "tg_push.py"
        if not tg_push_path.exists():
            print("[TG] tg_push.py not found")
            return False

        tg_mod = import_module(tg_push_path)

        # 读取报告内容
        if not report_file.exists():
            return False

        report_text = report_file.read_text(encoding="utf-8")

        # 提取摘要（前2000字符，TG限制4096）
        summary = report_text[:3000]
        if len(report_text) > 3000:
            summary += "\n\n... (报告过长，完整内容请查看文件)"

        # 发送消息
        chat_id = tg_mod.DEFAULT_CHAT_ID
        if not chat_id:
            # 尝试从 updates 获取
            chat_id = tg_mod.get_updates()

        if chat_id:
            result = tg_mod.send_message(chat_id, summary)
            if result and result.get("ok"):
                print(f"[TG] Report sent to {chat_id}")
                return True
            else:
                print(f"[TG] Send failed: {result}")
        else:
            print("[TG] No chat_id available")
    except Exception as e:
        print(f"[TG] Error: {e}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Stock Advisor Worker")
    parser.add_argument("--date", help="Date (YYYYMMDD)")
    parser.add_argument("--push", action="store_true", help="Push to Git")
    parser.add_argument("--notify", action="store_true", help="ntfy.sh notification")
    parser.add_argument("--tg", action="store_true", help="Telegram push")
    parser.add_argument("--force", action="store_true", help="Overwrite existing report")
    args = parser.parse_args()

    date_str = args.date or datetime.now().strftime("%Y%m%d")
    output_file = CLOUD_DIR / f"advisor_{date_str}.md"

    if output_file.exists() and not args.force:
        result = {"status": "skipped", "reason": f"already exists: {output_file.name}"}
    else:
        if output_file.exists():
            output_file.unlink()
        result = run_stock_advisor(date=args.date)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.push and result.get("status") in ("ok", "warning"):
        git_push()

    if args.notify:
        notify_ntfy(f"Stock Advisor: {result.get('status')} {result.get('output', '')}")

    if args.tg and result.get("status") in ("ok", "warning"):
        # 优先使用 cloud 目录的报告，否则使用 mine_output
        if not output_file.exists():
            output_file = WORKSPACE / "mine_output" / "advisor" / f"advisor_{date_str}.md"
        notify_tg(output_file)


if __name__ == "__main__":
    main()