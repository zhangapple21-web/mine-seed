#!/usr/bin/env python3
"""
OPS-004: Recovery First - 恢复优先
===================================

工作哲学: 任何 AI 接管项目, 第一件事不是 Bootstrap, 而是 Recovery
6 层接管检查: workspace/TG/models/zip/protocols/github
"""
import os, sys, json, argparse, subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from environment_first import scan_directory, build_recovery_graph

WORKSPACE = Path(__file__).parent.parent


def check_layer_workspace():
    return {"layer": "workspace", "exists": (WORKSPACE / "00_ROOT").exists(), "root": str(WORKSPACE), "protocols": len(list((WORKSPACE / "04_PROTOCOLS").glob("*.py")))}


def check_layer_telegram():
    has_api = bool(os.environ.get("TELEGRAM_API_ID") and os.environ.get("TELEGRAM_API_HASH"))
    has_bots = bool(os.environ.get("TG_BOT_TOKEN_1") or os.environ.get("TG_BOT_TOKEN_2"))
    return {"layer": "telegram", "api_credentials": has_api, "bot_tokens": sum(bool(os.environ.get(f"TG_BOT_TOKEN_{i}")) for i in range(1, 3)), "needs_recovery": not (has_api and has_bots)}


def check_layer_models():
    available = []
    if os.environ.get("GITHUB_PAT"): available.append("github_models")
    if os.environ.get("ZHIPU_KEY"): available.append("zhipu_glm")
    if any(os.environ.get(f"NIM_KEY_{i}") for i in range(1, 17)): available.append("nvidia_nim")
    if os.environ.get("OPENROUTER_KEY"): available.append("openrouter")
    return {"layer": "models", "available": available, "count": len(available), "needs_recovery": len(available) == 0}


def check_layer_zip():
    downloads = Path.home() / "Downloads"
    zips = []
    if downloads.exists():
        for f in downloads.iterdir():
            if f.suffix.lower() in {".zip", ".7z", ".tar"}:
                zips.append({"name": f.name, "size_mb": f.stat().st_size / 1024 / 1024})
    return {"layer": "zip_snapshot", "found_zips": len(zips), "needs_recovery": len(zips) > 0}


def check_layer_protocols():
    proto_dir = WORKSPACE / "04_PROTOCOLS"
    if not proto_dir.exists(): return {"layer": "protocols", "exists": False, "needs_recovery": True}
    return {"layer": "protocols", "exists": True, "count": len(list(proto_dir.glob("*.py"))), "needs_recovery": False}


def check_layer_github():
    try:
        r = subprocess.run(["git", "log", "--oneline", "-1"], cwd=str(WORKSPACE), capture_output=True, text=True, timeout=10)
        return {"layer": "github", "last_commit": r.stdout.strip(), "synced": r.returncode == 0}
    except:
        return {"layer": "github", "synced": False, "needs_recovery": True}


def recovery_first(check_only=False, layer=None):
    print(f"\n{'='*60}\nOPS-004 Recovery First\n{'='*60}\n")
    layers = {"workspace": check_layer_workspace, "telegram": check_layer_telegram, "models": check_layer_models, "zip": check_layer_zip, "protocols": check_layer_protocols, "github": check_layer_github}
    target = [layer] if layer else list(layers.keys())
    report = {"time": datetime.now().isoformat(), "mode": "check_only" if check_only else "execute", "layers": {}, "recovery_actions": []}
    for lyr in target:
        if lyr not in layers: continue
        result = layers[lyr]()
        report["layers"][lyr] = result
        icon = "[OK]" if not result.get("needs_recovery", False) else "[NEED]"
        print(f"{icon} {lyr}: {result.get('count', result.get('exists', '?'))}")
    needs = sum(1 for r in report["layers"].values() if r.get("needs_recovery"))
    total = len(report["layers"])
    report["summary"] = {"ok": total - needs, "needs_recovery": needs, "ready": needs == 0}
    print(f"\n{'='*60}\n  Status: {report['summary']['ok']}/{total} OK\n{'='*60}")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--layer", choices=["workspace", "telegram", "models", "zip", "protocols", "github"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = recovery_first(check_only=args.check, layer=args.layer)
    if args.json: print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    sys.exit(0 if result["summary"]["ready"] else 1)


if __name__ == "__main__":
    main()