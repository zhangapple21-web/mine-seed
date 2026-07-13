"""---
id: PROTO-029
type: protocol
title: "CONTRACT-001 Civilization Contract — 文明契约守护"
status: active
source: "028_ace_civilization_os: Runtime → Civilization only via Admission"
created: 2026-07-13
confidence: 0.95
lineage:
  - PROTO-020 (Admission Engine)
  - PROTO-016 (Nature Reserve)
  - 028_ace_civilization_os (Dual System Architecture)
tags: [contract, boundary, civilization, runtime, admission, guardian]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: 028_ace_civilization_os Interface Contract
"""
CONTRACT-001: Civilization Contract — 文明契约守护
====================================================

Design Source:
  028_ace_civilization_os defines a unidirectional dependency:
    Runtime -> Civilization (read-only)
    Civilization <- Runtime (write, only via Admission)

  This module makes that boundary checkable, rejectable, and auditable.

What it does:
  - can_read(path):  Runtime reading Civilization layer — default allow
  - can_write(path, via_admission): Runtime writing Civilization layer —
      via_admission=False -> REJECT and log violation
      via_admission=True  -> ALLOW (Admission Engine already reviewed)

What it does NOT do:
  - OS-level file permission enforcement (chmod, locks)
  - Actual Admission review (that is AdmissionEngine's job)
  - Modify any Civilization asset content

Violation Log Format:
  [CONTRACT-VIOLATION] {timestamp} | caller={caller} | path={path} | operation=write | via_admission=False | zone={zone}
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

WORKSPACE = Path(__file__).parent.parent

# ============================================================
# Civilization Protected Zone Definitions
# ============================================================

# Tier 1: Strictly Civilization — any write requires Admission
# These are the "why we live" — identity, axioms, assets
CIV_TIER1_PATHS = [
    "00_ROOT",                              # All files: axioms, principles, manifesto
    "02_MEMORY/civilization_assets",         # 28+ civilization asset documents
    "02_MEMORY/lineage",                     # Lineage index and reports
]

# Tier 2: Civilization Heritage — Runtime can append, but modifying existing requires Admission
# Archaeological evidence: once written, should not be modified
CIV_TIER2_PATHS = [
    "02_MEMORY/archaeology",                 # Archaeological findings and evidence
]

# Tier 3: Runtime Operational — Runtime can read/write freely
# These are "how we live" — operational data produced by Runtime
# (Not listed here explicitly; anything NOT in Tier1/Tier2 is Tier3 by default)
RUNTIME_OPERATIONAL_SUBDIRS = [
    "02_MEMORY/environment",
    "02_MEMORY/heartbeat",
    "02_MEMORY/diary",
    "02_MEMORY/ops_logs",
    "02_MEMORY/self_loop",
    "02_MEMORY/recovery",
    "02_MEMORY/question_center",
    "02_MEMORY/advisor_tracker",
    "02_MEMORY/exploration",
    "02_MEMORY/civilization_audit",
    "02_MEMORY/experience",
    "02_MEMORY/tg_sessions",
    "06_RUNTIME/archaeology_workspace",  # Staged archaeology (promoted via Admission)
]


class CivilizationContract:
    """Civilization Contract Guardian

    Enforces the boundary between Runtime and Civilization layers.
    Every Runtime code that wants to write to Civilization-protected paths
    MUST call can_write() first. Not calling it is a code standard violation.
    """

    def __init__(self):
        self.tier1 = [WORKSPACE / p for p in CIV_TIER1_PATHS]
        self.tier2 = [WORKSPACE / p for p in CIV_TIER2_PATHS]
        self.violation_log: List[Dict[str, Any]] = []
        self._logger = logging.getLogger("civilization_contract")

    def _resolve(self, path) -> Path:
        """Resolve path to absolute Path object"""
        if isinstance(path, str):
            p = Path(path)
            if not p.is_absolute():
                p = WORKSPACE / p
            return p
        return path

    def _classify_zone(self, path) -> str:
        """Classify a path into its zone (tier1/tier2/tier3/unknown)"""
        p = self._resolve(path)
        try:
            rel = p.relative_to(WORKSPACE)
        except ValueError:
            return "unknown"

        rel_str = str(rel).replace("\\", "/")

        # Check tier1
        for zone in self.tier1:
            try:
                zone_rel = zone.relative_to(WORKSPACE)
                rel_str_zone = str(rel).replace("\\", "/")
                prefix = str(zone_rel).replace("\\", "/")
                if rel_str_zone == prefix or rel_str_zone.startswith(prefix + "/"):
                    return "tier1"
            except ValueError:
                continue

        # Check tier2
        for zone in self.tier2:
            try:
                zone_rel = zone.relative_to(WORKSPACE)
                rel_str_zone = str(rel).replace("\\", "/")
                prefix = str(zone_rel).replace("\\", "/")
                if rel_str_zone == prefix or rel_str_zone.startswith(prefix + "/"):
                    return "tier2"
            except ValueError:
                continue

        return "tier3"

    def can_read(self, path) -> bool:
        """Check if Runtime can read the given path

        Runtime -> Civilization is read-only by default.
        All reads are allowed.

        Args:
            path: File path (str or Path), relative to workspace or absolute

        Returns:
            True (reads are always allowed)
        """
        return True

    def can_write(self, path, via_admission: bool = False,
                  caller: str = "unknown") -> bool:
        """Check if Runtime can write the given path

        Civilization-protected paths require via_admission=True.
        Runtime operational paths are always writable.

        Args:
            path: File path (str or Path), relative to workspace or absolute
            via_admission: Whether this write goes through Admission Engine
            caller: Name of the calling module/function (for audit trail)

        Returns:
            True if write is allowed, False if rejected
        """
        p = self._resolve(path)
        zone = self._classify_zone(p)

        # Tier3 (Runtime operational) — always allowed
        if zone == "tier3":
            return True

        # Tier1 or Tier2 — requires Admission
        if zone in ("tier1", "tier2"):
            if via_admission:
                self._logger.info(
                    "[CONTRACT-ALLOWED] %s | caller=%s | path=%s | operation=write | via_admission=True | zone=%s",
                    datetime.now().isoformat(), caller, p, zone
                )
                return True
            else:
                violation = {
                    "timestamp": datetime.now().isoformat(),
                    "caller": caller,
                    "path": str(p),
                    "operation": "write",
                    "via_admission": False,
                    "zone": zone,
                    "decision": "rejected",
                }
                self.violation_log.append(violation)
                self._logger.warning(
                    "[CONTRACT-VIOLATION] %s | caller=%s | path=%s | operation=write | via_admission=False | zone=%s",
                    datetime.now().isoformat(), caller, p, zone
                )
                return False

        # Unknown zone — reject by default
        return False

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all recorded violations"""
        return list(self.violation_log)

    def clear_violations(self):
        """Clear violation log (for testing)"""
        self.violation_log.clear()

    def get_zone_info(self, path) -> Dict[str, Any]:
        """Get zone classification info for a path"""
        p = self._resolve(path)
        zone = self._classify_zone(p)
        try:
            rel = p.relative_to(WORKSPACE)
            rel_str = str(rel).replace("\\", "/")
        except ValueError:
            rel_str = str(p)

        return {
            "path": str(p),
            "relative": rel_str,
            "zone": zone,
            "zone_description": {
                "tier1": "Strictly Civilization — any write requires Admission",
                "tier2": "Civilization Heritage — append allowed, modify requires Admission",
                "tier3": "Runtime Operational — free read/write",
                "unknown": "Outside workspace — rejected by default",
            }.get(zone, "unknown"),
            "can_read": self.can_read(path),
            "can_write_without_admission": zone == "tier3",
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get contract summary"""
        return {
            "tier1_count": len(self.tier1),
            "tier2_count": len(self.tier2),
            "tier1_paths": [str(p.relative_to(WORKSPACE)).replace("\\", "/") for p in self.tier1],
            "tier2_paths": [str(p.relative_to(WORKSPACE)).replace("\\", "/") for p in self.tier2],
            "total_violations": len(self.violation_log),
        }


# Module-level singleton
contract = CivilizationContract()


# ============================================================
# Unit Tests (run with: python civilization_contract.py --test)
# ============================================================
def _run_tests():
    """Basic unit tests"""
    c = CivilizationContract()
    print("Running CivilizationContract unit tests...")

    # Test 1: can_read always returns True
    assert c.can_read("00_ROOT/PRINCIPLES.md") is True, "can_read should always return True"
    assert c.can_read("02_MEMORY/civilization_assets/001_provider_watchdog.md") is True
    assert c.can_read("02_MEMORY/heartbeat/beat_20260710.json") is True
    assert c.can_read("04_PROTOCOLS/heartbeat.py") is True
    print("  [PASS] can_read always returns True")

    # Test 2: can_write tier1 without Admission -> rejected
    result = c.can_write("00_ROOT/PRINCIPLES.md", via_admission=False, caller="test")
    assert result is False, "Tier1 write without Admission should be rejected"
    assert len(c.get_violations()) == 1, "Should have 1 violation logged"
    print("  [PASS] Tier1 write without Admission is rejected + logged")

    # Test 3: can_write tier1 with Admission -> allowed
    result = c.can_write("00_ROOT/PRINCIPLES.md", via_admission=True, caller="admission_engine")
    assert result is True, "Tier1 write with Admission should be allowed"
    print("  [PASS] Tier1 write with Admission is allowed")

    # Test 4: can_write tier2 without Admission -> rejected
    c.clear_violations()
    result = c.can_write("02_MEMORY/archaeology/evidence_graph_r1_kernel.json", via_admission=False, caller="test")
    assert result is False, "Tier2 write without Admission should be rejected"
    assert len(c.get_violations()) == 1
    print("  [PASS] Tier2 write without Admission is rejected + logged")

    # Test 5: can_write tier3 (Runtime operational) -> always allowed
    c.clear_violations()
    result = c.can_write("02_MEMORY/heartbeat/beat_20260710.json", via_admission=False, caller="heartbeat")
    assert result is True, "Tier3 write should be always allowed"
    assert len(c.get_violations()) == 0
    print("  [PASS] Tier3 write is always allowed (no violation)")

    # Test 6: can_write to civilization_assets (tier1) -> rejected without Admission
    c.clear_violations()
    result = c.can_write("02_MEMORY/civilization_assets/029_new_asset.md", via_admission=False, caller="test")
    assert result is False, "civilization_assets write without Admission should be rejected"
    print("  [PASS] civilization_assets write without Admission is rejected")

    # Test 7: can_write to lineage (tier1) -> rejected without Admission
    result = c.can_write("02_MEMORY/lineage/lineage_index.json", via_admission=False, caller="test")
    assert result is False, "lineage write without Admission should be rejected"
    print("  [PASS] lineage write without Admission is rejected")

    # Test 8: get_zone_info classification
    info = c.get_zone_info("00_ROOT/PRINCIPLES.md")
    assert info["zone"] == "tier1", f"00_ROOT should be tier1, got {info['zone']}"
    info = c.get_zone_info("02_MEMORY/archaeology/test.json")
    assert info["zone"] == "tier2", f"archaeology should be tier2, got {info['zone']}"
    info = c.get_zone_info("02_MEMORY/heartbeat/beat.json")
    assert info["zone"] == "tier3", f"heartbeat should be tier3, got {info['zone']}"
    print("  [PASS] Zone classification is correct")

    # Test 9: violation log format
    c.clear_violations()
    c.can_write("00_ROOT/MANIFESTO.md", via_admission=False, caller="rogue_module")
    v = c.get_violations()[0]
    assert v["caller"] == "rogue_module"
    assert v["via_admission"] is False
    assert v["zone"] == "tier1"
    assert v["decision"] == "rejected"
    print("  [PASS] Violation log format is correct")

    print("\nAll 9 tests passed.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Civilization Contract Guardian")
    parser.add_argument("--test", action="store_true", help="Run unit tests")
    parser.add_argument("--summary", action="store_true", help="Show contract summary")
    parser.add_argument("--check", type=str, help="Check a path's zone classification")
    parser.add_argument("--violations", action="store_true", help="Show recorded violations")
    args = parser.parse_args()

    if args.test:
        _run_tests()
    elif args.summary:
        import json
        print(json.dumps(contract.get_summary(), ensure_ascii=False, indent=2))
    elif args.check:
        import json
        print(json.dumps(contract.get_zone_info(args.check), ensure_ascii=False, indent=2))
    elif args.violations:
        import json
        print(json.dumps(contract.get_violations(), ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
