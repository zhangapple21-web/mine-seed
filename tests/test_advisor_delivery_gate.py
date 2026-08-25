import importlib.util
import os
from pathlib import Path


def _load_runner():
    path = Path(__file__).resolve().parents[1] / "05_TOOLS" / "advisor" / "daily_runner.py"
    spec = importlib.util.spec_from_file_location("advisor_daily_runner", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_delivery_defaults_to_no_send(monkeypatch):
    runner = _load_runner()
    for name in (
        "ACE_STOCK_ADVISOR_AUTO_PUSH",
        "ACE_TG_ENABLED",
        "ACE_ADVISOR_DATA_READY",
        "ACE_ADVISOR_RISK_READY",
        "ACE_OWNER_TG_CHAT_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    decision = runner.telegram_delivery_readiness({"allow_internal_push": True})
    assert decision["allowed"] is False
    assert decision["decision"] == "NO_SEND"
    assert set(decision["reasons"]) == {
        "auto_push_disabled",
        "telegram_disabled",
        "data_not_ready",
        "risk_not_ready",
        "owner_chat_id_missing",
    }


def test_owner_controlled_send_requires_every_hard_gate(monkeypatch):
    runner = _load_runner()
    for name in (
        "ACE_STOCK_ADVISOR_AUTO_PUSH",
        "ACE_TG_ENABLED",
        "ACE_ADVISOR_DATA_READY",
        "ACE_ADVISOR_RISK_READY",
    ):
        monkeypatch.setenv(name, "true")
    monkeypatch.setenv("ACE_OWNER_TG_CHAT_ID", "owner-only")
    decision = runner.telegram_delivery_readiness({"allow_internal_push": True})
    assert decision == {
        "allowed": True,
        "decision": "OWNER_TG_CONTROLLED_SEND",
        "reasons": [],
        "owner_chat_id": "owner-only",
    }


def test_publication_denial_remains_no_send_even_when_environment_is_ready(monkeypatch):
    runner = _load_runner()
    for name in (
        "ACE_STOCK_ADVISOR_AUTO_PUSH",
        "ACE_TG_ENABLED",
        "ACE_ADVISOR_DATA_READY",
        "ACE_ADVISOR_RISK_READY",
    ):
        monkeypatch.setenv(name, "true")
    monkeypatch.setenv("ACE_OWNER_TG_CHAT_ID", "owner-only")
    decision = runner.telegram_delivery_readiness({
        "allow_publication": False,
        "allow_internal_push": False,
    })
    assert decision["allowed"] is False
    assert decision["reasons"] == ["publication_gate_denied"]
