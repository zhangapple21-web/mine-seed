#!/usr/bin/env python3
"""
ACE Heartbeat - Silent background heartbeat
============================================

Default: silent (logs to file only)
  - Logs: 02_MEMORY/logs/heartbeat_YYYYMMDD.log
  - No console output unless --verbose
"""
import os, sys, json, time, argparse, logging
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

import importlib.util

def import_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    ef = import_module(WORKSPACE / "04_PROTOCOLS" / "environment_first.py")
    lm = import_module(WORKSPACE / "04_PROTOCOLS" / "local_miner.py")
    ops_004 = import_module(WORKSPACE / "04_PROTOCOLS" / "ops_004_recovery_first.py")
    mem = import_module(WORKSPACE / "06_RUNTIME" / "core" / "memory_manager.py")
    ace_logger = import_module(WORKSPACE / "06_RUNTIME" / "core" / "ace_logger.py")
    env_sensor_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "environment_sensor.py")
    awareness_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "awareness_loop.py")
    state_gen_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "state_generator.py")
    question_engine_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "question_engine.py")
    debate_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "multi_agent_debate.py")
    explorer_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "explorer_v2.py")
    evolution_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "self_evolution.py")
    qc_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "question_center.py")

    scan_directory = ef.scan_directory
    build_recovery_graph = ef.build_recovery_graph
    task_signal_discovery = lm.task_signal_discovery
    task_archivist = lm.task_archivist
    ops_004_check = ops_004.recovery_first
    MemoryManager = mem.MemoryManager
    get_logger = ace_logger.get_logger
    silence_all = ace_logger.silence_all
    EnvironmentSensor = env_sensor_mod.EnvironmentSensor
    SituationBuilder = env_sensor_mod.SituationBuilder
    AwarenessLoop = awareness_mod.AwarenessLoop
    StateGenerator = state_gen_mod.StateGenerator
    QuestionEngine = question_engine_mod.QuestionEngine
    DebateRoom = debate_mod.DebateRoom
    ExplorerV2 = explorer_mod.ExplorerV2
    SelfEvolution = evolution_mod.SelfEvolution
    QuestionCenter = qc_mod.QuestionCenter
except Exception as e:
    print(f"[HEARTBEAT] Import error: {e}", file=sys.stderr)
    sys.exit(1)


def beat(log):
    ts = datetime.now().isoformat()
    beat_id = ts.replace("-", "").replace(":", "").replace(".", "")[:15]
    log.info(f"=== Heartbeat {beat_id} ===")
    
    report = {
        "beat_id": beat_id,
        "time": ts,
        "status": "ok",
        "steps": {},
    }

    mm = MemoryManager()

    # OPS-004 Recovery First
    try:
        ops_004 = ops_004_check(check_only=True)
        report["ops_004_status"] = ops_004.get("summary", {})
        mm.save_memory("heartbeat", f"ops_004_{beat_id}", ops_004)
        if not ops_004.get("summary", {}).get("ready", False):
            log.warning(f"OPS-004 not ready: {ops_004['summary']}")
    except Exception as e:
        report["ops_004_status"] = {"error": str(e)}
        log.error(f"OPS-004 error: {e}")

    # EFP
    try:
        idx = scan_directory(WORKSPACE, max_depth=3)
        report["steps"]["efp"] = {
            "files": idx["files_total"],
            "recovery_assets": len(idx["recovery_assets"])
        }
        mm.save_memory("environment", "latest_scan", idx)
        log.info(f"EFP: {idx['files_total']} files, {len(idx['recovery_assets'])} recovery assets")
    except Exception as e:
        report["steps"]["efp"] = {"error": str(e)}
        log.error(f"EFP error: {e}")

    # Signal
    try:
        sig = task_signal_discovery()
        report["steps"]["signal"] = {"status": sig.get("status"), "model": sig.get("model")}
        log.info(f"Signal: {sig.get('status')}")
    except Exception as e:
        report["steps"]["signal"] = {"error": str(e)}
        log.error(f"Signal error: {e}")

    # Archivist
    try:
        arc = task_archivist()
        report["steps"]["archivist"] = {"status": arc.get("status"), "model": arc.get("model")}
        log.info(f"Archivist: {arc.get('status')}")
    except Exception as e:
        report["steps"]["archivist"] = {"error": str(e)}
        log.error(f"Archivist error: {e}")

    # ENV-001: Environment Sensor
    try:
        sensor = EnvironmentSensor()
        builder = SituationBuilder()
        obs = sensor.scan_all(sources=["local", "providers"])
        situation = builder.build(obs)
        report["steps"]["env_sensor"] = {
            "total": situation["total_observations"],
            "new": situation["new_observations"],
            "high_priority": len(situation["high_priority"]),
        }
        if situation["high_priority"]:
            log.warning(f"EnvSensor: {len(situation['high_priority'])} high priority items")
        else:
            log.info(f"EnvSensor: {situation['new_observations']} new observations")
    except Exception as e:
        report["steps"]["env_sensor"] = {"error": str(e)}
        log.error(f"EnvSensor error: {e}")

    # ENV-002: Awareness Loop — 扫描→提问→派单→研究→沉淀
    # 关键：只有有新观察或高优先级项时才跑，避免无意义重复
    try:
        env_step = report["steps"].get("env_sensor", {})
        has_new = env_step.get("new", 0) > 0
        has_high = env_step.get("high_priority", 0) > 0
        if has_new or has_high:
            log.info(f"AwarenessLoop: triggering (new={has_new}, high={has_high})")
            loop = AwarenessLoop()
            loop_result = loop.run(scan_only=False)
            reports_saved = loop_result.get("experiences_saved", [])
            questions = loop_result.get("questions", [])
            report["steps"]["awareness_loop"] = {
                "questions": len(questions),
                "reports_saved": len(reports_saved),
                "questions_detail": [{"priority": q["priority"], "question": q["question"][:100]} for q in questions],
            }
            if reports_saved:
                log.info(f"AwarenessLoop: {len(reports_saved)} experiences saved")
            else:
                log.info(f"AwarenessLoop: {len(questions)} questions, 0 experiences saved")
        else:
            report["steps"]["awareness_loop"] = {"status": "skipped", "reason": "no new observations"}
            log.info("AwarenessLoop: skipped (no new observations)")
    except Exception as e:
        report["steps"]["awareness_loop"] = {"error": str(e)}
        log.error(f"AwarenessLoop error: {e}")

    # QE-002: Question Engine — 把环境观察变成"为什么"的问题
    try:
        env_step = report["steps"].get("env_sensor", {})
        has_new = env_step.get("new", 0) > 0
        if has_new:
            log.info("QuestionEngine: generating questions from new observations")
            qe = QuestionEngine()
            situation_file = WORKSPACE / "02_MEMORY" / "environment" / "latest_situation.json"
            obs_file = WORKSPACE / "02_MEMORY" / "environment" / "latest_observations.json"
            observations = []
            if situation_file.exists():
                situation = json.loads(situation_file.read_text(encoding="utf-8"))
                observations = situation.get("all_observations", [])
            # Fallback: if all_observations is empty (already seen), use latest_observations.json
            if not observations and obs_file.exists():
                observations = json.loads(obs_file.read_text(encoding="utf-8"))
            candidates = qe.generate_batch(observations)
            created = qe.push_to_question_center(candidates)
            report["steps"]["question_engine"] = {
                "candidates": len(candidates),
                "created": len(created),
                "qids": created,
            }
            log.info(f"QuestionEngine: {len(created)} new questions created")
        else:
            report["steps"]["question_engine"] = {"status": "skipped", "reason": "no new observations"}
            log.info("QuestionEngine: skipped (no new observations)")
    except Exception as e:
        report["steps"]["question_engine"] = {"error": str(e)}
        log.error(f"QuestionEngine error: {e}")

    # DEB-001: Multi-Agent Debate — 对开放问题进行角色竞争与决策
    try:
        qc = QuestionCenter()
        open_qs = qc.get_open_questions()
        if open_qs:
            log.info(f"DebateRoom: debating {len(open_qs)} open questions")
            room = DebateRoom()
            # 每次心跳最多辩论 3 个问题，控制成本
            debate_results = room.debate_batch(open_qs[:3])
            approved = [r for r in debate_results if r.get("decision") == "approved"]
            report["steps"]["multi_agent_debate"] = {
                "debated": len(debate_results),
                "approved": len(approved),
                "deferred": len([r for r in debate_results if r.get("decision") == "deferred"]),
                "rejected": len([r for r in debate_results if r.get("decision") == "rejected"]),
            }
            log.info(f"DebateRoom: {len(approved)} approved, {len(debate_results) - len(approved)} not approved")
        else:
            report["steps"]["multi_agent_debate"] = {"status": "skipped", "reason": "no open questions"}
            log.info("DebateRoom: skipped (no open questions)")
    except Exception as e:
        report["steps"]["multi_agent_debate"] = {"error": str(e)}
        log.error(f"DebateRoom error: {e}")

    # EXP-002: Explorer v2 — 每天主动探索一个主题
    try:
        # 每天只运行一次（通过检查今天的报告是否存在）
        today_str = datetime.now().strftime("%Y%m%d")
        today_report = WORKSPACE / "02_MEMORY" / "exploration" / f"exploration_{today_str}.md"
        if not today_report.exists():
            log.info("ExplorerV2: starting daily exploration")
            explorer = ExplorerV2()
            exp_report = explorer.run(dry_run=False)
            report["steps"]["explorer_v2"] = {
                "topic": exp_report.get("topic", {}).get("name"),
                "recommendation": exp_report.get("absorb_recommendation"),
                "qid": exp_report.get("qid"),
            }
            log.info(f"ExplorerV2: explored {exp_report.get('topic', {}).get('name')}")
        else:
            report["steps"]["explorer_v2"] = {"status": "skipped", "reason": "already explored today"}
            log.info("ExplorerV2: skipped (already explored today)")
    except Exception as e:
        report["steps"]["explorer_v2"] = {"error": str(e)}
        log.error(f"ExplorerV2 error: {e}")

    # EVO-001: Self Evolution — 把 approved 决策变成代码/配置变更
    try:
        qc = QuestionCenter()
        # 获取最近 approved 但还没演化过的决策
        recent_decisions = [d for d in qc.decisions if d.get("outcome") == "approved"]
        # 过滤：只处理最近 24 小时内的
        recent_decisions = [
            d for d in recent_decisions
            if (datetime.now() - datetime.fromisoformat(d.get("created_at", "2000-01-01T00:00:00"))).total_seconds() < 86400
        ]
        if recent_decisions:
            log.info(f"SelfEvolution: processing {len(recent_decisions)} recent approved decisions")
            evo = SelfEvolution()
            evo_results = evo.process_approved_decisions(recent_decisions)
            evolved = [r for r in evo_results if r.get("status") == "evolved"]
            report["steps"]["self_evolution"] = {
                "processed": len(evo_results),
                "evolved": len(evolved),
                "deferred": len([r for r in evo_results if r.get("status") == "deferred_to_human"]),
                "failed": len([r for r in evo_results if r.get("status") in ["failed", "error"]]),
            }
            log.info(f"SelfEvolution: {len(evolved)} evolved, {len(evo_results) - len(evolved)} not evolved")
        else:
            report["steps"]["self_evolution"] = {"status": "skipped", "reason": "no recent approved decisions"}
            log.info("SelfEvolution: skipped (no recent approved decisions)")
    except Exception as e:
        report["steps"]["self_evolution"] = {"error": str(e)}
        log.error(f"SelfEvolution error: {e}")

    # CIV-001: Civilization Map Monitor
    try:
        civ_map_mod = import_module(WORKSPACE / "04_PROTOCOLS" / "civilization_map.py")
        repos = civ_map_mod.fetch_repos()
        if repos:
            civ_report = civ_map_mod.analyze_repos(repos)
            for repo in civ_report["repos"]:
                if repo["days_stale"] > repo["max_stale_days"]:
                    civ_map_mod.sediment_stale_experience(repo["name"], repo)
            civ_map_mod.update_current_state(civ_report)
            report["steps"]["civilization_map"] = {
                "total_repos": civ_report["total_repos"],
                "stale_count": civ_report["stale_count"],
                "critical_stale": civ_report["critical_stale"],
            }
            if civ_report["stale_count"] > 0:
                log.warning(f"CivMap: {civ_report['stale_count']} stale repos")
            else:
                log.info(f"CivMap: {civ_report['total_repos']} repos, all fresh")
    except Exception as e:
        report["steps"]["civilization_map"] = {"error": str(e)}
        log.error(f"CivMap error: {e}")

    # STATE-001: Update Current State Dashboard
    try:
        sg = StateGenerator()
        sg.update_current_state()
        report["steps"]["state_generator"] = {"status": "updated"}
        log.info("CURRENT_STATE.md updated")
    except Exception as e:
        report["steps"]["state_generator"] = {"error": str(e)}
        log.error(f"StateGenerator error: {e}")

    # TG Push — push heartbeat summary to Telegram if Bot available
    try:
        tg_result = _push_heartbeat_summary(report, log)
        report["steps"]["tg_push"] = tg_result
    except Exception as e:
        report["steps"]["tg_push"] = {"status": "error", "error": str(e)}
        log.error(f"TG push error: {e}")

    # Save
    mm.save_memory("heartbeat", f"beat_{beat_id}", report)
    log.info("Heartbeat saved")
    return report


def _push_heartbeat_summary(report: dict, log) -> dict:
    """Push a brief heartbeat summary to TG via Bot (if available)"""
    import urllib.request, json as _json
    from pathlib import Path

    # Load bot token from miner_env.sh
    env_file = Path(__file__).parent.parent / "05_TOOLS" / "miner" / "miner_env.sh"
    token = None
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "export TG_BOT_TOKEN_2=" in line:
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if not token:
        return {"status": "skipped", "reason": "no TG_BOT_TOKEN_2"}

    # Get chat_id from getUpdates
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates?limit=5"
        resp = urllib.request.urlopen(url, timeout=10)
        data = _json.loads(resp.read())
        chat_id = None
        for u in data.get("result", []):
            if "message" in u:
                chat_id = u["message"]["chat"]["id"]
                break
            if "channel_post" in u:
                chat_id = u["channel_post"]["chat"]["id"]
                break
        if not chat_id:
            return {"status": "skipped", "reason": "no chat_id (user has not messaged the bot yet)"}
    except Exception as e:
        return {"status": "error", "reason": f"getUpdates failed: {e}"}

    # Build summary message
    steps = report.get("steps", {})
    beat_id = report.get("beat_id", "?")
    ts = report.get("timestamp", "")[:19]

    lines = [f"ACE Heartbeat #{beat_id}", f"Time: {ts}", ""]

    # Key metrics
    if "environment" in steps:
        env = steps["environment"]
        lines.append(f"Env: {env.get('observations', 0)} obs, {env.get('new', 0)} new")
    if "question_engine" in steps:
        qe = steps["question_engine"]
        lines.append(f"Questions: {qe.get('generated', 0)} generated")
    if "debate" in steps:
        db = steps["debate"]
        lines.append(f"Debate: {db.get('approved', 0)} approved, {db.get('deferred', 0)} deferred")
    if "self_evolution" in steps:
        se = steps["self_evolution"]
        lines.append(f"Evolution: {se.get('processed', 0)} processed")
    if "explorer_v2" in steps:
        ex = steps["explorer_v2"]
        if ex.get("status") != "skipped":
            lines.append(f"Explorer: {ex.get('status', '?')}")

    # Check for alerts
    alerts = []
    for name, step in steps.items():
        if isinstance(step, dict) and step.get("error"):
            alerts.append(f"  {name}: {step['error'][:50]}")
    if alerts:
        lines.append("")
        lines.append("Alerts:")
        lines.extend(alerts[:3])

    text = "\n".join(lines)[:1000]  # TG message limit

    # Send
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = _json.dumps({
            "chat_id": str(chat_id),
            "text": text,
            "disable_web_page_preview": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = _json.loads(resp.read())
        if result.get("ok"):
            log.info(f"TG push sent to chat_id={chat_id}")
            return {"status": "sent", "chat_id": chat_id}
        else:
            return {"status": "failed", "result": result}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def loop(interval_min=15, log=None):
    log.info(f"Heartbeat loop started (interval={interval_min}min)")
    while True:
        beat(log)
        time.sleep(interval_min * 60)


def main():
    parser = argparse.ArgumentParser(description="ACE Heartbeat (silent by default)")
    parser.add_argument("--loop", action="store_true", help="Run as background loop")
    parser.add_argument("--interval", type=int, default=15, help="Interval in minutes")
    parser.add_argument("--verbose", action="store_true", help="Print to console")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="Log level")
    args = parser.parse_args()

    log_level = getattr(logging, args.log_level)
    log = get_logger("heartbeat", level=log_level, silent=not args.verbose)
    silence_all()

    if args.loop:
        loop(args.interval, log=log)
    else:
        result = beat(log)
        if args.verbose:
            print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()