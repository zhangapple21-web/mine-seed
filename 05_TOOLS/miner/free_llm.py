#!/usr/bin/env python3
"""
ACE Runtime — 免费 LLM 直连库
0 依赖 TRAE 额度，0 依赖 Gateway
直接调用 GLM / NIM / GitHub Models / Ollama

用法:
  from free_llm import call
  result = call("你好", max_tokens=100)
  # 自动选择可用渠道：GLM → NIM → GitHub → Ollama
"""

import os
import json
import time
import threading
import urllib.request
import logging
from typing import Optional

log = logging.getLogger("ACE.FreeLLM")

# 渠道优先级：GLM(无限) > NIM(16key) > GitHub(限流) > Ollama(本地)
CHANNELS = ["glm", "nim", "github", "ollama"]

# NIM key 轮询状态（线程安全）
_nim_key_index = 0
_nim_key_lock = threading.Lock()

# 代理设置：GLM是国内API不需要代理，其他海外API需要
_PROXY = os.environ.get("HTTPS_PROXY", os.environ.get("https_proxy", ""))
_NO_PROXY = os.environ.get("NO_PROXY", os.environ.get("no_proxy", ""))


def _needs_proxy(host: str) -> bool:
    """判断是否需要代理"""
    no_proxy_hosts = [h.strip() for h in _NO_PROXY.split(",") if h.strip()]
    for h in no_proxy_hosts:
        if h in host:
            return False
    # GLM 是国内 API，直连
    if "bigmodel.cn" in host:
        return False
    # 其他海外 API 需要代理
    return True


def _urlopen(req, timeout: int = 60):
    """智能 urlopen：国内直连，海外走代理"""
    url = req.full_url if hasattr(req, 'full_url') else str(req.selector)
    if _PROXY and _needs_proxy(url):
        handler = urllib.request.ProxyHandler({
            'http': _PROXY,
            'https': _PROXY,
        })
        opener = urllib.request.build_opener(handler)
        return opener.open(req, timeout=timeout)
    else:
        return urllib.request.urlopen(req, timeout=timeout)


def _get_nim_key() -> str:
    """轮询获取 NIM key（线程安全）"""
    global _nim_key_index
    keys = [os.environ.get(f"NIM_KEY_{i}", "") for i in range(1, 17)]
    keys = [k for k in keys if k]
    if not keys:
        return ""
    with _nim_key_lock:
        key = keys[_nim_key_index % len(keys)]
        _nim_key_index += 1
    return key


def _call_glm(messages: list, max_tokens: int, temperature: float) -> Optional[dict]:
    """调用智谱 GLM"""
    url = os.environ.get("GLM_BASE", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
    key = os.environ.get("GLM_KEY", "")
    model = os.environ.get("GLM_MODEL", "glm-4-flash")
    
    if not key:
        return None
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST"
        )
        with _urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            return {"content": content, "model": model, "channel": "GLM", "raw": result}
    except Exception as e:
        log.warning(f"[GLM] Error: {e}")
        return None


def _call_nim(messages: list, max_tokens: int, temperature: float) -> Optional[dict]:
    """调用 NVIDIA NIM"""
    url = os.environ.get("NIM_BASE", "https://integrate.api.nvidia.com/v1/chat/completions")
    key = _get_nim_key()
    model = os.environ.get("NIM_MODEL", "meta/llama-3.1-8b-instruct")
    
    if not key:
        return None
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST"
        )
        with _urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            return {"content": content, "model": model, "channel": "NIM", "raw": result}
    except Exception as e:
        log.warning(f"[NIM] Error: {e}")
        return None


def _call_github(messages: list, max_tokens: int, temperature: float) -> Optional[dict]:
    """调用 GitHub Models"""
    url = os.environ.get("GH_MODELS_BASE", "https://models.inference.ai.azure.com/chat/completions")
    key = os.environ.get("GH_MODELS_KEY", "")
    model = os.environ.get("GH_MODELS_MODEL", "gpt-4o-mini")
    
    if not key:
        return None
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST"
        )
        with _urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            return {"content": content, "model": model, "channel": "GitHub", "raw": result}
    except Exception as e:
        log.warning(f"[GitHub] Error: {e}")
        return None


def _call_ollama(messages: list, max_tokens: int, temperature: float) -> Optional[dict]:
    """调用本地 Ollama"""
    url = os.environ.get("OLLAMA_BASE", "http://localhost:11434/api/chat")
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
    
    data = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        }
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with _urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            content = result.get("message", {}).get("content", "")
            return {"content": content, "model": model, "channel": "Ollama", "raw": result}
    except Exception as e:
        log.warning(f"[Ollama] Error: {e}")
        return None


# 渠道调用映射
_CHANNEL_FUNCS = {
    "glm": _call_glm,
    "nim": _call_nim,
    "github": _call_github,
    "ollama": _call_ollama,
}


def call(prompt: str, system: str = "", max_tokens: int = 2000, temperature: float = 0.3,
         prefer: str = None) -> dict:
    """
    调用免费 LLM，自动 fallback。
    
    参数:
        prompt: 用户消息
        system: 系统消息（可选）
        max_tokens: 最大输出 token
        temperature: 温度
        prefer: 优先渠道 ("glm"/"nim"/"github"/"ollama")
    
    返回:
        {"content": str, "model": str, "channel": str}
    
    异常:
        RuntimeError: 所有渠道都失败
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    # 确定渠道顺序
    channels = list(CHANNELS)
    if prefer and prefer in channels:
        channels.remove(prefer)
        channels.insert(0, prefer)
    
    # 逐个尝试
    for ch in channels:
        func = _CHANNEL_FUNCS.get(ch)
        if not func:
            continue
        
        t0 = time.time()
        result = func(messages, max_tokens, temperature)
        elapsed = time.time() - t0
        
        if result and result.get("content"):
            result["elapsed"] = elapsed
            log.info(f"[FreeLLM] {ch}/{result['model']}: {len(result['content'])} chars in {elapsed:.1f}s")
            return result
    
    raise RuntimeError("所有免费 API 渠道均失败")


def call_with_retry(prompt: str, system: str = "", max_tokens: int = 2000,
                    retries: int = 2, **kwargs) -> dict:
    """带重试的调用"""
    last_error = None
    for i in range(retries + 1):
        try:
            return call(prompt, system, max_tokens, **kwargs)
        except RuntimeError as e:
            last_error = e
            log.warning(f"[FreeLLM] Attempt {i+1} failed: {e}")
            time.sleep(2)
    raise last_error


if __name__ == "__main__":
    # 自测
    logging.basicConfig(level=logging.INFO)
    print("Testing free LLM channels...")
    
    result = call("用一句话介绍你自己", max_tokens=50)
    print(f"\nChannel: {result['channel']}")
    print(f"Model: {result['model']}")
    print(f"Content: {result['content']}")
    print(f"Elapsed: {result['elapsed']:.1f}s")
