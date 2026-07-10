#!/usr/bin/env python3
"""
Local Miner v2 - 多源模型调用，不依赖 TRAE
================================================
模型优先级：Ollama(本地) → GitHub Models → Zhipu GLM → OpenRouter

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
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Ollama 本地模型（默认 localhost:11434）
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "huihui_ai/qwen2.5-vl-abliterated:7b")

# 模型 fallback 链
MODEL_FALLBACK_CHAIN = [
    ("ollama", OLLAMA_MODEL),
    ("github", "gpt-4o-mini"),
    ("zhipu", "glm-4-flash"),
    ("openrouter", "meta-llama/llama-3.3-70b-instruct:free"),
]


def call_ollama(prompt, model=None, max_tokens=500, temperature=0.7):
    """调用本地 Ollama 模型"""
    model = model or OLLAMA_MODEL
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": temperature},
    }
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/chat",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read().decode())
            # 转换为 OpenAI 兼容格式
            return {
                "choices": [{"message": {"content": resp.get("message", {}).get("content", "")}}],
                "model": model,
                "source": "ollama",
            }
    except urllib.error.URLError as e:
        return {"error": f"Ollama URLError: {e}", "source": "ollama"}
    except Exception as e:
        return {"error": f"Ollama error: {e}", "source": "ollama"}


def check_ollama_available() -> bool:
    """检测 Ollama 是否可用"""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read().decode())
            return len(data.get("models", [])) > 0
    except Exception:
        return False


def call_github_models(prompt, model="gpt-4o-mini", max_tokens=500, temperature=0.7):
    if not GITHUB_PAT: return {"error": "GITHUB_PAT not set", "source": "github"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": temperature}
    req = urllib.request.Request(f"{GITHUB_BASE}/chat/completions", data=json.dumps(data).encode(), headers={"Authorization": f"Bearer {GITHUB_PAT}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read().decode())
            result["source"] = "github"
            return result
    except urllib.error.URLError as e: return {"error": f"URLError: {e}", "source": "github"}
    except Exception as e: return {"error": f"Error: {e}", "source": "github"}


def call_zhipu(prompt, model="glm-4-flash", max_tokens=500, temperature=0.7):
    if not ZHIPU_KEY: return {"error": "ZHIPU_KEY not set", "source": "zhipu"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    req = urllib.request.Request(f"{ZHIPU_BASE}/chat/completions", data=json.dumps(data).encode(), headers={"Authorization": f"Bearer {ZHIPU_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read().decode())
            result["source"] = "zhipu"
            return result
    except Exception as e: return {"error": f"Error: {e}", "source": "zhipu"}


def call_openrouter(prompt, model="meta-llama/llama-3.3-70b-instruct:free", max_tokens=500, temperature=0.7):
    if not OPENROUTER_KEY: return {"error": "OPENROUTER_KEY not set", "source": "openrouter"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://ace.local", "X-Title": "ACE Miner"}
    req = urllib.request.Request(f"{OPENROUTER_BASE}/chat/completions", data=json.dumps(data).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read().decode())
            result["source"] = "openrouter"
            return result
    except Exception as e: return {"error": f"Error: {e}", "source": "openrouter"}


# Provider 注册表
PROVIDERS = {
    "ollama": call_ollama,
    "github": call_github_models,
    "zhipu": call_zhipu,
    "openrouter": call_openrouter,
}


def call_model(prompt, max_tokens=500, temperature=0.7, prefer=None):
    """统一模型调用 — 自动 fallback

    优先级：prefer(如果指定) → ollama → github → zhipu → openrouter
    任何一个成功就返回，不继续尝试。
    """
    chain = list(MODEL_FALLBACK_CHAIN)
    if prefer and prefer in PROVIDERS:
        # 把 prefer 移到最前面
        chain = [(prefer, chain[0][1])] + [(p, m) for p, m in chain if p != prefer]

    errors = []
    for provider_name, model_name in chain:
        provider_fn = PROVIDERS.get(provider_name)
        if not provider_fn:
            continue
        # 快速检测 ollama 是否可用（避免每次都等超时）
        if provider_name == "ollama" and not check_ollama_available():
            errors.append(f"ollama: not available")
            continue

        result = provider_fn(prompt, model=model_name, max_tokens=max_tokens, temperature=temperature)
        if "error" not in result:
            result.setdefault("model", model_name)
            result["provider"] = provider_name
            return result
        errors.append(f"{provider_name}: {result['error']}")

    return {"error": "All providers failed", "errors": errors}


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
    result = call_model(prompt, max_tokens=800)
    if "error" in result: return {"status": "error", "error": result["error"]}
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"status": "ok", "task": "signal_discovery", "model": result.get("model"), "provider": result.get("provider"), "time": datetime.now().isoformat(), "response": content}


def task_archivist():
    print(f"[MINER] Archivist @ {datetime.now().isoformat()}")
    prompt = """你是ACE矿工的档案整理层。分析今日工作区状态并给出归档建议。

输出JSON格式:
{"to_archive": ["文件1", "文件2"], "to_distill": ["需要蒸馏的文件"], "review_notes": "备注"}
"""
    result = call_model(prompt, max_tokens=500)
    if "error" in result: return {"status": "error", "error": result["error"]}
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"status": "ok", "task": "archivist", "model": result.get("model"), "provider": result.get("provider"), "time": datetime.now().isoformat(), "response": content}


TASKS = {"signal_discovery": task_signal_discovery, "archivist": task_archivist}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=list(TASKS.keys()))
    parser.add_argument("--test", action="store_true", help="Test model connectivity")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.test:
        print("=== Model Connectivity Test ===")
        print(f"  Ollama ({OLLAMA_BASE}): {'OK' if check_ollama_available() else 'NOT AVAILABLE'}")
        print(f"  GitHub Models: {'OK' if GITHUB_PAT else 'NO PAT'}")
        print(f"  Zhipu: {'OK' if ZHIPU_KEY else 'NO KEY'}")
        print(f"  OpenRouter: {'OK' if OPENROUTER_KEY else 'NO KEY'}")
        print("\n  Testing call_model()...")
        r = call_model("Say hello in one word.", max_tokens=10)
        if "error" in r:
            print(f"  Result: FAILED — {r.get('errors', r.get('error'))}")
        else:
            print(f"  Result: OK — provider={r.get('provider')}, model={r.get('model')}")
        return

    if not args.task:
        parser.print_help()
        return

    result = TASKS.get(args.task)()
    if args.json: print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {result.get('status')}")
        if result.get('status') == 'ok':
            print(f"Provider: {result.get('provider')}, Model: {result.get('model')}")
            print(result.get('response', '')[:500])
        else: print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()