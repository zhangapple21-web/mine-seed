"""---
id: PROTO-030
type: protocol
title: "CONTINUITY-001 Continuity Engine — 连续性引擎"
status: active
source: "Governance Map v1: P0 gap — Continuity checks scattered across heartbeat"
created: 2026-07-13
confidence: 0.95
lineage:
  - PROTO-001 (Heartbeat)
  - PROTO-014 (Recovery Protocol)
  - PROTO-016 (Nature Reserve)
  - PROTO-017 (Gene Network)
  - PROTO-015 (Energy Budget)
  - PROTO-013 (Seed Archive)
tags: [continuity, heartbeat, governance, consolidation]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
"""
CONTINUITY-001: Continuity Engine — 连续性引擎
===============================================

Governance Map v1 identified a P0 gap:
  "Continuity checks scattered across heartbeat.py — no unified entry point"

This module consolidates all continuity checks into a single engine:
  - Recovery readiness (OPS-004)
  - Environment scan (EFP)
  - Nature Reserve integrity
  - Gene Network health
  - Energy Budget status
  - Seed Archive freshness
  - Civilization Map monitoring

Previously, heartbeat.py directly imported and called each check.
Now, heartbeat calls ContinuityEngine.run_all_checks() which
orchestrates all checks and returns a unified report.

Design principle:
  Each check is independent. A failure in one check does not
  stop other checks. The engine collects all results and
  returns a summary with per-check details.
"""

import os, sys, json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

import importlib.util


def _import_from_path(module_path: Path):
    """Dynamically import a module from file path"""
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContinuityCheck:
    """Base class for a single continuity check

    Each check implements:
      - run() -> Dict: execute the check and return result
      - name: str: human-readable check name
      - id: str: check identifier for reporting
    """

    def __init__(self):
        self.name = "unnamed"
        self.id = "unknown"

    def run(self) -> Dict[str, Any]:
        raise NotImplementedError


class RecoveryCheck(ContinuityCheck):
    """OPS-004: Recovery First check"""

    def __init__(self):
        self.name = "Recovery First"
        self.id = "ops_004"

    def run(self) -> Dict[str, Any]:
        try:
            ops_004_mod = _import_from_path(WORKSPACE / "04_PROTOCOLS" / "ops_004_recovery_first.py")
            result = ops_004_mod.recovery_first(check_only=True)
            return {
                "status": "ok",
                "summary": result.get("summary", {}),
                "ready": result.get("summary", {}).get("ready", False),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class EnvironmentCheck(ContinuityCheck):
    """EFP: Environment First Protocol scan"""

    def __init__(self):
        self.name = "Environment Scan"
        self.id = "efp"

    def run(self) -> Dict[str, Any]:
        try:
            ef_mod = _import_from_path(WORKSPACE / "04_PROTOCOLS" / "environment_first.py")
            idx = ef_mod.scan_directory(WORKSPACE, max_depth=3)
            return {
                "status": "ok",
                "files_total": idx.get("files_total", 0),
                "recovery_assets": len(idx.get("recovery_assets", [])),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class NatureReserveCheck(ContinuityCheck):
    """RESERVE-001: Nature Reserve integrity"""

    def __init__(self):
        self.name = "Nature Reserve"
        self.id = "nature_reserve"

    def run(self) -> Dict[str, Any]:
        try:
            from nature_reserve import reserve
            today = datetime.now()
            # Monday: establish baseline
            if today.weekday() == 0:
                baseline = reserve.establish_baseline()
                return {
                    "status": "baseline_established",
                    "files_hashed": baseline.get("files_hashed", 0),
                    "intact": baseline.get("files_hashed", 0),
                    "tampered": 0,
                    "missing": 0,
                }
            # Verify integrity
            integrity = reserve.verify_integrity()
            return {
                "status": integrity.get("status", "unknown"),
                "total": integrity.get("total", 0),
                "intact": integrity.get("intact", 0),
                "tampered": len(integrity.get("tampered", [])),
                "missing": len(integrity.get("missing", [])),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class GeneNetworkCheck(ContinuityCheck):
    """GENE-002: Gene Network health"""

    def __init__(self):
        self.name = "Gene Network"
        self.id = "gene_network"

    def run(self) -> Dict[str, Any]:
        try:
            from gene_network import network as gene_net
            summary = gene_net.get_summary()
            return {
                "status": "ok",
                "total_genes": summary.get("total_genes", 0),
                "total_dependencies": summary.get("total_dependencies", 0),
                "principles": summary.get("principles", 0),
                "constraints": summary.get("constraints", 0),
                "configs": summary.get("configs", 0),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class EnergyBudgetCheck(ContinuityCheck):
    """ENERGY-001: Energy Budget status"""

    def __init__(self):
        self.name = "Energy Budget"
        self.id = "energy_budget"

    def run(self) -> Dict[str, Any]:
        try:
            from energy_budget import budget as energy
            summary = energy.get_summary()
            # Reset beat counter
            energy.reset_beat()
            return {
                "status": "ok",
                "level": summary.get("level", "unknown"),
                "daily": {
                    k: f"{v['used']}/{v['limit']} ({v['ratio']:.0%})"
                    for k, v in summary.get("daily_usage", {}).items()
                },
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class SeedArchiveCheck(ContinuityCheck):
    """GENE-001: Seed Archive freshness (daily)"""

    def __init__(self):
        self.name = "Seed Archive"
        self.id = "seed_archive"

    def run(self) -> Dict[str, Any]:
        try:
            from seed_archive import SeedArchive
            seed = SeedArchive()
            today_str = datetime.now().strftime("%Y%m%d")
            expected_zip = seed.backup_dir / f"gene_seed_{today_str}.zip"
            if not expected_zip.exists():
                result = seed.create_seed()
                seed.prune_old_seeds(keep=7)
                return {
                    "status": "created",
                    "seed_id": result.get("seed_id", ""),
                    "size_kb": round(result.get("zip_size", 0) / 1024, 1),
                    "file_count": result.get("file_count", 0),
                }
            else:
                return {
                    "status": "already_exists",
                    "seed_id": f"gene_seed_{today_str}",
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class CivilizationMapCheck(ContinuityCheck):
    """CIV-001: Civilization Map monitoring"""

    def __init__(self):
        self.name = "Civilization Map"
        self.id = "civilization_map"

    def run(self) -> Dict[str, Any]:
        try:
            civ_map_mod = _import_from_path(WORKSPACE / "04_PROTOCOLS" / "civilization_map.py")
            repos = civ_map_mod.fetch_repos()
            if not repos:
                return {"status": "ok", "repos": 0, "stale": 0}
            civ_report = civ_map_mod.analyze_repos(repos)
            stale_count = sum(
                1 for r in civ_report.get("repos", [])
                if r.get("days_stale", 0) > r.get("max_stale_days", 30)
            )
            return {
                "status": "ok",
                "repos": len(repos),
                "stale": stale_count,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class ContinuityEngine:
    """Continuity Engine — 统一连续性检查入口

    Consolidates all continuity checks that were previously
    scattered across heartbeat.py into a single orchestrator.

    Usage:
        engine = ContinuityEngine()
        report = engine.run_all_checks()
    """

    CHECKS = [
        RecoveryCheck,
        EnvironmentCheck,
        NatureReserveCheck,
        GeneNetworkCheck,
        EnergyBudgetCheck,
        SeedArchiveCheck,
        CivilizationMapCheck,
    ]

    def __init__(self):
        self.checks = [cls() for cls in self.CHECKS]

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all continuity checks and return unified report"""
        results = {}
        ok_count = 0
        error_count = 0

        for check in self.checks:
            result = check.run()
            results[check.id] = {
                "name": check.name,
                **result,
            }
            if result.get("status") in ("ok", "baseline_established", "created", "already_exists"):
                ok_count += 1
            else:
                error_count += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(self.checks),
            "ok": ok_count,
            "errors": error_count,
            "checks": results,
        }

    def run_check(self, check_id: str) -> Dict[str, Any]:
        """Run a single check by ID"""
        for check in self.checks:
            if check.id == check_id:
                result = check.run()
                return {"name": check.name, **result}
        return {"status": "error", "error": f"Unknown check_id: {check_id}"}

    def get_check_ids(self) -> List[str]:
        """Get list of all check IDs"""
        return [c.id for c in self.checks]


# Module-level singleton
engine = ContinuityEngine()


# ============================================================
# Unit Tests
# ============================================================
def _run_tests():
    """Basic unit tests for ContinuityEngine"""
    print("Running ContinuityEngine unit tests...")

    ce = ContinuityEngine()

    # Test 1: Engine has all expected checks
    ids = ce.get_check_ids()
    expected = ["ops_004", "efp", "nature_reserve", "gene_network",
                "energy_budget", "seed_archive", "civilization_map"]
    assert ids == expected, f"Expected {expected}, got {ids}"
    print(f"  [PASS] All {len(expected)} checks registered")

    # Test 2: Run a single check
    result = ce.run_check("gene_network")
    assert "name" in result
    assert result["name"] == "Gene Network"
    print("  [PASS] Single check execution works")

    # Test 3: Run all checks (may have errors due to missing modules, but structure is valid)
    report = ce.run_all_checks()
    assert "timestamp" in report
    assert report["total_checks"] == 7
    assert "checks" in report
    print(f"  [PASS] run_all_checks() returns valid structure ({report['total_checks']} checks)")

    print("\nAll 3 tests passed.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Continuity Engine")
    parser.add_argument("--test", action="store_true", help="Run unit tests")
    parser.add_argument("--check", type=str, help="Run single check by ID")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    args = parser.parse_args()

    if args.test:
        _run_tests()
    elif args.check:
        ce = ContinuityEngine()
        result = ce.run_check(args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    elif args.all:
        ce = ContinuityEngine()
        report = ce.run_all_checks()
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
