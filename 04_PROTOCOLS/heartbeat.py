"""---
id: PROTO-001
type: protocol
title: "Heartbeat — 文明心跳循环"
status: active
source: "R2 Development"
created: 2026-07-12
confidence: 0.95
lineage:
  - OPS-005
  - OPS-004
related: [PROTO-002, PROTO-004, PROTO-005]
tags: [heartbeat, loop, core, runtime]
archaeology:
  state: original
---
"""
#!/usr/bin/env python3
"""
ACE Heartbeat - Silent background heartbeat
============================================

Default: silent (logs to file only)
  - Logs: 02_MEMORY/logs/heartbeat_YYYYMMDD.log
  - No console output unless --verbose
"""
import os, sys, json, time, argparse, logging
from typing import Optional
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
        # 过滤：跳过冷却中的问题（deferred 后 4 小时内不再辩论）
        # 过滤：辩论次数 >= 5 次的问题自动关闭（避免无限循环）
        now = datetime.now()
        eligible = []
        for q in open_qs:
            debate_count = q.get("debate_count", 0)
            last_debated = q.get("last_debated_at")
            if debate_count >= 5:
                # 辩论次数过多，自动关闭
                q["status"] = "closed"
                q["close_reason"] = "debate_limit_exceeded"
                log.warning(f"DebateRoom: {q['qid']} closed after {debate_count} debates")
                continue
            if last_debated:
                hours_since = (now - datetime.fromisoformat(last_debated)).total_seconds() / 3600
                if hours_since < 4:
                    continue  # 冷却中
            eligible.append(q)

        if eligible:
            log.info(f"DebateRoom: debating {len(eligible)} open questions ({len(open_qs)} total)")
            room = DebateRoom()
            # 每次心跳最多辩论 3 个问题，控制成本
            debate_results = room.debate_batch(eligible[:3])
            approved = [r for r in debate_results if r.get("decision") == "approved"]
            # 更新辩论计数和时间
            for result in debate_results:
                qid = result.get("qid", "")
                for q in qc.questions:
                    if q["qid"] == qid:
                        q["debate_count"] = q.get("debate_count", 0) + 1
                        q["last_debated_at"] = now.isoformat()
                        break
            qc._save_all()
            report["steps"]["multi_agent_debate"] = {
                "debated": len(debate_results),
                "approved": len(approved),
                "deferred": len([r for r in debate_results if r.get("decision") == "deferred"]),
                "rejected": len([r for r in debate_results if r.get("decision") == "rejected"]),
            }
            log.info(f"DebateRoom: {len(approved)} approved, {len(debate_results) - len(approved)} not approved")
        else:
            report["steps"]["multi_agent_debate"] = {"status": "skipped", "reason": "no eligible questions (all in cooldown or closed)"}
            log.info("DebateRoom: skipped (no eligible questions)")
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
            skipped = [r for r in evo_results if r.get("status") == "skipped"]
            report["steps"]["self_evolution"] = {
                "processed": len(evo_results),
                "skipped": len(skipped),
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

    # GOV-001: RoundTable Debate — 红蓝对抗辩论
    try:
        from roundtable import debate_open_questions
        debate_result = debate_open_questions(priority="P1", max_debates=5)
        if "error" not in debate_result:
            total = debate_result.get("total_debated", 0)
            approved = sum(1 for r in debate_result.get("results", []) if r.get("verdict") == "approved")
            rejected = sum(1 for r in debate_result.get("results", []) if r.get("verdict") == "rejected")
            pending = sum(1 for r in debate_result.get("results", []) if r.get("verdict") == "pending")
            report["steps"]["debate"] = {
                "total_debated": total,
                "approved": approved,
                "rejected": rejected,
                "pending": pending,
                "priority_threshold": debate_result.get("priority_threshold", "P1"),
            }
            log.info(f"Debate: {total} debated ({approved} approved, {rejected} rejected, {pending} pending)")
        else:
            report["steps"]["debate"] = {"error": debate_result["error"]}
    except Exception as e:
        report["steps"]["debate"] = {"error": str(e)}
        log.error(f"Debate error: {e}")

    # SLE-001: Self-Learning Engine — 从经验中自动学习
    try:
        from self_learning_engine import SelfLearningEngine
        sle = SelfLearningEngine()
        learn_result = sle.run_learning_cycle()
        m = learn_result["metrics"]
        report["steps"]["self_learning"] = {
            "experiences": m["total_experiences"],
            "seeded": learn_result.get("seed_results", {}).get("total_seeded", 0),
            "failure_patterns": learn_result["patterns"]["failure_patterns_detected"],
            "success_patterns": learn_result["patterns"]["success_patterns_detected"],
            "hypotheses": learn_result["hypotheses"]["total_generated"],
            "questions_pushed": learn_result["hypotheses"].get("pushed_to_question_center", 0),
            "experiments_recommended": learn_result["experiments"]["recommended"],
            "experiments_auto_executed": learn_result["experiments"]["auto_executed"],
        }
        seeded = learn_result.get("seed_results", {}).get("total_seeded", 0)
        log.info(f"SelfLearning: {m['total_experiences']} exps (+{seeded}), {learn_result['hypotheses']['total_generated']} hypotheses, {learn_result['hypotheses'].get('pushed_to_question_center', 0)} pushed")
    except Exception as e:
        report["steps"]["self_learning"] = {"error": str(e)}
        log.error(f"SelfLearning error: {e}")

    # MISSION-001: Mission Protocol — 文明任务监控
    try:
        from mission_protocol import protocol
        summary = protocol.get_summary()
        active_missions = protocol.list_active()
        report["steps"]["missions"] = {
            "total": summary["total"],
            "active": summary["active"],
            "by_status": summary["by_status"],
            "active_list": [
                {"mid": m.mid, "name": m.name, "priority": m.priority, "status": m.status}
                for m in active_missions
            ],
        }
        log.info(f"Missions: {summary['active']} active / {summary['total']} total")
    except Exception as e:
        report["steps"]["missions"] = {"error": str(e)}
        log.error(f"Missions error: {e}")

    # DFP-001: Drawer First Protocol — 抽屉扫描检查
    try:
        from mission_protocol import protocol
        all_missions = protocol.list_all()
        missing_drawer = [m.mid for m in all_missions if m.status == "ACTIVE" and not m.drawer_scan_done]
        report["steps"]["drawer_scan"] = {
            "active_missions": len(all_missions),
            "missing_drawer_scan": len(missing_drawer),
            "drawer_scan_required": missing_drawer,
        }
        if missing_drawer:
            log.warning(f"DFP: {len(missing_drawer)} active missions missing drawer scan: {missing_drawer}")
        else:
            log.info("DFP: All active missions have completed drawer scan")
    except Exception as e:
        report["steps"]["drawer_scan"] = {"error": str(e)}
        log.error(f"DrawerScan error: {e}")

    # REPO-001: Civilization Repository — 文明仓库监控
    try:
        from repository import Repository
        from repository_store import RepositoryStore
        repo = Repository()
        store = RepositoryStore(repo)
        store.load()
        stats = repo.stats()
        report["steps"]["civ_repo"] = {
            "total_assets": stats["total"],
            "by_type": stats["by_type"],
            "active": stats["active"],
        }
        log.info(f"CivRepo: {stats['total']} assets total")
    except Exception as e:
        report["steps"]["civ_repo"] = {"error": str(e)}
        log.error(f"CivRepo error: {e}")

    # IDENT-001: Identity Core check
    try:
        from identity_core import identity
        ident = identity.get_full_identity()
        report["steps"]["identity"] = {
            "name": ident["civilizational"]["name"],
            "version": ident["operational"]["version"],
            "personas": len(ident["personas"]),
            "capabilities": len(ident["operational"]["capabilities"]),
        }
    except Exception as e:
        report["steps"]["identity"] = {"error": str(e)}
        log.error(f"Identity error: {e}")

    # CONTINUITY-001: Continuity Engine — 统一连续性检查
    # (ARCH-012: 将分散在 heartbeat 中的连续性检查整合为独立模块)
    try:
        from continuity_engine import ContinuityEngine
        ce = ContinuityEngine()
        continuity_report = ce.run_all_checks()

        # 将各检查结果映射到 report["steps"]
        for check_id, check_result in continuity_report["checks"].items():
            report["steps"][check_id] = check_result

            # 日志输出
            status = check_result.get("status", "unknown")
            name = check_result.get("name", check_id)
            if status in ("error", "alert"):
                log.warning(f"Continuity[{name}]: {status}")
            else:
                log.info(f"Continuity[{name}]: {status}")

        report["steps"]["continuity_summary"] = {
            "total": continuity_report["total_checks"],
            "ok": continuity_report["ok"],
            "errors": continuity_report["errors"],
        }
    except Exception as e:
        report["steps"]["continuity"] = {"error": str(e)}
        log.error(f"ContinuityEngine error: {e}")

    # CONSTRAINT-001: Three Unloseable Constraints Validation
    # (ARCH-013: Automated validation of Continuity/L∞/Admission constraints)
    try:
        from constraint_validator import ConstraintValidator
        cv = ConstraintValidator()
        constraint_report = cv.validate_all()

        # 将各约束结果映射到 report["steps"]
        for constraint_id, constraint_result in constraint_report["constraints"].items():
            report["steps"][f"constraint_{constraint_id}"] = constraint_result

            # 日志输出
            status = constraint_result.get("status", "unknown")
            severity = constraint_result.get("severity", "unknown")
            name = constraint_result.get("name", constraint_id)
            if severity in ("critical", "high"):
                log.critical(f"Constraint[{name}]: {status} — {constraint_result.get('message', '')}")
            elif severity == "medium":
                log.warning(f"Constraint[{name}]: {status}")
            else:
                log.info(f"Constraint[{name}]: {status}")

        report["steps"]["constraint_summary"] = {
            "overall_status": constraint_report["overall_status"],
            "overall_severity": constraint_report["overall_severity"],
            "total": constraint_report["total_constraints"],
            "satisfied": constraint_report["satisfied"],
            "violated": constraint_report["violated"],
            "errors": constraint_report["errors"],
        }
    except Exception as e:
        report["steps"]["constraints"] = {"error": str(e)}
        log.error(f"ConstraintValidator error: {e}")

    # AUTO-001: Autophagy — 良性自噬（轻度，每次心跳）
    # NOTE: autophagy_engine.py 当前不存在，保留错误处理作为模块缺失记录
    try:
        from autophagy_engine import AutophagyEngine
        auto = AutophagyEngine()
        light_result = auto.run_light()
        report["steps"]["autophagy"] = {
            "items_cleaned": light_result["items_cleaned"],
            "kb_saved": light_result["kb_saved"],
            "level": "light",
        }
        log.info(f"Autophagy: {light_result['items_cleaned']} items, {light_result['kb_saved']} KB saved")
    except Exception as e:
        report["steps"]["autophagy"] = {"error": str(e)}
        log.error(f"Autophagy error: {e}")

    # Worker Health Check
    try:
        from worker_registry import WorkerRegistry
        registry = WorkerRegistry()
        ws = registry.summary()
        unhealthy = [w for w in registry.list_all() if w.get("health", 1.0) < 0.7]
        report["steps"]["worker_health"] = {
            "total": ws["total"],
            "active": ws["active"],
            "avg_health": round(ws["avg_health"], 2),
            "capabilities": ws["total_capabilities"],
            "unhealthy": len(unhealthy),
        }
        log.info(f"Worker Health: {ws['active']}/{ws['total']} active, avg_health={ws['avg_health']:.2f}")
    except Exception as e:
        report["steps"]["worker_health"] = {"error": str(e)}
        log.error(f"WorkerHealth error: {e}")

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

    # Advisor Review — 荐股复核 (T+1/T+7/T+15/T+30) + 胜率统计
    try:
        review_result = _run_advisor_review(log)
        report["steps"]["advisor_review"] = review_result
    except Exception as e:
        report["steps"]["advisor_review"] = {"status": "error", "error": str(e)}
        log.error(f"Advisor review error: {e}")

    # Civilization Audit — 每周一次（周一运行）
    try:
        today = datetime.now()
        if today.weekday() == 0:  # Monday
            from civilization_auditor import CivilizationAuditor
            auditor = CivilizationAuditor()
            audit_report = auditor.run_all()
            report["steps"]["civilization_audit"] = {
                "status": "completed",
                "health_score": audit_report["stats"]["health_score"],
                "duplicates": audit_report["stats"]["duplicate_clusters"],
                "zombies": audit_report["stats"]["zombie_files"],
                "missing_links": audit_report["stats"]["missing_links"],
            }
            log.info(f"Civilization audit: health={audit_report['stats']['health_score']}/100")
        else:
            report["steps"]["civilization_audit"] = {"status": "skipped", "reason": "not Monday"}
    except Exception as e:
        report["steps"]["civilization_audit"] = {"status": "error", "error": str(e)}
        log.error(f"Civilization audit error: {e}")

    # Civilization Diary — 每日生成 Yesterday Report
    try:
        diary = _generate_yesterday_report(log)
        report["steps"]["civilization_diary"] = diary
        if diary.get("status") == "generated":
            log.info(f"Civilization Diary: {diary['date']}, {diary.get('discoveries', 0)} discoveries")
    except Exception as e:
        report["steps"]["civilization_diary"] = {"status": "error", "error": str(e)}
        log.error(f"Civilization Diary error: {e}")

    # Save
    mm.save_memory("heartbeat", f"beat_{beat_id}", report)
    log.info("Heartbeat saved")
    return report


def _push_heartbeat_summary(report: dict, log) -> dict:
    """Push heartbeat summary + stock advisor to TG via Bot.

    静默原则：只有重要事情才推送，普通心跳不打扰。
    推送条件（满足任一）：
      - 有告警/错误
      - 有新问题生成（question_engine 创建了新问题）
      - 自我演化处理了决策（processed > 0）
      - 多智能体辩论有结果（debated > 0）
      - Explorer 有新探索发现
      - 新的 Awareness Loop 经验沉淀
      - 每周一的 Civilization Audit
    """
    from pathlib import Path
    from datetime import datetime

    # Load credentials
    env_file = Path(__file__).parent.parent / "05_TOOLS" / "miner" / "miner_env.sh"
    token = None
    chat_id = None
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "export TG_BOT_TOKEN_2=" in line:
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif "export TG_CHAT_ID=" in line:
                chat_id = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not token:
        return {"status": "skipped", "reason": "no TG_BOT_TOKEN_2"}

    # Get chat_id from getUpdates if not in env
    if not chat_id:
        chat_id = _get_chat_id(token)
        if not chat_id:
            return {"status": "skipped", "reason": "no chat_id"}

    # Import TGPusher
    sys.path.insert(0, str(Path(__file__).parent.parent / "06_RUNTIME" / "connectors"))
    from tg_pusher import TGPusher

    pusher = TGPusher(token=token, chat_id=chat_id)
    results = []

    # 判断：这次心跳是否值得推送
    steps = report.get("steps", {})
    should_push = _should_push_heartbeat(steps)

    if should_push:
        summary_html = _build_heartbeat_html(report)
        msg_result = pusher.send_message(summary_html, parse_mode="HTML")
        if msg_result.get("ok"):
            results.append({"type": "heartbeat", "status": "sent"})
            log.info(f"TG heartbeat sent (important)")
        else:
            results.append({"type": "heartbeat", "status": "failed", "error": msg_result.get("description")})
            log.error(f"TG heartbeat failed: {msg_result.get('description')}")
    else:
        results.append({"type": "heartbeat", "status": "silent", "reason": "nothing important to report"})
        log.info(f"TG heartbeat: silent (nothing important)")

    # Push today's stock advisor report (if exists and not pushed today)
    advisor_result = _push_today_advisor(pusher, log)
    if advisor_result:
        results.append(advisor_result)

    return {"status": "completed", "results": results, "chat_id": chat_id}


def _should_push_heartbeat(steps: dict) -> bool:
    """判断这次心跳是否值得推送。

    推送条件（满足任一即推）：
      1. 有错误/告警
      2. 生成了新问题
      3. 多智能体辩论有结果
      4. 自我演化处理了决策
      5. Explorer 有新探索
      6. Awareness Loop 沉淀了新经验
      7. Civilization Audit 完成了
    """
    # 1. 错误
    for name, step in steps.items():
        if isinstance(step, dict) and step.get("error"):
            return True

    # 2. 新问题
    qe = steps.get("question_engine", {})
    if isinstance(qe, dict) and qe.get("created", 0) > 0:
        return True

    # 3. 辩论有结果
    debate = steps.get("multi_agent_debate", {})
    if isinstance(debate, dict) and debate.get("debated", 0) > 0:
        return True

    # 4. 自我演化处理了决策
    se = steps.get("self_evolution", {})
    if isinstance(se, dict) and se.get("processed", 0) > 0:
        return True

    # 5. Explorer 有新探索
    ex = steps.get("explorer_v2", {})
    if isinstance(ex, dict) and ex.get("status") not in ("skipped", None):
        return True

    # 6. Awareness Loop 有新经验
    al = steps.get("awareness_loop", {})
    if isinstance(al, dict) and al.get("reports_saved", 0) > 0:
        return True

    # 7. Civilization Audit
    ca = steps.get("civilization_audit", {})
    if isinstance(ca, dict) and ca.get("status") == "completed":
        return True

    return False


def _get_chat_id(token: str) -> Optional[str]:
    """Get chat_id from Telegram Bot getUpdates."""
    import urllib.request, json
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates?limit=5"
        resp = urllib.request.urlopen(url, timeout=10)
        data = json.loads(resp.read())
        for u in data.get("result", []):
            if "message" in u:
                return str(u["message"]["chat"]["id"])
            if "channel_post" in u:
                return str(u["channel_post"]["chat"]["id"])
        return None
    except Exception:
        return None


def _build_heartbeat_html(report: dict) -> str:
    """Build Chinese HTML summary for TG."""
    from tg_pusher import TGPusher
    p = TGPusher

    steps = report.get("steps", {})
    beat_id = report.get("beat_id", "?")
    ts = report.get("timestamp", "")[:19]

    parts = [
        p._bold(f"ACE Heartbeat #{beat_id}"),
        p._italic(f"时间: {ts}"),
        "",
    ]

    if "environment" in steps:
        env = steps["environment"]
        parts.append(f"环境观测: {env.get('observations', 0)} 条, 新增 {env.get('new', 0)} 条")
    if "question_engine" in steps:
        qe = steps["question_engine"]
        parts.append(f"问题生成: {qe.get('generated', 0)} 个")
    if "debate" in steps:
        db = steps["debate"]
        if "error" not in db:
            total = db.get("total_debated", 0)
            approved = db.get("approved", 0)
            rejected = db.get("rejected", 0)
            pending = db.get("pending", 0)
            if total > 0:
                parts.append(f"红蓝辩论: {total}场 (✅{approved} ❌{rejected} ⏳{pending})")
        else:
            parts.append(f"红蓝辩论: 异常 ({db.get('error', '')[:20]})")
    if "self_evolution" in steps:
        se = steps["self_evolution"]
        if se.get("status") == "skipped":
            parts.append(f"自我演化: 跳过 ({se.get('reason', '')})")
        else:
            processed = se.get("processed", 0)
            skipped = se.get("skipped", 0)
            new_processed = processed - skipped
            if new_processed > 0:
                parts.append(f"自我演化: 新处理 {new_processed} 个, 跳过 {skipped} 个")
            else:
                parts.append(f"自我演化: 跳过 {skipped} 个 (已处理)")
    if "self_learning" in steps:
        sl = steps["self_learning"]
        if "error" not in sl:
            exps = sl.get("experiences", 0)
            seeded = sl.get("seeded", 0)
            hypos = sl.get("hypotheses", 0)
            pushed = sl.get("questions_pushed", 0)
            patterns = sl.get("failure_patterns", 0) + sl.get("success_patterns", 0)
            seed_str = f" (+{seeded})" if seeded > 0 else ""
            push_str = f", 推送{pushed}问" if pushed > 0 else ""
            parts.append(f"自学习: {exps}{seed_str} 经验, {patterns} 模式, {hypos} 假设{push_str}")
        else:
            parts.append(f"自学习: 异常 ({sl.get('error', '')[:30]})")
    if "missions" in steps:
        ms = steps["missions"]
        if "error" not in ms:
            active = ms.get("active", 0)
            total = ms.get("total", 0)
            active_list = ms.get("active_list", [])
            if active > 0:
                top = active_list[0] if active_list else None
                top_str = f" → {top['mid']}" if top else ""
                parts.append(f"任务: {active}/{total} 进行中{top_str}")
            else:
                parts.append(f"任务: {total} 个, 无活跃")
        else:
            parts.append(f"任务: 异常 ({ms.get('error', '')[:20]})")
    if "civ_repo" in steps:
        cr = steps["civ_repo"]
        if "error" not in cr:
            total = cr.get("total_assets", 0)
            by_type = cr.get("by_type", {})
            # 只显示有资产的类型
            has_types = [k for k, v in by_type.items() if v > 0]
            if has_types:
                type_str = ", ".join(f"{k[:3]}_{v}" for k, v in by_type.items() if v > 0)
                parts.append(f"文明: {total} 资产 ({type_str})")
            else:
                parts.append(f"文明: 空仓库")
        else:
            parts.append(f"文明: 异常 ({cr.get('error', '')[:20]})")
    if "autophagy" in steps:
        au = steps["autophagy"]
        if "error" not in au:
            items = au.get("items_cleaned", 0)
            kb = au.get("kb_saved", 0)
            if items > 0:
                parts.append(f"自噬: 清{items}项, 省{kb:.0f}KB")
        else:
            parts.append(f"自噬: 异常 ({au.get('error', '')[:20]})")
    if "nature_reserve" in steps:
        nr = steps["nature_reserve"]
        if "error" not in nr:
            status = nr.get("status", "?")
            if status == "alert":
                parts.append(f"保留区: ⚠️ 篡改{nr.get('tampered', 0)} 缺失{nr.get('missing', 0)}")
            elif status == "clean":
                parts.append(f"保留区: {nr.get('intact', 0)}/{nr.get('total', 0)} 完整")
        else:
            parts.append(f"保留区: 异常 ({nr.get('error', '')[:20]})")
    if "gene_network" in steps:
        gn = steps["gene_network"]
        if "error" not in gn:
            parts.append(f"基因网络: {gn.get('total_genes', 0)}基因, {gn.get('total_dependencies', 0)}依赖")
    if "energy_budget" in steps:
        eb = steps["energy_budget"]
        if "error" not in eb:
            level = eb.get("level", "?")
            level_emoji = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴"}
            parts.append(f"能量: {level_emoji.get(level, '?')}{level}")
    if "seed_archive" in steps:
        sa = steps["seed_archive"]
        if "error" not in sa:
            action = sa.get("action", "")
            if action == "created":
                parts.append(f"基因备份: {sa.get('seed_id', '?')} ({sa.get('size_kb', 0)}KB)")
    if "worker_health" in steps:
        wh = steps["worker_health"]
        if "error" not in wh:
            parts.append(
                f"Worker健康: {wh.get('active', 0)}/{wh.get('total', 0)} 活跃, "
                f"健康度 {wh.get('avg_health', 0):.2f}"
            )
    if "explorer_v2" in steps:
        ex = steps["explorer_v2"]
        if ex.get("status") != "skipped":
            parts.append(f"探索者: {ex.get('status', '?')}")

    alerts = []
    for name, step in steps.items():
        if isinstance(step, dict) and step.get("error"):
            alerts.append(f"• {p._bold(name)}: {step['error'][:50]}")
    if alerts:
        parts.append("")
        parts.append(p._bold("⚠️ 告警:"))
        parts.extend(alerts[:3])

    return "\n".join(parts)[:3800]


def _push_today_advisor(pusher, log) -> Optional[dict]:
    """Push today's stock advisor report if not already pushed.

    非交易日跳过荐股推送（法定节日 + 周末）。
    """
    from datetime import datetime, date
    from pathlib import Path

    # 检查是否为交易日
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "05_TOOLS" / "advisor"))
        from trading_calendar import is_trading_day
        if not is_trading_day():
            return {"type": "advisor", "status": "skipped", "reason": "非交易日（周末/节假日）"}
    except ImportError:
        pass  # 模块不存在时 fallback 到原逻辑

    today = datetime.now().strftime("%Y%m%d")
    advisor_dir = Path(__file__).parent.parent / "05_TOOLS" / "mine_output" / "advisor"
    report_path = advisor_dir / f"advisor_{today}.md"

    if not report_path.exists():
        return {"type": "advisor", "status": "skipped", "reason": "no report today"}

    # Check if already pushed today
    pushed_dir = Path(__file__).parent.parent / "02_MEMORY" / "recovery"
    pushed_file = pushed_dir / f"advisor_pushed_{today}.flag"
    if pushed_file.exists():
        return {"type": "advisor", "status": "skipped", "reason": "already pushed today"}

    # Push report
    result = pusher.send_report(str(report_path))
    if result.get("ok"):
        pushed_file.write_text("pushed", encoding="utf-8")
        log.info(f"TG advisor report sent")
        return {"type": "advisor", "status": "sent"}
    else:
        log.error(f"TG advisor failed: {result.get('error')}")
        return {"type": "advisor", "status": "failed", "error": result.get("error")}


def _run_advisor_review(log) -> dict:
    """运行荐股复核 — T+1/T+7/T+15/T+30 收盘价对比 + 胜率统计

    每个交易日收盘后自动复核到期的荐股记录。
    """
    from pathlib import Path

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "05_TOOLS" / "advisor"))
        from advisor_tracker import AdvisorTracker

        tracker = AdvisorTracker()
        tracker.sync_records()
        result = tracker.review_pending()
        report = tracker.generate_win_rate_report()

        reviewed = len(result.get("reviewed", []))
        skipped = len(result.get("skipped", []))
        log.info(f"Advisor review: {reviewed} reviewed, {skipped} skipped")

        # 如果有新复核结果，推送胜率摘要
        if reviewed > 0:
            win_rate_summary = _build_win_rate_summary(report)
            if win_rate_summary:
                # 加载 TG pusher
                env_file = Path(__file__).parent.parent / "05_TOOLS" / "miner" / "miner_env.sh"
                token = None
                chat_id = None
                if env_file.exists():
                    for line in env_file.read_text(encoding="utf-8").splitlines():
                        if "export TG_BOT_TOKEN_2=" in line:
                            token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        elif "export TG_CHAT_ID=" in line:
                            chat_id = line.split("=", 1)[1].strip().strip('"').strip("'")
                if token and not chat_id:
                    chat_id = _get_chat_id(token)
                if token and chat_id:
                    sys.path.insert(0, str(Path(__file__).parent.parent / "06_RUNTIME" / "connectors"))
                    from tg_pusher import TGPusher
                    pusher = TGPusher(token=token, chat_id=chat_id)
                    pusher.send_message(win_rate_summary, parse_mode="HTML")
                    log.info(f"Win rate summary pushed to TG")

        return {
            "status": "completed",
            "reviewed": reviewed,
            "skipped": skipped,
            "total_records": report.get("total_records", 0),
        }
    except Exception as e:
        log.error(f"Advisor review error: {e}")
        return {"status": "error", "error": str(e)}


def _build_win_rate_summary(report: dict) -> Optional[str]:
    """构建胜率摘要 HTML 消息"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "06_RUNTIME" / "connectors"))
        from tg_pusher import TGPusher
        p = TGPusher
    except ImportError:
        return None

    lines = [
        p._bold("📊 荐股胜率报告"),
        p._italic(f"总荐股数: {report.get('total_records', 0)}"),
        "",
    ]

    periods = report.get("periods", {})
    has_data = False
    for period_name in ["T+1", "T+7", "T+15", "T+30"]:
        p_data = periods.get(period_name, {})
        total = p_data.get("total", 0)
        if total > 0:
            has_data = True
            wins = p_data.get("wins", 0)
            win_rate = p_data.get("win_rate", 0)
            avg_ret = p_data.get("avg_return", 0)
            lines.append(
                f"{p._bold(period_name)}: {wins}/{total} 胜率 {win_rate}% "
                f"(平均 {avg_ret:+.2f}%)"
            )

    if not has_data:
        return None

    return "\n".join(lines)[:3800]


def loop(interval_min=15, log=None):
    log.info(f"Heartbeat loop started (interval={interval_min}min)")
    while True:
        beat(log)
        time.sleep(interval_min * 60)


def _generate_yesterday_report(log) -> dict:
    """生成文明日志（Yesterday Report）

    内容：
      - 昨天系统发现了什么？
      - 系统学到了什么？
      - 哪些东西一直重复发生？
      - 哪些东西值得今天继续研究？

    数据源：
      - Heartbeat 记录（昨天的心跳）
      - Question Center（新问题/决策）
      - Experience（新经验）
      - Explorer（新发现）
    """
    from datetime import datetime, timedelta
    from pathlib import Path
    import json

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")

    beat_dir = WORKSPACE / "02_MEMORY" / "heartbeat"
    yesterday_beats = []
    for bf in sorted(beat_dir.glob("beat_*.json")):
        try:
            beat_time = datetime.strptime(bf.stem.replace("beat_", ""), "%Y%m%dT%H%M%S")
            if yesterday.date() == beat_time.date():
                data = json.loads(bf.read_text(encoding="utf-8"))
                yesterday_beats.append(data)
        except Exception:
            pass

    if not yesterday_beats:
        return {"status": "skipped", "reason": "no heartbeat data for yesterday", "date": date_str}

    discoveries = []
    learnings = []
    repetitions = []
    follow_ups = []

    for beat in yesterday_beats:
        steps = beat.get("steps", {})

        qe = steps.get("question_engine", {})
        if isinstance(qe, dict) and qe.get("created", 0) > 0:
            discoveries.append(f"生成了 {qe['created']} 个新问题")

        debate = steps.get("multi_agent_debate", {})
        if isinstance(debate, dict):
            debated = debate.get("debated", 0)
            approved = debate.get("approved", 0)
            if debated > 0:
                learnings.append(f"辩论了 {debated} 个问题，{approved} 个通过")

        se = steps.get("self_evolution", {})
        if isinstance(se, dict):
            evolved = se.get("evolved", 0)
            deferred = se.get("deferred", 0)
            if evolved > 0:
                learnings.append(f"自我演化了 {evolved} 个决策")
            if deferred > 0:
                follow_ups.append(f"{deferred} 个决策需要人工干预")

        ex = steps.get("explorer_v2", {})
        if isinstance(ex, dict) and ex.get("status") not in ("skipped", None):
            discoveries.append(f"Explorer 探索了新领域")

        al = steps.get("awareness_loop", {})
        if isinstance(al, dict) and al.get("reports_saved", 0) > 0:
            learnings.append(f"沉淀了 {al['reports_saved']} 条新经验")

        for name, step in steps.items():
            if isinstance(step, dict) and step.get("error"):
                repetitions.append(f"{name} 出错: {step['error'][:30]}")

    qc_dir = WORKSPACE / "02_MEMORY" / "question_center"
    new_questions = []
    try:
        if (qc_dir / "questions.json").exists():
            questions = json.loads((qc_dir / "questions.json").read_text(encoding="utf-8"))
            for q in questions:
                if q.get("created_at"):
                    try:
                        ct = datetime.fromisoformat(q["created_at"].replace("Z", "+00:00"))
                        if ct.date() == yesterday.date():
                            new_questions.append(q["question"][:50])
                    except Exception:
                        pass
    except Exception:
        pass

    if new_questions:
        discoveries.extend(new_questions)

    diary = {
        "status": "generated",
        "date": date_str,
        "discoveries": len(discoveries),
        "learnings": len(learnings),
        "repetitions": len(repetitions),
        "follow_ups": len(follow_ups),
        "items": {
            "discoveries": discoveries[:10],
            "learnings": learnings[:10],
            "repetitions": repetitions[:5],
            "follow_ups": follow_ups[:5],
        },
    }

    diary_path = WORKSPACE / "02_MEMORY" / "diary"
    diary_path.mkdir(exist_ok=True)
    diary_file = diary_path / f"diary_{date_str}.json"
    diary_file.write_text(json.dumps(diary, ensure_ascii=False, indent=2), encoding="utf-8")

    return diary


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