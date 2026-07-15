#!/usr/bin/env python3
"""
Distillation Factory（孟婆）— 主动遗忘机制

Mission: AUM-MISSION-DISTILL-001
Identity: 经验 → 洗掉噪音 → 保留结构 → 重新出生
Version: v1.0 (2026-07-15)

Core Flow:
    Raw Experience → Wash (Remove Noise) → Distill (Extract Pattern) → Compress (Compress Rules) → Reborn

Principles:
    1. Forget Details, Retain Patterns
    2. Pollution Isolation: Any Pollution Must Be Washed
    3. Memory Decay Is Active, Not Passive
    4. Rebirth > Death

Never Rules:
    - 直接删除原始证据（必须经过 Distillation）
    - 污染性记忆跨过滤线
    - 主动遗忘变成彻底删除
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from hashlib import sha256


class PollutionType(Enum):
    """污染类型"""
    NOISE = "noise"              # 噪音
    DRIFT = "drift"              # 漂移
    CONTAMINATION = "contamination"  # 污染
    CONFLICT = "conflict"        # 冲突
    DECAY = "decay"              # 衰减


class MemoryType(Enum):
    """记忆类型"""
    EXPERIENCE = "experience"    # 原始经验
    PATTERN = "pattern"          # 提炼的规律
    RULE = "rule"                # 压缩的规则
    ESSENCE = "essence"          # 核心精华


@dataclass
class DistillationRecord:
    """蒸馏记录"""
    record_id: str
    source_experience: Dict
    pollution_detected: List[str] = field(default_factory=list)
    pattern_extracted: Optional[str] = None
    rule_compressed: Optional[str] = None
    essence: Optional[str] = None
    confidence: float = 1.0
    timestamp: str = ""

    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "source_hash": sha256(json.dumps(self.source_experience, sort_keys=True).encode()).hexdigest()[:16],
            "pollution_detected": self.pollution_detected,
            "pattern_extracted": self.pattern_extracted,
            "rule_compressed": self.rule_compressed,
            "essence": self.essence,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }


class PollutionDetector:
    """污染检测器"""

    def __init__(self):
        self.indicators = {
            PollutionType.NOISE: ["random_fluctuation", "irrelevant_data", "low_signal_ratio"],
            PollutionType.DRIFT: ["temporal_drift", "concept_drift", "regime_change"],
            PollutionType.CONTAMINATION: ["external_injection", "untrusted_source", "validation_failed"],
            PollutionType.CONFLICT: ["contradicting_evidence", "conflicting_rules", "competing_signals"],
            PollutionType.DECAY: ["expired_data", "outdated_rule", "stale_evidence"]
        }

    def detect(self, experience: Dict) -> List[PollutionType]:
        """检测经验中的污染"""
        detected = []
        # 简化实现：检查 metadata 中的污染标记
        metadata = experience.get("metadata", {})
        for pollution_type, indicators in self.indicators.items():
            for indicator in indicators:
                if metadata.get(indicator):
                    detected.append(pollution_type)
        return detected


class PatternExtractor:
    """规律提取器"""

    def extract(self, experience: Dict, pollution: List[PollutionType]) -> Optional[str]:
        """从经验中提取规律（去除噪音）"""
        if PollutionType.CONTAMINATION in pollution:
            return None  # 污染性经验不提取

        # 简化实现：提取核心特征
        core = experience.get("core_features", {})
        if not core:
            return None

        return f"PATTERN: {json.dumps(core, sort_keys=True)}"


class RuleCompressor:
    """规则压缩器"""

    def compress(self, patterns: List[str]) -> Optional[str]:
        """将多个规律压缩为单条规则"""
        if not patterns:
            return None

        # 简化实现：合并规律为通用规则
        combined = f"RULE: When [condition] then [action] (from {len(patterns)} patterns)"
        return combined


class DistillationFactory:
    """
    孟婆：Distillation Factory
    主动遗忘机制
    """

    def __init__(self, store_path: str = "02_MEMORY/distilled"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.pollution_detector = PollutionDetector()
        self.pattern_extractor = PatternExtractor()
        self.rule_compressor = RuleCompressor()

    def wash(self, experience: Dict) -> tuple[Dict, List[PollutionType]]:
        """
        Phase 1: 洗（Wash）
        识别并标记污染
        """
        pollution = self.pollution_detector.detect(experience)
        return experience, pollution

    def distill(self, experience: Dict, pollution: List[PollutionType]) -> Optional[str]:
        """
        Phase 2: 蒸馏（Distill）
        提取规律
        """
        if PollutionType.CONTAMINATION in pollution:
            return None
        return self.pattern_extractor.extract(experience, pollution)

    def compress(self, patterns: List[str]) -> Optional[str]:
        """
        Phase 3: 压缩（Compress）
        合并规律为规则
        """
        return self.rule_compressor.compress(patterns)

    def reborn(self, essence: str) -> str:
        """
        Phase 4: 重新出生（Reborn）
        精华成为新 Seed
        """
        seed_id = f"SEED-{int(time.time())}-{sha256(essence.encode()).hexdigest()[:8]}"
        seed_file = self.store_path / f"{seed_id}.json"

        seed_data = {
            "seed_id": seed_id,
            "essence": essence,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "type": MemoryType.ESSENCE.value
        }

        with open(seed_file, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, ensure_ascii=False, indent=2)

        return seed_id

    def process(self, experience: Dict) -> Optional[DistillationRecord]:
        """
        完整流程：经验 → 洗 → 蒸馏 → 压缩 → 重新出生
        """
        # Phase 1: Wash
        _, pollution = self.wash(experience)
        if PollutionType.CONTAMINATION in pollution:
            # 污染性经验：仅记录，不进入下一步
            return DistillationRecord(
                record_id=f"DIST-{int(time.time())}",
                source_experience=experience,
                pollution_detected=[p.value for p in pollution],
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            )

        # Phase 2: Distill
        pattern = self.distill(experience, pollution)
        if not pattern:
            return None

        # Phase 3: Compress
        rule = self.compress([pattern])

        # Phase 4: Reborn
        essence = rule or pattern
        seed_id = self.reborn(essence)

        return DistillationRecord(
            record_id=f"DIST-{int(time.time())}",
            source_experience=experience,
            pollution_detected=[p.value for p in pollution],
            pattern_extracted=pattern,
            rule_compressed=rule,
            essence=essence,
            confidence=0.9 if not pollution else 0.6,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )


if __name__ == "__main__":
    factory = DistillationFactory()
    print("=== ACE Distillation Factory (孟婆) v1.0 ===")

    # Test 1: Clean experience
    print("\n[TEST 1] Clean experience")
    clean_exp = {
        "core_features": {"feature_a": "high", "feature_b": "stable"},
        "metadata": {}
    }
    record = factory.process(clean_exp)
    if record:
        print(f"  → Pattern: {record.pattern_extracted}")
        print(f"  → Rule: {record.rule_compressed}")
        print(f"  → Confidence: {record.confidence}")

    # Test 2: Polluted experience
    print("\n[TEST 2] Polluted experience (should be blocked)")
    polluted_exp = {
        "core_features": {"feature_a": "high"},
        "metadata": {"untrusted_source": True}
    }
    record = factory.process(polluted_exp)
    if record and record.pollution_detected:
        print(f"  → Pollution detected: {record.pollution_detected}")
        print(f"  → Blocked from distillation")

    print("\n=== Distillation Factory Diagnostics Complete ===")