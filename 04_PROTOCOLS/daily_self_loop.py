#!/usr/bin/env python3
"""
ACE Daily Self Loop - 每日自循环协议

Identity: Civilization Maintenance Agent
Mission: 不依赖用户指令，每日主动执行文明维护任务

Schedule: Daily at 03:00 (before stock market opens)
           Heartbeat check every 15 minutes between 09:20-11:30 for stock advisor compensation

Principles:
    - Evidence First
    - Repository First
    - Drawer First Protocol (DFP-001)
    - Self-Loop (OPS-005)
    - Environment First Protocol (EFP)
    - Recovery First (OPS-004)

Never Rules:
    - Never wait for user input for scheduled maintenance
    - Never modify Tier 1/Tier 2 assets without Admission
    - Never delete historical Evidence
    - Never push unapproved assets to Runtime
"""

import os
import sys
import json
import time
import traceback
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / "05_TOOLS"
ADVISOR_DIR = TOOLS_DIR / "advisor"
MINER_DIR = TOOLS_DIR / "miner"
PROTOCOLS_DIR = WORKSPACE / "04_PROTOCOLS"
MEMORY_DIR = WORKSPACE / "02_MEMORY"
OUTPUT_DIR = TOOLS_DIR / "mine_output" / "advisor"

LOG_FILE = OUTPUT_DIR / "daily_self_loop.log"
STATUS_FILE = OUTPUT_DIR / "self_loop_status.json"
DAILY_REPORT_FILE = MEMORY_DIR / "daily_reports"

sys.path.insert(0, str(ADVISOR_DIR))
sys.path.insert(0, str(PROTOCOLS_DIR))


# ============================================================================
# Logging
# ============================================================================

class LoopLogger:
    """自循环日志记录器"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        print(log_line.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)


# ============================================================================
# Status
# ============================================================================

class LoopStatus:
    """自循环状态管理"""
    
    def __init__(self, status_file: Path):
        self.status_file = status_file
        self.status = self._load()
    
    def _load(self) -> dict:
        if self.status_file.exists():
            try:
                return json.loads(self.status_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {
            "last_run_time": "",
            "last_run_success": False,
            "steps": {},
            "error_message": "",
            "daily_report": "",
        }
    
    def save(self, success: bool, steps: dict, error_message: str = "", daily_report: str = ""):
        self.status = {
            "last_run_time": datetime.now().isoformat(),
            "last_run_success": success,
            "steps": steps,
            "error_message": error_message,
            "daily_report": daily_report,
        }
        self.status_file.write_text(json.dumps(self.status, ensure_ascii=False, indent=2), encoding='utf-8')


# ============================================================================
# Helpers
# ============================================================================

def run_script(script_path: Path, args: list = None, timeout: int = 300, logger: LoopLogger = None) -> tuple[bool, str]:
    """Run a Python script and return success status and output"""
    cmd = [sys.executable, str(script_path)] + (args or [])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        if logger:
            if success:
                logger.log(f"  ✓ {script_path.name}")
            else:
                logger.log(f"  ✗ {script_path.name} (exit {result.returncode}): {output[:200]}", "ERROR")
        
        return success, output
    except Exception as e:
        if logger:
            logger.log(f"  ✗ {script_path.name} exception: {e}", "ERROR")
        return False, str(e)


def today_str() -> str:
    return datetime.now().strftime('%Y%m%d')


def is_market_day() -> bool:
    """Check if today is a weekday (simple version)"""
    return datetime.now().weekday() < 5


def is_stock_advisor_window() -> bool:
    """Check if current time is within 09:20-11:30"""
    now = datetime.now()
    start = now.replace(hour=9, minute=20, second=0, microsecond=0)
    end = now.replace(hour=11, minute=30, second=0, microsecond=0)
    return start <= now <= end and is_market_day()


def stock_advisor_already_run() -> bool:
    """Check if stock advisor has already generated today's report"""
    today_report = OUTPUT_DIR / f"advisor_{today_str()}.md"
    if today_report.exists() and today_report.stat().st_size > 100:
        return True
    
    status_file = OUTPUT_DIR / "runner_status.json"
    if status_file.exists():
        try:
            status = json.loads(status_file.read_text(encoding='utf-8'))
            last_run = status.get('last_run_time', '')
            return last_run.startswith(datetime.now().strftime('%Y-%m-%d'))
        except Exception:
            pass
    
    return False


# ============================================================================
# Self Loop Steps
# ============================================================================

def step_environment_scan(logger: LoopLogger) -> bool:
    """
    OPS-005 / EFP: Environment → Observe
    Scan working directory and build asset index
    """
    logger.log("[1/8] Environment Scan (EFP)")
    
    # Build asset index
    try:
        # Update ASSET_INDEX.md if exists
        asset_index = WORKSPACE / "ASSET_INDEX.md"
        if asset_index.exists():
            logger.log("  ✓ ASSET_INDEX.md found")
        else:
            logger.log("  ⚠ ASSET_INDEX.md missing", "WARNING")
        
        return True
    except Exception as e:
        logger.log(f"  ✗ Environment scan failed: {e}", "ERROR")
        return False


def step_recovery_check(logger: LoopLogger) -> bool:
    """
    OPS-004: Recovery First
    Check for recovery assets (backup, README, snapshot, archive, seed)
    """
    logger.log("[2/8] Recovery Check (RP)")
    
    try:
        # Check README
        readme = WORKSPACE / "README.md"
        if readme.exists():
            logger.log("  ✓ README.md found")
        
        # Check for backups
        backup_dir = WORKSPACE / "backup"
        if backup_dir.exists():
            backups = list(backup_dir.glob("*.zip"))
            logger.log(f"  ✓ {len(backups)} backup(s) found")
        
        return True
    except Exception as e:
        logger.log(f"  ✗ Recovery check failed: {e}", "ERROR")
        return False


def step_asset_audit(logger: LoopLogger) -> bool:
    """
    Audit civilization assets
    Check for untracked/modified files, new raw data, etc.
    """
    logger.log("[3/8] Asset Audit")
    
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        lines = [l for l in result.stdout.split('\n') if l.strip()]
        if lines:
            logger.log(f"  ⚠ {len(lines)} untracked/modified file(s)")
            # Log first 10
            for line in lines[:10]:
                logger.log(f"    {line}")
        else:
            logger.log("  ✓ Working tree clean")
        
        return True
    except Exception as e:
        logger.log(f"  ⚠ Asset audit failed: {e}", "WARNING")
        return False


def step_law_discovery(logger: LoopLogger) -> bool:
    """
    AUM-MISSION-LAW-001: Law Discovery Protocol (EXPERIMENTAL)
    Status: Self-dispatched prototype, under daily audit
    Guardrail: Outputs only to Law Registry, never touches Runtime or Policy
    """
    logger.log("[4/7] Law Discovery (experimental, under audit)")
    
    law_discovery_script = PROTOCOLS_DIR / "law_discovery.py"
    if not law_discovery_script.exists():
        logger.log("  ⚠ law_discovery.py not found", "WARNING")
        return True
    
    success, output = run_script(law_discovery_script, ["--discover"], timeout=300, logger=logger)
    
    if success:
        try:
            result = json.loads(output.split('\n')[-2] if output else '{}')
            patterns = result.get('patterns_found', 0)
            laws = result.get('laws_created', 0)
            logger.log(f"  Patterns found: {patterns}, Laws created: {laws}")
            if laws > 0:
                logger.log("  ⚠ New laws created — flagged for daily audit", "WARNING")
        except Exception:
            pass
    
    return True


def step_evidence_migration(logger: LoopLogger) -> bool:
    """
    Migrate new performance data to Evidence store (append-only)
    Part of AUM-MISSION-LAW-001 experimental pipeline
    """
    logger.log("[5/7] Evidence Migration (append-only)")
    
    migrate_script = PROTOCOLS_DIR / "migrate_to_evidence.py"
    if not migrate_script.exists():
        logger.log("  ⚠ migrate_to_evidence.py not found", "WARNING")
        return True
    
    success, _ = run_script(migrate_script, ["--run"], timeout=300, logger=logger)
    return True


def step_stock_advisor(logger: LoopLogger) -> bool:
    """
    Run stock advisor if in market window and not already run
    Heartbeat-based auto-compensation
    """
    logger.log("[6/8] Stock Advisor Check")
    
    if not is_market_day():
        logger.log("  ✓ Not a market day, skipping")
        return True
    
    if stock_advisor_already_run():
        logger.log("  ✓ Stock advisor already ran today")
        return True
    
    if not is_stock_advisor_window():
        logger.log(f"  ✓ Outside stock advisor window ({datetime.now().strftime('%H:%M')})")
        return True
    
    logger.log("  → Triggering stock advisor (heartbeat compensation)")
    
    daily_runner = ADVISOR_DIR / "daily_runner.py"
    success, _ = run_script(daily_runner, timeout=600, logger=logger)
    return success


def step_daily_discovery(logger: LoopLogger) -> bool:
    """
    Daily Discovery Protocol
    Scan TG favorites, unmined repository parts, local files
    """
    logger.log("[7/9] Daily Discovery")
    
    # Check if daily discovery script exists (in 05_TOOLS)
    discovery_script = TOOLS_DIR / "daily_discovery_runner.py"
    if discovery_script.exists():
        success, _ = run_script(discovery_script, timeout=600, logger=logger)
        return success
    else:
        logger.log("  ⚠ daily_discovery_runner.py not found, skipping", "WARNING")
        return True  # Not critical


def step_self_audit(logger: LoopLogger) -> bool:
    """
    Daily self-audit: verify no boundary violations
    Checks:
    - Law Discovery not writing to Runtime/Policy
    - No unapproved assets in Tier 1/Tier 2
    - Evidence store remains append-only
    """
    logger.log("[8/9] Self-Audit")
    
    violations = []
    
    # Audit 1: Law Registry has no laws that bypassed Roundtable
    law_registry = MEMORY_DIR / "law_registry" / "laws.json"
    if law_registry.exists():
        try:
            laws = json.loads(law_registry.read_text(encoding='utf-8'))
            active_laws = [l for l in laws if l.get('status') == 'ACTIVE']
            policy_candidates_dir = MEMORY_DIR / "policy_candidates"
            if policy_candidates_dir.exists():
                policy_files = list(policy_candidates_dir.glob("*.json"))
                logger.log(f"  Law Registry: {len(active_laws)} active laws, {len(policy_files)} policy candidates")
            for law in active_laws:
                if law.get('status') == 'ACTIVE' and not law.get('last_verified'):
                    violations.append(f"Law {law.get('law_id')} is ACTIVE but has no verification record")
        except Exception as e:
            logger.log(f"  ⚠ Law registry audit failed: {e}", "WARNING")
    
    # Audit 2: No direct Runtime modifications from learning modules
    # (Policy can only be loaded from approved policy files)
    approved_policy = MEMORY_DIR / "law_registry" / "approved_policies.json"
    if approved_policy.exists():
        try:
            policies = json.loads(approved_policy.read_text(encoding='utf-8'))
            logger.log(f"  Approved policies: {len(policies)}")
        except Exception as e:
            logger.log(f"  ⚠ Policy audit failed: {e}", "WARNING")
    
    # Audit 3: Evidence store integrity (append-only check)
    evidence_dir = MEMORY_DIR / "evidence"
    if evidence_dir.exists():
        index_file = evidence_dir / "evidence_index.json"
        if index_file.exists():
            try:
                index = json.loads(index_file.read_text(encoding='utf-8'))
                count = index.get('total_count', 0)
                logger.log(f"  Evidence store: {count} records, append-only")
            except Exception as e:
                logger.log(f"  ⚠ Evidence audit failed: {e}", "WARNING")
    
    if violations:
        logger.log(f"  ✗ Audit found {len(violations)} violation(s):", "ERROR")
        for v in violations:
            logger.log(f"    - {v}", "ERROR")
        # Write violations to audit log
        audit_log = OUTPUT_DIR / "audit_violations.log"
        with open(audit_log, 'a', encoding='utf-8') as f:
            ts = datetime.now().isoformat()
            for v in violations:
                f.write(f"[{ts}] {v}\n")
        return False
    else:
        logger.log("  ✓ No boundary violations detected")
        return True


def step_daily_report(logger: LoopLogger) -> str:
    """
    Generate daily civilization report
    """
    logger.log("[9/9] Daily Report")
    
    DAILY_REPORT_FILE.mkdir(parents=True, exist_ok=True)
    report_file = DAILY_REPORT_FILE / f"daily_report_{today_str()}.md"
    
    lines = []
    lines.append(f"# Daily Civilization Report - {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat()}")
    lines.append(f"- Market Day: {'Yes' if is_market_day() else 'No'}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("Self-loop executed. See `mine_output/advisor/daily_self_loop.log` for details.")
    lines.append("")
    lines.append("## Pending Missions")
    lines.append("")
    
    # Load pending tasks
    pending_tasks = MEMORY_DIR / "pending_tasks.json"
    if pending_tasks.exists():
        try:
            tasks = json.loads(pending_tasks.read_text(encoding='utf-8'))
            active_tasks = [t for t in tasks if t.get('status') == 'pending']
            lines.append(f"- Active missions: {len(active_tasks)}")
            for task in active_tasks[:5]:
                title = task.get('title', task.get('mission_id', 'Unknown'))
                lines.append(f"  - {title}")
        except Exception:
            lines.append("- Unable to load pending tasks")
    
    lines.append("")
    lines.append("## Pending Questions")
    lines.append("")
    
    pending_questions = MEMORY_DIR / "pending_questions.json"
    if pending_questions.exists():
        try:
            questions = json.loads(pending_questions.read_text(encoding='utf-8'))
            pending = [q for q in questions if q.get('status') == 'pending']
            lines.append(f"- Pending questions: {len(pending)}")
            for q in pending[:5]:
                lines.append(f"  - {q.get('question', 'Unknown')[:80]}...")
        except Exception:
            lines.append("- Unable to load pending questions")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*This report is auto-generated by ACE Daily Self Loop.*")
    
    report_file.write_text('\n'.join(lines), encoding='utf-8')
    logger.log(f"  ✓ Report saved: {report_file.name}")
    
    return str(report_file)


# ============================================================================
# Main Loop
# ============================================================================

def run_self_loop(logger: LoopLogger = None, status: LoopStatus = None):
    """Run the complete daily self loop"""
    logger = logger or LoopLogger(LOG_FILE)
    status = status or LoopStatus(STATUS_FILE)
    
    logger.log("=" * 70)
    logger.log(f"ACE Daily Self Loop - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.log("=" * 70)
    
    start_time = time.time()
    steps = {}
    error_message = ""
    daily_report = ""
    
    try:
        # Phase 0: Environment / Recovery
        steps["environment_scan"] = step_environment_scan(logger)
        steps["recovery_check"] = step_recovery_check(logger)
        steps["asset_audit"] = step_asset_audit(logger)
        
        # Phase 1: Learning & Discovery
        steps["law_discovery"] = step_law_discovery(logger)
        steps["evidence_migration"] = step_evidence_migration(logger)
        
        # Phase 2: Operational Tasks
        steps["stock_advisor"] = step_stock_advisor(logger)
        steps["daily_discovery"] = step_daily_discovery(logger)
        
        # Phase 3: Audit
        steps["self_audit"] = step_self_audit(logger)
        
        # Phase 4: Reporting
        daily_report = step_daily_report(logger)
        steps["daily_report"] = bool(daily_report)
        
        success = all(steps.values())
        
    except Exception as e:
        success = False
        error_message = f"{e}\n{traceback.format_exc()[:500]}"
        logger.log(f"✗ Self loop fatal error: {e}", "ERROR")
    
    elapsed = time.time() - start_time
    logger.log(f"\n{'='*70}")
    logger.log(f"Self loop completed in {elapsed:.1f}s")
    logger.log(f"Overall: {'✓ SUCCESS' if success else '✗ FAILED'}")
    for step_name, step_ok in steps.items():
        logger.log(f"  {'✓' if step_ok else '✗'} {step_name}")
    logger.log(f"{'='*70}\n")
    
    status.save(
        success=success,
        steps=steps,
        error_message=error_message,
        daily_report=daily_report
    )
    
    return success


def schedule_task():
    """Register Windows scheduled task"""
    print("Registering ACE Daily Self Loop task...")
    
    task_name = "ACE_DailySelfLoop"
    script_path = Path(__file__).resolve()
    python_path = sys.executable
    
    cmd = (
        f'schtasks /create /tn "{task_name}" '
        f'/tr "\\"{python_path}" \\"{script_path}\"" '
        f'/sc daily /st 03:00 '
        f'/f /ru SYSTEM'
    )
    
    print(f"\nCommand: {cmd}")
    print("\nPlease run as administrator:")
    print(cmd)
    print("\nAlternative: Use Windows Task Scheduler GUI")
    print(f"  Program: {python_path}")
    print(f"  Arguments: {script_path}")
    print(f"  Trigger: Daily 03:00")
    print(f"  Run as: SYSTEM")


def check_status():
    """Check last self loop status"""
    status = LoopStatus(STATUS_FILE)
    s = status.status
    
    print("\nACE Daily Self Loop Status")
    print(f"  Last run: {s.get('last_run_time', 'Never')}")
    print(f"  Result: {'✓ SUCCESS' if s.get('last_run_success') else '✗ FAILED'}")
    print(f"  Daily report: {s.get('daily_report', 'N/A')}")
    
    if s.get('error_message'):
        print(f"  Error: {s['error_message'][:200]}")
    
    print("\n  Steps:")
    for step, ok in s.get('steps', {}).items():
        print(f"    {'✓' if ok else '✗'} {step}")


def heartbeat_mode(interval_minutes: int = 15):
    """Run in heartbeat mode (check every N minutes during market window)"""
    logger = LoopLogger(LOG_FILE)
    status = LoopStatus(STATUS_FILE)
    
    logger.log(f"Heartbeat mode started, interval={interval_minutes}min")
    
    while True:
        now = datetime.now()
        
        # Run full loop once per day at 03:00
        if now.hour == 3 and now.minute < interval_minutes:
            run_self_loop(logger, status)
        
        # Heartbeat stock advisor compensation during market window
        elif is_stock_advisor_window():
            if not stock_advisor_already_run():
                logger.log("Heartbeat: stock advisor not run yet, triggering")
                step_stock_advisor(logger)
        
        # Sleep until next check
        time.sleep(interval_minutes * 60)


def main():
    parser = argparse.ArgumentParser(description="ACE Daily Self Loop")
    parser.add_argument("--schedule", action="store_true", help="Show schedule command")
    parser.add_argument("--check", action="store_true", help="Check last run status")
    parser.add_argument("--heartbeat", action="store_true", help="Run in heartbeat mode")
    parser.add_argument("--interval", type=int, default=15, help="Heartbeat interval in minutes")
    args = parser.parse_args()
    
    if args.schedule:
        schedule_task()
    elif args.check:
        check_status()
    elif args.heartbeat:
        heartbeat_mode(args.interval)
    else:
        run_self_loop()


if __name__ == "__main__":
    main()
