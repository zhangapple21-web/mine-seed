#!/usr/bin/env python3
"""
DFP-001: Drawer First Protocol - 抽屉优先协议
==============================================

**公理根基**: #002 / #010 / #018 / #021

**核心**: 任何设计、实现、重构、派单之前，必须先扫描现有文明资产。

**约束编号**: C-00X

**角色**: 文明 Runtime 的第一层入口

七步扫描流程:
  ① Scan Existing Modules    — 扫描现有模块
  ② Check RFC                — 检查 RFC
  ③ Check Protocol           — 检查协议
  ④ Check Experience         — 检查经验
  ⑤ Check Constraint         — 检查约束
  ⑥ Check Blueprint          — 检查蓝图
  ⑦ Decision                 — 决策（Reuse / Extend / New）

决策规则:
  - 存在完整实现 → Reuse（复用）
  - 存在但不完整 → Extend（扩展）
  - 不存在或不满足 → New（新建）

禁止重复发明已经存在的文明资产。

用法:
  python ops_000_asset_first.py "实现信号路由"     # 检查目标是否已有
  python ops_000_asset_first.py --scan            # 完整抽屉扫描
  python ops_000_asset_first.py --list            # 列出所有已有资产
  python ops_000_asset_first.py --json            # JSON 输出
  python ops_000_asset_first.py --mission <mid>   # 为 Mission 做抽屉扫描
"""
import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from collections import defaultdict

WORKSPACE = Path(__file__).parent.parent
GITHUB_PAT = os.environ.get("GITHUB_PAT", "")

# 资产类型定义
ASSET_TYPES = {
    "module": {"label": "模块", "dir": "04_PROTOCOLS", "pattern": "*.py"},
    "rfc": {"label": "RFC", "dir": "r1_archaeology/rfc", "pattern": "*.md"},
    "protocol": {"label": "协议", "dir": "04_PROTOCOLS", "pattern": "*.py"},
    "experience": {"label": "经验", "dir": "02_MEMORY/experience", "pattern": "*.json"},
    "constraint": {"label": "约束", "dir": "03_DATA/CONSTRAINTS", "pattern": "*.md"},
    "blueprint": {"label": "蓝图", "dir": "03_DATA/raw_sources/docs", "pattern": "*.md"},
    "repository": {"label": "仓库", "dir": "03_DATA/CIV_REPOSITORY", "pattern": "*.json"},
}

# 模块分类映射
MODULE_CATEGORIES = {
    "recovery": ["recovery", "restore", "awaken", "environment"],
    "governance": ["governor", "roundtable", "debate", "constraint"],
    "memory": ["memory", "experience", "journal", "archive", "seed"],
    "routing": ["router", "worker", "pool", "dispatch"],
    "mission": ["mission", "question", "task"],
    "repository": ["repository", "store", "manager"],
    "admission": ["admission", "curator"],
    "evolution": ["evolution", "learning", "self"],
    "heartbeat": ["heartbeat", "monitor", "health"],
}


def scan_modules(target):
    """扫描现有模块"""
    print("[①] Scanning Modules...")
    matches = []
    target_low = target.lower()
    proto_dir = WORKSPACE / "04_PROTOCOLS"
    if not proto_dir.exists():
        return {"source": "modules", "matches": []}

    for f in proto_dir.glob("*.py"):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")[:5000]
            if target_low in content.lower() or target_low in f.name.lower():
                # 判断模块类别
                category = "other"
                for cat_key, cat_terms in MODULE_CATEGORIES.items():
                    if any(term in f.name.lower() for term in cat_terms):
                        category = cat_key
                        break

                matches.append({
                    "path": str(f.relative_to(WORKSPACE)),
                    "name": f.stem,
                    "category": category,
                    "description": _extract_description(content),
                })
        except Exception:
            pass
    print(f"    {len(matches)} matches")
    return {"source": "modules", "matches": matches}


def scan_rfc(target):
    """检查 RFC"""
    print("[②] Checking RFC...")
    matches = []
    target_low = target.lower()
    rfc_dir = WORKSPACE / "r1_archaeology" / "rfc"
    if not rfc_dir.exists():
        return {"source": "rfc", "matches": []}

    for f in rfc_dir.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")[:3000]
            if target_low in content.lower():
                matches.append({
                    "path": str(f.relative_to(WORKSPACE)),
                    "name": f.stem,
                    "is_protocol": "PROTOCOL" in content.upper(),
                })
        except Exception:
            pass
    print(f"    {len(matches)} matches")
    return {"source": "rfc", "matches": matches}


def scan_protocols(target):
    """检查协议"""
    print("[③] Checking Protocols...")
    matches = []
    target_low = target.lower()
    proto_dir = WORKSPACE / "04_PROTOCOLS"
    if not proto_dir.exists():
        return {"source": "protocols", "matches": []}

    for f in proto_dir.glob("*.py"):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")[:3000]
            if '"""' in content:
                doc_start = content.index('"""') + 3
                doc_end = content.index('"""', doc_start)
                doc = content[doc_start:doc_end]
                if target_low in doc.lower():
                    matches.append({
                        "path": str(f.relative_to(WORKSPACE)),
                        "name": f.stem,
                        "doc": doc[:100],
                    })
        except Exception:
            pass
    print(f"    {len(matches)} matches")
    return {"source": "protocols", "matches": matches}


def scan_experience(target):
    """检查经验"""
    print("[④] Checking Experience...")
    matches = []
    target_low = target.lower()
    exp_dir = WORKSPACE / "02_MEMORY" / "experience"
    if not exp_dir.exists():
        return {"source": "experience", "matches": []}

    for f in exp_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="ignore"))
            if target_low in str(data).lower():
                matches.append({
                    "path": str(f.relative_to(WORKSPACE)),
                    "type": data.get("type", "unknown"),
                    "timestamp": data.get("timestamp", ""),
                })
        except Exception:
            pass
    print(f"    {len(matches)} matches")
    return {"source": "experience", "matches": matches}


def scan_constraints(target):
    """检查约束"""
    print("[⑤] Checking Constraints...")
    matches = []
    target_low = target.lower()
    const_dir = WORKSPACE / "03_DATA" / "CONSTRAINTS"
    if not const_dir.exists():
        return {"source": "constraints", "matches": []}

    for f in const_dir.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")[:3000]
            if target_low in content.lower():
                matches.append({
                    "path": str(f.relative_to(WORKSPACE)),
                    "name": f.stem,
                })
        except Exception:
            pass
    print(f"    {len(matches)} matches")
    return {"source": "constraints", "matches": matches}


def scan_blueprints(target):
    """检查蓝图"""
    print("[⑥] Checking Blueprints...")
    matches = []
    target_low = target.lower()
    bp_dir = WORKSPACE / "03_DATA" / "raw_sources" / "docs"
    if not bp_dir.exists():
        bp_dir = WORKSPACE / "03_DATA"
    if not bp_dir.exists():
        return {"source": "blueprints", "matches": []}

    for f in bp_dir.rglob("*.md"):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")[:3000]
            if target_low in content.lower():
                matches.append({
                    "path": str(f.relative_to(WORKSPACE)),
                    "name": f.stem,
                })
        except Exception:
            pass
    print(f"    {len(matches)} matches")
    return {"source": "blueprints", "matches": matches}


def _extract_description(content):
    """提取文件描述"""
    try:
        if '"""' in content:
            doc_start = content.index('"""') + 3
            doc_end = content.index('"""', doc_start)
            doc = content[doc_start:doc_end].strip()
            lines = doc.split("\n")
            for line in lines:
                if line.strip() and not line.startswith("#") and not line.startswith("="):
                    return line.strip()[:80]
        return ""
    except Exception:
        return ""


def make_decision(steps):
    """根据扫描结果做出决策"""
    total_matches = sum(len(s.get("matches", [])) for s in steps.values())

    # 检查是否有完整实现
    has_module = len(steps.get("modules", {}).get("matches", [])) > 0
    has_protocol = len(steps.get("protocols", {}).get("matches", [])) > 0
    has_blueprint = len(steps.get("blueprints", {}).get("matches", [])) > 0

    if has_module and has_protocol:
        verdict = "REUSE"
        recommendation = "已存在完整实现，建议复用现有模块"
    elif has_module or has_protocol:
        verdict = "EXTEND"
        recommendation = "存在部分实现，建议扩展现有模块"
    elif total_matches > 0:
        verdict = "EXTEND"
        recommendation = "存在相关资产，建议基于现有资产扩展"
    else:
        verdict = "NEW"
        recommendation = "确认不存在，可新建"

    return {
        "verdict": verdict,
        "recommendation": recommendation,
        "total_matches": total_matches,
    }


def draw_scan(target):
    """完整抽屉扫描"""
    print(f"\n{'='*70}")
    print(f"DFP-001: Drawer First Protocol — {target}")
    print(f"{'='*70}\n")

    report = {
        "target": target,
        "time": datetime.now().isoformat(),
        "steps": {},
        "decision": {},
    }

    # 七步扫描
    steps = [
        ("① Modules", scan_modules),
        ("② RFC", scan_rfc),
        ("③ Protocols", scan_protocols),
        ("④ Experience", scan_experience),
        ("⑤ Constraints", scan_constraints),
        ("⑥ Blueprints", scan_blueprints),
    ]

    for label, fn in steps:
        result = fn(target)
        report["steps"][label] = result

    # ⑦ Decision
    report["decision"] = make_decision(report["steps"])

    print(f"\n{'='*70}")
    print(f"Verdict: {report['decision']['verdict']}")
    print(f"Recommendation: {report['decision']['recommendation']}")
    print(f"Total matches: {report['decision']['total_matches']}")
    print(f"{'='*70}")

    return report


def list_all_assets():
    """列出所有文明资产"""
    print(f"\n{'='*70}")
    print("Civilization Asset Map — 文明资产总览")
    print(f"{'='*70}\n")

    asset_map = {}

    # 模块
    proto_dir = WORKSPACE / "04_PROTOCOLS"
    if proto_dir.exists():
        asset_map["protocols"] = [f.name for f in proto_dir.glob("*.py")]

    # RFC
    rfc_dir = WORKSPACE / "r1_archaeology" / "rfc"
    if rfc_dir.exists():
        asset_map["rfcs"] = [f.name for f in rfc_dir.glob("*.md")]

    # 经验
    exp_dir = WORKSPACE / "02_MEMORY" / "experience"
    if exp_dir.exists():
        asset_map["experiences"] = [f.name for f in exp_dir.glob("*.json")]

    # 约束
    const_dir = WORKSPACE / "03_DATA" / "CONSTRAINTS"
    if const_dir.exists():
        asset_map["constraints"] = [f.name for f in const_dir.glob("*.md")]

    # 文明仓库
    repo_dir = WORKSPACE / "03_DATA" / "CIV_REPOSITORY"
    if repo_dir.exists():
        try:
            index_file = repo_dir / "index.json"
            if index_file.exists():
                data = json.loads(index_file.read_text(encoding="utf-8"))
                asset_map["repository"] = {
                    "version": data.get("version", "unknown"),
                    "total_assets": data.get("total_assets", 0),
                    "by_type": data.get("by_type", {}),
                }
        except Exception:
            pass

    # 公理
    principles = WORKSPACE / "00_ROOT" / "PRINCIPLES.md"
    if principles.exists():
        content = principles.read_text(encoding="utf-8")
        axiom_count = content.count("#0")
        asset_map["axioms"] = f"{axiom_count} 条"

    return asset_map


def scan_for_mission(mid):
    """为 Mission 做抽屉扫描"""
    try:
        from mission_protocol import protocol
        mission = protocol.get(mid)
        if not mission:
            return {"error": f"Mission {mid} not found"}

        target = mission.name
        print(f"\n{'='*70}")
        print(f"DFP-001: Drawer Scan for Mission — {mid}")
        print(f"{'='*70}\n")

        report = draw_scan(target)

        # 更新 Mission 的 scope 添加抽屉扫描报告
        if mission.scope:
            mission.scope += "\n\n"
        mission.scope += f"""## Phase 0: Drawer Scan Report

**Target**: {target}
**Time**: {report['time']}
**Verdict**: {report['decision']['verdict']}
**Recommendation**: {report['decision']['recommendation']}
**Total matches**: {report['decision']['total_matches']}

### Scan Results

"""
        for step_name, step_data in report["steps"].items():
            matches = step_data.get("matches", [])
            mission.scope += f"#### {step_name}\n"
            if matches:
                for m in matches[:5]:
                    mission.scope += f"- {m.get('name', m.get('path', ''))}\n"
            else:
                mission.scope += "- (无匹配)\n"
            mission.scope += "\n"

        protocol._save(mission)
        print(f"\nDrawer Report saved to Mission {mid}")

        return report
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="DFP-001: Drawer First Protocol")
    parser.add_argument("target", nargs="?", help="目标关键词")
    parser.add_argument("--scan", action="store_true", help="完整抽屉扫描")
    parser.add_argument("--list", action="store_true", help="列出所有已有资产")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--mission", type=str, help="为指定 Mission 做抽屉扫描")
    args = parser.parse_args()

    if args.list:
        asset_map = list_all_assets()
        if args.json:
            print(json.dumps(asset_map, ensure_ascii=False, indent=2))
        else:
            for category, items in asset_map.items():
                print(f"\n{category}:")
                if isinstance(items, list):
                    for item in items[:10]:
                        print(f"  - {item}")
                    if len(items) > 10:
                        print(f"  ... ({len(items) - 10} more)")
                else:
                    print(f"  {items}")

    elif args.mission:
        result = scan_for_mission(args.mission)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.target or args.scan:
        target = args.target or "full_scan"
        result = draw_scan(target)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
