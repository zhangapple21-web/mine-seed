#!/usr/bin/env python3
import os, sys, json, time, argparse, subprocess, shutil
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent.parent
sys.path.insert(0, str(WORKSPACE))

import importlib.util

def import_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

env_scan = import_module(WORKSPACE / "06_RUNTIME" / "core" / "environment_scan.py")
mem_manager = import_module(WORKSPACE / "06_RUNTIME" / "core" / "memory_manager.py")
tg_push_module = import_module(WORKSPACE / "06_RUNTIME" / "connectors" / "tg_pusher.py")

scan_environment = env_scan.scan_environment
MemoryManager = mem_manager.MemoryManager
TGPusher = tg_push_module.TGPusher

CLOUD_DIR = WORKSPACE / "cloud"
MEM_DIR = WORKSPACE / "02_MEMORY"
PUSHED_FILES = MEM_DIR / "tg_pushed.json"


def load_pushed_files():
    if PUSHED_FILES.exists():
        try:
            with open(PUSHED_FILES, encoding="utf-8") as f:
                return set(json.load(f))
        except:
            pass
    return set()


def save_pushed_files(pushed):
    with open(PUSHED_FILES, "w", encoding="utf-8") as f:
        json.dump(list(pushed), f)


def git_pull():
    try:
        result = subprocess.run(["git", "pull", "--rebase", "origin", "main"],
                               cwd=str(WORKSPACE), capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"    Pull successful")
            return True
        else:
            print(f"    Pull failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"    Pull error: {e}")
        return False


def detect_new_reports(pushed):
    new_files = []
    for worker_type in ["advisor", "signals", "archivist", "miner"]:
        worker_dir = CLOUD_DIR / worker_type
        if not worker_dir.exists():
            continue
        for f in worker_dir.iterdir():
            if f.name not in pushed:
                new_files.append(f)
    return sorted(new_files)


def archive_report(file_path):
    archive_dir = MEM_DIR / "cloud_reports"
    archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(file_path, archive_dir / file_path.name)


def run_cycle(chat_id=None, dry_run=False):
    ts = datetime.now().isoformat()
    print(f"\n[RUNTIME] Cycle @ {ts}")
    
    pushed = load_pushed_files()
    mm = MemoryManager()
    
    # 1. EFP 环境扫描
    print("  [1/5] Environment Scan...")
    try:
        scan_result = scan_environment(WORKSPACE)
        mm.save_memory("environment", "latest_scan", scan_result)
        print(f"    Scanned: {len(scan_result['files'])} files, {len(scan_result['recovery_assets'])} recovery assets")
    except Exception as e:
        print(f"    Scan failed: {e}")
    
    # 2. Git Pull
    print("  [2/5] Git Pull...")
    git_pull()
    
    # 3. 检测新报告
    print("  [3/5] Detecting new reports...")
    new_files = detect_new_reports(pushed)
    print(f"    Found {len(new_files)} new files")
    
    # 4. 推送 TG
    if new_files and chat_id:
        print(f"  [4/5] Pushing to TG ({len(new_files)})...")
        pusher = TGPusher(chat_id=chat_id)
        for f in new_files:
            if dry_run:
                print(f"    DRY: {f.name}")
            else:
                content = f.read_text(encoding="utf-8")[:4000]
                title = f.name.replace(".md", "")
                result = pusher.send_message(f"📊 {title}\n\n{content}")
                if result.get("ok"):
                    pushed.add(f.name)
                    archive_report(f)
                    print(f"    ✓ {f.name}")
                else:
                    print(f"    ✗ {f.name}: {result.get('error')}")
        save_pushed_files(pushed)
    
    # 5. 心跳
    print("  [5/5] Heartbeat...")
    try:
        result = subprocess.run([sys.executable, str(WORKSPACE / "04_PROTOCOLS" / "heartbeat.py")],
                               cwd=str(WORKSPACE), capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("    Heartbeat ok")
        else:
            print(f"    Heartbeat failed: {result.stderr}")
    except Exception as e:
        print(f"    Heartbeat error: {e}")
    
    print(f"[RUNTIME] Cycle complete")


def run_daemon(interval_min=15, chat_id=None):
    print(f"[RUNTIME] Daemon started (interval={interval_min}min)")
    while True:
        run_cycle(chat_id=chat_id)
        time.sleep(interval_min * 60)


def main():
    parser = argparse.ArgumentParser(description="ACE Runtime")
    parser.add_argument("--daemon", action="store_true", help="持续运行")
    parser.add_argument("--interval", type=int, default=15, help="间隔(分钟)")
    parser.add_argument("--chat-id", help="TG Chat ID")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    args = parser.parse_args()
    
    if args.daemon:
        run_daemon(interval_min=args.interval, chat_id=args.chat_id)
    else:
        run_cycle(chat_id=args.chat_id, dry_run=args.dry_run)


if __name__ == "__main__":
    main()