#!/usr/bin/env python3
# TYPE: dev_tool
"""
OPS-001: Asset Before Action (ABA) - 行动前资产检查
==================================================

工作哲学: 任何开发之前, 先检查文明资产.
用法: python ops_001_aba.py "实现X功能"
"""
import sys, argparse, json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from ops_000_asset_first import asset_first


def check_before_action(target, force=False):
    print(f"\n{'='*60}\nOPS-001 ABA: {target}\n{'='*60}\n")
    if force:
        return {"decision": "FORCED", "target": target, "time": datetime.now().isoformat()}
    report = asset_first(target)
    total = report["total_matches"]
    high_value = 0
    for label, step in report["steps"].items():
        for m in step.get("matches", []):
            if isinstance(m, dict):
                if m.get("is_protocol") or "rfc" in str(m.get("path", "")).lower():
                    high_value += 1
    if high_value >= 2:
        decision = "EXISTS_REUSE"
        recommendation = f"发现 {high_value} 个高价值资产 (RFC/Protocol), 必须先考古复用"
    elif total >= 3:
        decision = "PARTIAL_REUSE"
        recommendation = f"发现 {total} 个相关资产, 建议考古后再决定"
    elif total > 0:
        decision = "MAYBE_REUSE"
        recommendation = f"发现 {total} 个弱相关, 可以新建但需记录理由"
    else:
        decision = "NOT_FOUND_CREATE"
        recommendation = "确认不存在, 可以新建"
    print(f"\nDECISION: {decision}\nRECOMMENDATION: {recommendation}\nTotal: {total} (high-value: {high_value})")
    return {"decision": decision, "recommendation": recommendation, "target": target, "matches": total, "high_value": high_value, "details": report}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.target:
        parser.print_help(); sys.exit(1)
    result = check_before_action(args.target, force=args.force)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    code_map = {"NOT_FOUND_CREATE": 0, "MAYBE_REUSE": 2, "PARTIAL_REUSE": 2, "EXISTS_REUSE": 1, "FORCED": 0}
    sys.exit(code_map.get(result["decision"], 0))


if __name__ == "__main__":
    main()