#!/usr/bin/env python3
"""
Felo API Provider — PROV-FELO-001
Core Position: Cross-language evidence supplement channel
- Does NOT replace main chain
- Does NOT serve as sole information source
- Does NOT exceed daily quota

Priority: 3 (GLM -> NIM -> Felo -> GitHub Models -> Local)
Daily Budget: 200 credits (UTC 0:00 reset, no carryover)
"""
import os
import requests
import json
from datetime import datetime, timezone
from pathlib import Path


def _load_repo_env():
    env_file = Path(__file__).resolve().parents[2] / ".env"
    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)
    except OSError:
        pass


_load_repo_env()

FELO_API_KEY = os.getenv("FELO_API_KEY")
FELO_BASE_URL = os.getenv("FELO_BASE_URL", "https://openapi.felo.ai")

# Quota tracking
_DAILY_BUDGET = 200
_SEARCH_COST = 15
_CHAT_COST = 30
_quota_file = os.path.join(os.path.dirname(__file__), "data", "felo_quota.json")


def _format_api_error(resp):
    code = ""
    message = ""
    try:
        error = resp.json()
        if isinstance(error, dict):
            detail = error.get("error", error)
            if isinstance(detail, dict):
                code = str(detail.get("code", error.get("code", "")))[:80]
                message = str(detail.get("message", error.get("message", "")))[:200]
            else:
                code = str(error.get("code", ""))[:80]
                message = str(error.get("message", detail))[:200]
    except (ValueError, TypeError):
        pass
    details = [f"status={resp.status_code}"]
    if code:
        details.append(f"code={code}")
    if message:
        details.append(f"message={message}")
    return "Felo API returned " + ", ".join(details)

def _load_quota():
    """Load today's quota usage"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        with open(_quota_file) as f:
            data = json.load(f)
        if data.get("date") == today:
            return data
    except Exception:
        pass
    return {"date": today, "used": 0, "search_count": 0, "chat_count": 0}


def _save_quota(data):
    """Save quota usage"""
    os.makedirs(os.path.dirname(_quota_file), exist_ok=True)
    with open(_quota_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _check_quota(cost):
    """Check if quota allows this call"""
    quota = _load_quota()
    if quota["used"] + cost > _DAILY_BUDGET:
        return False, quota
    return True, quota


def _deduct(cost, call_type):
    """Deduct quota after successful call"""
    quota = _load_quota()
    quota["used"] += cost
    if call_type == "search":
        quota["search_count"] += 1
    elif call_type == "chat":
        quota["chat_count"] += 1
    _save_quota(quota)
    return quota


def get_quota_status():
    """Get current quota status"""
    quota = _load_quota()
    remaining = _DAILY_BUDGET - quota["used"]
    return {
        "date": quota["date"],
        "used": quota["used"],
        "remaining": remaining,
        "search_count": quota["search_count"],
        "chat_count": quota["chat_count"],
        "budget": _DAILY_BUDGET,
    }


def felo_search(query, source_langs=None):
    """
    Call Felo professional search.
    Returns structured results with sources.

    Args:
        query: Search query string
        source_langs: List of source languages (default: en, ja, zh)

    Returns:
        dict with keys: source标识, core_conclusion, citations, adoption_suggestion
    """
    if not FELO_API_KEY:
        return {"error": "FELO_API_KEY not set", "source": "[Felo-Search]"}

    source_langs = source_langs or ["en", "ja", "zh"]

    # Quota check
    ok, quota = _check_quota(_SEARCH_COST)
    if not ok:
        return {
            "error": f"Daily quota exceeded ({quota['used']}/{_DAILY_BUDGET})",
            "source": "[Felo-Search]",
            "quota": get_quota_status(),
        }

    headers = {
        "Authorization": f"Bearer {FELO_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    try:
        resp = requests.post(
            f"{FELO_BASE_URL.rstrip('/')}/v2/chat",
            json=payload,
            headers=headers,
            timeout=30,
        )
        if resp.status_code == 200:
            _deduct(_SEARCH_COST, "search")
            data = resp.json()
            return {
                "source": "[Felo-Search]",
                "core_conclusion": data.get("data", {}).get("answer", data.get("answer", data.get("summary", ""))),
                "citations": data.get("data", {}).get("resources", data.get("sources", data.get("references", []))),
                "adoption_suggestion": "External Observation - requires Evidence->Candidate->Admission before adoption",
                "quota": get_quota_status(),
                "raw": data,
            }
        else:
            return {
                "error": _format_api_error(resp),
                "source": "[Felo-Search]",
            }
    except Exception as e:
        return {"error": f"Felo search error: {e}", "source": "[Felo-Search]"}


def felo_chat(prompt, model="felo-chat"):
    """
    Call Felo supplementary chat.
    Only for summary/verification, NOT for core reasoning or code generation.

    Args:
        prompt: Input prompt
        model: Model name (default: felo-chat)

    Returns:
        dict with keys: source标识, core_conclusion, adoption_suggestion
    """
    if not FELO_API_KEY:
        return {"error": "FELO_API_KEY not set", "source": "[Felo-Chat]"}

    # Quota check
    ok, quota = _check_quota(_CHAT_COST)
    if not ok:
        return {
            "error": f"Daily quota exceeded ({quota['used']}/{_DAILY_BUDGET})",
            "source": "[Felo-Chat]",
            "quota": get_quota_status(),
        }

    headers = {
        "Authorization": f"Bearer {FELO_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"query": prompt}

    try:
        resp = requests.post(
            f"{FELO_BASE_URL.rstrip('/')}/v2/chat",
            json=payload,
            headers=headers,
            timeout=30,
        )
        if resp.status_code == 200:
            _deduct(_CHAT_COST, "chat")
            data = resp.json()
            nested = data.get("data", {})
            if not isinstance(nested, dict):
                nested = {}
            content = nested.get(
                "answer", data.get("answer", data.get("summary", ""))
            )
            return {
                "source": "[Felo-Chat]",
                "core_conclusion": content,
                "adoption_suggestion": "External Observation - requires Evidence->Candidate->Admission before adoption",
                "quota": get_quota_status(),
                "raw": data,
            }
        else:
            return {
                "error": _format_api_error(resp),
                "source": "[Felo-Chat]",
            }
    except Exception as e:
        return {"error": f"Felo chat error: {e}", "source": "[Felo-Chat]"}


# ==================== ProviderAdapter Integration ====================
# Compatible with task_router.py ProviderAdapter pattern

class FeloAdapter:
    """Felo Provider Adapter for task_router.py integration.

    Position: search_and_evidence provider (priority 3)
    Role: cross-language evidence supplement, NOT main chain
    """

    PROVIDER_CONFIG = {
        "name": "felo",
        "type": "search_and_evidence",
        "base_url": "https://openapi.felo.ai",
        "models": ["felo-search", "felo-chat", "gpt-4o", "claude-3.5-sonnet"],
        "daily_budget": 200,
        "search_cost": 15,
        "chat_cost": 30,
        "fallback": ["glm", "github_models"],
        "priority": 3,
        "allow_paid": False,
    }

    def __init__(self):
        self.name = "felo"
        self._key = os.getenv("FELO_API_KEY")

    def is_available(self):
        return bool(self._key)

    def probe(self):
        if not self.is_available():
            return []
        return self.PROVIDER_CONFIG["models"]

    def call(self, model, messages, max_tokens=500, temperature=0.7):
        """Route to search or chat based on model name."""
        if not self.is_available():
            return {"error": "Felo API key not configured", "success": False}

        if model == "felo-search":
            # Extract query from messages
            query = ""
            for msg in messages:
                if msg.get("role") == "user":
                    query = msg.get("content", "")
                    break
            result = felo_search(query)
            if "error" not in result:
                return {
                    "content": result.get("core_conclusion", ""),
                    "model": model,
                    "provider": "felo",
                    "success": True,
                    "citations": result.get("citations", []),
                }
            return {"error": result.get("error"), "success": False}

        else:
            # Use chat for felo-chat, gpt-4o, claude-3.5-sonnet
            prompt = ""
            for msg in messages:
                if msg.get("role") == "user":
                    prompt = msg.get("content", "")
                    break
            result = felo_chat(prompt, model=model)
            if "error" not in result:
                return {
                    "content": result.get("core_conclusion", ""),
                    "model": model,
                    "provider": "felo",
                    "success": True,
                }
            return {"error": result.get("error"), "success": False}

    def get_models(self):
        return {
            "felo-search": {
                "capabilities": ["cross_language_search", "evidence_supplement", "citation_lookup"],
                "context_window": 0,
                "avg_latency": 10,
                "success_rate": 0.9,
            },
            "felo-chat": {
                "capabilities": ["summary", "verification", "cross_language"],
                "context_window": 16000,
                "avg_latency": 8,
                "success_rate": 0.9,
            },
        }


if __name__ == "__main__":
    # Quick test
    print("=== Felo Provider Test ===")
    print(f"API Key configured: {bool(FELO_API_KEY)}")
    print(f"Base URL: {FELO_BASE_URL}")
    print(f"Quota: {get_quota_status()}")
