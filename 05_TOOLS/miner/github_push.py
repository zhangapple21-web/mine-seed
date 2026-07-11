#!/usr/bin/env python3
"""
GitHub API 直推脚本 — 不依赖 git CLI
用 GitHub REST API 推送文件，避免 PAT 认证问题

用法:
  python3 github_push.py --file /path/to/file.md --path cloud/miner/file.md
  python3 github_push.py --dir cloud/miner/ --prefix cloud/miner/
"""

import os
import sys
import json
import base64
import argparse
import urllib.request
from pathlib import Path
from datetime import datetime

# GitHub 配置
GH_TOKEN = os.environ.get("GH_PUSH_TOKEN", os.environ.get("GITHUB_PAT_NEW", ""))
GH_OWNER = os.environ.get("GH_OWNER", "zhangapple21-web")
GH_REPO = os.environ.get("GH_REPO", "mine-seed")
GH_BRANCH = os.environ.get("GH_BRANCH", "main")

API_BASE = f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}"


def get_file_sha(path: str) -> str:
    """获取文件的当前 SHA（如果存在）"""
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "10",
             "-H", f"Authorization: token {GH_TOKEN}",
             "-H", "Accept: application/vnd.github.v3+json",
             f"{API_BASE}/contents/{path}?ref={GH_BRANCH}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        return data.get("sha", "")
    except:
        return ""


def push_file(file_path: str, repo_path: str, commit_msg: str = "") -> bool:
    """推送单个文件到 GitHub"""
    if not GH_TOKEN:
        print("[GH] ERROR: GH_PUSH_TOKEN not set")
        return False
    
    if not Path(file_path).exists():
        print(f"[GH] File not found: {file_path}")
        return False
    
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    
    if not commit_msg:
        commit_msg = f"cloud: {Path(file_path).name} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
    
    sha = get_file_sha(repo_path)
    
    data = {
        "message": commit_msg,
        "content": content,
        "branch": GH_BRANCH,
    }
    if sha:
        data["sha"] = sha
    
    url = f"{API_BASE}/contents/{repo_path}"
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"token {GH_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            },
            method="PUT"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            print(f"[GH] Pushed: {repo_path} (commit: {result['commit']['sha'][:7]})")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"[GH] HTTP {e.code}: {body[:200]}")
        return False
    except Exception as e:
        print(f"[GH] Error: {e}")
        return False


def push_dir(dir_path: str, prefix: str = "") -> int:
    """推送目录下所有文件"""
    pushed = 0
    for f in Path(dir_path).rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            repo_path = f"{prefix}{f.relative_to(dir_path)}" if prefix else str(f.relative_to(dir_path))
            if push_file(str(f), repo_path):
                pushed += 1
    return pushed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub API Direct Push")
    parser.add_argument("--file", help="Single file to push")
    parser.add_argument("--path", help="Target path in repo")
    parser.add_argument("--dir", help="Directory to push")
    parser.add_argument("--prefix", default="", help="Repo path prefix for dir push")
    parser.add_argument("--message", default="", help="Commit message")
    args = parser.parse_args()
    
    if args.file:
        sys.exit(0 if push_file(args.file, args.path or args.file, args.message) else 1)
    elif args.dir:
        count = push_dir(args.dir, args.prefix)
        print(f"[GH] Pushed {count} files")
        sys.exit(0 if count > 0 else 1)
    else:
        parser.print_help()
