"""
LLM Provider Router

目标：
- 结构化地管理多 provider（主力 → 备用1 → 备用2）
- 按优先级自动 fallback
- 密钥只允许存在于本地 `.secrets/`（仓库内只放模板）

注意：
- 本模块不会打印或记录任何 api_key 内容
- 所有网络请求默认短超时，失败即尝试下一个 provider
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


class ProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class Provider:
    name: str
    priority: int
    enabled: bool = True
    # OpenAI-compatible base URL
    base_url: Optional[str] = None
    # Gemini full endpoint (generateContent)
    endpoint: Optional[str] = None
    api_key: Optional[str] = None

    def kind(self) -> str:
        if self.endpoint and not self.base_url:
            return "gemini"
        return "openai"


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_providers_config(
    config_path: Optional[str] = None,
    *,
    repo_root: Optional[str] = None,
) -> List[Provider]:
    """
    从本地 `.secrets/llm_providers.json` 读取 provider 列表。

    默认路径：
    - <repo_root>/.secrets/llm_providers.json
    - 若 repo_root 未提供，则使用当前文件向上推断到 `mine-seed` 根目录
    """

    if config_path is None:
        if repo_root is None:
            # .../mine-seed/05_TOOLS/llm_provider/provider_router.py -> mine-seed/
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        config_path = os.path.join(repo_root, ".secrets", "llm_providers.json")

    if not os.path.exists(config_path):
        raise ProviderError(
            f"providers config not found: {config_path}. "
            f"请复制 `docs/llm_providers.example.json` 到该位置并填写 api_key。"
        )

    data = _read_json(config_path)
    raw = data.get("providers", [])
    providers: List[Provider] = []
    for item in raw:
        providers.append(
            Provider(
                name=str(item.get("name", "")).strip(),
                priority=int(item.get("priority", 999)),
                enabled=bool(item.get("enabled", True)),
                base_url=(item.get("base_url") or None),
                endpoint=(item.get("endpoint") or None),
                api_key=(item.get("api_key") or None),
            )
        )

    providers = [p for p in providers if p.name and p.enabled and p.api_key]
    providers.sort(key=lambda p: (p.priority, p.name))
    if not providers:
        raise ProviderError("no enabled providers with api_key found in config")
    return providers


def _http_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    body: Optional[bytes],
    timeout_s: float,
) -> Tuple[int, bytes]:
    req = urllib.request.Request(url=url, method=method, headers=headers, data=body)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return int(resp.status), resp.read()
    except Exception as e:
        raise ProviderError(f"http request failed: {method} {url}: {e}") from e


def _openai_models_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/v1/models"


def _openai_chat_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/v1/chat/completions"


def ping_provider(provider: Provider, *, timeout_s: float = 6.0) -> bool:
    """
    轻量健康检查：
    - OpenAI-compatible: GET /v1/models
    - Gemini: POST generateContent（最小 payload）

    注意：失败返回 False，不抛异常（便于 fallback）。
    """
    try:
        if provider.kind() == "openai":
            url = _openai_models_url(provider.base_url or "")
            code, _ = _http_request(
                "GET",
                url,
                headers={"Authorization": f"Bearer {provider.api_key}"},
                body=None,
                timeout_s=timeout_s,
            )
            return code == 200

        # Gemini
        endpoint = provider.endpoint or ""
        if "key=" not in endpoint:
            sep = "&" if ("?" in endpoint) else "?"
            endpoint = endpoint + f"{sep}key={urllib.parse.quote(provider.api_key or '')}"
        payload = {
            "contents": [{"parts": [{"text": "ping"}]}],
        }
        code, _ = _http_request(
            "POST",
            endpoint,
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload).encode("utf-8"),
            timeout_s=timeout_s,
        )
        return code == 200
    except Exception:
        return False


def openai_chat_completions_with_fallback(
    messages: List[Dict[str, Any]],
    *,
    model: str = "gpt-4.1-mini",
    temperature: float = 0.2,
    max_tokens: int = 512,
    timeout_s: float = 30.0,
    config_path: Optional[str] = None,
    repo_root: Optional[str] = None,
    enable_ping: bool = True,
) -> Dict[str, Any]:
    """
    对 OpenAI-compatible 的 provider 执行 `/v1/chat/completions`，失败自动 fallback。

    说明：
    - 这是一个“最小可用”的统一入口，方便后续在考古脚本里复用
    - Gemini 不是 OpenAI-compatible，这里不会走 Gemini；如果需要 Gemini，可单独实现 generateContent 入口
    """
    providers = load_providers_config(config_path=config_path, repo_root=repo_root)

    last_err: Optional[Exception] = None
    for p in providers:
        if p.kind() != "openai":
            continue
        if enable_ping and not ping_provider(p, timeout_s=6.0):
            last_err = ProviderError(f"provider ping failed: {p.name}")
            continue

        url = _openai_chat_url(p.base_url or "")
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            code, raw = _http_request(
                "POST",
                url,
                headers={
                    "Authorization": f"Bearer {p.api_key}",
                    "Content-Type": "application/json",
                },
                body=json.dumps(payload).encode("utf-8"),
                timeout_s=timeout_s,
            )
            if code != 200:
                last_err = ProviderError(f"{p.name} http {code}")
                continue
            return json.loads(raw.decode("utf-8", errors="ignore"))
        except Exception as e:
            last_err = e
            continue
        finally:
            # 避免过快连打（也方便日志里区分）
            time.sleep(0.2)

    raise ProviderError(f"all openai-compatible providers failed. last_err={last_err}")


if __name__ == "__main__":
    # 仅用于本地快速自检：确认配置可读、provider 列表可解析。
    # 不会输出 api_key。
    prov = load_providers_config()
    print("providers_loaded=", len(prov))
    for p in prov:
        print(f"- {p.name} kind={p.kind()} priority={p.priority} enabled={p.enabled}")

