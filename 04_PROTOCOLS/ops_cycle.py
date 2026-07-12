#!/usr/bin/env python3
# TYPE: dev_tool
"""
OPS Cycle - 运营闭环
====================

公理根基:
  #002 考古不是搬家是炼金
  #008 认知主循环: 感知->重构->锚定->输出
  #014 本地推理为主, 外部模型只当嘴

三层架构:
  ABP (Bootstrap) — 能启动
  OPS (Operations) — 能持续运行
  GOV (Governance) — 能演化

OPS 负责今天怎么运营:
  09:00 发现Git更新 → Discovery → Candidate → RoundTable → Archivist → Repository → Memory → Constraint → Evolution → 明天Seed

执行语义:
  这是真正的运营循环，不是心跳。
  心跳只是"活着"，OPS是"干活"。

七步闭环:
  1. Discovery   — 发现环境变化（Git更新/Downloads新文件/Telegram收藏）
  2. Candidate   — 提取候选资产（哪些值得处理）
  3. RoundTable  — 圆桌会议（Archivist/Governor/Validator审议）
  4. Archivist   — 归档整理（distill → compress → review）
  5. Repository  — 入库（决定是否成为文明的一部分）
  6. Memory      — 记忆沉淀（提取原则/公理/结构）
  7. Evolution   — 演化（更新约束/生成明天Seed）

用法:
  python ops_cycle.py              # 单次完整运营周期
  python ops_cycle.py --loop       # 无限循环（每30分钟）
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Load miner_env.sh
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

# Import protocols
sys.path.insert(0, str(Path(__file__).parent))
try:
    from environment_first import scan_directory, build_recovery_graph
    from local_miner import task_signal_discovery, task_archivist, call_github_models
except ImportError as e:
    print(f"[OPS] Import error: {e}")
    sys.exit(1)

OPS_LOG_DIR = Path(__file__).parent.parent / "02_MEMORY" / "ops_logs"

def step_discovery(workspace: Path) -> dict:
    """
    Step 1: Discovery — 发现环境变化
    扫描 Git状态/Downloads新文件/Telegram收藏
    """
    print("[OPS] Step 1: Discovery...")
    
    changes = {
        "git_changes": [],
        "new_downloads": [],
        "recovery_candidates": [],
    }
    
    # Git changes
    import subprocess
    try:
        r = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            changes["git_changes"] = r.stdout.strip().split("\n")[:20]
            print(f"  Git: {len(changes['git_changes'])} changes")
    except:
        pass
    
    # Downloads new files
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        new_files = []
        for f in downloads.iterdir():
            if f.is_file() and f.suffix.lower() in {".zip", ".json", ".md", ".txt"}:
                try:
                    # Files modified in last 24 hours
                    if f.stat().st_mtime > time.time() - 86400:
                        new_files.append(str(f.name))
                except:
                    pass
        changes["new_downloads"] = new_files[:20]
        print(f"  Downloads: {len(changes['new_downloads'])} new files")
    
    # Recovery candidates (from EFP)
    try:
        index = scan_directory(workspace, max_depth=3)
        recovery = build_recovery_graph(index)
        candidates = []
        for s in recovery.get("recovery_sets", [])[:10]:
            if s["highest_priority"] in ("HIGH", "MEDIUM"):
                candidates.append(s["set_id"])
        changes["recovery_candidates"] = candidates
        print(f"  Recovery: {len(candidates)} HIGH/MEDIUM candidates")
    except:
        pass
    
    return changes

def step_candidate(discovery: dict) -> dict:
    """
    Step 2: Candidate — 提取候选资产
    从Discovery结果中提取值得处理的候选
    """
    print("[OPS] Step 2: Candidate...")
    
    candidates = {
        "from_git": [],
        "from_downloads": [],
        "from_recovery": [],
    }
    
    # Git candidates: untracked files that look like assets
    for change in discovery.get("git_changes", []):
        if change.startswith("??"):
            fname = change[3:]
            low = fname.lower()
            if any(kw in low for kw in ["readme", "rfc", "skill", "principle", "daily", "seed", "constraint"]):
                candidates["from_git"].append(fname)
    print(f"  Git candidates: {len(candidates['from_git'])}")
    
    # Downloads candidates: zip/json/md files
    for fname in discovery.get("new_downloads", []):
        low = fname.lower()
        if any(kw in low for kw in ["backup", "archive", "snapshot", "ace", "r1", "r2", "seed"]):
            candidates["from_downloads"].append(fname)
    print(f"  Downloads candidates: {len(candidates['from_downloads'])}")
    
    # Recovery candidates: already filtered by priority
    candidates["from_recovery"] = discovery.get("recovery_candidates", [])
    print(f"  Recovery candidates: {len(candidates['from_recovery'])}")
    
    return candidates

def step_roundtable(candidates: dict) -> dict:
    """
    Step 3: RoundTable — 圆桌会议
    Archivist/Governor/Validator审议候选资产
    """
    print("[OPS] Step 3: RoundTable...")
    
    # Call external model for governance reasoning
    prompt = f"""
你是ACE圆桌会议的Governor。审议以下候选资产，决定哪些值得进入文明资产池。

候选资产:
{json.dumps(candidates, ensure_ascii=False, indent=2)}

请输出JSON格式:
{{"approved": ["批准入库的资产"], "rejected": ["拒绝的资产"], "pending": ["需要更多信息的资产"], "reasoning": "简要说明决策理由"}}
"""
    
    result = call_github_models(prompt, model="gpt-4o-mini", max_tokens=500)
    
    if "error" in result:
        print(f"  ERROR: {result['error']}")
        return {"approved": [], "rejected": [], "pending": [], "error": result["error"]}
    
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    # Parse JSON from response
    try:
        # Find JSON block in response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            decision = json.loads(content[start:end])
        else:
            decision = {"approved": [], "rejected": [], "pending": [], "raw": content}
    except:
        decision = {"approved": [], "rejected": [], "pending": [], "raw": content}
    
    print(f"  Approved: {len(decision.get('approved', []))}")
    print(f"  Rejected: {len(decision.get('rejected', []))}")
    print(f"  Pending: {len(decision.get('pending', []))}")
    
    return decision

def step_archivist(decision: dict, workspace: Path) -> dict:
    """
    Step 4: Archivist — 归档整理
    distill → compress → review
    """
    print("[OPS] Step 4: Archivist...")
    
    report = {
        "distilled": [],
        "compressed": [],
        "reviewed": [],
    }
    
    approved = decision.get("approved", [])
    
    if not approved:
        print("  No approved assets to archive")
        return report
    
    # Call Archivist task from local_miner
    arc_result = task_archivist()
    
    if arc_result.get("status") == "ok":
        # Parse archivist response
        content = arc_result.get("response", "")
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                arc_data = json.loads(content[start:end])
                report["distilled"] = arc_data.get("to_distill", [])
                report["compressed"] = arc_data.get("to_archive", [])
                report["reviewed"] = [arc_data.get("review_notes", "")]
        except:
            report["reviewed"] = [content[:200]]
    
    print(f"  Distilled: {len(report['distilled'])}")
    print(f"  Compressed: {len(report['compressed'])}")
    
    return report

def step_repository(archivist: dict, workspace: Path) -> dict:
    """
    Step 5: Repository — 入库
    决定是否成为文明的一部分
    """
    print("[OPS] Step 5: Repository...")
    
    repo = {
        "committed": [],
        "staged": [],
        "pending_governance": [],
    }
    
    # For now: all approved assets go to pending_governance
    # Real implementation would check constraints, run tests, etc.
    
    import subprocess
    try:
        # Check current git status
        r = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0:
            staged = [line for line in r.stdout.split("\n") if line.startswith("A ") or line.startswith("M ")]
            repo["staged"] = staged[:10]
    except:
        pass
    
    print(f"  Staged: {len(repo['staged'])}")
    
    return repo

def step_memory(repository: dict, workspace: Path) -> dict:
    """
    Step 6: Memory — 记忆沉淀
    提取原则/公理/结构
    """
    print("[OPS] Step 6: Memory...")
    
    memory = {
        "new_principles": [],
        "new_axioms": [],
        "new_structures": [],
    }
    
    # Check if PRINCIPLES.md was modified
    principles = workspace / "00_ROOT" / "PRINCIPLES.md"
    if principles.exists():
        try:
            with open(principles, encoding="utf-8") as f:
                content = f.read()
                # Count axioms
                axiom_count = content.count("#")
                memory["axiom_count"] = axiom_count
        except:
            pass
    
    print(f"  Current axioms: {memory.get('axiom_count', '?')}")
    
    return memory

def step_evolution(memory: dict) -> dict:
    """
    Step 7: Evolution — 演化
    更新约束/生成明天Seed
    """
    print("[OPS] Step 7: Evolution...")
    
    evolution = {
        "seed_for_tomorrow": None,
        "constraint_updates": [],
    }
    
    # Generate seed for tomorrow
    prompt = """
你是ACE的演化层。根据今天的运营情况，生成明天的Seed（工作建议）。

输出JSON格式:
{"seed": "明天首先要做的事", "priority": "HIGH/MEDIUM/LOW", "reason": "为什么这是第一优先级"}
"""
    
    result = call_github_models(prompt, model="gpt-4o-mini", max_tokens=300)
    
    if "error" not in result:
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                evolution["seed_for_tomorrow"] = json.loads(content[start:end])
        except:
            evolution["seed_for_tomorrow"] = {"raw": content[:200]}
    
    if evolution["seed_for_tomorrow"]:
        print(f"  Seed: {evolution['seed_for_tomorrow'].get('seed', '?')[:60]}")
    
    return evolution

def ops_cycle(workspace: Path) -> dict:
    """完整运营周期"""
    ts = datetime.now().isoformat()
    cycle_id = ts.replace("-", "").replace(":", "").replace(".", "")[:15]
    
    print(f"\n{'='*60}")
    print(f"OPS Cycle #{cycle_id}")
    print(f"{'='*60}\n")
    
    report = {
        "cycle_id": cycle_id,
        "time": ts,
        "steps": {},
    }
    
    # Step 1: Discovery
    report["steps"]["discovery"] = step_discovery(workspace)
    
    # Step 2: Candidate
    report["steps"]["candidate"] = step_candidate(report["steps"]["discovery"])
    
    # Step 3: RoundTable
    report["steps"]["roundtable"] = step_roundtable(report["steps"]["candidate"])
    
    # Step 4: Archivist
    report["steps"]["archivist"] = step_archivist(report["steps"]["roundtable"], workspace)
    
    # Step 5: Repository
    report["steps"]["repository"] = step_repository(report["steps"]["archivist"], workspace)
    
    # Step 6: Memory
    report["steps"]["memory"] = step_memory(report["steps"]["repository"], workspace)
    
    # Step 7: Evolution
    report["steps"]["evolution"] = step_evolution(report["steps"]["memory"])
    
    # Summary
    print(f"\n{'='*60}")
    print(f"OPS Cycle #{cycle_id} Complete")
    print(f"{'='*60}\n")
    
    # Save log
    OPS_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = OPS_LOG_DIR / f"ops_{cycle_id}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[OPS] Saved: {log_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="OPS Cycle - 运营闭环")
    parser.add_argument("--loop", action="store_true", help="无限循环")
    parser.add_argument("--interval", type=int, default=30, help="循环间隔(分钟)")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    args = parser.parse_args()
    
    workspace = Path(__file__).parent.parent
    
    if args.loop:
        print(f"[OPS] Starting infinite loop (interval={args.interval}min)")
        while True:
            ops_cycle(workspace)
            print(f"[OPS] Sleeping {args.interval} minutes...")
            time.sleep(args.interval * 60)
    else:
        report = ops_cycle(workspace)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()