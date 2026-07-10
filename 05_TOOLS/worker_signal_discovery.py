#!/usr/bin/env python3
import os, sys, json, argparse, subprocess, urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

CLOUD_DIR = WORKSPACE / "cloud" / "signals"


def run_signal_discovery():
    CLOUD_DIR.mkdir(parents=True, exist_ok=True)
    output_file = CLOUD_DIR / f"signals_{datetime.now().strftime('%Y%m%d')}.json"

    try:
        from signals.signal_discovery import discover_signals
        signals = discover_signals()
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(signals, f, ensure_ascii=False, indent=2)
        return {"status": "ok", "output": str(output_file), "count": len(signals)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def git_push():
    try:
        subprocess.run(["git", "add", "cloud/"], cwd=str(WORKSPACE), capture_output=True)
        subprocess.run(["git", "commit", "-m", f"cloud: signals {datetime.now().strftime('%Y%m%d')}"],
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
            headers={"Title": "ACE Signal Discovery"},
        )
        urllib.request.urlopen(req, timeout=10)
    except:
        pass


def main():
    parser = argparse.ArgumentParser(description="Signal Discovery Worker")
    parser.add_argument("--push", action="store_true", help="Push Git")
    parser.add_argument("--notify", action="store_true", help="ntfy.sh 通知")
    args = parser.parse_args()

    result = run_signal_discovery()
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.push and result.get("status") == "ok":
        git_push()

    if args.notify:
        notify_ntfy(f"Signal Discovery: {result.get('status')} {result.get('count', 0)} signals")


if __name__ == "__main__":
    main()