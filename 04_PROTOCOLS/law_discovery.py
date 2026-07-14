#!/usr/bin/env python3
"""
Law Discovery Protocol - 规律发现协议

Mission: AUM-MISSION-LAW-001
Identity: Law Discovery Engine = Evidence-Driven Law Discovery System

Core Flow:
    Observation -> Evidence -> Pattern Mining -> Hypothesis -> Evidence Validation -> Law -> Roundtable -> Admission -> Policy Candidate

Principles:
    1. Evidence First: 任何规律必须来自 Evidence，不得人为指定规律
    2. Pattern != Law: Pattern 只是重复现象，Law 必须经过 Validation
    3. Law != Policy: 规律不是策略，一个 Law 可以生成多个 Policy
    4. Learning Cannot Modify Recommendation: Learning 永远不能直接修改 Recommendation Engine
    5. Admission Is The Only Gate: 任何 Policy 更新必须经过 Roundtable -> Admission -> Policy Update
    6. Evidence Immutable: Evidence 不允许修改，只能追加
    7. Law Evolves: Law 可以新增、强化、弱化、废弃，不能静态永久存在

Never Rules:
    - 人工写死"规律因子"
    - 丁元英评分
    - 强势文化评分
    - 情绪因子=20
    - Miner 修改 Recommendation
    - Law 直接进入 Runtime
    - 未验证规律进入 Policy
    - 修改历史 Evidence
"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


# ============================================================================
# Constants
# ============================================================================

MIN_EVIDENCE_FOR_PATTERN = 30
MIN_SAMPLE_FOR_VALIDATION = 50
P_VALUE_THRESHOLD = 0.05

MEMORY_DIR = Path(__file__).parent.parent / "02_MEMORY"
EVIDENCE_DIR = MEMORY_DIR / "evidence"
LAW_REGISTRY_DIR = MEMORY_DIR / "law_registry"
POLICY_CANDIDATE_DIR = MEMORY_DIR / "policy_candidates"


# ============================================================================
# Enums
# ============================================================================

class LawStatus(str, Enum):
    """Law Status State Machine: DRAFT -> ACTIVE -> WEAKENING -> INVALID -> ARCHIVED"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    WEAKENING = "WEAKENING"
    INVALID = "INVALID"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"  # Roundtable rejected


class PatternType(str, Enum):
    """Pattern types discovered from Evidence"""
    CORRELATION = "CORRELATION"      # A and B occur together
    SEQUENCE = "SEQUENCE"            # A followed by B
    DISTRIBUTION = "DISTRIBUTION"    # A clusters in certain ranges
    FAILURE = "FAILURE"              # A leads to failure
    SUCCESS = "SUCCESS"              # A leads to success


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Observation:
    """Raw observation from Recommendation execution
    
    Collected from:
        - Market changes
        - Max return
        - Max drawdown
        - Industry strength
        - Volume
        - Market sentiment
        - Recommendation reasons
        - Recommendation factors
        - Execution results
    
    Does NOT do analysis. Only responsible for recording.
    """
    observation_id: str
    timestamp: str
    recommendation_id: str
    ticker: str
    ticker_name: str
    
    # Market data
    recommend_price: float
    close_price: Optional[float] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    volume: Optional[int] = None
    
    # Returns
    return_t1: Optional[float] = None
    return_t3: Optional[float] = None
    return_t5: Optional[float] = None
    return_t10: Optional[float] = None
    return_t20: Optional[float] = None
    
    # Context
    industry: Optional[str] = None
    market_sentiment: Optional[str] = None
    turnover_rate: Optional[float] = None
    pe: Optional[float] = None
    total_capital: Optional[float] = None
    
    # Recommendation context
    layer1_reasons: List[str] = field(default_factory=list)
    layer1_reject_flags: List[str] = field(default_factory=list)
    layer2_reasons: List[str] = field(default_factory=list)
    layer3_reasons: List[str] = field(default_factory=list)
    tech_signals: List[str] = field(default_factory=list)
    
    # Result
    status: str = "pending"  # pending / partial / complete
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Observation":
        return cls(**d)


@dataclass
class Evidence:
    """Immutable evidence derived from Observation
    
    Evidence is immutable. Cannot modify historical Evidence.
    Only append new Evidence.
    """
    evidence_id: str
    observation_id: str
    timestamp: str
    evidence_type: str  # success / failure / neutral
    ticker: str
    
    # Outcome
    outcome_period: str  # T+1, T+3, T+5, T+10, T+20
    outcome_return: float
    
    # Factors present
    factors: List[str] = field(default_factory=list)
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Hash for immutability verification
    content_hash: str = ""
    
    def __post_init__(self):
        if not self.content_hash:
            content = json.dumps({
                "observation_id": self.observation_id,
                "evidence_type": self.evidence_type,
                "outcome_return": self.outcome_return,
                "factors": sorted(self.factors),
                "conditions": self.conditions
            }, sort_keys=True)
            self.content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Evidence":
        return cls(**d)


@dataclass
class Pattern:
    """Pattern discovered from Evidence mining
    
    Pattern is NOT Law. Pattern is just repeated phenomenon.
    Law must go through Validation.
    """
    pattern_id: str
    timestamp: str
    pattern_type: PatternType
    
    # Pattern definition
    description: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Evidence support
    evidence_count: int = 0
    evidence_ids: List[str] = field(default_factory=list)
    
    # Pattern statistics
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    
    # Applicable scope
    scope: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Pattern":
        return cls(**d)


@dataclass
class Hypothesis:
    """Hypothesis converted from Pattern
    
    At this stage: NOT allowed to modify Policy.
    """
    hypothesis_id: str
    timestamp: str
    pattern_id: str
    
    # Hypothesis statement
    statement: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""
    
    # Validation status
    validation_status: str = "pending"  # pending / validating / validated / rejected
    validation_result: Optional[Dict] = None
    
    # Evidence support
    evidence_count: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Hypothesis":
        return cls(**d)


@dataclass
class Law:
    """Verified Law from Hypothesis validation
    
    Law CANNOT directly affect Recommendation.
    Must go through Roundtable -> Admission -> Policy Update.
    """
    law_id: str
    timestamp: str
    hypothesis_id: str
    
    # Law definition
    statement: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""
    
    # Evidence support
    evidence_count: int = 0
    confidence: float = 0.0  # 0-1
    
    # Applicable scope
    scope: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: LawStatus = LawStatus.DRAFT
    
    # Verification
    created_time: str = ""
    last_verified: str = ""
    verification_count: int = 0
    
    # Policy candidates generated
    policy_candidates: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Law":
        return cls(**d)


@dataclass
class PolicyCandidate:
    """Policy Candidate generated from Law through Roundtable
    
    Must be approved by Admission before entering Runtime.
    """
    candidate_id: str
    timestamp: str
    law_id: str
    
    # Policy definition
    policy_type: str  # factor_weight / filter_rule / scoring_rule
    policy_name: str
    policy_value: Any
    
    # Expected impact
    expected_win_rate_change: float = 0.0
    expected_return_change: float = 0.0
    affected_scope: List[str] = field(default_factory=list)
    
    # Roundtable result
    roundtable_status: str = "pending"  # pending / approved / rejected
    roundtable_votes: Dict[str, str] = field(default_factory=dict)  # voter -> vote
    roundtable_notes: List[str] = field(default_factory=list)
    
    # Admission result
    admission_status: str = "pending"  # pending / approved / rejected
    admission_reason: str = ""
    
    # Version control
    version: str = "v1.0"
    rollback_version: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "PolicyCandidate":
        return cls(**d)


# ============================================================================
# Law Registry
# ============================================================================

class LawRegistry:
    """Law Registry - manages all Laws lifecycle
    
    Laws are NOT Policy. Law Registry does NOT affect Runtime.
    Only Approved Policy can enter Runtime.
    """
    
    def __init__(self, registry_dir: Path = None):
        self.registry_dir = registry_dir or LAW_REGISTRY_DIR
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.laws_file = self.registry_dir / "laws.json"
        self.candidates_file = self.registry_dir / "law_candidates.json"
        self.laws: Dict[str, Law] = {}
        self.candidates: Dict[str, Law] = {}
        self._load()
    
    def _load(self):
        """Load laws from disk"""
        if self.laws_file.exists():
            try:
                data = json.loads(self.laws_file.read_text(encoding='utf-8'))
                for law_id, law_data in data.items():
                    self.laws[law_id] = Law.from_dict(law_data)
            except Exception:
                pass
        
        if self.candidates_file.exists():
            try:
                data = json.loads(self.candidates_file.read_text(encoding='utf-8'))
                for law_id, law_data in data.items():
                    self.candidates[law_id] = Law.from_dict(law_data)
            except Exception:
                pass
    
    def _save(self):
        """Save laws to disk"""
        laws_data = {law_id: law.to_dict() for law_id, law in self.laws.items()}
        self.laws_file.write_text(json.dumps(laws_data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        candidates_data = {law_id: law.to_dict() for law_id, law in self.candidates.items()}
        self.candidates_file.write_text(json.dumps(candidates_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def register_law(self, law: Law) -> bool:
        """Register a new Law (as candidate first)"""
        if law.law_id in self.laws or law.law_id in self.candidates:
            return False
        
        self.candidates[law.law_id] = law
        self._save()
        return True
    
    def activate_law(self, law_id: str) -> bool:
        """Activate a candidate Law"""
        if law_id not in self.candidates:
            return False
        
        law = self.candidates.pop(law_id)
        law.status = LawStatus.ACTIVE
        law.last_verified = datetime.now().isoformat()
        self.laws[law_id] = law
        self._save()
        return True
    
    def weaken_law(self, law_id: str) -> bool:
        """Mark a Law as weakening"""
        if law_id not in self.laws:
            return False
        
        self.laws[law_id].status = LawStatus.WEAKENING
        self._save()
        return True
    
    def invalidate_law(self, law_id: str) -> bool:
        """Mark a Law as invalid"""
        if law_id not in self.laws:
            return False
        
        self.laws[law_id].status = LawStatus.INVALID
        self._save()
        return True
    
    def get_active_laws(self) -> List[Law]:
        """Get all active laws"""
        return [law for law in self.laws.values() if law.status == LawStatus.ACTIVE]
    
    def get_law(self, law_id: str) -> Optional[Law]:
        """Get a specific law"""
        return self.laws.get(law_id) or self.candidates.get(law_id)
    
    def verify_law(self, law_id: str, confidence: float) -> bool:
        """Update law verification"""
        law = self.get_law(law_id)
        if not law:
            return False
        
        law.last_verified = datetime.now().isoformat()
        law.verification_count += 1
        law.confidence = confidence
        
        # Auto status transition based on confidence
        if confidence < 0.3 and law.status == LawStatus.ACTIVE:
            law.status = LawStatus.WEAKENING
        elif confidence < 0.1:
            law.status = LawStatus.INVALID
        
        self._save()
        return True


# ============================================================================
# Evidence Store
# ============================================================================

class EvidenceStore:
    """Evidence storage - immutable, append-only
    
    Evidence cannot be modified. Only append new Evidence.
    """
    
    def __init__(self, evidence_dir: Path = None):
        self.evidence_dir = evidence_dir or EVIDENCE_DIR
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.evidence_dir / "evidence_index.json"
        self.evidence_index: Dict[str, str] = {}  # evidence_id -> file_path
        self._load_index()
    
    def _load_index(self):
        """Load evidence index"""
        if self.index_file.exists():
            try:
                self.evidence_index = json.loads(self.index_file.read_text(encoding='utf-8'))
            except Exception:
                pass
    
    def _save_index(self):
        """Save evidence index"""
        self.index_file.write_text(json.dumps(self.evidence_index, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def append(self, evidence: Evidence) -> bool:
        """Append new evidence (immutable)"""
        if evidence.evidence_id in self.evidence_index:
            return False  # Already exists
        
        # Save to dated file
        date_str = datetime.now().strftime('%Y%m%d')
        evidence_file = self.evidence_dir / f"evidence_{date_str}.jsonl"
        
        with open(evidence_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(evidence.to_dict(), ensure_ascii=False) + '\n')
        
        self.evidence_index[evidence.evidence_id] = str(evidence_file)
        self._save_index()
        return True
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """Get specific evidence"""
        if evidence_id not in self.evidence_index:
            return None
        
        file_path = Path(self.evidence_index[evidence_id])
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    if data.get('evidence_id') == evidence_id:
                        return Evidence.from_dict(data)
        
        return None
    
    def get_all_evidence(self, limit: int = 1000) -> List[Evidence]:
        """Get all evidence"""
        evidence_list = []
        
        for evidence_file in sorted(self.evidence_dir.glob("evidence_*.jsonl")):
            with open(evidence_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            evidence_list.append(Evidence.from_dict(data))
                        except Exception:
                            continue
            
            if len(evidence_list) >= limit:
                break
        
        return evidence_list[:limit]


# ============================================================================
# Law Discovery Engine
# ============================================================================

class LawDiscoveryEngine:
    """Law Discovery Engine - Evidence-Driven Law Discovery System
    
    Flow:
        Observation -> Evidence -> Pattern Mining -> Hypothesis -> Evidence Validation -> Law -> Roundtable -> Admission -> Policy Candidate
    
    Principles:
        - Evidence First: 任何规律必须来自 Evidence
        - Pattern != Law: Pattern 必须经过 Validation
        - Law != Policy: Law 必须经过 Roundtable -> Admission
        - Learning Cannot Modify Recommendation: 本引擎不修改 Runtime
    """
    
    def __init__(self):
        self.evidence_store = EvidenceStore()
        self.law_registry = LawRegistry()
    
    def convert_observation_to_evidence(self, observation: Observation) -> List[Evidence]:
        """Convert Observation to Evidence (immutable)
        
        Returns multiple Evidence for different outcome periods.
        """
        evidence_list = []
        
        periods = [
            ('T+1', observation.return_t1),
            ('T+3', observation.return_t3),
            ('T+5', observation.return_t5),
            ('T+10', observation.return_t10),
            ('T+20', observation.return_t20),
        ]
        
        for period, return_val in periods:
            if return_val is None:
                continue
            
            # Determine evidence type
            if return_val > 0:
                evidence_type = "success"
            elif return_val < 0:
                evidence_type = "failure"
            else:
                evidence_type = "neutral"
            
            # Collect factors
            factors = []
            factors.extend(observation.layer1_reasons)
            factors.extend(observation.layer2_reasons)
            factors.extend(observation.layer3_reasons)
            factors.extend(observation.tech_signals)
            
            # Create evidence
            evidence = Evidence(
                evidence_id=f"{observation.observation_id}_{period}",
                observation_id=observation.observation_id,
                timestamp=observation.timestamp,
                evidence_type=evidence_type,
                ticker=observation.ticker,
                outcome_period=period,
                outcome_return=return_val,
                factors=factors,
                conditions={
                    "industry": observation.industry,
                    "pe": observation.pe,
                    "turnover_rate": observation.turnover_rate,
                    "total_capital": observation.total_capital,
                    "market_sentiment": observation.market_sentiment,
                }
            )
            
            evidence_list.append(evidence)
            self.evidence_store.append(evidence)
        
        return evidence_list
    
    def mine_patterns(self, min_evidence: int = MIN_EVIDENCE_FOR_PATTERN) -> List[Pattern]:
        """Mine patterns from Evidence
        
        Pattern is NOT Law. Pattern is just repeated phenomenon.
        """
        all_evidence = self.evidence_store.get_all_evidence(limit=10000)
        
        if len(all_evidence) < min_evidence:
            return []
        
        patterns = []
        
        # Group evidence by factors
        factor_evidence: Dict[str, List[Evidence]] = {}
        for evidence in all_evidence:
            for factor in evidence.factors:
                factor_key = factor.split()[0] if ' ' in factor else factor
                if factor_key not in factor_evidence:
                    factor_evidence[factor_key] = []
                factor_evidence[factor_key].append(evidence)
        
        # Analyze each factor group for patterns
        for factor, evidences in factor_evidence.items():
            if len(evidences) < min_evidence:
                continue
            
            success_count = sum(1 for e in evidences if e.evidence_type == "success")
            failure_count = sum(1 for e in evidences if e.evidence_type == "failure")
            total = len(evidences)
            
            success_rate = success_count / total if total > 0 else 0
            
            # Pattern detection: success_rate significantly different from random
            if success_rate > 0.6 or success_rate < 0.4:
                pattern_type = PatternType.SUCCESS if success_rate > 0.6 else PatternType.FAILURE
                
                pattern = Pattern(
                    pattern_id=f"pattern_{factor}_{int(time.time())}",
                    timestamp=datetime.now().isoformat(),
                    pattern_type=pattern_type,
                    description=f"Factor '{factor}' has success rate {success_rate:.1%}",
                    conditions={"factor": factor},
                    evidence_count=total,
                    evidence_ids=[e.evidence_id for e in evidences],
                    success_count=success_count,
                    failure_count=failure_count,
                    success_rate=success_rate,
                    scope={"factor": factor}
                )
                patterns.append(pattern)
        
        return patterns
    
    def generate_hypothesis(self, pattern: Pattern) -> Hypothesis:
        """Generate Hypothesis from Pattern
        
        At this stage: NOT allowed to modify Policy.
        """
        hypothesis = Hypothesis(
            hypothesis_id=f"hypo_{pattern.pattern_id}",
            timestamp=datetime.now().isoformat(),
            pattern_id=pattern.pattern_id,
            statement=f"When factor '{pattern.conditions.get('factor', 'unknown')}' is present, "
                     f"success rate is {pattern.success_rate:.1%}",
            conditions=pattern.conditions,
            expected_outcome="success" if pattern.success_rate > 0.5 else "failure",
            evidence_count=pattern.evidence_count
        )
        
        return hypothesis
    
    def validate_hypothesis(self, hypothesis: Hypothesis, 
                            min_sample: int = MIN_SAMPLE_FOR_VALIDATION,
                            p_threshold: float = P_VALUE_THRESHOLD) -> Tuple[bool, Dict]:
        """Validate Hypothesis through statistical testing
        
        Returns: (is_valid, validation_result)
        """
        # Get all evidence
        all_evidence = self.evidence_store.get_all_evidence(limit=10000)
        
        # Filter evidence matching hypothesis conditions
        matching_evidence = []
        for evidence in all_evidence:
            factor = hypothesis.conditions.get('factor', '')
            if factor in evidence.factors:
                matching_evidence.append(evidence)
        
        if len(matching_evidence) < min_sample:
            return False, {"reason": "insufficient_sample", "count": len(matching_evidence)}
        
        # Statistical test (simplified chi-square)
        success_count = sum(1 for e in matching_evidence if e.evidence_type == "success")
        failure_count = sum(1 for e in matching_evidence if e.evidence_type == "failure")
        total = len(matching_evidence)
        
        observed_success_rate = success_count / total
        
        # Simplified validation: check if success rate is statistically significant
        # (In production, use proper statistical tests)
        import math
        if total > 0:
            # Standard error approximation
            se = math.sqrt(observed_success_rate * (1 - observed_success_rate) / total)
            z_score = (observed_success_rate - 0.5) / se if se > 0 else 0
            
            # z > 1.96 for p < 0.05
            is_significant = abs(z_score) > 1.96
        else:
            is_significant = False
        
        validation_result = {
            "sample_size": total,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": observed_success_rate,
            "z_score": z_score if total > 0 else 0,
            "p_value": 0.05 if is_significant else 0.5,  # Simplified
            "is_significant": is_significant
        }
        
        is_valid = is_significant and total >= min_sample
        
        return is_valid, validation_result
    
    def create_law(self, hypothesis: Hypothesis, validation_result: Dict) -> Law:
        """Create Law from validated Hypothesis
        
        Law CANNOT directly affect Recommendation.
        """
        law = Law(
            law_id=f"law_{hypothesis.hypothesis_id}",
            timestamp=datetime.now().isoformat(),
            hypothesis_id=hypothesis.hypothesis_id,
            statement=hypothesis.statement,
            conditions=hypothesis.conditions,
            expected_outcome=hypothesis.expected_outcome,
            evidence_count=hypothesis.evidence_count,
            confidence=validation_result.get("success_rate", 0.5),
            scope=hypothesis.conditions,
            status=LawStatus.DRAFT,
            created_time=datetime.now().isoformat(),
            last_verified=datetime.now().isoformat(),
            verification_count=1
        )
        
        self.law_registry.register_law(law)
        
        return law
    
    def run_discovery_cycle(self) -> Dict[str, Any]:
        """Run one complete discovery cycle
        
        Returns summary of what was discovered.
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "patterns_found": 0,
            "hypotheses_generated": 0,
            "laws_created": 0,
            "details": []
        }
        
        # 1. Mine patterns
        patterns = self.mine_patterns()
        result["patterns_found"] = len(patterns)
        
        for pattern in patterns:
            # 2. Generate hypothesis
            hypothesis = self.generate_hypothesis(pattern)
            result["hypotheses_generated"] += 1
            
            # 3. Validate hypothesis
            is_valid, validation = self.validate_hypothesis(hypothesis)
            
            if is_valid:
                # 4. Create law
                law = self.create_law(hypothesis, validation)
                result["laws_created"] += 1
                result["details"].append({
                    "pattern": pattern.pattern_id,
                    "hypothesis": hypothesis.hypothesis_id,
                    "law": law.law_id,
                    "confidence": law.confidence
                })
        
        return result


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Law Discovery Protocol")
    parser.add_argument("--discover", action="store_true", help="Run discovery cycle")
    parser.add_argument("--laws", action="store_true", help="List all laws")
    parser.add_argument("--evidence", action="store_true", help="List all evidence")
    parser.add_argument("--validate", type=str, help="Validate a specific law ID")
    args = parser.parse_args()
    
    engine = LawDiscoveryEngine()
    
    if args.discover:
        result = engine.run_discovery_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if args.laws:
        laws = engine.law_registry.get_active_laws()
        print(f"Active Laws: {len(laws)}")
        for law in laws:
            print(f"  {law.law_id}: {law.statement[:50]}... (confidence: {law.confidence:.2%})")
    
    if args.evidence:
        evidence = engine.evidence_store.get_all_evidence(limit=100)
        print(f"Evidence Count: {len(evidence)}")
    
    if args.validate:
        law = engine.law_registry.get_law(args.validate)
        if law:
            is_valid, validation = engine.validate_hypothesis(
                Hypothesis(
                    hypothesis_id=law.hypothesis_id,
                    timestamp=law.timestamp,
                    pattern_id="",
                    statement=law.statement,
                    conditions=law.conditions
                )
            )
            print(f"Validation result for {args.validate}:")
            print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()