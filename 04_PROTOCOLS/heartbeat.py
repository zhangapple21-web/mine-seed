#!/usr/bin/env python3
import os, sys, json, time, argparse
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

import importlib.util

def import_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    ef = import_module(WORKSPACE / "04_PROTOCOLS" / "environment_first.py")
    lm = import_module(WORKSPACE / "04_PROTOCOLS" / "local_miner.py")
    ops_004 = import_module(WORKSPACE / "04_PROTOCOLS" / "ops_004_recovery_first.py")
    mem = import_module(WORKSPACE / "06_RUNTIME" / "core" / "memory_manager.py")

    scan_directory = ef.scan_directory
    build_recovery_graph = ef.build_recovery_graph
    task_signal_discovery = lm.task_signal_discovery
    task_archivist = lm.task_archivist
    ops_004_check = ops_004.recovery_first
    MemoryManager = mem.MemoryManager
except Exception as e:
    print(f"[HEARTBEAT] Import error: {e}")
    sys.exit(1)


def beat():
    ts = datetime.now().isoformat()
    beat_id = ts.replace("-", "").replace(":", "").replace(".", "")[:15]
    print(f"[HEARTBEAT] Beat @ {ts}")
    report = {
        "beat_id": beat_id,
        "time": ts,
        "status": "ok",
        "ops_principles": ["ops_000", "ops_001", "ops_002", "ops_003", "ops_004", "ops_005"],
        "steps": {},
    }

    mm = MemoryManager()

    # OPS-004 Recovery First check
    try:
        ops_004 = ops_004_check(check_only=True)
        report["ops_004_status"] = ops_004.get("summary", {})
        mm.save_memory("heartbeat", f"ops_004_{beat_id}", ops_004)
        if not ops_004.get("summary", {}).get("ready", False):
            print(f"  [OPS-004] {ops_004['summary']}")
    except Exception as e:
        report["ops_004_status"] = {"error": str(e)}

    # EFP
    try:
        idx = scan_directory(WORKSPACE, max_depth=3)
        report["steps"]["efp"] = {"files": idx["files_total"], "recovery_assets": len(idx["recovery_assets"])}
        mm.save_memory("environment", "latest_scan", idx)
        print(f"  [EFP] {idx['files_total']} files")
    except Exception as e:
        report["steps"]["efp"] = {"error": str(e)}

    # Signal
    try:
        sig = task_signal_discovery()
        report["steps"]["signal"] = {"status": sig.get("status"), "model": sig.get("model")}
        print(f"  [SIGNAL] {sig.get('status')}")
    except Exception as e:
        report["steps"]["signal"] = {"error": str(e)}

    # Archivist
    try:
        arc = task_archivist()
        report["steps"]["archivist"] = {"status": arc.get("status"), "model": arc.get("model")}
        print(f"  [ARCHIVIST] {arc.get('status')}")
    except Exception as e:
        report["steps"]["archivist"] = {"error": str(e)}

    # Save
    mm.save_memory("heartbeat", f"beat_{beat_id}", report)
    print(f"[HEARTBEAT] Saved: beat_{beat_id}")
    return report


def loop(interval_min=15):
    print(f"[HEARTBEAT] loop interval={interval_min}min")
    while True:
        beat()
        time.sleep(interval_min * 60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=int, default=15)
    args = parser.parse_args()
    if args.loop:
        loop(args.interval)
    else:
        print(json.dumps(beat(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()