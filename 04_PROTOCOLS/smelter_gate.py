#!/usr/bin/env python3
"""
Smelter Gate（废墟熔炼厂）— 失败结构回收

Mission: AUM-MISSION-SMELTER-001
Identity: 失败不是结束，而是回收
Version: v1.0 (2026-07-15)

Core Flow:
    Failed Structure → Disassemble → Extract Threads → Smelt → New Seed

协同关系:
    失败结构 → 孟婆(过滤污染) → 废墟熔炼厂(拆解/提炼) → 新 Seed

Principles:
    1. Death Is Not End, But Recycling
    2. Threads Are Indestructible (线 = 记忆核，不可删除)
    3. Smelt After MengPo Filter
    4. Every Failure Has Recyclable Value

Never Rules:
    - 直接删除失败结构（必须经过拆解）
    - 跳过孟婆过滤直接熔炼
    - 熔炼后不生成 Seed
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from hashlib import sha256


class FailureType(Enum):
    """失败类型"""
    HYPOTHESIS_REJECTED = "hypothesis_rejected"    # 假设被否决
    LAW_INVALIDATED = "law_invalidated"            # 规律失效
    POLICY_REVERTED = "policy_reverted"            # 策略回退
    EXPERIMENT_FAILED = "experiment_failed"        # 实验失败
    ADMISSION_DENIED = "admission_denied"          # 准入被拒
    ROUNDTABLE_REJECTED = "roundtable_rejected"    # 圆桌否决


class ThreadType(Enum):
    """线（碎片）类型 — 不可被孟婆删除"""
    LOGIC = "logic"              # 逻辑线
    PATTERN = "pattern"          # 模式线
    CONSTRAINT = "constraint"    # 约束线
    EVIDENCE = "evidence"        # 证据线
    CONTEXT = "context"          # 上下文线


class SmeltStatus(Enum):
    """熔炼状态"""
    PENDING = "PENDING"
    MENGPO_FILTERED = "MENGPO_FILTERED"
    DISASSEMBLED = "DISASSEMBLED"
    THREADS_EXTRACTED = "THREADS_EXTRACTED"
    SMELTED = "SMELTED"
    REBORN = "REBORN"
    BLOCKED = "BLOCKED"          # 污染严重，无法熔炼


@dataclass
class Thread:
    """
    线（碎片）— 记忆核
    不可被孟婆删除
    """
    thread_id: str
    thread_type: ThreadType
    content: str
    source_failure: str
    indestructible: bool = True   # 线不可删除
    content_hash: str = ""

    def __post_init__(self):
        self.content_hash = sha256(self.content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict:
        return {
            "thread_id": self.thread_id,
            "thread_type": self.thread_type.value,
            "content": self.content,
            "source_failure": self.source_failure,
            "indestructible": self.indestructible,
            "content_hash": self.content_hash
        }


@dataclass
class SmeltRecord:
    """熔炼记录"""
    record_id: str
    source_failure: Dict
    failure_type: str
    status: SmeltStatus
    threads_extracted: List[Dict] = field(default_factory=list)
    seed_generated: Optional[str] = None
    timestamp: str = ""
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "failure_type": self.failure_type,
            "status": self.status.value,
            "threads_count": len(self.threads_extracted),
            "threads": self.threads_extracted,
            "seed_generated": self.seed_generated,
            "timestamp": self.timestamp,
            "notes": self.notes
        }


class FailureDisassembler:
    """失败结构拆解器"""

    def disassemble(self, failure: Dict) -> Dict[str, Any]:
        """
        拆解失败结构为组件
        """
        components = {
            "hypothesis": failure.get("hypothesis", ""),
            "evidence": failure.get("evidence", {}),
            "context": failure.get("context", {}),
            "constraints": failure.get("constraints", []),
            "reason": failure.get("rejection_reason", ""),
            "what_worked": failure.get("partial_successes", []),
            "what_failed": failure.get("failure_points", [])
        }
        return components


class ThreadExtractor:
    """线提取器 — 从拆解的组件中提取不可删除的线"""

    def extract(self, components: Dict, failure_id: str) -> List[Thread]:
        """提取线（碎片）"""
        threads = []

        # 提取逻辑线
        if components.get("what_worked"):
            for i, success in enumerate(components["what_worked"]):
                threads.append(Thread(
                    thread_id=f"THR-LOG-{failure_id}-{i}",
                    thread_type=ThreadType.LOGIC,
                    content=f"Worked: {success}",
                    source_failure=failure_id
                ))

        # 提取证据线
        evidence = components.get("evidence", {})
        if evidence:
            threads.append(Thread(
                thread_id=f"THR-EVI-{failure_id}-0",
                thread_type=ThreadType.EVIDENCE,
                content=f"Evidence: {json.dumps(evidence, sort_keys=True)}",
                source_failure=failure_id
            ))

        # 提取约束线
        constraints = components.get("constraints", [])
        for i, constraint in enumerate(constraints):
            threads.append(Thread(
                thread_id=f"THR-CON-{failure_id}-{i}",
                thread_type=ThreadType.CONSTRAINT,
                content=f"Constraint: {constraint}",
                source_failure=failure_id
            ))

        # 提取上下文线
        context = components.get("context", {})
        if context:
            threads.append(Thread(
                thread_id=f"THR-CTX-{failure_id}-0",
                thread_type=ThreadType.CONTEXT,
                content=f"Context: {json.dumps(context, sort_keys=True)}",
                source_failure=failure_id
            ))

        # 提取模式线（从失败原因中）
        reason = components.get("reason", "")
        if reason:
            threads.append(Thread(
                thread_id=f"THR-PAT-{failure_id}-0",
                thread_type=ThreadType.PATTERN,
                content=f"Failure Pattern: {reason}",
                source_failure=failure_id
            ))

        return threads


class Smelter:
    """熔炼器 — 将线合并为新 Seed"""

    def smelt(self, threads: List[Thread]) -> Optional[str]:
        """将多条线熔炼为一条精华"""
        if not threads:
            return None

        # 按类型分组
        by_type: Dict[ThreadType, List[str]] = {}
        for t in threads:
            by_type.setdefault(t.thread_type, []).append(t.content)

        # 合并为精华
        essence_parts = []
        for thread_type, contents in by_type.items():
            essence_parts.append(f"[{thread_type.value}] {' | '.join(contents)}")

        essence = "\n".join(essence_parts)
        return essence


class SmelterGate:
    """
    废墟熔炼厂
    失败结构 → 拆解 → 提取线 → 熔炼 → 新 Seed
    """

    def __init__(self, store_path: str = "02_MEMORY/smelted"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.disassembler = FailureDisassembler()
        self.thread_extractor = ThreadExtractor()
        self.smelter = Smelter()

    def process(self, failure: Dict, mengpo_filtered: bool = False) -> SmeltRecord:
        """
        完整流程：失败结构 → 拆解 → 提取线 → 熔炼 → 新 Seed

        Args:
            failure: 失败结构
            mengpo_filtered: 是否已通过孟婆过滤
        """
        failure_id = failure.get("id", f"FAIL-{int(time.time())}")
        failure_type = failure.get("type", FailureType.EXPERIMENT_FAILED.value)
        record_id = f"SMELT-{int(time.time())}-{sha256(failure_id.encode()).hexdigest()[:8]}"

        record = SmeltRecord(
            record_id=record_id,
            source_failure=failure,
            failure_type=failure_type,
            status=SmeltStatus.PENDING,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )

        # Step 0: 检查孟婆过滤
        if not mengpo_filtered:
            record.status = SmeltStatus.BLOCKED
            record.notes = "Blocked: Must pass MengPo filter first"
            return record

        record.status = SmeltStatus.MENGPO_FILTERED

        # Step 1: 拆解
        components = self.disassembler.disassemble(failure)
        record.status = SmeltStatus.DISASSEMBLED

        # Step 2: 提取线
        threads = self.thread_extractor.extract(components, failure_id)
        record.status = SmeltStatus.THREADS_EXTRACTED
        record.threads_extracted = [t.to_dict() for t in threads]

        if not threads:
            record.status = SmeltStatus.BLOCKED
            record.notes = "No threads could be extracted"
            return record

        # Step 3: 熔炼
        essence = self.smelter.smelt(threads)
        record.status = SmeltStatus.SMELTED

        if not essence:
            record.status = SmeltStatus.BLOCKED
            record.notes = "Smelting produced no essence"
            return record

        # Step 4: 重新出生（生成新 Seed）
        seed_id = f"SEED-SMELT-{int(time.time())}-{sha256(essence.encode()).hexdigest()[:8]}"
        seed_file = self.store_path / f"{seed_id}.json"

        seed_data = {
            "seed_id": seed_id,
            "source": "smelter_gate",
            "source_failure_id": failure_id,
            "essence": essence,
            "threads_count": len(threads),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        with open(seed_file, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, ensure_ascii=False, indent=2)

        record.seed_generated = seed_id
        record.status = SmeltStatus.REBORN
        record.notes = f"Reborn as {seed_id} from {len(threads)} threads"

        return record


if __name__ == "__main__":
    gate = SmelterGate()
    print("=== ACE Smelter Gate (废墟熔炼厂) v1.0 ===")

    # Test: 失败结构回收
    print("\n[TEST] Recycling a failed hypothesis")
    failed_hypothesis = {
        "id": "HYP-001",
        "type": FailureType.HYPOTHESIS_REJECTED.value,
        "hypothesis": "Volume spike predicts price increase",
        "evidence": {"sample_size": 30, "success_rate": 0.4},
        "context": {"market": "BTC-USDT", "period": "2026-06"},
        "constraints": ["min_confidence=0.8", "min_sample=30"],
        "rejection_reason": "Success rate 0.4 < threshold 0.8",
        "partial_successes": ["Volume spike correlates with volatility"],
        "failure_points": ["Direction prediction incorrect"]
    }

    record = gate.process(failed_hypothesis, mengpo_filtered=True)
    print(f"  → Status: {record.status.value}")
    print(f"  → Threads extracted: {len(record.threads_extracted)}")
    print(f"  → Seed generated: {record.seed_generated}")
    print(f"  → Notes: {record.notes}")

    # Test: 未通过孟婆过滤
    print("\n[TEST] Blocked by MengPo filter")
    record = gate.process(failed_hypothesis, mengpo_filtered=False)
    print(f"  → Status: {record.status.value}")
    print(f"  → Notes: {record.notes}")

    print("\n=== Smelter Gate Diagnostics Complete ===")