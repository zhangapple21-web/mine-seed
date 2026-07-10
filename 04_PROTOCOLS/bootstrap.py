#!/usr/bin/env python3
"""
ACE Bootstrap Protocol (ABP) - 环境引导协议
============================================

目标: 给我一台全新的电脑, 30 分钟内恢复 ACE 生态
七层: OS/Runtime/AI/Connector/Workspace/Observer/Autonomy
"""
import os, sys, json, subprocess, urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent


def check_os():
    checks = {"os": sys.platform, "python_version": sys.version.split()[0], "python_path": sys.executable}
    try:
        r = subprocess.run(["powershell", "-Command", "$PSVersionTable.PSVersion"], capture_output=True, text=True, timeout=5)
        checks["powershell"] = r.stdout.strip() if r.returncode == 0 else "NOT_FOUND"
    except: checks["powershell"] = "ERROR"
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
        checks["git"] = r.stdout.strip() if r.returncode == 0 else "NOT_FOUND"
    except: checks["git"] = "NOT_FOUND"
    try:
        r = subprocess.run(["7z"], capture_output=True, text=True, timeout=5)
        checks["7z"] = "OK" if r.returncode == 0 else "NOT_FOUND"
    except: checks["7z"] = "NOT_FOUND"
    checks["status"] = "OK" if checks.get("git") != "NOT_FOUND" else "NEED_INSTALL"
    return checks


def check_runtime():
    checks = {}
    for pkg in ["requests", "urllib3"]:
        try: __import__(pkg); checks[f"pkg_{pkg}"] = "OK"
        except ImportError: checks[f"pkg_{pkg}"] = "MISSING"
    try:
        r = subprocess.run(["uv", "--version"], capture_output=True, text=True, timeout=5)
        checks["uv"] = r.stdout.strip() if r.returncode == 0 else "NOT_FOUND"
    except: checks["uv"] = "NOT_FOUND"
    checks["status"] = "OK"
    return checks


def check_ai():
    checks = {}
    gh_pat = os.environ.get("GITHUB_PAT", "")
    checks["github_pat_set"] = "YES" if gh_pat else "NO"
    if gh_pat:
        try:
            url = "https://models.inference.ai.azure.com/models"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {gh_pat}"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                checks["github_models"] = f"OK ({len(data)} models)"
        except Exception as e:
            checks["github_models"] = f"ERROR: {str(e)[:50]}"
    else: checks["github_models"] = "NO_KEY"
    checks["nim_keys"] = f"{sum(1 for i in range(1, 17) if os.environ.get(f'NIM_KEY_{i}'))} keys"
    checks["zhipu_key"] = "YES" if os.environ.get("ZHIPU_KEY") else "NO"
    checks["openrouter_key"] = "YES" if os.environ.get("OPENROUTER_KEY") else "NO"
    checks["status"] = "OK" if "OK" in str(checks.get("github_models", "")) else "NO_AI"
    return checks


def check_connector():
    checks = {}
    checks["tg_api_credentials"] = "YES" if os.environ.get("TELEGRAM_API_ID") and os.environ.get("TELEGRAM_API_HASH") else "NO"
    checks["github_token"] = "YES" if os.environ.get("GITHUB_PAT") else "NO"
    downloads = Path.home() / "Downloads"
    checks["downloads_folder"] = "EXISTS" if downloads.exists() else "MISSING"
    checks["status"] = "OK" if checks["github_token"] == "YES" else "PARTIAL"
    return checks


def check_workspace():
    checks = {}
    checks["mine_seed"] = f"EXISTS" if (WORKSPACE / "00_ROOT").exists() else "MISSING"
    for f in ["00_ROOT/PRINCIPLES.md", "04_PROTOCOLS/bootstrap.py", "05_TOOLS/miner/miner_env.sh"]:
        checks[f"file_{Path(f).stem}"] = "EXISTS" if (WORKSPACE / f).exists() else "MISSING"
    for p in ["environment_first.py", "recovery_protocol.py", "awaken.py", "ops_005_self_loop.py"]:
        checks[p.replace(".py", "")] = "EXISTS" if (WORKSPACE / "04_PROTOCOLS" / p).exists() else "MISSING"
    ok = sum(1 for v in checks.values() if v == "EXISTS")
    checks["status"] = "OK" if ok >= 5 else "NEED_RECOVER"
    return checks


def check_observers():
    checks = {}
    try:
        r = subprocess.run(["schtasks", "/query", "/tn", "ACE_Heartbeat"], capture_output=True, text=True, timeout=5)
        checks["windows_task_heartbeat"] = "OK" if r.returncode == 0 else "NOT_FOUND"
    except: checks["windows_task_heartbeat"] = "ERROR"
    checks["git_repo"] = "OK" if (WORKSPACE / ".git").exists() else "NOT_GIT_REPO"
    checks["status"] = "OK" if "OK" in str(checks.values()) else "NEED_SETUP"
    return checks


def check_autonomy():
    checks = {}
    checks["seed_dir"] = "EXISTS" if (WORKSPACE / "02_MEMORY").exists() else "MISSING"
    checks["governance_dir"] = "EXISTS" if (WORKSPACE / "r1_archaeology").exists() else "MISSING"
    checks["status"] = "OK" if (WORKSPACE / "02_MEMORY").exists() else "PARTIAL"
    return checks


LAYERS = {"os": ("01_OS", check_os), "runtime": ("02_Runtime", check_runtime), "ai": ("03_AI", check_ai), "connector": ("04_CONNECTOR", check_connector), "workspace": ("05_WORKSPACE", check_workspace), "observers": ("06_OBSERVERS", check_observers), "autonomy": ("07_AUTONOMY", check_autonomy)}


def bootstrap(layer=None):
    report = {"time": datetime.now().isoformat(), "host": os.environ.get("COMPUTERNAME", "unknown"), "user": os.environ.get("USERNAME", "unknown"), "layers": {}}
    for lyr in ([layer] if layer else LAYERS.keys()):
        if lyr in LAYERS:
            report["layers"][LAYERS[lyr][0]] = LAYERS[lyr][1]()
    ok = sum(1 for v in report["layers"].values() if v.get("status") == "OK")
    total = len(report["layers"])
    report["summary"] = {"ok_layers": ok, "total_layers": total, "ready": ok >= total * 0.7}
    return report


def main():
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--layer", choices=list(LAYERS.keys()))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    r = bootstrap(layer=args.layer)
    if args.json: print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"ABP: {r['summary']['ok_layers']}/{r['summary']['total_layers']} OK | Ready: {r['summary']['ready']}")
        for name, checks in r["layers"].items():
            print(f"  {name}: {checks.get('status', '?')}")
    sys.exit(0 if r["summary"]["ready"] else 1)


if __name__ == "__main__":
    main()