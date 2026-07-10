#!/usr/bin/env python3
"""
ACE Runtime Main - Local daemon (silent by default)
===================================================

Default behavior: silent background operation
  - Logs go to 02_MEMORY/logs/runtime_YYYYMMDD.log
  - No console output unless --verbose
  - Critical errors printed to stderr even in silent mode

Usage:
  python runtime_main.py                    # silent, single cycle
  python runtime_main.py --daemon           # silent, background loop
  python runtime_main.py --verbose          # console output for debugging
  python runtime_main.py --daemon --verbose # loop with console output
"""
import os, sys, json, time, argparse, subprocess, shutil, logging
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

# Import components
ace_logger = import_module(WORKSPACE / "06_RUNTIME" / "core" / "ace_logger.py")
env_scan = import_module(WORKSPACE / "06_RUNTIME" / "core" / "environment_scan.py")
mem_manager = import_module(WORKSPACE / "06_RUNTIME" / "core" / "memory_manager.py")
tg_push_module = import_module(WORKSPACE / "06_RUNTIME" / "connectors" / "tg_pusher.py")

get_logger = ace_logger.get_logger
silence_all = ace_logger.silence_all
scan_environment = env_scan.scan_environment
MemoryManager = mem_manager.MemoryManager
TGPusher = tg_push_module.TGPusher

CLOUD_DIR = WORKSPACE / "cloud"
MEM_DIR = WORKSPACE / "02_MEMORY"
PUSHED_FILES = MEM_DIR / "tg_pushed.json"

# Global logger, initialized in main()
log = None


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
        # Stash any local changes before pulling
        subprocess.run(
            ["git", "stash"],
            cwd=str(WORKSPACE), capture_output=True, text=True, timeout=10
        )
        result = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=str(WORKSPACE), capture_output=True, text=True, timeout=30
        )
        # Restore stashed changes
        subprocess.run(
            ["git", "stash", "pop"],
            cwd=str(WORKSPACE), capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            log.info("Git pull successful")
            return True
        else:
            log.warning(f"Git pull failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        log.error(f"Git pull error: {e}")
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
    log.info(f"=== Cycle start @ {ts} ===")
    
    pushed = load_pushed_files()
    mm = MemoryManager()
    
    # 1. EFP Environment Scan
    try:
        scan_result = scan_environment(WORKSPACE)
        mm.save_memory("environment", "latest_scan", scan_result)
        log.info(f"EFP scan: {len(scan_result['files'])} files, {len(scan_result['recovery_assets'])} recovery assets")
    except Exception as e:
        log.error(f"EFP scan failed: {e}")
    
    # 2. Git Pull
    log.info("Git pull...")
    git_pull()
    
    # 3. Detect new reports
    new_files = detect_new_reports(pushed)
    if new_files:
        log.info(f"Found {len(new_files)} new cloud reports")
    else:
        log.debug("No new reports")
    
    # 4. Push to TG
    if new_files and chat_id:
        log.info(f"Pushing {len(new_files)} reports to TG...")
        pusher = TGPusher(chat_id=chat_id)
        for f in new_files:
            if dry_run:
                log.info(f"[DRY] Would push: {f.name}")
            else:
                try:
                    result = pusher.send_report(str(f))
                    if result.get("ok"):
                        pushed.add(f.name)
                        archive_report(f)
                        log.info(f"Pushed: {f.name} (msg={result.get('message_sent')}, doc={result.get('document_sent')})")
                    else:
                        log.error(f"TG push failed for {f.name}: {result.get('error')}")
                except Exception as e:
                    log.error(f"TG push error for {f.name}: {e}")
        save_pushed_files(pushed)
    
    # 5. Heartbeat
    try:
        result = subprocess.run(
            [sys.executable, str(WORKSPACE / "04_PROTOCOLS" / "heartbeat.py")],
            cwd=str(WORKSPACE), capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            log.debug("Heartbeat ok")
        else:
            log.warning(f"Heartbeat failed: {result.stderr.strip()}")
    except Exception as e:
        log.error(f"Heartbeat error: {e}")
    
    log.info("=== Cycle complete ===")


def run_daemon(interval_min=15, chat_id=None):
    log.info(f"Daemon started (interval={interval_min}min, silent=True)")
    while True:
        run_cycle(chat_id=chat_id)
        time.sleep(interval_min * 60)


def main():
    parser = argparse.ArgumentParser(description="ACE Runtime (silent by default)")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    parser.add_argument("--interval", type=int, default=15, help="Cycle interval in minutes")
    parser.add_argument("--chat-id", help="TG Chat ID for notifications")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without sending")
    parser.add_argument("--verbose", action="store_true", help="Print logs to console")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="Log level")
    args = parser.parse_args()
    
    # Setup logging
    global log
    log_level = getattr(logging, args.log_level)
    log = get_logger("runtime", level=log_level, silent=not args.verbose)
    silence_all()
    
    if args.daemon:
        run_daemon(interval_min=args.interval, chat_id=args.chat_id)
    else:
        run_cycle(chat_id=args.chat_id, dry_run=args.dry_run)


if __name__ == "__main__":
    main()