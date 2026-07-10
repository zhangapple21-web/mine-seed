#!/usr/bin/env python3
"""
OPS-005: Self-Loop (自循环) - 用户=观察源之一
==============================================

工作哲学: 用户不是任务派发器, 而是文明观察源之一
14 步自治闭环: Environment→Observe→Audit→Recovery→Discovery→Candidate
             →Seed→Task→Validator→Governor→Archive→Evolution→Heartbeat→Repeat
"""
import os, sys, json, time, argparse, subprocess
from pathlib import Path
from datetime import datetime

def load_env():
    env_path = Path(__file__).parent.parent / "05_TOOLS" / "miner" / "miner_env.sh"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("export ") and "=" in line:
                    k, v = line[7:].split("=", 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)

load_env()

sys.path.insert(0, str(Path(__file__).parent))
try:
    from environment_first import scan_directory
except:
    pass

WORKSPACE = Path(__file__).parent.parent
SELF_LOOP_DIR = WORKSPACE / "02_MEMORY" / "self_loop"


def step_environment(): return {"step": "environment", "python": sys.version.split()[0], "cwd": str(WORKSPACE), "git_repo": (WORKSPACE / ".git").exists()}


def step_observe():
    changes = {"git_changes": 0}
    try:
        r = subprocess.run(["git", "status", "--short"], cwd=str(WORKSPACE), capture_output=True, text=True, timeout=10)
        if r.returncode == 0: changes["git_changes"] = len(r.stdout.strip().split("\n")) if r.stdout.strip() else 0
    except: pass
    return {"step": "observe", "changes": changes}


def step_audit():
    proto = len(list((WORKSPACE / "04_PROTOCOLS").glob("*.py"))) if (WORKSPACE / "04_PROTOCOLS").exists() else 0
    principles = WORKSPACE / "00_ROOT" / "PRINCIPLES.md"
    axioms = principles.read_text(encoding="utf-8").count("#") if principles.exists() else 0
    return {"step": "audit", "protocols": proto, "axioms": axioms}


def step_recovery():
    try:
        idx = scan_directory(WORKSPACE, max_depth=2)
        return {"step": "recovery", "files": idx["files_total"], "recovery_assets": len(idx["recovery_assets"])}
    except: return {"step": "recovery", "error": True}


def step_discovery(): return {"step": "discovery", "new_archives": []}
def step_candidate(): return {"step": "candidate", "candidates": []}
def step_seed(): return {"step": "seed", "seeds": []}
def step_task(): return {"step": "task", "active_tasks": [], "queue_depth": 0}
def step_validator(): return {"step": "validator", "validated": 0, "failed": 0}
def step_governor(): return {"step": "governor", "decisions": []}
def step_archive(): return {"step": "archive", "archived": 0}
def step_evolution(): return {"step": "evolution", "constraints_updated": 0, "new_principles": 0}
def step_heartbeat(): return {"step": "heartbeat", "alive": True, "ts": datetime.now().isoformat()}
def step_repeat(): return {"step": "repeat", "next": "ready"}


STEPS = [step_environment, step_observe, step_audit, step_recovery, step_discovery, step_candidate, step_seed, step_task, step_validator, step_governor, step_archive, step_evolution, step_heartbeat, step_repeat]


def self_loop():
    cycle_id = datetime.now().strftime("%Y%m%dT%H%M%S")
    print(f"\n{'='*60}\nOPS-005 Self-Loop #{cycle_id}\n{'='*60}\n")
    report = {"cycle_id": cycle_id, "time": datetime.now().isoformat(), "steps": {}}
    for fn in STEPS:
        name = fn.__name__.replace("step_", "")
        try:
            result = fn()
            report["steps"][name] = result
            print(f"  [{name:12s}] OK")
        except Exception as e:
            report["steps"][name] = {"error": str(e)}
            print(f"  [{name:12s}] ERR")
    SELF_LOOP_DIR.mkdir(parents=True, exist_ok=True)
    log_file = SELF_LOOP_DIR / f"loop_{cycle_id}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  Cycle complete | Log: {log_file.name}")
    return report


def loop(interval_min=60):
    print(f"[SELF-LOOP] loop interval={interval_min}min")
    while True:
        self_loop()
        time.sleep(interval_min * 60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.loop: loop(args.interval)
    else:
        r = self_loop()
        if args.json: print(json.dumps(r, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()