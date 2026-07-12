#!/usr/bin/env python3
# TYPE: dev_tool
"""
organize_recovery - 恢复资产归档器
===================================

公理根基:
  #002 考古不是搬家是炼金
  #010 演化只允许增加结构, 不允许破坏不变量
  #020 每次变更必须有diff和原因

执行语义:
  Recovery Protocol 恢复出的文件往往是扁平结构 (R1 备份默认扁平).
  本脚本按命名规则把扁平文件映射回 mine-seed 的标准子目录结构.
  映射失败的进入 99_UNSORTED/ 等待人工处理.

用法:
  python organize_recovery.py <recovery_root> <workspace_root>  # dry-run
  python organize_recovery.py <recovery_root> <workspace_root> --apply
"""
import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Standard mine-seed directory structure
# Map: filename prefix -> target subdir
RULES = [
    # 00_ROOT
    ("ARCHITECTURE",             "00_ROOT"),
    ("PRINCIPLES",               "00_ROOT"),
    ("ROOT_STATE",               "00_ROOT"),
    ("MANIFESTO",                "00_ROOT"),
    ("LETTER_TO_FUTURE",         "00_ROOT"),
    ("AUTONOMOUS_LOOP",          "00_ROOT"),

    # 02_MEMORY
    ("MEMORY",                   "02_MEMORY"),
    ("MEMORY_INDEX",             "02_MEMORY"),
    ("EMAIL_RULES",              "02_MEMORY"),
    ("TOOLS",                    "02_MEMORY"),
    ("observation_log",          "02_MEMORY"),
    ("observation_",             "02_MEMORY"),
    ("experience.json",          "02_MEMORY"),
    ("experience_",              "02_MEMORY"),
    ("thought_seed_",            "02_MEMORY"),
    ("seed_2026",                "02_MEMORY"),
    ("seed_momentum",            "02_MEMORY"),
    ("seed_volatility",          "02_MEMORY"),
    ("binary_sense_demo",        "02_MEMORY"),
    ("knowledge_night",          "02_MEMORY"),
    ("knowledge_shift",          "02_MEMORY"),
    ("protocol_index",           "02_MEMORY"),
    ("principle_compression",    "02_MEMORY"),
    ("principle_classification", "02_MEMORY"),
    ("memory_architecture",      "02_MEMORY"),
    ("memory_dual_write",        "02_MEMORY"),
    ("knowledge_shift_quality", "02_MEMORY"),
    ("memory_index_2026",        "02_MEMORY"),

    # 03_DATA / research / signals
    ("SIGNAL_REGISTRY",          "03_DATA"),
    ("SIGNAL_TAXONOMY",          "03_DATA"),
    ("routing_constraints",      "03_DATA"),
    ("signal_registry",          "03_DATA"),
    ("signal_taxonomy",          "03_DATA"),
    ("layer_stats",              "03_DATA"),
    ("lexicon_2026",             "03_DATA"),
    ("lexicon_latest",           "03_DATA"),
    ("lexicon_categories",       "03_DATA"),
    ("active_manifest",          "03_DATA"),
    ("reference_akshare",        "03_DATA"),
    ("reference_lab",            "03_DATA"),
    ("reference_tomorrow",       "03_DATA"),
    ("reference_zhang",          "03_DATA"),
    ("reference_r1_",            "03_DATA"),
    ("overview.json",            "03_DATA"),
    ("HOST_PROFILE",             "03_DATA"),
    ("host_profile",             "03_DATA"),
    ("WORKER_REGISTRY",          "03_DATA"),
    ("worker_registry",          "03_DATA"),
    ("ace_config",               "03_DATA"),
    ("ACE_CONFIG",               "03_DATA"),

    # 04_PROTOCOLS (python scripts)
    ("lab_bus",                  "04_PROTOCOLS"),
    ("lab_comm",                 "04_PROTOCOLS"),
    ("lab_ntfy",                 "04_PROTOCOLS"),
    ("shared_api",               "04_PROTOCOLS"),

    # 05_TOOLS
    ("miner_24h",                "05_TOOLS/miner"),
    ("miner_cron",               "05_TOOLS/miner"),
    ("miner_env",                "05_TOOLS/miner"),
    ("model_router",             "05_TOOLS/miner"),
    ("task_router",              "05_TOOLS/miner"),
    ("advisor_cron",             "05_TOOLS/advisor"),
    ("stock_advisor",            "05_TOOLS/advisor"),
    ("stock_query",              "05_TOOLS/advisor"),
    ("lineage_review",           "05_TOOLS/advisor"),
    ("archivist.py",             "05_TOOLS/memory"),
    ("archivist_cron",           "05_TOOLS/memory"),
    ("experience_engine",        "05_TOOLS/memory"),
    ("knowledge_cron",           "05_TOOLS/memory"),
    ("asset_curator",            "05_TOOLS"),
    ("__init__",                 "05_TOOLS/assets"),
    ("dragon_leader",            "05_TOOLS/signals"),
    ("fitness_tracker",          "05_TOOLS/signals"),
    ("signal_cron",              "05_TOOLS/signals"),
    ("signal_discovery",         "05_TOOLS/signals"),
    ("capsule",                  "05_TOOLS/aether_capsule"),
    ("bridge-check",             "05_TOOLS"),
    ("SETUP",                    "05_TOOLS"),
    ("setup",                    "05_TOOLS"),
    ("CRONTAB",                  "05_TOOLS"),
    ("crontab",                  "05_TOOLS"),
    ("advisor_cron",             "05_TOOLS/advisor"),

    # 06_RUNTIME
    ("RECOVERY_CHECKLIST",       "06_RUNTIME"),
    ("RECOVERY_PLAN",            "06_RUNTIME"),
    ("GITHUB_STRUCTURE",         "06_RUNTIME"),
    ("DEPLOY_GUIDE",             "06_RUNTIME"),
    ("constraint_injector",      "06_RUNTIME"),
    ("constraint_proposer",      "06_RUNTIME"),
    ("deploy_constraints",       "06_RUNTIME"),
    ("sync_constraints",         "06_RUNTIME"),
    ("call_chain",               "06_RUNTIME"),
    ("CALL_CHAIN",               "06_RUNTIME"),
    ("index.html",               "06_RUNTIME"),
    ("index.md",                 "06_RUNTIME"),
    ("index.json",               "06_RUNTIME"),
    ("styles.css",               "06_RUNTIME"),
    ("daemon_state",             "06_RUNTIME"),
    ("DAEMON_STATE",             "06_RUNTIME"),

    # 07_GUARDIAN
    ("NETWORK_BRIDGE",           "07_GUARDIAN"),
    ("backtrack",                "07_GUARDIAN"),
    ("conservation",             "07_GUARDIAN"),
    ("gravity",                  "07_GUARDIAN"),
    ("repair",                   "07_GUARDIAN"),
    ("EVENT_JOURNAL",            "07_GUARDIAN"),
    ("event_journal",            "07_GUARDIAN"),
    ("DELIVERY_CHECKLIST",       "07_GUARDIAN"),
    ("delivery_checklist",       "07_GUARDIAN"),
    ("sync_to_production",       "07_GUARDIAN"),
    ("SYNC_TO_PRODUCTION",       "07_GUARDIAN"),

    # Daily reports -> r1_archaeology/daily
    ("2026-06-",                 "r1_archaeology/daily"),
    ("2026062",                  "r1_archaeology/daily"),
    ("2026063",                  "r1_archaeology/daily"),
    ("daily_evolution",          "r1_archaeology/daily"),
    ("archaeology_report",       "r1_archaeology/daily"),
    ("continuity_archive",       "r1_archaeology/daily"),
    ("daily_",                   "r1_archaeology/daily"),

    # R1 research -> r1_archaeology
    ("R1_legacy",                "r1_archaeology"),
    ("R1_CIVILIZATION_GRAPH",    "r1_archaeology"),
    ("CIVILIZATION_MAP",         "r1_archaeology"),
    ("CIVILIZATION_MANIFEST",    "r1_archaeology"),
    ("civilization_manifest",    "r1_archaeology"),
    ("civilization_map",         "r1_archaeology"),
    ("R2-KERNEL",                "r1_archaeology"),
    ("R2_Learning_Path",         "r1_archaeology"),
    ("R1_五大",                  "r1_archaeology"),
    ("R1认知",                   "r1_archaeology"),
    ("r1_dag_real",              "r1_archaeology"),
    ("r1_early_design",          "r1_archaeology"),
    ("r1_axiom_",                "r1_archaeology"),
    ("r1_ruins",                 "r1_archaeology"),
    ("a00_",                     "r1_archaeology/charters"),
    ("a08_",                     "r1_archaeology/fragments"),
    ("a09_",                     "r1_archaeology/fragments"),
    ("a10_",                     "r1_archaeology/atlas"),
    ("a11_",                     "r1_archaeology/survivor"),
    ("a12_",                     "r1_archaeology/axioms"),
    ("a13_",                     "r1_archaeology"),
    ("a14_",                     "r1_archaeology"),
    ("a15_",                     "r1_archaeology"),
    ("constraint_catacombs",     "r1_archaeology"),
    ("constraint_graph_audit",   "r1_archaeology"),
    ("catacombs_dependency",     "r1_archaeology"),
    ("dual_entity_",             "r1_archaeology"),
    ("persona_decoupling",       "r1_archaeology"),
    ("persona_matrix",           "r1_archaeology"),
    ("dola_three_layer",         "r1_archaeology"),
    ("aetherflow_",              "r1_archaeology/fragments"),
    ("binary_analysis_",         "r1_archaeology"),
    ("binary_sense_",            "r1_archaeology"),
    ("idempotent_lock",          "r1_archaeology"),
    ("prompt_injection",         "r1_archaeology"),
    ("volatility_clustering",    "r1_archaeology"),
    ("regime_transition",        "r1_archaeology"),
    ("volume_volatility",        "r1_archaeology"),
    ("hypothesis_investigation", "r1_archaeology"),
    ("data_coverage_gap",        "r1_archaeology"),
    ("data_source_migration",    "r1_archaeology"),
    ("information_digestion",    "r1_archaeology"),
    ("dynamic_loading",          "r1_archaeology"),
    ("security_domain",          "r1_archaeology"),
    ("collaboration_protocol",   "r1_archaeology"),
    ("community_self",           "r1_archaeology"),
    ("continuity_infrastructure","r1_archaeology"),
    ("domain_boundaries",        "r1_archaeology"),
    ("precipitation_chain",      "r1_archaeology"),
    ("meyo_comment",             "r1_archaeology"),
    ("avoid_smooth",             "r1_archaeology"),
    ("open_source_research",     "r1_archaeology"),
    ("multi_agent_patterns",     "r1_archaeology"),
    ("meaning-layer",            "r1_archaeology"),
    ("roots-discover",           "r1_archaeology"),
    ("knowledge_shift_analysis", "r1_archaeology"),
    ("instreet-visit",           "r1_archaeology"),
    ("case_20260620",            "r1_archaeology/cases"),
    ("case_20260621",            "r1_archaeology/cases"),
    ("community_log",            "r1_archaeology"),
    ("shared_bridge_plan",       "r1_archaeology"),
    ("review_002",               "r1_archaeology"),
    ("review_protocol",          "r1_archaeology"),
    ("constraint_source_map",    "r1_archaeology"),
    ("v6_architecture",          "r1_archaeology"),

    # RFCs -> r1_archaeology/rfc
    ("V6-RFC-",                  "r1_archaeology/rfc"),
    ("EGP-",                     "r1_archaeology/rfc"),
    ("t00_",                     "r1_archaeology/rfc"),
    ("t01_",                     "r1_archaeology/rfc"),

    # Skills -> r1_archaeology/skills
    ("SKILL-",                   "r1_archaeology/skills"),

    # Charters
    ("a00_",                     "r1_archaeology/charters"),

    # ASSET_INVENTORY / INVESTIGATION
    ("ASSET_INVENTORY",          "r1_archaeology"),
    ("INVESTIGATION",            "r1_archaeology"),
    ("ARCHITECTURE_REAL",        "r1_archaeology"),
    ("WORLD_MODEL",              "r1_archaeology"),

    # User profile / agent SOUL
    ("SOUL",                     "01_AGENTS"),
    ("USER",                     "01_AGENTS"),
    ("PROFILE",                  "01_AGENTS"),
    ("PROTOCOLS",                "01_AGENTS"),
    ("R1_legacy_compression",    "01_AGENTS"),

    # Unsorted catch-all
    ("CONSTRAINT_LEDGER",        "06_RUNTIME"),
    ("E2C_Closure_Principles",   "02_MEMORY"),
    ("Evolution_Engine",         "06_RUNTIME"),
    ("GOVERNANCE",               "00_ROOT"),
    ("memory_index_latest",      "02_MEMORY"),
    ("pending",                  "02_MEMORY"),
    ("README",                   "00_ROOT"),
    ("summary_phase_1",          "r1_archaeology"),
    ("tasks",                    "02_MEMORY"),
    ("validation_report",        "02_MEMORY"),
]

# Daily files that should map to recent_memory/daily
RECENT_MEMORY_DAILY = ("2026-06-", "2026-07-")

def classify(name: str) -> str:
    """Map filename to target subdir in mine-seed."""
    # Daily files in 02_MEMORY/recent_memory/daily
    for prefix in RECENT_MEMORY_DAILY:
        if name.startswith(prefix) and name.endswith(".md"):
            return "02_MEMORY/recent_memory/daily"
    for prefix, target in RULES:
        if name.startswith(prefix) or name == prefix:
            return target
    return ""  # unsorted

def organize(root: Path, target_base: Path, apply: bool = False) -> dict:
    """
    Walk root, find flat files, map to target_base/<subdir>/<name>.
    Returns report.
    """
    root = root.resolve()
    target_base = target_base.resolve()
    counts = defaultdict(int)
    plan = []  # (source, dest) pairs
    unsorted = []
    skipped = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        parts = rel.parts
        # Handle two patterns:
        # 1. <root>/<name>  (root level files, simple)
        # 2. <root>/<job>/mine-seed/<name>  (R1 backup flat structure inside job subdir)
        if len(parts) == 1:
            # Root level: process
            name = path.name
            target_subdir = classify(name)
        elif len(parts) == 3 and parts[1] == "mine-seed":
            # Job/mine-seed/<name>: process (R1 flat structure)
            name = parts[2]
            target_subdir = classify(name)
        else:
            skipped.append(str(rel))
            continue
        # Skip our own scripts and reports
        if name in ("environment_first.py", "recovery_protocol.py", "awaken.py",
                    "compare_integrate.py", "organize_recovery.py"):
            continue
        if not target_subdir:
            unsorted.append(name)
            counts["unsorted"] += 1
            continue
        target_path = target_base / target_subdir / name
        plan.append((str(path), str(target_path), target_subdir))
        counts[target_subdir] += 1

    report = {
        "time": datetime.now().isoformat(),
        "root": str(root),
        "target": str(target_base),
        "mode": "APPLY" if apply else "DRY-RUN",
        "total_files": len(plan),
        "unsorted_count": len(unsorted),
        "skipped_count": len(skipped),
        "by_target": dict(counts),
        "unsorted": unsorted[:50],
        "applied": 0,
        "errors": [],
    }

    if apply:
        for src, dst, sub in plan:
            try:
                dst_p = Path(dst)
                dst_p.parent.mkdir(parents=True, exist_ok=True)
                if not dst_p.exists():
                    shutil.copy2(src, dst)
                    report["applied"] += 1
            except Exception as e:
                report["errors"].append(f"{Path(src).name}: {e}")

    return report

def print_report(report: dict):
    print("=" * 70)
    print(f"  Organize Recovery - 归档计划")
    print(f"  Root: {report['root']}")
    print(f"  Target: {report['target']}")
    print(f"  Mode: {report['mode']}")
    print("=" * 70)
    print(f"  Total files to move: {report['total_files']}")
    print(f"  Unsorted (no rule)  : {report['unsorted_count']}")
    print(f"  Skipped (in subdir) : {report['skipped_count']}")
    if report["mode"] == "APPLY":
        print(f"  Applied             : {report['applied']}")
    print()
    print("--- Target Distribution ---")
    for sub, cnt in sorted(report["by_target"].items(), key=lambda x: -x[1])[:20]:
        if sub == "unsorted": continue
        print(f"  {sub:35s}: {cnt}")
    if report["unsorted"]:
        print()
        print(f"--- UNSORTED (need manual rule) ---")
        for u in report["unsorted"][:30]:
            print(f"  ? {u}")
    if report["errors"]:
        print()
        print(f"--- ERRORS ({len(report['errors'])}) ---")
        for e in report["errors"][:5]:
            print(f"  {e}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Organize flat recovery files into mine-seed subdirs")
    parser.add_argument("source", help="Recovery root (e.g. 99_RECOVERY_TEMP)")
    parser.add_argument("target", help="mine-seed root")
    parser.add_argument("--apply", action="store_true", help="Actually move files (default is dry-run)")
    args = parser.parse_args()

    report = organize(Path(args.source), Path(args.target), apply=args.apply)
    print_report(report)

if __name__ == "__main__":
    main()
