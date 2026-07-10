#!/usr/bin/env python3
"""
Local Miner v1 - 直连 GitHub Models + GLM，不依赖远程 ONE-API
执行信号发现 + 档案整理 + Archivist 任务

公理根基:
  #002 考古不是搬家是炼金
  #005 隐私是盾, 行动是剑
  #014 本地推理为主, 外部模型只当嘴
"""
import os, sys, json, argparse, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

# Load keys from miner_env.sh
def load_env():
    env_path = Path(__file__).parent.parent / "05_TOOLS" / "miner" / "miner_env.sh"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("export ") and "=" in line:
                    k, v = line[7:].split("=", 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)

load_env()

GITHUB_PAT = os.environ.get("GITHUB_PAT", "")
GITHUB_BASE = "https://models.inference.ai.azure.com"
ZHIPU_KEY = os.environ.get("ZHIPU_KEY", "")
ZHIPU_BASE = "https://open.bigmodel.cn/api/paas/v4"


def call_github_models(prompt, model="gpt-4o-mini", max_tokens=500, temperature=0.7):
    if not GITHUB_PAT: return {"error": "GITHUB_PAT not set"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": temperature}
    req = urllib.request.Request(f"{GITHUB_BASE}/chat/completions", data=json.dumps(data).encode(), headers={"Authorization": f"Bearer {GITHUB_PAT}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.URLError as e: return {"error": f"URLError: {e}"}
    except Exception as e: return {"error": f"Error: {e}"}


def call_zhipu(prompt, model="glm-4-flash", max_tokens=500):
    if not ZHIPU_KEY: return {"error": "ZHIPU_KEY not set"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    req = urllib.request.Request(f"{ZHIPU_BASE}/chat/completions", data=json.dumps(data).encode(), headers={"Authorization": f"Bearer {ZHIPU_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except Exception as e: return {"error": f"Error: {e}"}


def task_signal_discovery():
    print(f"[MINER] Signal Discovery @ {datetime.now().isoformat()}")
    obs_path = Path(__file__).parent.parent / "03_DATA" / "observation_log.json"
    observations = []
    if obs_path.exists():
        try:
            with open(obs_path) as f: observations = json.load(f).get("observations", [])[-20:]
        except: pass
    if not observations:
        observations = [
            {"time": "2026-07-10T14:00:00", "type": "market", "data": "HS300 volume spike +15%"},
            {"time": "2026-07-10T14:30:00", "type": "market", "data": "VIX down -8%"},
        ]
    prompt = f"""你是ACE矿工的信号发现层。分析以下观察记录，提取可能有效的市场信号模式。

观察记录:
{json.dumps(observations, ensure_ascii=False, indent=2)}

请输出JSON格式:
{{"signals": [...], "validation": "...", "risk": "..."}}
"""
    result = call_github_models(prompt, model="gpt-4o-mini", max_tokens=800)
    if "error" in result: return {"status": "error", "error": result["error"]}
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"status": "ok", "task": "signal_discovery", "model": "gpt-4o-mini", "time": datetime.now().isoformat(), "response": content}


def task_archivist():
    print(f"[MINER] Archivist @ {datetime.now().isoformat()}")
    prompt = """你是ACE矿工的档案整理层。分析今日工作区状态并给出归档建议。

输出JSON格式:
{"to_archive": ["文件1", "文件2"], "to_distill": ["需要蒸馏的文件"], "review_notes": "备注"}
"""
    result = call_github_models(prompt, model="gpt-4o-mini", max_tokens=500)
    if "error" in result: return {"status": "error", "error": result["error"]}
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"status": "ok", "task": "archivist", "model": "gpt-4o-mini", "time": datetime.now().isoformat(), "response": content}


TASKS = {"signal_discovery": task_signal_discovery, "archivist": task_archivist}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=list(TASKS.keys()), required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = TASKS.get(args.task)()
    if args.json: print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {result.get('status')}")
        if result.get('status') == 'ok': print(f"Model: {result.get('model')}\n{result.get('response', '')[:500]}")
        else: print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()