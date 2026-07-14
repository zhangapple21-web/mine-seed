#!/usr/bin/env python3
"""
E→C Closure Protocol — 经验到约束的闭环

核心原则：
- 经验是数据，约束才是行动
- O→E是记录，E→C是执行
- 失败组合自动规避，冷却优于硬删

触发条件：node.status 变为 degraded/dead
输出：active_constraints.json + task_mapping + constraint_trace

使用：python e2c_closure.py [--observe] [--threshold 3] [--cooling-hours 24]
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from pathlib import Path

# Default paths (relative to mine-seed)
BASE_DIR = Path(__file__).parent.parent
OBSERVATION_FILE = BASE_DIR / "05_TOOLS" / "mine_output" / "observation_log.json"
CONSTRAINT_FILE = BASE_DIR / "05_TOOLS" / "constraints" / "active_constraints.json"
TASK_MAPPING_FILE = BASE_DIR / "05_TOOLS" / "constraints" / "task_mapping.json"
CONSTRAINT_TRACE_FILE = BASE_DIR / "05_TOOLS" / "constraints" / "constraint_trace.json"

# Default thresholds
THRESHOLD_DEFAULT = 3
COOLING_HOURS_DEFAULT = 24


class ConstraintEntry:
    """Constraint entry model"""

    def __init__(
        self,
        constraint_type: str,  # FORBID | AVOID | PREFER
        target: str,           # node_id or worker_id
        scope: str,            # scheduler | routing | fallback
        reason: str,           # observation reference
        source_observation: str = "",
        cooling_until: Optional[str] = None,
    ):
        self.constraint_type = constraint_type
        self.target = target
        self.scope = scope
        self.reason = reason
        self.source_observation = source_observation
        self.cooling_until = cooling_until
        self.created_at = datetime.now().isoformat()
        self.status = "ACTIVE"

    def to_dict(self) -> dict:
        return {
            "type": self.constraint_type,
            "target": self.target,
            "scope": self.scope,
            "reason": self.reason,
            "source_observation": self.source_observation,
            "cooling_until": self.cooling_until,
            "created_at": self.created_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConstraintEntry":
        entry = cls(
            constraint_type=data.get("type", "AVOID"),
            target=data.get("target", ""),
            scope=data.get("scope", "scheduler"),
            reason=data.get("reason", ""),
            source_observation=data.get("source_observation", ""),
            cooling_until=data.get("cooling_until"),
        )
        entry.created_at = data.get("created_at", datetime.now().isoformat())
        entry.status = data.get("status", "ACTIVE")
        return entry


class CoolingManager:
    """Cooling period manager — 冷却优于硬删"""

    def __init__(self, cooling_hours: int = COOLING_HOURS_DEFAULT):
        self.cooling_hours = cooling_hours

    def is_in_cooling(self, constraint: ConstraintEntry) -> bool:
        """Check if a constraint is still in cooling period"""
        if not constraint.cooling_until:
            return False
        try:
            cooling_end = datetime.fromisoformat(constraint.cooling_until)
            return datetime.now() < cooling_end
        except (ValueError, TypeError):
            return False

    def set_cooling(self, constraint: ConstraintEntry) -> None:
        """Set cooling period for a constraint"""
        cooling_end = datetime.now() + timedelta(hours=self.cooling_hours)
        constraint.cooling_until = cooling_end.isoformat()

    def should_reactivate(self, constraint: ConstraintEntry) -> bool:
        """Check if a constraint should be reactivated after cooling"""
        if constraint.status != "COOLING":
            return False
        return not self.is_in_cooling(constraint)


class ConstraintTrace:
    """Constraint trace for replay — 支持回放追溯"""

    def __init__(self, trace_file: Path = CONSTRAINT_TRACE_FILE):
        self.trace_file = trace_file
        self.traces = self._load_traces()

    def _load_traces(self) -> List[dict]:
        if not self.trace_file.exists():
            return []
        try:
            with open(self.trace_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def add_trace(
        self,
        constraint: ConstraintEntry,
        trigger_reason: str,
        observation_ids: List[str],
    ) -> None:
        """Add a trace entry for a constraint"""
        trace_entry = {
            "timestamp": datetime.now().isoformat(),
            "constraint_id": f"{constraint.target}_{constraint.scope}_{constraint.constraint_type}",
            "constraint_type": constraint.constraint_type,
            "target": constraint.target,
            "scope": constraint.scope,
            "trigger_reason": trigger_reason,
            "observation_ids": observation_ids,
            "constraint_snapshot": constraint.to_dict(),
        }
        self.traces.append(trace_entry)
        self._save_traces()

    def _save_traces(self) -> None:
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.trace_file, "w", encoding="utf-8") as f:
            json.dump(self.traces, f, ensure_ascii=False, indent=2)

    def get_traces_for_target(self, target: str) -> List[dict]:
        """Get all traces for a specific target"""
        return [t for t in self.traces if t.get("target") == target]

    def get_traces_for_observation(self, obs_id: str) -> List[dict]:
        """Get all traces triggered by a specific observation"""
        return [t for t in self.traces if obs_id in t.get("observation_ids", [])]


class E2CClosure:
    """
    E→C Closure Protocol — 经验到约束的闭环

    WHEN node.status changes to degraded/dead:
      1. READ recent_failures FROM observation_log
      2. GENERATE constraint_entry
      3. WRITE active_constraints.json
      4. UPDATE task_mapping
      5. LOG constraint_trace

    ENFORCE constraint BEFORE task_dispatch:
      - CHECK skip_set first
      - REJECT if FORBID
      - DOWNGRADE if AVOID
      - BOOST if PREFER
    """

    def __init__(
        self,
        observation_file: Path = OBSERVATION_FILE,
        constraint_file: Path = CONSTRAINT_FILE,
        task_mapping_file: Path = TASK_MAPPING_FILE,
        threshold: int = THRESHOLD_DEFAULT,
        cooling_hours: int = COOLING_HOURS_DEFAULT,
    ):
        self.observation_file = observation_file
        self.constraint_file = constraint_file
        self.task_mapping_file = task_mapping_file
        self.threshold = threshold
        self.cooling_manager = CoolingManager(cooling_hours)
        self.trace = ConstraintTrace()

    def load_observations(self) -> List[dict]:
        """Load observation log"""
        if not self.observation_file.exists():
            return []
        try:
            with open(self.observation_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("observations", [])
        except (json.JSONDecodeError, IOError):
            return []

    def load_constraints(self) -> Dict:
        """Load active constraints"""
        if not self.constraint_file.exists():
            return {"version": "1.0", "updated": "", "constraints": []}
        try:
            with open(self.constraint_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"version": "1.0", "updated": "", "constraints": []}

    def save_constraints(self, constraints: Dict) -> None:
        """Save active constraints"""
        self.constraint_file.parent.mkdir(parents=True, exist_ok=True)
        constraints["updated"] = datetime.now().isoformat()
        with open(self.constraint_file, "w", encoding="utf-8") as f:
            json.dump(constraints, f, ensure_ascii=False, indent=2)

    def load_task_mapping(self) -> Dict:
        """Load task mapping"""
        if not self.task_mapping_file.exists():
            return {"version": "1.0", "mappings": {}}
        try:
            with open(self.task_mapping_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"version": "1.0", "mappings": {}}

    def save_task_mapping(self, task_mapping: Dict) -> None:
        """Save task mapping"""
        self.task_mapping_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.task_mapping_file, "w", encoding="utf-8") as f:
            json.dump(task_mapping, f, ensure_ascii=False, indent=2)

    def analyze_failures(self, observations: List[dict]) -> Dict[str, Dict]:
        """Analyze failure patterns from observations

        Returns:
            Dict mapping target -> failure stats
        """
        failure_stats = defaultdict(lambda: {"success": 0, "fail": 0, "errors": [], "observation_ids": []})

        for obs in observations:
            # Support both "success" field and "status" field
            is_success = obs.get("success", obs.get("status") == "success")
            target = obs.get("worker_id", obs.get("target", ""))
            if not target:
                continue

            if is_success:
                failure_stats[target]["success"] += 1
            else:
                failure_stats[target]["fail"] += 1
                error_msg = obs.get("error", obs.get("message", ""))[:100]
                if error_msg:
                    failure_stats[target]["errors"].append(error_msg)
                obs_id = obs.get("id", obs.get("observation_id", ""))
                if obs_id:
                    failure_stats[target]["observation_ids"].append(obs_id)

        return failure_stats

    def generate_constraint(
        self,
        target: str,
        stats: Dict,
        constraint_type: str = "AVOID",
    ) -> Optional[ConstraintEntry]:
        """Generate a constraint entry for a failing target"""
        if stats["fail"] < self.threshold:
            return None

        # Determine constraint type based on failure count
        if stats["fail"] >= 5:
            constraint_type = "FORBID"
        elif stats["fail"] >= 3:
            constraint_type = "AVOID"

        # Build reason
        total = stats["success"] + stats["fail"]
        fail_rate = stats["fail"] / total if total else 1.0
        reason = f"{stats['fail']} failures, {stats['success']} success, fail_rate={fail_rate:.1%}"

        # Source observation reference
        obs_ids = stats.get("observation_ids", [])
        source_obs = obs_ids[-1] if obs_ids else ""

        entry = ConstraintEntry(
            constraint_type=constraint_type,
            target=target,
            scope="scheduler",
            reason=reason,
            source_observation=source_obs,
        )

        # Set cooling period for AVOID constraints
        if constraint_type == "AVOID":
            self.cooling_manager.set_cooling(entry)

        return entry

    def update_task_mapping(
        self,
        task_mapping: Dict,
        constraint: ConstraintEntry,
    ) -> None:
        """Update task mapping with new constraint"""
        target = constraint.target
        if target not in task_mapping["mappings"]:
            task_mapping["mappings"][target] = {
                "constraint_type": constraint.constraint_type,
                "scope": constraint.scope,
                "status": constraint.status,
                "updated": datetime.now().isoformat(),
            }
        else:
            # Update existing mapping
            existing = task_mapping["mappings"][target]
            # Only upgrade constraint type (AVOID -> FORBID), never downgrade
            type_order = {"PREFER": 0, "AVOID": 1, "FORBID": 2}
            if type_order.get(constraint.constraint_type, 0) > type_order.get(existing.get("constraint_type", "AVOID"), 1):
                existing["constraint_type"] = constraint.constraint_type
            existing["updated"] = datetime.now().isoformat()

    def run(self, auto_confirm: bool = False) -> List[ConstraintEntry]:
        """Run the E→C closure protocol

        Args:
            auto_confirm: If True, automatically confirm and write constraints

        Returns:
            List of generated constraint entries
        """
        print("=== E→C Closure Protocol ===")
        print(f"Failure threshold: {self.threshold}")
        print()

        # Load observations
        observations = self.load_observations()
        print(f"Observations loaded: {len(observations)}")

        # Analyze failures
        failure_stats = self.analyze_failures(observations)
        print(f"Targets analyzed: {len(failure_stats)}")

        # Generate constraints for targets exceeding threshold
        new_constraints = []
        for target, stats in failure_stats.items():
            if stats["fail"] >= self.threshold:
                constraint = self.generate_constraint(target, stats)
                if constraint:
                    new_constraints.append(constraint)
                    print(f"  Generated constraint: {constraint.constraint_type} {target}")
                    print(f"    Reason: {constraint.reason}")

        print(f"\nNew constraints: {len(new_constraints)}")

        if not new_constraints:
            print("No new constraints to add.")
            return []

        # Load existing constraints
        constraints_data = self.load_constraints()
        existing_targets = {
            c.get("target") for c in constraints_data.get("constraints", [])
        }

        # Filter out already existing constraints
        new_entries = [c for c in new_constraints if c.target not in existing_targets]
        print(f"New entries to add: {len(new_entries)} (skipped existing: {len(new_constraints) - len(new_entries)})")

        if not new_entries:
            print("All constraints already exist.")
            return []

        if auto_confirm:
            # Write constraints
            constraints_data["constraints"].extend([c.to_dict() for c in new_entries])
            self.save_constraints(constraints_data)
            print(f"\nConstraints written to {self.constraint_file}")

            # Update task mapping
            task_mapping = self.load_task_mapping()
            for constraint in new_entries:
                self.update_task_mapping(task_mapping, constraint)
            self.save_task_mapping(task_mapping)
            print(f"Task mapping updated: {self.task_mapping_file}")

            # Log traces
            for constraint in new_entries:
                self.trace.add_trace(
                    constraint=constraint,
                    trigger_reason=f"failures >= {self.threshold}",
                    observation_ids=[constraint.source_observation] if constraint.source_observation else [],
                )
            print(f"Constraint traces logged: {self.trace.trace_file}")
        else:
            print("\n--- Pending constraints (use --auto-confirm to apply) ---")
            for c in new_entries:
                print(f"  {c.constraint_type} {c.target}: {c.reason}")

        return new_entries

    def check_cooling_reactivation(self) -> List[str]:
        """Check and reactivate constraints that have finished cooling

        Returns:
            List of reactivated targets
        """
        constraints_data = self.load_constraints()
        reactivated = []

        for constraint_dict in constraints_data.get("constraints", []):
            constraint = ConstraintEntry.from_dict(constraint_dict)
            if self.cooling_manager.should_reactivate(constraint):
                constraint.status = "ACTIVE"
                constraint.cooling_until = None
                # Update the dict in place
                constraint_dict.update(constraint.to_dict())
                reactivated.append(constraint.target)

        if reactivated:
            self.save_constraints(constraints_data)
            print(f"Reactivated from cooling: {reactivated}")

        return reactivated


class SchedulerPrecheck:
    """
    Scheduler pre-check — 调度前置检查

    ENFORCE constraint BEFORE task_dispatch:
      - CHECK skip_set first
      - REJECT if FORBID
      - DOWNGRADE if AVOID
      - BOOST if PREFER
    """

    def __init__(self, constraint_file: Path = CONSTRAINT_FILE):
        self.constraint_file = constraint_file

    def load_constraints(self) -> Dict:
        """Load active constraints"""
        if not self.constraint_file.exists():
            return {"version": "1.0", "constraints": []}
        try:
            with open(self.constraint_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"version": "1.0", "constraints": []}

    def check_target(self, target: str) -> Tuple[bool, str, Optional[str]]:
        """Check if a target can be dispatched

        Returns:
            (allowed, action, reason)
            - allowed: True if dispatch is allowed
            - action: ALLOW | REJECT | DOWNGRADE | BOOST
            - reason: Explanation for the action
        """
        constraints_data = self.load_constraints()

        # Build skip_set (FORBID targets)
        skip_set = set()
        avoid_set = set()
        prefer_set = set()

        for c in constraints_data.get("constraints", []):
            if c.get("status") != "ACTIVE":
                continue

            target_c = c.get("target", "")
            ctype = c.get("type", "AVOID")

            if ctype == "FORBID":
                skip_set.add(target_c)
            elif ctype == "AVOID":
                avoid_set.add(target_c)
            elif ctype == "PREFER":
                prefer_set.add(target_c)

        if target in skip_set:
            return False, "REJECT", f"Target {target} is FORBID"

        if target in avoid_set:
            # Allow but with downgrade
            return True, "DOWNGRADE", f"Target {target} is AVOID (downgrade priority)"

        if target in prefer_set:
            return True, "BOOST", f"Target {target} is PREFER (boost priority)"

        return True, "ALLOW", "No constraint"

    def get_available_targets(self, candidates: List[str]) -> Tuple[List[str], List[str]]:
        """Filter candidates by constraints

        Returns:
            (allowed, rejected)
        """
        allowed = []
        rejected = []

        for target in candidates:
            ok, action, reason = self.check_target(target)
            if ok:
                allowed.append(target)
            else:
                rejected.append(target)

        return allowed, rejected


def main():
    parser = argparse.ArgumentParser(description="E→C Closure Protocol")
    parser.add_argument("--observe", action="store_true", help="Run in observe mode (analyze only)")
    parser.add_argument("--threshold", type=int, default=THRESHOLD_DEFAULT, help="Failure threshold")
    parser.add_argument("--cooling-hours", type=int, default=COOLING_HOURS_DEFAULT, help="Cooling period in hours")
    parser.add_argument("--auto-confirm", action="store_true", help="Automatically confirm constraints")
    parser.add_argument("--check-cooling", action="store_true", help="Check and reactivate cooling constraints")
    parser.add_argument("--precheck", type=str, help="Check if a target can be dispatched")
    args = parser.parse_args()

    if args.precheck:
        # Scheduler pre-check mode
        prechecker = SchedulerPrecheck()
        ok, action, reason = prechecker.check_target(args.precheck)
        print(f"Target: {args.precheck}")
        print(f"Action: {action}")
        print(f"Reason: {reason}")
        print(f"Allowed: {ok}")
        return

    if args.check_cooling:
        # Cooling reactivation mode
        closure = E2CClosure(
            threshold=args.threshold,
            cooling_hours=args.cooling_hours,
        )
        reactivated = closure.check_cooling_reactivation()
        if reactivated:
            print(f"Reactivated: {reactivated}")
        else:
            print("No constraints to reactivate.")
        return

    # Normal E→C closure mode
    closure = E2CClosure(
        threshold=args.threshold,
        cooling_hours=args.cooling_hours,
    )

    closure.run(auto_confirm=args.auto_confirm)


if __name__ == "__main__":
    main()