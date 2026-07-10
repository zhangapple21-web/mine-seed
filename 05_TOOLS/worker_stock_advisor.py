#!/usr/bin/env python3
import os, sys, json, argparse, subprocess, urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

CLOUD_DIR = WORKSPACE / "cloud" / "advisor"


def run_stock_advisor(date=None):
    date_str = date or datetime.now().strftime("%Y%m%d")
    CLOUD_DIR.mkdir(parents=True, exist_ok=True)
    output_file = CLOUD_DIR / f"advisor_{date_str}.md"

    if output_file.exists():
        return {"status": "skipped", "reason": f"already exists"}

    try:
        from advisor.stock_advisor import generate_report
        report = generate_report(date=date_str)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        return {"status": "ok", "output": str(output_file), "date": date_str, "size": len(report)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


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


def main():
    parser = argparse.ArgumentParser(description="Stock Advisor Worker")
    parser.add_argument("--date", help="日期 (YYYYMMDD)")
    parser.add_argument("--push", action="store_true", help="Push Git")
    parser.add_argument("--notify", action="store_true", help="ntfy.sh 通知")
    args = parser.parse_args()

    result = run_stock_advisor(date=args.date)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.push and result.get("status") == "ok":
        git_push()

    if args.notify:
        notify_ntfy(f"Stock Advisor: {result.get('status')} {result.get('output', '')}")


if __name__ == "__main__":
    main()