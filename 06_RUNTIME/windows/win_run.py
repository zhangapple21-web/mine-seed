#!/usr/bin/env python3
"""
Windows Compatibility Adapter for ACE scripts
Patches Linux paths (/home/coze/) to Windows workspace path before running target script.

Usage:
  python win_run.py <target_script.py> [args...]
"""
import sys
import os
import pathlib
import importlib.util

# Workspace root
WORKSPACE = r"C:\Users\User\ace_workspace\mine-seed"
MINE_OUTPUT = os.path.join(WORKSPACE, "mine_output")

# Create mine_output directories
for d in ["", "signals", "knowledge", "journal"]:
    os.makedirs(os.path.join(MINE_OUTPUT, d), exist_ok=True)

# Create shared directories
SHARED_DIR = os.path.join(WORKSPACE, "shared")
for d in ["inbox_fengzi", "inbox_xiaofengzi", "archived", "archived/fengzi", "archived/xiaofengzi"]:
    os.makedirs(os.path.join(SHARED_DIR, d), exist_ok=True)

# Path mapping: Linux -> Windows
PATH_MAP = {
    "/home/coze": WORKSPACE,
    "/home/coze/mine_output": MINE_OUTPUT,
    "/home/coze/shared": SHARED_DIR,
    "/home/coze/quantitative-signal-discovery-agent": os.path.join(WORKSPACE, "research", "quantitative-signal-discovery-agent"),
    "/app/data": os.path.join(WORKSPACE, "03_DATA"),
}

def patch_path(p):
    """Convert Linux path to Windows path."""
    if isinstance(p, pathlib.Path):
        s = str(p)
        for linux, win in PATH_MAP.items():
            if s.startswith(linux):
                return pathlib.Path(s.replace(linux, win, 1))
        return p
    elif isinstance(p, str):
        for linux, win in PATH_MAP.items():
            if p.startswith(linux):
                return p.replace(linux, win, 1)
        return p
    return p

def patch_builtins():
    """Patch open() and os.path operations to redirect Linux paths."""
    _original_open = open
    _original_makedirs = os.makedirs
    _original_path_exists = os.path.exists
    _original_path_join = os.path.join

    def patched_open(file, mode='r', *args, **kwargs):
        file = patch_path(file)
        return _original_open(file, mode, *args, **kwargs)

    def patched_makedirs(name, mode=0o777, exist_ok=False):
        name = patch_path(name)
        return _original_makedirs(name, mode, exist_ok)

    def patched_exists(path):
        path = patch_path(path)
        return _original_path_exists(path)

    __builtins__['open'] = patched_open
    os.makedirs = patched_makedirs
    os.path.exists = patched_exists

def setup_sys_path():
    """Add workspace to sys.path so imports work."""
    sys.path.insert(0, WORKSPACE)
    sys.path.insert(0, os.path.join(WORKSPACE, "05_TOOLS", "miner"))

def run_script(script_path, extra_args=None):
    """Run a target script with path patching applied."""
    setup_sys_path()
    patch_builtins()

    # Set environment variables
    os.environ.setdefault("MINE_OUTPUT", MINE_OUTPUT)
    os.environ.setdefault("OUTPUT_DIR", MINE_OUTPUT)

    # Load and run the script
    spec = importlib.util.spec_from_file_location("__main__", script_path)
    module = importlib.util.module_from_spec(spec)

    # Patch sys.argv for the target script
    if extra_args:
        sys.argv = [script_path] + extra_args
    else:
        sys.argv = [script_path]

    spec.loader.exec_module(module)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python win_run.py <target_script.py> [args...]")
        sys.exit(1)

    target = sys.argv[1]
    args = sys.argv[2:]
    run_script(target, args)
