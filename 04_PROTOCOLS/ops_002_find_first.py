#!/usr/bin/env python3
# TYPE: dev_tool
"""
OPS-002: Find Before Build (笨者生存) - 建造前先找
==================================================

工作哲学: 先找 → 找不到 → 再拼 → 拼不了 → 最后才创造
7 层查找金字塔
"""
import sys, argparse, json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from ops_000_asset_first import search_local, search_github, search_archive, search_tg_collections, search_zip_snapshots, search_pr_history, search_rfc_protocol, search_free_miners


def find_before_build(target, deep=False):
    print(f"\n{'='*60}\nOPS-002 Find Before Build: {target}\n{'='*60}\n")
    layers = [
        ("L1: Current Workspace", search_local),
        ("L2: GitHub", search_github),
        ("L3: Archive / R1", search_archive),
        ("L4: TG Collections", search_tg_collections),
        ("L5: ZIP / Snapshot", search_zip_snapshots),
        ("L6: PR History", search_pr_history),
        ("L7: Free Miners", search_free_miners),
    ]
    result = {"target": target, "time": datetime.now().isoformat(), "layers": {}, "first_hit": None, "decision": None}
    for label, fn in layers:
        step = fn(target)
        result["layers"][label] = step
        matches = step.get("matches", [])
        if "L7" not in label and matches and not deep:
            if result["first_hit"] is None:
                result["first_hit"] = {"layer": label, "matches": matches[:3]}
                break
    if result["first_hit"]:
        result["decision"] = "FOUND_REUSE"
        hit = result["first_hit"]
        print(f"\n[FOUND] {hit['layer']} 命中 {len(hit['matches'])} 个")
    else:
        result["decision"] = "ALL_EMPTY_CREATE"
        print("\n[EMPTY] 7 层全部为空, 可以创造")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = find_before_build(args.target, deep=args.deep)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    code_map = {"FOUND_REUSE": 1, "ALL_EMPTY_CREATE": 0}
    sys.exit(code_map.get(result["decision"], 0))


if __name__ == "__main__":
    main()