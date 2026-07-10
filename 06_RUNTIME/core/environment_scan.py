#!/usr/bin/env python3
import os, json, subprocess
from pathlib import Path
from datetime import datetime


def scan_environment(workspace):
    workspace = Path(workspace)
    scan = {
        "scan_time": datetime.now().isoformat(),
        "workspace": str(workspace),
        "directories": [],
        "files": [],
        "recovery_assets": [],
        "git_status": None,
        "environment_vars": {},
    }

    for root, dirs, files in os.walk(workspace):
        depth = len(Path(root).relative_to(workspace).parts)
        if depth > 3:
            dirs[:] = []
            continue

        dirs[:] = sorted(d for d in dirs if d not in [".git", "__pycache__", "node_modules", ".DS_Store"])

        scan["directories"].append({
            "path": str(Path(root).relative_to(workspace)),
            "depth": depth,
            "subdirs": len(dirs),
            "files": len(files),
        })

        for f in sorted(files):
            fpath = Path(root) / f
            if f.lower().endswith((".py", ".md", ".json", ".sh", ".ps1")):
                try:
                    size = fpath.stat().st_size
                    mtime = datetime.fromtimestamp(fpath.stat().st_mtime).isoformat()
                    scan["files"].append({
                        "path": str(fpath.relative_to(workspace)),
                        "size": size,
                        "mtime": mtime,
                    })
                except:
                    pass

            if any(keyword in f.lower() for keyword in ["backup", "snapshot", "archive", "recovery", "seed"]):
                scan["recovery_assets"].append(str(fpath.relative_to(workspace)))

    try:
        result = subprocess.run(["git", "status", "--short"],
                               cwd=str(workspace), capture_output=True, text=True, timeout=10)
        scan["git_status"] = result.stdout.strip() or "clean"
    except:
        scan["git_status"] = "unavailable"

    for key in ["TG_BOT_TOKEN_1", "NTPY_TOPIC", "GITHUB_TOKEN"]:
        if key in os.environ:
            scan["environment_vars"][key] = "***"

    return scan


def main():
    workspace = Path(__file__).parent.parent.parent
    scan = scan_environment(workspace)
    print(json.dumps(scan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()