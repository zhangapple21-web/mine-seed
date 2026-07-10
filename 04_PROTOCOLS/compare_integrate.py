#!/usr/bin/env python3
"""
Compare & Integrate - 对比/合并工具
====================================

公理根基:
  #002 考古不是搬家是炼金
  #010 演化只允许增加结构, 不允许破坏不变量
  #021 贡献不可回收

执行语义:
  对比 source 与 target 两个目录, 找出:
    - target_only: 已存在但 source 没有 (保留)
    - source_only: source 有但 target 没有 (新内容, 待蒸馏后合并)
    - common_same: 同名同内容 (skip)
    - common_differ: 同名不同内容 (用 supersede 机制: target 旧版归档, source 新版入位)
  这是 Recovery Protocol 之后的整理步骤.

用法:
  python compare_integrate.py <source> <target>            # 仅报告
  python compare_integrate.py <source> <target> --merge    # 自动 merge (用 supersede)
  python compare_integrate.py <source> <target> --json     # JSON 输出
"""
import os
import sys
import json
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 忽略模式
IGNORE = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".vscode", ".idea"}

def file_hash(p: Path, algo="md5", chunk=65536) -> str:
    h = hashlib.new(algo)
    try:
        with open(p, "rb") as f:
            for block in iter(lambda: f.read(chunk), b""):
                h.update(block)
        return h.hexdigest()
    except Exception:
        return ""

def walk_files(root: Path, ignore=IGNORE) -> dict:
    """Walk a directory tree, returning {rel_path: hash}."""
    root = root.resolve()
    files = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(p in ignore for p in rel_parts):
            continue
        try:
            h = file_hash(path)
            if h:
                files[str(path.relative_to(root))] = h
        except OSError:
            continue
    return files

def supersede_path(target_root: Path, rel: str) -> Path:
    """Generate a SUPERSEDED archive path for an old file."""
    p = target_root / rel
    parent = p.parent
    stem = p.stem
    suffix = p.suffix
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return parent / f"{stem}.SUPERSEDED_{ts}{suffix}"

def merge_with_supersede(source: Path, target: Path, dry_run: bool = True) -> dict:
    """
    Merge source into target:
    - source_only files: copy to target
    - common_differ files: archive old target as SUPERSEDED, copy new from source
    - common_same files: skip
    - target_only files: keep as-is
    """
    source = source.resolve()
    target = target.resolve()
    if not source.exists() or not target.exists():
        return {"error": "source or target does not exist"}

    print(f"Indexing source: {source}")
    src_files = walk_files(source)
    print(f"  {len(src_files)} files")

    print(f"Indexing target: {target}")
    tgt_files = walk_files(target)
    print(f"  {len(tgt_files)} files")

    src_set = set(src_files.keys())
    tgt_set = set(tgt_files.keys())
    only_src = sorted(src_set - tgt_set)
    common = sorted(src_set & tgt_set)
    only_tgt = sorted(tgt_set - src_set)
    differing = sorted([c for c in common if src_files[c] != tgt_files[c]])

    report = {
        "source": str(source),
        "target": str(target),
        "time": datetime.now().isoformat(),
        "dry_run": dry_run,
        "counts": {
            "source_files": len(src_files),
            "target_files": len(tgt_files),
            "source_only": len(only_src),
            "common_same": len(common) - len(differing),
            "common_differ": len(differing),
            "target_only": len(only_tgt),
        },
        "merged": 0,
        "superseded": 0,
        "skipped": 0,
        "errors": [],
        "merged_files": [],
        "superseded_files": [],
    }

    if dry_run:
        report["preview_source_only"] = only_src[:30]
        report["preview_common_differ"] = differing[:30]
        return report

    # 1. Copy source-only files to target
    for rel in only_src:
        src_p = source / rel
        tgt_p = target / rel
        try:
            tgt_p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_p, tgt_p)
            report["merged"] += 1
            report["merged_files"].append(rel)
        except Exception as e:
            report["errors"].append(f"copy:{rel}: {e}")

    # 2. For differing files: archive old as SUPERSEDED, then copy new
    for rel in differing:
        src_p = source / rel
        tgt_p = target / rel
        try:
            if tgt_p.exists():
                archive_p = supersede_path(target, rel)
                if not archive_p.exists():  # don't overwrite prior archive
                    shutil.move(str(tgt_p), str(archive_p))
                    report["superseded"] += 1
                    report["superseded_files"].append(str(archive_p.relative_to(target)))
            shutil.copy2(src_p, tgt_p)
            report["merged"] += 1
            report["merged_files"].append(rel)
        except Exception as e:
            report["errors"].append(f"diff:{rel}: {e}")

    return report

def print_report(report: dict, verbose: bool = False):
    print("=" * 70)
    print(f"  Compare & Integrate Report")
    print(f"  Source: {report['source']}")
    print(f"  Target: {report['target']}")
    print(f"  Time: {report['time']}")
    print(f"  Mode: {'DRY-RUN' if report.get('dry_run') else 'EXECUTE'}")
    print("=" * 70)
    c = report["counts"]
    print(f"  Source files        : {c['source_files']}")
    print(f"  Target files        : {c['target_files']}")
    print(f"  Source-only (NEW)   : {c['source_only']}")
    print(f"  Common (same)       : {c['common_same']}")
    print(f"  Common (differ)     : {c['common_differ']}  (will be SUPERSEDED)")
    print(f"  Target-only         : {c['target_only']}  (will be KEPT)")
    if not report.get("dry_run"):
        print()
        print(f"  Merged     : {report['merged']}")
        print(f"  Superseded : {report['superseded']}")
        print(f"  Errors     : {len(report['errors'])}")
    if verbose:
        if report.get("preview_source_only"):
            print()
            print("--- Source-only preview (NEW files) ---")
            for f in report["preview_source_only"]:
                print(f"  + {f}")
        if report.get("preview_common_differ"):
            print()
            print("--- Common-differ preview (will be SUPERSEDED) ---")
            for f in report["preview_common_differ"]:
                print(f"  ~ {f}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Compare/merge two directories with supersede mechanism")
    parser.add_argument("source", help="Source directory (recovery)")
    parser.add_argument("target", help="Target directory (workspace)")
    parser.add_argument("--merge", action="store_true", help="Actually perform merge (default is dry-run)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", action="store_true", help="Show file previews")
    args = parser.parse_args()

    report = merge_with_supersede(
        Path(args.source),
        Path(args.target),
        dry_run=not args.merge,
    )
    if args.json:
        # Trim previews for JSON
        out = {k: v for k, v in report.items() if not k.startswith("preview_")}
        if "preview_source_only" in report:
            out["preview_source_only"] = report["preview_source_only"][:20]
        if "preview_common_differ" in report:
            out["preview_common_differ"] = report["preview_common_differ"][:20]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print_report(report, verbose=args.verbose)

    sys.exit(0 if not report.get("errors") else 1)

if __name__ == "__main__":
    main()
