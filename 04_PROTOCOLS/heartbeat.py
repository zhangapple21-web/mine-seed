#!/usr/bin/env python3
"""
ACE Heartbeat - 自治循环心跳 (集成五大 OPS 原则)
==================================================

执行: EFP + Signal + Archivist + OPS-004 检查, 15 分钟一次

五大 OPS 原则集成:
  OPS-000 Asset First     — 已通过环境发现
  OPS-001 ABA             — 行动前先检查
  OPS-002 Find Before     — 7 层查找
  OPS-003 Worker Pool     — github_models 作为主矿工
  OPS-004 Recovery First  — 每次心跳检查接管状态
  OPS-005 Self-Loop       — 心跳是自循环的一部分
"""
import os, sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
try:
    from environment_first import scan_directory, build_recovery_graph
    from local_miner import task_signal_discovery, task_archivist
    from ops_004_recovery_first import recovery_first as ops_004_check
except ImportError as e:
    print(f"[HEARTBEAT] Import error: {e}")
    sys.exit(1)

HEARTBEAT_DIR = Path(__file__).parent.parent / "02_MEMORY" / "heartbeat"


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
    # OPS-004 Recovery First check
    try:
        ops_004 = ops_004_check(check_only=True)
        report["ops_004_status"] = ops_004.get("summary", {})
        if not ops_004.get("summary", {}).get("ready", False):
            print(f"  [OPS-004] {ops_004['summary']}")
    except Exception as e:
        report["ops_004_status"] = {"error": str(e)}
    # EFP
    workspace = Path(__file__).parent.parent
    try:
        idx = scan_directory(workspace, max_depth=3)
        report["steps"]["efp"] = {"files": idx["files_total"], "recovery_assets": len(idx["recovery_assets"])}
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
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    log_file = HEARTBEAT_DIR / f"beat_{beat_id}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[HEARTBEAT] Saved: {log_file.name}")
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
    if args.loop: loop(args.interval)
    else: print(json.dumps(beat(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()