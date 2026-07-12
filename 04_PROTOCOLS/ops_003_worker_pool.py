#!/usr/bin/env python3
# TYPE: dev_tool
"""
OPS-003: Worker Pool (矿工调度) - 劳动力资源池
================================================

工作哲学: 矿工 = Worker, 资源池, 按能力自动分配任务
"""
import os, sys, json, argparse, urllib.request
from datetime import datetime

WORKER_REGISTRY = {
    "github_models": {"type": "external", "base": "https://models.inference.ai.azure.com/chat/completions", "models": ["gpt-4o-mini"], "best_for": ["code_review", "quick_inference"], "env_key": "GITHUB_PAT"},
    "zhipu_glm": {"type": "external", "base": "https://open.bigmodel.cn/api/paas/v4/chat/completions", "models": ["glm-4-flash"], "best_for": ["report_generation", "chinese_content"], "env_key": "ZHIPU_KEY"},
    "nvidia_nim": {"type": "external", "base": "https://integrate.api.nvidia.com/v1/chat/completions", "models": ["meta/llama-3.3-70b-instruct"], "best_for": ["embedding", "long_context"], "env_key": "NIM_KEY_1"},
    "openrouter": {"type": "external", "base": "https://openrouter.ai/api/v1/chat/completions", "models": ["meta-llama/llama-3.1-8b-instruct:free"], "best_for": ["experimentation"], "env_key": "OPENROUTER_KEY"},
    "local_runtime": {"type": "local", "models": ["python_scripts"], "best_for": ["file_ops", "scheduled_tasks"], "env_key": None},
}


def _is_available(name):
    info = WORKER_REGISTRY.get(name, {})
    if info.get("type") == "local": return True
    ek = info.get("env_key")
    if not ek: return False
    if ek == "NIM_KEY_1": return any(os.environ.get(f"NIM_KEY_{i}") for i in range(1, 17))
    return bool(os.environ.get(ek))


def smart_assign(task_desc):
    print(f"\n{'='*60}\nOPS-003 Worker Pool: {task_desc}\n{'='*60}\n")
    task_low = task_desc.lower()
    scores = {}
    for name, info in WORKER_REGISTRY.items():
        if not _is_available(name): scores[name] = 0; continue
        score = sum(2 for kw in info.get("best_for", []) if kw in task_low)
        scores[name] = score
    sorted_w = sorted(scores.items(), key=lambda x: -x[1])
    for name, score in sorted_w:
        info = WORKER_REGISTRY[name]
        avail = "AVAILABLE" if _is_available(name) else "NO_KEY"
        print(f"  [{score:2d}] {name:20s} {avail}")
    best = sorted_w[0]
    if best[1] == 0: best = ("github_models", 1)
    print(f"\n[ASSIGNED] {best[0]}")
    return {"task": task_desc, "assigned": best[0], "scores": dict(sorted_w)}


def list_workers():
    print(f"\n{'='*60}\nWorker Pool Status\n{'='*60}\n")
    for name, info in WORKER_REGISTRY.items():
        icon = "[OK]" if _is_available(name) else "[NO]"
        print(f"{icon} {name:20s} | {info.get('type')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assign", metavar="TASK")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.list: list_workers()
    elif args.assign:
        result = smart_assign(args.assign)
        if args.json: print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()