#!/usr/bin/env python3
"""
Trigger Engine v2.0 — 事件驱动调度内核

Mission: AUM-MISSION-TRIGGER-001
Identity: Trigger Engine = Evidence-Gated Dispatch System
Version: v2.0 (2026-07-15)

Core Flow:
    Event/Condition → Trigger Registry → Evidence Gate → Dispatch → Worker/Mission

Principles:
    1. Evidence First: 每个 Trigger 激活生成 Evidence Record
    2. Capability-Driven: Trigger 面向 Capability，而非 Document
    3. Mission vs Runtime: 长期任务和即时任务分离调度
    4. CONFIRM Mode: 重要任务需要 Governor 确认
    5. M4 Guardian: L0 边界守卫，永远不解锁

Never Rules:
    - Trigger 直接执行任务（必须经过 Evidence Gate）
    - 依赖文档编号（使用 Capability Dictionary）
    - M4 解锁（永远 READ_ONLY）
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from hashlib import sha256


class TriggerType(Enum):
    """触发类型"""
    EVENT = "EVENT"           # 信号驱动
    STATE = "STATE"           # 条件驱动
    RESOURCE = "RESOURCE"     # 资源状态
    TIME = "TIME"             # 时间到达
    DEPENDENCY = "DEPENDENCY" # 前置依赖
    THRESHOLD = "THRESHOLD"   # 阈值触发
    MANUAL = "MANUAL"         # 手动触发


class ActivationMode(Enum):
    """激活模式"""
    AUTO = "AUTO"         # 自动执行
    CONFIRM = "CONFIRM"   # 需要确认
    MANUAL = "MANUAL"     # 完全手动


class TriggerStatus(Enum):
    """触发状态"""
    PENDING = "PENDING"
    FIRED = "FIRED"
    CONFIRMED = "CONFIRMED"
    DISPATCHED = "DISPATCHED"
    ABORTED = "ABORTED"


@dataclass
class TriggerEvidence:
    """触发证据 — Evidence First 原则"""
    trigger_id: str
    triggered_at: str
    trigger_type: str
    capability: Optional[str] = None
    event_type: Optional[str] = None
    condition_value: Dict[str, Any] = field(default_factory=dict)
    evidence_sources: List[str] = field(default_factory=list)
    confidence: float = 1.0
    activation_mode: str = "AUTO"
    confirmation_status: str = "PENDING"
    confirmation_deadline: Optional[str] = None
    dispatch_status: str = "PENDING"

    def to_dict(self) -> Dict:
        return {
            "trigger_id": self.trigger_id,
            "triggered_at": self.triggered_at,
            "trigger_type": self.trigger_type,
            "capability": self.capability,
            "event_type": self.event_type,
            "condition_value": self.condition_value,
            "evidence_sources": self.evidence_sources,
            "confidence": self.confidence,
            "activation_mode": self.activation_mode,
            "confirmation_status": self.confirmation_status,
            "confirmation_deadline": self.confirmation_deadline,
            "dispatch_status": self.dispatch_status
        }


class CapabilityRegistry:
    """能力注册表 — 解耦文档编号"""

    def __init__(self, registry_path: str = "03_DATA/MISSIONS/capability_registry.json"):
        self.registry_path = Path(registry_path)
        self.capabilities: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for cap in data.get("capabilities", []):
                    self.capabilities[cap["id"]] = cap

    def check(self, capability_id: str) -> bool:
        """检查能力是否就绪"""
        cap = self.capabilities.get(capability_id)
        if not cap:
            return False
        return cap.get("status") == "ACTIVE"


class EventTypesRegistry:
    """事件类型注册表"""

    def __init__(self, registry_path: str = "03_DATA/MISSIONS/event_types.json"):
        self.registry_path = Path(registry_path)
        self.event_types: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for et in data.get("event_types", []):
                    self.event_types[et["type"]] = et

    def get_targets(self, event_type: str) -> Dict[str, List[str]]:
        """获取事件的目标 Workers 和 Missions"""
        et = self.event_types.get(event_type)
        if not et:
            return {"workers": [], "missions": []}
        return {
            "workers": et.get("target_workers", []),
            "missions": et.get("trigger_missions", [])
        }


class TriggerRegistry:
    """触发注册表 — Mission vs Runtime 分离"""

    def __init__(self):
        self.mission_triggers: Dict[str, Dict] = {}
        self.runtime_triggers: Dict[str, Dict] = {}

    def register_mission_trigger(self, mission_id: str, config: Dict):
        """注册 Mission 触发器"""
        self.mission_triggers[mission_id] = config

    def register_runtime_trigger(self, worker_id: str, config: Dict):
        """注册 Runtime 触发器"""
        self.runtime_triggers[worker_id] = config


class EvidenceGate:
    """证据门 — 验证触发条件，生成 Evidence Record"""

    def __init__(self, evidence_store_path: str = "02_MEMORY/evidence"):
        self.evidence_store_path = Path(evidence_store_path)
        self.evidence_store_path.mkdir(parents=True, exist_ok=True)

    def validate_and_record(
        self,
        trigger_type: TriggerType,
        capability: Optional[str] = None,
        event_type: Optional[str] = None,
        condition_value: Optional[Dict] = None,
        activation_mode: ActivationMode = ActivationMode.AUTO
    ) -> TriggerEvidence:
        """验证触发条件，生成 Evidence"""

        trigger_id = f"TRG-{int(time.time())}-{sha256(str(condition_value).encode()).hexdigest()[:8]}"
        triggered_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        evidence = TriggerEvidence(
            trigger_id=trigger_id,
            triggered_at=triggered_at,
            trigger_type=trigger_type.value,
            capability=capability,
            event_type=event_type,
            condition_value=condition_value or {},
            confidence=self._calculate_confidence(condition_value),
            activation_mode=activation_mode.value
        )

        # CONFIRM 模式设置确认窗口
        if activation_mode == ActivationMode.CONFIRM:
            evidence.confirmation_deadline = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(time.time() + 86400)  # 24h 窗口
            )

        # 写入 Evidence Store
        self._write_evidence(evidence)

        return evidence

    def _calculate_confidence(self, condition_value: Optional[Dict]) -> float:
        """计算置信度"""
        if not condition_value:
            return 0.5
        # 简单实现：有数据源则高置信度
        if condition_value.get("evidence_sources"):
            return 0.95
        return 0.8

    def _write_evidence(self, evidence: TriggerEvidence):
        """写入 Evidence Store"""
        date_str = time.strftime("%Y%m%d", time.gmtime())
        evidence_file = self.evidence_store_path / f"trigger_evidence_{date_str}.jsonl"

        with open(evidence_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(evidence.to_dict()) + "\n")


class TriggerEngine:
    """触发引擎 — L1 调度核心"""

    def __init__(self):
        self.capability_registry = CapabilityRegistry()
        self.event_types_registry = EventTypesRegistry()
        self.trigger_registry = TriggerRegistry()
        self.evidence_gate = EvidenceGate()

    def check_state_trigger(self, capability: str) -> Optional[TriggerEvidence]:
        """检查 STATE 触发"""
        if self.capability_registry.check(capability):
            return self.evidence_gate.validate_and_record(
                trigger_type=TriggerType.STATE,
                capability=capability,
                condition_value={"capability": capability, "status": "ACTIVE"}
            )
        return None

    def handle_event(self, event_type: str, payload: Dict) -> List[TriggerEvidence]:
        """处理 EVENT 触发"""
        targets = self.event_types_registry.get_targets(event_type)
        evidences = []

        # 触发 Workers
        for worker in targets["workers"]:
            evidence = self.evidence_gate.validate_and_record(
                trigger_type=TriggerType.EVENT,
                event_type=event_type,
                condition_value={"worker": worker, "payload": payload},
                activation_mode=ActivationMode.AUTO
            )
            evidences.append(evidence)

        # 触发 Missions
        for mission in targets["missions"]:
            evidence = self.evidence_gate.validate_and_record(
                trigger_type=TriggerType.EVENT,
                event_type=event_type,
                condition_value={"mission": mission, "payload": payload},
                activation_mode=ActivationMode.CONFIRM
            )
            evidences.append(evidence)

        return evidences

    def manual_trigger(self, target: str, is_mission: bool = False) -> TriggerEvidence:
        """处理 MANUAL 触发"""
        activation = ActivationMode.CONFIRM if is_mission else ActivationMode.AUTO
        return self.evidence_gate.validate_and_record(
            trigger_type=TriggerType.MANUAL,
            condition_value={"target": target, "is_mission": is_mission},
            activation_mode=activation
        )


if __name__ == "__main__":
    # Runtime self-diagnostic
    engine = TriggerEngine()
    print("=== ACE Trigger Engine v2.0 Diagnostics Initialized ===")

    # Test STATE trigger
    print("\n[TEST] STATE trigger: LawDiscoveryEngineReady")
    evidence = engine.check_state_trigger("LawDiscoveryEngineReady")
    if evidence:
        print(f"  → Triggered: {evidence.trigger_id}")
        print(f"  → Evidence recorded at: {evidence.triggered_at}")
    else:
        print("  → Not ready")

    # Test EVENT trigger
    print("\n[TEST] EVENT trigger: WorkerFailed")
    evidences = engine.handle_event("WorkerFailed", {
        "worker_id": "M02",
        "error_code": "TIMEOUT",
        "error_message": "Connection timeout",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })
    for e in evidences:
        print(f"  → {e.trigger_id} (activation: {e.activation_mode})")