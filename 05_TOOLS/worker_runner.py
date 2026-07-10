#!/usr/bin/env python3
import os, sys, json, argparse, subprocess, urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
NTPY_TOPIC = os.environ.get("NTPY_TOPIC", "ace-cloud-worker")

workers_map = {
    "stock_advisor": "worker_stock_advisor.py",
    "signal_discovery": "worker_signal_discovery.py",
    "archivist": "worker_archivist.py",
    "miner": "worker_miner.py",
}


def run_worker(worker_name, **kwargs):
    if worker_name not in workers_map:
        return {"error": f"unknown worker: {worker_name}"}
    
    worker_file = WORKSPACE / "05_TOOLS" / workers_map[worker_name]
    if not worker_file.exists():
        return {"error": f"worker file not found: {worker_file}"}
    
    print(f"[WORKER] Running: {worker_name}")
    cmd = [sys.executable, str(worker_file)]
    if kwargs.get("date"):
        cmd.extend(["--date", kwargs["date"]])
    
    try:
        result = subprocess.run(cmd, cwd=str(WORKSPACE), capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def git_push():
    try:
        subprocess.run(["git", "add", "cloud/"], cwd=str(WORKSPACE), capture_output=True)
        subprocess.run(["git", "commit", "-m", f"cloud: {datetime.now().strftime('%Y%m%d')} worker output"],
                       cwd=str(WORKSPACE), capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=str(WORKSPACE), capture_output=True)
        return True
    except Exception as e:
        print(f"[GIT] Push failed: {e}")
        return False


def notify_ntfy(message):
    if not NTPY_TOPIC:
        return
    try:
        req = urllib.request.Request(
            f"https://ntfy.sh/{NTPY_TOPIC}",
            data=message.encode(),
            headers={"Title": "ACE Cloud Worker"},
        )
        urllib.request.urlopen(req, timeout=10)
    except:
        pass


def main():
    parser = argparse.ArgumentParser(description="Worker Runner")
    parser.add_argument("--worker", required=True, choices=["stock_advisor", "signal_discovery", "archivist", "miner"])
    parser.add_argument("--date", help="日期 (YYYYMMDD)")
    parser.add_argument("--push", action="store_true", help="Push Git")
    parser.add_argument("--notify", action="store_true", help="ntfy.sh 通知")
    args = parser.parse_args()
    
    result = run_worker(args.worker, date=args.date)
    
    if args.push and result.get("status") == "ok":
        git_push()
    
    if args.notify:
        msg = f"{args.worker}: {result.get('status')} {result.get('output', '')}"
        notify_ntfy(msg)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()