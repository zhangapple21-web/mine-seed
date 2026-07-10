#!/usr/bin/env python3
"""
OPS-000: Asset First Protocol - 资产优先协议
=============================================

工作哲学 (不是功能):
  收到目标 → 7 步资产盘点 → 确认不存在才动手

  ① 看 GitHub (文明地图)
  ② 看本地 Workspace
  ③ 看 Archive
  ④ 看 TG 收藏夹
  ⑤ 看历史 PR
  ⑥ 看以前失败记录
  ⑦ 看免费矿工能力

公理根基:
  #002 考古不是搬家是炼金
  #011 记忆是推断的不是存储的
  #018 拆壳不拆骨, 核心不变量不可删

用法:
  python ops_000_asset_first.py "实现信号路由"     # 检查目标是否已有
  python ops_000_asset_first.py --list             # 列出所有已有资产
  python ops_000_asset_first.py --json             # JSON 输出
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

ASSET_KEYWORDS = {
    "miner": ["miner", "矿工", "mining", "routing", "路由"],
    "signal": ["signal", "信号", "discovery", "发现"],
    "archivist": ["archivist", "档案", "archive"],
    "governance": ["governance", "治理", "roundtable", "圆桌", "governor"],
    "constraint": ["constraint", "约束", "RFC", "EGP"],
    "bootstrap": ["bootstrap", "ABP", "启动"],
    "recovery": ["recovery", "恢复", "RP", "recover"],
    "heartbeat": ["heartbeat", "心跳"],
    "evolution": ["evolution", "演化", "seed"],
    "memory": ["memory", "记忆", "memory_index"],
    "model": ["model", "模型", "router", "nim", "glm"],
    "watcher": ["watcher", "observer", "观察", "monitoring"],
}


def search_local(target):
    print("[②] Local Workspace...")
    matches = []
    target_low = target.lower()
    for search_dir in ["r1_archaeology", "04_PROTOCOLS", "00_ROOT", "05_TOOLS"]:
        d = WORKSPACE / search_dir
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if not f.is_file():
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if target_low in content.lower():
                    rel = str(f.relative_to(WORKSPACE))
                    matches.append({"path": rel, "size": f.stat().st_size, "category": search_dir})
                    if len(matches) >= 5:
                        break
            except:
                pass
        if len(matches) >= 5:
            break
    print(f"    {len(matches)} matches")
    return {"source": "local_workspace", "matches": matches}


def search_github(target):
    print("[①] GitHub...")
    if not GITHUB_PAT:
        return {"source": "github", "matches": [], "error": "no_token"}
    matches = []
    try:
        url = "https://api.github.com/search/code"
        params = f"q={urllib.parse.quote(target)}+org:zhangapple21-web"
        req = urllib.request.Request(f"{url}?{params}", headers={"Authorization": f"Bearer {GITHUB_PAT}", "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            for item in data.get("items", [])[:5]:
                matches.append({"repo": item.get("repository", {}).get("full_name"), "path": item.get("path"), "url": item.get("html_url")})
    except Exception as e:
        return {"source": "github", "matches": [], "error": str(e)[:50]}
    print(f"    {len(matches)} matches")
    return {"source": "github", "matches": matches}


def search_archive(target):
    print("[③] Archive...")
    matches = []
    target_low = target.lower()
    for archive_dir in ["02_MEMORY", "r1_archaeology"]:
        d = WORKSPACE / archive_dir
        if not d.exists():
            continue
        for sub in d.rglob("*"):
            if sub.is_dir() and target_low in sub.name.lower():
                matches.append({"path": str(sub.relative_to(WORKSPACE)), "type": "directory"})
    print(f"    {len(matches)} matches")
    return {"source": "archive", "matches": matches}


def search_tg_collections(target):
    print("[④] TG 收藏夹...")
    matches = []
    target_low = target.lower()
    tg_cache_dirs = [WORKSPACE / "03_DATA" / "tg_collections", Path.home() / "Downloads" / "Telegram Desktop"]
    for d in tg_cache_dirs:
        if not d.exists():
            continue
        for f in d.rglob("*.json"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if target_low in content.lower():
                    matches.append({"path": str(f.relative_to(d))})
                    if len(matches) >= 5:
                        break
            except:
                pass
        if len(matches) >= 5:
            break
    print(f"    {len(matches)} matches")
    return {"source": "tg_collections", "matches": matches}


def search_zip_snapshots(target):
    print("[⑤] ZIP / Snapshot...")
    matches = []
    target_low = target.lower()
    for d in [WORKSPACE / "99_RECOVERY_TEMP", Path.home() / "Downloads"]:
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.suffix.lower() in {".zip", ".7z", ".tar", ".gz"} and target_low in f.name.lower():
                matches.append({"path": str(f), "size": f.stat().st_size})
    print(f"    {len(matches)} matches")
    return {"source": "zip_snapshot", "matches": matches}


def search_pr_history(target):
    print("[⑥] PR History...")
    matches = []
    target_low = target.lower()
    git_dir = WORKSPACE / ".git"
    if git_dir.exists():
        try:
            import subprocess
            r = subprocess.run(["git", "log", "--all", "--oneline", f"--grep={target_low}"], cwd=str(WORKSPACE), capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                for line in r.stdout.strip().split("\n")[:5]:
                    if line:
                        matches.append({"commit": line})
        except:
            pass
    print(f"    {len(matches)} matches")
    return {"source": "pr_history", "matches": matches}


def search_rfc_protocol(target):
    print("[⑦] RFC / Protocol...")
    matches = []
    target_low = target.lower()
    for d in [WORKSPACE / "r1_archaeology" / "rfc", WORKSPACE / "04_PROTOCOLS"]:
        if not d.exists():
            continue
        for f in d.rglob("*.md"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")[:5000]
                if target_low in content.lower():
                    matches.append({"path": str(f.relative_to(WORKSPACE)), "is_protocol": "PROTOCOL" in content.upper() or "RFC" in f.name.upper()})
                    if len(matches) >= 5:
                        break
            except:
                pass
        if len(matches) >= 5:
            break
    print(f"    {len(matches)} matches")
    return {"source": "rfc_protocol", "matches": matches}


def search_free_miners(target):
    print("[⑧] Free Miners...")
    capabilities = {
        "github_models": {"available": bool(GITHUB_PAT), "models": ["gpt-4o-mini", "Phi-3", "Llama-3.2"], "best_for": ["code_review", "quick_inference"]},
        "zhipu_glm": {"available": bool(os.environ.get("ZHIPU_KEY")), "models": ["glm-4-flash"], "best_for": ["report_generation"]},
        "nim_keys": {"available": any(os.environ.get(f"NIM_KEY_{i}") for i in range(1, 17)), "count": sum(1 for i in range(1, 17) if os.environ.get(f"NIM_KEY_{i}"))},
        "openrouter": {"available": bool(os.environ.get("OPENROUTER_KEY"))},
    }
    return {"source": "free_miners", "capabilities": capabilities}


def asset_first(target):
    print(f"\n{'='*60}\nOPS-000 Asset First: {target}\n{'='*60}\n")
    report = {"target": target, "time": datetime.now().isoformat(), "steps": {}, "total_matches": 0, "verdict": "unknown"}
    steps = [("① GitHub", search_github), ("② Local", search_local), ("③ Archive", search_archive), ("④ TG", search_tg_collections), ("⑤ ZIP", search_zip_snapshots), ("⑥ PR", search_pr_history), ("⑦ RFC", search_rfc_protocol), ("⑧ Miners", search_free_miners)]
    for label, fn in steps:
        result = fn(target)
        report["steps"][label] = result
        if "matches" in result:
            report["total_matches"] += len(result["matches"])
    if report["total_matches"] > 0:
        report["verdict"] = "EXISTS_MAYBE_REUSE"
        report["recommendation"] = "已有相关资产,建议先考古再决定是否新建"
    else:
        report["verdict"] = "NOT_FOUND_CAN_CREATE"
        report["recommendation"] = "确认不存在,可以新建"
    return report


def list_all_assets():
    print(f"\n{'='*60}\nAsset Map - 文明资产总览\n{'='*60}\n")
    asset_map = {}
    proto_dir = WORKSPACE / "04_PROTOCOLS"
    if proto_dir.exists():
        asset_map["protocols"] = [f.name for f in proto_dir.glob("*.py")]
    principles = WORKSPACE / "00_ROOT" / "PRINCIPLES.md"
    if principles.exists():
        asset_map["axioms"] = principles.read_text(encoding="utf-8").count("#")
    r1_dir = WORKSPACE / "r1_archaeology"
    if r1_dir.exists():
        rfcs = list((r1_dir / "rfc").rglob("*.md")) if (r1_dir / "rfc").exists() else []
        dailies = list((r1_dir / "daily").rglob("*.md")) if (r1_dir / "daily").exists() else []
        asset_map["r1_archaeology"] = {"rfcs": len(rfcs), "dailies": len(dailies)}
    return asset_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.list:
        print(json.dumps(list_all_assets(), ensure_ascii=False, indent=2))
    elif args.target:
        result = asset_first(args.target)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"Total: {result['total_matches']}, Verdict: {result['verdict']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()