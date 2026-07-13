"""---
id: PROTO-031
type: protocol
title: "CONSTRAINT-001 — Three Unloseable Constraints Validator"
status: active
source: "Governance Map v1: P0 gap — Automated validation of three unloseable constraints"
created: 2026-07-13
confidence: 0.95
lineage:
  - PROTO-030 (Continuity Engine)
  - PROTO-016 (Nature Reserve)
  - PROTO-012 (Admission Engine)
tags: [constraint, validation, governance, l_infinity]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
"""
CONSTRAINT-001: Three Unloseable Constraints Validator

Governance Map v1 identified a P0 gap:
  "Automated validation of three unloseable constraints missing"

Three unloseable constraints:
  1. Continuity Constraint — Continuity Engine must always be running
  2. L∞ Constraint — Nature Reserve must protect all 36 core files
  3. Admission Constraint — Admission Engine must be the only write channel

This module automates checking these constraints and raises alerts
when any constraint is violated.
"""

import os, sys, json, logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

log = logging.getLogger(__name__)


class ContinuityConstraint:
    """Check: Continuity Engine is running and all checks pass"""

    def __init__(self):
        self.name = "Continuity Constraint"
        self.id = "continuity"
        self.description = "Continuity Engine must always be running"

    def validate(self) -> Dict[str, Any]:
        try:
            from continuity_engine import ContinuityEngine
            ce = ContinuityEngine()
            report = ce.run_all_checks()

            if report["errors"] > 0:
                failed = [k for k, v in report["checks"].items()
                          if v.get("status") not in ("ok", "baseline_established", "created", "already_exists")]
                return {
                    "status": "violated",
                    "severity": "high",
                    "message": f"Continuity Engine has {report['errors']} failed checks: {', '.join(failed)}",
                    "details": report,
                }

            return {
                "status": "satisfied",
                "severity": "ok",
                "message": f"Continuity Engine: {report['ok']}/{report['total_checks']} checks passed",
                "details": {"checks_passed": report["ok"], "total_checks": report["total_checks"]},
            }
        except Exception as e:
            return {
                "status": "error",
                "severity": "critical",
                "message": f"Continuity Constraint check failed: {e}",
                "details": str(e),
            }


class LInfinityConstraint:
    """Check: Nature Reserve protects all 36 core files (L∞ seal)"""

    def __init__(self):
        self.name = "L∞ Constraint"
        self.id = "l_infinity"
        self.description = "Nature Reserve must protect all 36 core files"

    def validate(self) -> Dict[str, Any]:
        try:
            from nature_reserve import reserve
            integrity = reserve.verify_integrity()

            if integrity["status"] == "no_baseline":
                return {
                    "status": "violated",
                    "severity": "critical",
                    "message": "L∞ Constraint violated: No baseline established",
                    "details": integrity,
                }

            tampered_count = len(integrity.get("tampered", []))
            missing_count = len(integrity.get("missing", []))

            if tampered_count > 0:
                return {
                    "status": "violated",
                    "severity": "critical",
                    "message": f"L∞ Constraint violated: {tampered_count} files tampered",
                    "details": {"tampered": integrity.get("tampered", []), "total": integrity.get("total", 0)},
                }

            if missing_count > 0:
                return {
                    "status": "violated",
                    "severity": "critical",
                    "message": f"L∞ Constraint violated: {missing_count} files missing",
                    "details": {"missing": integrity.get("missing", []), "total": integrity.get("total", 0)},
                }

            return {
                "status": "satisfied",
                "severity": "ok",
                "message": f"L∞ Constraint satisfied: {integrity.get('intact', 0)}/{integrity.get('total', 0)} files intact",
                "details": {"intact": integrity.get("intact", 0), "total": integrity.get("total", 0)},
            }
        except Exception as e:
            return {
                "status": "error",
                "severity": "critical",
                "message": f"L∞ Constraint check failed: {e}",
                "details": str(e),
            }


class AdmissionConstraint:
    """Check: Admission Engine is the only write channel to Civilization layer"""

    def __init__(self):
        self.name = "Admission Constraint"
        self.id = "admission"
        self.description = "Admission Engine must be the only write channel to Civilization layer"

    def validate(self) -> Dict[str, Any]:
        try:
            from admission_engine import engine as admission
            from civilization_contract import contract

            # Check 1: Admission Engine is available
            if not admission:
                return {
                    "status": "violated",
                    "severity": "critical",
                    "message": "Admission Constraint violated: Admission Engine not available",
                    "details": "admission_engine module exists but engine singleton is None",
                }

            # Check 2: Contract is available
            if not contract:
                return {
                    "status": "violated",
                    "severity": "critical",
                    "message": "Admission Constraint violated: Contract not available",
                    "details": "civilization_contract module exists but contract singleton is None",
                }

            # Check 3: Admission Engine has review_asset method
            if not hasattr(admission, "review_asset"):
                return {
                    "status": "violated",
                    "severity": "high",
                    "message": "Admission Constraint violated: Admission Engine missing review_asset method",
                    "details": "Expected method: review_asset",
                }

            # Check 4: Contract has can_write method
            if not hasattr(contract, "can_write"):
                return {
                    "status": "violated",
                    "severity": "critical",
                    "message": "Admission Constraint violated: Contract missing can_write method",
                    "details": "Expected method: can_write",
                }

            # Check 5: Contract blocks direct writes to Tier 1 without admission
            test_tier1_path = "02_MEMORY/civilization_assets/test.md"
            can_write_direct = contract.can_write(test_tier1_path, via_admission=False, caller="test")
            if can_write_direct:
                return {
                    "status": "violated",
                    "severity": "critical",
                    "message": "Admission Constraint violated: Contract allows direct write to Tier 1",
                    "details": f"can_write('{test_tier1_path}', via_admission=False) returned True",
                }

            # Check 6: Contract allows writes with admission
            can_write_via_admission = contract.can_write(test_tier1_path, via_admission=True, caller="test")
            if not can_write_via_admission:
                return {
                    "status": "violated",
                    "severity": "high",
                    "message": "Admission Constraint violated: Contract blocks write even with admission",
                    "details": f"can_write('{test_tier1_path}', via_admission=True) returned False",
                }

            return {
                "status": "satisfied",
                "severity": "ok",
                "message": "Admission Constraint satisfied: Admission is the only write channel",
                "details": {
                    "admission_available": True,
                    "contract_available": True,
                    "direct_write_blocked": True,
                    "admission_write_allowed": True,
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "severity": "critical",
                "message": f"Admission Constraint check failed: {e}",
                "details": str(e),
            }


class ConstraintValidator:
    """Three Unloseable Constraints Validator

    Validates the three foundational constraints that must never be violated:
      1. Continuity Constraint — Continuity Engine must always be running
      2. L∞ Constraint — Nature Reserve must protect all 36 core files
      3. Admission Constraint — Admission Engine must be the only write channel

    Usage:
        validator = ConstraintValidator()
        report = validator.validate_all()
    """

    CONSTRAINTS = [
        ContinuityConstraint,
        LInfinityConstraint,
        AdmissionConstraint,
    ]

    def __init__(self):
        self.constraints = [cls() for cls in self.CONSTRAINTS]

    def validate_all(self) -> Dict[str, Any]:
        """Validate all three constraints"""
        results = {}
        satisfied_count = 0
        violated_count = 0
        error_count = 0

        for constraint in self.constraints:
            result = constraint.validate()
            results[constraint.id] = {
                "name": constraint.name,
                "description": constraint.description,
                **result,
            }
            if result["status"] == "satisfied":
                satisfied_count += 1
            elif result["status"] == "violated":
                violated_count += 1
            else:
                error_count += 1

        overall_status = "satisfied"
        overall_severity = "ok"
        if violated_count > 0:
            overall_status = "violated"
            overall_severity = "critical"
        elif error_count > 0:
            overall_status = "error"
            overall_severity = "high"

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "overall_severity": overall_severity,
            "total_constraints": len(self.constraints),
            "satisfied": satisfied_count,
            "violated": violated_count,
            "errors": error_count,
            "constraints": results,
        }

    def validate(self, constraint_id: str) -> Dict[str, Any]:
        """Validate a single constraint by ID"""
        for constraint in self.constraints:
            if constraint.id == constraint_id:
                result = constraint.validate()
                return {"name": constraint.name, "description": constraint.description, **result}
        return {"status": "error", "error": f"Unknown constraint_id: {constraint_id}"}

    def get_constraint_ids(self) -> List[str]:
        """Get list of all constraint IDs"""
        return [c.id for c in self.constraints]


# Module-level singleton
validator = ConstraintValidator()


# ============================================================
# Unit Tests
# ============================================================
def _run_tests():
    print("Running ConstraintValidator unit tests...")

    cv = ConstraintValidator()

    # Test 1: Validator has all three constraints
    ids = cv.get_constraint_ids()
    expected = ["continuity", "l_infinity", "admission"]
    assert ids == expected, f"Expected {expected}, got {ids}"
    print(f"  [PASS] All {len(expected)} constraints registered")

    # Test 2: Run a single constraint
    result = cv.validate("admission")
    assert "name" in result
    assert result["name"] == "Admission Constraint"
    print("  [PASS] Single constraint validation works")

    # Test 3: Run all constraints (may have errors, but structure is valid)
    report = cv.validate_all()
    assert "timestamp" in report
    assert report["total_constraints"] == 3
    assert "overall_status" in report
    assert "constraints" in report
    print(f"  [PASS] validate_all() returns valid structure (overall_status: {report['overall_status']})")

    # Test 4: Admission constraint correctly blocks direct writes
    from civilization_contract import contract
    assert not contract.can_write("02_MEMORY/civilization_assets/test.md", via_admission=False, caller="test")
    print("  [PASS] Contract blocks direct writes to Tier 1")

    # Test 5: Admission constraint allows writes via admission
    assert contract.can_write("02_MEMORY/civilization_assets/test.md", via_admission=True, caller="test")
    print("  [PASS] Contract allows writes with admission")

    print("\nAll 5 tests passed.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Three Unloseable Constraints Validator")
    parser.add_argument("--test", action="store_true", help="Run unit tests")
    parser.add_argument("--validate", type=str, help="Validate single constraint by ID")
    parser.add_argument("--all", action="store_true", help="Validate all constraints")
    args = parser.parse_args()

    if args.test:
        _run_tests()
    elif args.validate:
        cv = ConstraintValidator()
        result = cv.validate(args.validate)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    elif args.all:
        cv = ConstraintValidator()
        report = cv.validate_all()
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
