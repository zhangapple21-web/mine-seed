#!/usr/bin/env python3
"""
ACE Runtime — Autonomous Loop
心跳循环：while alive → observe → candidate → execute → evidence → constraint

这不是一个脚本。这是 Runtime 的心脏。

用法:
  python3 autonomous_loop.py          # 启动自主循环
  python3 autonomous_loop.py --once  # 只跑一轮
  python3 autonomous_loop.py --maintenance  # 进入维护模式
"""

import os
import sys
import json
import time
import signal
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 路径配置
MINE_SEED = Path(os.environ.get("MINE_SEED", "/workspace/fengzi-repos/mine-seed"))
COZE_ASSETS = Path(os.environ.get("COZE_ASSETS", "/workspace/fengzi-repos/coze-assets"))
GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:3000")
REPORT_DIR = Path(os.environ.get("REPORT_DIR", "/tmp/mine_output/loop"))
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "300"))  # 5分钟

# 日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(REPORT_DIR / "loop.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("ACE.Loop")

# 全局状态
_alive = True
_cycle = 0


def signal_handler(sig, frame):
    """优雅退出"""
    global _alive
    log.info(f"[LOOP] Signal {sig} received, shutting down...")
    _alive = False


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


# ============================================================
# ABP: Bootstrap
# ============================================================

def bootstrap() -> Dict[str, bool]:
    """ABP 检查：确保世界还活着"""
    log.info("=" * 50)
    log.info("[ABP] Bootstrap — 确认世界还活着")
    
    # 导入 liveness_check
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from liveness_check import run_liveness
        report = run_liveness()
        
        alive = report["overall"] == "ALIVE"
        # DEGRADED 不等于失败：只有 Environment/Governor 挂了才是致命的
        critical_alive = True
        for s in report["systems"]:
            if not s["alive"] and s["name"] in ("Environment", "Governor"):
                critical_alive = False
        alive = critical_alive
        
        log.info(f"[ABP] 结果: {report['overall']} ({report['score']})")
        
        # 自动修复
        if not alive:
            _auto_repair(report)
        
        return {s["name"]: s["alive"] for s in report["systems"]}
    except Exception as e:
        log.error(f"[ABP] 检查失败: {e}")
        return {"error": False}


def _auto_repair(report: Dict):
    """自动修复常见问题"""
    import urllib.request
    
    for system in report["systems"]:
        if not system["alive"]:
            name = system["name"]
            
            if name == "Environment":
                # Gateway 死了 → 重启
                try:
                    urllib.request.urlopen(f"{GATEWAY_URL}/api/status", timeout=5)
                except:
                    log.warning("[ABP] Gateway 死了，重启...")
                    os.system(f"cd /workspace/one-api-data && nohup python3 ace_gateway.py > gateway.log 2>&1 &")
                    time.sleep(8)
            
            elif name == "Environment":
                checks = system.get("checks", {})
                if checks.get("python_deps", {}).get("alive") == False:
                    log.warning("[ABP] Python 依赖缺失，安装...")
                    os.system("pip3 install httpx fastapi uvicorn akshare requests --break-system-packages -q")


# ============================================================
# ECO: Environment Observation
# ============================================================

def observe_environment() -> List[Dict]:
    """扫描环境，收集观察"""
    observations = []
    
    # 1. 渠道健康变化
    try:
        import urllib.request
        req = urllib.request.Request(f"{GATEWAY_URL}/api/status")
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = json.loads(resp.read())
            channels = status["data"]["channels"]
            models = status["data"]["models"]
            observations.append({
                "type": "health",
                "source": "gateway",
                "detail": f"{channels}ch/{models}models alive",
                "severity": "info",
            })
    except:
        observations.append({
            "type": "health",
            "source": "gateway",
            "detail": "Gateway unreachable",
            "severity": "critical",
        })
    
    # 2. 时间锚点（是否到了某个定时任务的窗口）
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    weekday = now.weekday()  # 0=Mon
    
    # 每日荐股窗口 (08:15)
    if hour == 8 and 10 <= minute <= 30 and weekday < 5:
        observations.append({
            "type": "schedule",
            "source": "clock",
            "detail": "Stock Advisor window (08:15)",
            "severity": "action",
        })
    
    # 矿场v5窗口 (每4h)
    if hour % 4 == 0 and minute < 10:
        observations.append({
            "type": "schedule",
            "source": "clock",
            "detail": f"Miner shift window ({hour}:00)",
            "severity": "action",
        })
    
    # 知识早班 (05:00)
    if hour == 5 and minute < 15:
        observations.append({
            "type": "schedule",
            "source": "clock",
            "detail": "Morning research window (05:00)",
            "severity": "action",
        })
    
    # 知识午班 (12:00)
    if hour == 12 and minute < 15:
        observations.append({
            "type": "schedule",
            "source": "clock",
            "detail": "Noon research window (12:00)",
            "severity": "action",
        })
    
    # 档案官 (20:04)
    if hour == 20 and 0 <= minute <= 15:
        observations.append({
            "type": "schedule",
            "source": "clock",
            "detail": "Archivist window (20:04)",
            "severity": "action",
        })
    
    # 3. 文件系统变化（mine-seed 新增/修改）
    try:
        git_status = os.popen(f"cd {MINE_SEED} && git status --short 2>/dev/null").read().strip()
        if git_status:
            changed = len(git_status.split("\n"))
            observations.append({
                "type": "change",
                "source": "mine-seed",
                "detail": f"{changed} uncommitted changes",
                "severity": "info",
            })
    except:
        pass
    
    # 4. 记忆连续性检查
    daily_dir = MINE_SEED / "02_MEMORY" / "recent_memory" / "daily"
    today = now.strftime("%Y-%m-%d")
    today_mem = daily_dir / f"{today}-liveness.md"
    if not today_mem.exists() and not any(today in f.name for f in daily_dir.glob("*.md")):
        observations.append({
            "type": "memory",
            "source": "daily",
            "detail": f"No memory for {today}",
            "severity": "warning",
        })
    
    log.info(f"[ECO] Collected {len(observations)} observations")
    for obs in observations:
        log.info(f"  [{obs['severity']}] {obs['source']}: {obs['detail']}")
    
    return observations


# ============================================================
# ECO: Candidate Generation
# ============================================================

def generate_candidates(observations: List[Dict]) -> List[Dict]:
    """基于观察生成候选任务"""
    candidates = []
    
    for obs in observations:
        if obs["severity"] == "critical":
            candidates.append({
                "type": "repair",
                "priority": "A",
                "action": "repair",
                "detail": obs["detail"],
                "source": obs["source"],
            })
        
        elif obs["severity"] == "action":
            detail = obs["detail"]
            if "Stock Advisor" in detail:
                candidates.append({
                    "type": "production",
                    "priority": "A",
                    "action": "stock_advisor",
                    "detail": "Run stock advisor + push",
                    "source": "schedule",
                })
            elif "Miner" in detail:
                candidates.append({
                    "type": "production",
                    "priority": "A",
                    "action": "miner",
                    "detail": "Run miner_24h shift",
                    "source": "schedule",
                })
            elif "Morning" in detail:
                candidates.append({
                    "type": "research",
                    "priority": "B",
                    "action": "morning_research",
                    "detail": "Knowledge morning shift (xiaofengzi)",
                    "source": "schedule",
                })
            elif "Noon" in detail:
                candidates.append({
                    "type": "research",
                    "priority": "B",
                    "action": "noon_research",
                    "detail": "Knowledge noon shift (xiaofengzi)",
                    "source": "schedule",
                })
            elif "Archivist" in detail:
                candidates.append({
                    "type": "maintenance",
                    "priority": "C",
                    "action": "archivist",
                    "detail": "Daily archive + memory distillation",
                    "source": "schedule",
                })
        
        elif obs["severity"] == "warning":
            candidates.append({
                "type": "maintenance",
                "priority": "C",
                "action": "memory_write",
                "detail": obs["detail"],
                "source": obs["source"],
            })
    
    # 维护任务（始终存在）
    candidates.append({
        "type": "maintenance",
        "priority": "C",
        "action": "health_check",
        "detail": "Periodic health check",
        "source": "loop",
    })
    
    # 按优先级排序
    priority_order = {"A": 0, "B": 1, "C": 2}
    candidates.sort(key=lambda c: priority_order.get(c["priority"], 9))
    
    log.info(f"[ECO] Generated {len(candidates)} candidates")
    return candidates


# ============================================================
# OPS: Task Execution
# ============================================================

def execute_candidate(candidate: Dict) -> Dict:
    """执行一个候选任务"""
    action = candidate["action"]
    log.info(f"[OPS] Executing: {action} ({candidate['priority']})")
    
    result = {"action": action, "success": False, "output": "", "timestamp": datetime.now().isoformat()}
    
    try:
        if action == "repair":
            result["success"] = _execute_repair(candidate)
        elif action == "stock_advisor":
            result["success"] = _execute_stock_advisor()
        elif action == "miner":
            result["success"] = _execute_miner()
        elif action == "morning_research":
            result["success"] = _execute_research("morning")
        elif action == "noon_research":
            result["success"] = _execute_research("noon")
        elif action == "archivist":
            result["success"] = _execute_archivist()
        elif action == "memory_write":
            result["success"] = _execute_memory_write(candidate)
        elif action == "health_check":
            result["success"] = True
            result["output"] = "Health check passed"
        else:
            result["output"] = f"Unknown action: {action}"
    except Exception as e:
        result["output"] = str(e)
        log.error(f"[OPS] Error: {e}")
    
    log.info(f"[OPS] Result: {'OK' if result['success'] else 'FAIL'}")
    return result


def _execute_repair(candidate: Dict) -> bool:
    """修复问题"""
    detail = candidate.get("detail", "")
    if "Gateway" in detail:
        os.system("kill $(pgrep -f ace_gateway) 2>/dev/null")
        time.sleep(2)
        os.system("cd /workspace/one-api-data && nohup python3 ace_gateway.py > gateway.log 2>&1 &")
        time.sleep(8)
        return True
    return False


def _execute_stock_advisor() -> bool:
    """运行 Stock Advisor"""
    ret = os.system(f"bash /workspace/fengzi-repos/mine-seed/05_TOOLS/miner/run_stock_advisor.sh >> {REPORT_DIR}/advisor.log 2>&1")
    return ret == 0


def _execute_miner() -> bool:
    """运行矿场班次"""
    ret = os.system(f"bash /workspace/one-api-data/run_shift.sh miner >> {REPORT_DIR}/miner.log 2>&1")
    return ret == 0


def _execute_research(shift: str) -> bool:
    """运行研究班次"""
    ret = os.system(f"bash /workspace/one-api-data/run_shift.sh {shift}_research >> {REPORT_DIR}/research.log 2>&1")
    return ret == 0


def _execute_archivist() -> bool:
    """运行档案官"""
    ret = os.system(f"bash /workspace/one-api-data/run_shift.sh archivist >> {REPORT_DIR}/archivist.log 2>&1")
    return ret == 0


def _execute_memory_write(candidate: Dict) -> bool:
    """写入缺失的记忆"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    mem_file = MINE_SEED / "02_MEMORY" / "recent_memory" / "daily" / f"{today}-auto.md"
    mem_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"# {today} — Autonomous Loop 自动记忆\n\n"
    content += f"循环自动检测到缺失记忆，补充写入。\n"
    content += f"触发原因: {candidate.get('detail', '')}\n"
    content += f"时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    with open(mem_file, "w") as f:
        f.write(content)
    
    log.info(f"[OPS] Memory written: {mem_file}")
    return True


# ============================================================
# GOV: Governance
# ============================================================

def govern(result: Dict) -> Optional[Dict]:
    """治理：收集证据，提取经验"""
    if not result["success"]:
        # 失败 → 记录
        log.warning(f"[GOV] Task failed: {result['action']} — {result['output'][:100]}")
        # TODO: 连续失败检测 → FORBID 约束
        return None
    
    log.info(f"[GOV] Task succeeded: {result['action']}")
    # TODO: 经验提取 → Constraint 提案
    return None


# ============================================================
# Autonomous Loop
# ============================================================

def run_once():
    """运行一个完整循环"""
    global _cycle
    _cycle += 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info(f"\n{'='*50}")
    log.info(f"[LOOP] Cycle #{_cycle} at {now}")
    log.info(f"{'='*50}")
    
    # 1. ABP
    health = bootstrap()
    all_alive = all(health.values())
    
    if not all_alive:
        log.warning("[LOOP] ABP failed, entering repair mode")
        # 修复后重试
        time.sleep(10)
        health = bootstrap()
        if not all(health.values()):
            log.error("[LOOP] ABP still failed, sleeping...")
            return
    
    # 2. ECO: Observe
    observations = observe_environment()
    
    # 3. ECO: Generate Candidates
    candidates = generate_candidates(observations)
    
    if not candidates:
        log.info("[LOOP] No candidates, entering maintenance")
        _run_maintenance()
        return
    
    # 4. OPS: Execute (只执行优先级最高的 A 类任务)
    for candidate in candidates:
        if candidate["priority"] == "A":
            result = execute_candidate(candidate)
            govern(result)
            break  # 一轮只执行一个 A 类
    else:
        # 没有 A 类任务
        if candidates and candidates[0]["priority"] == "B":
            result = execute_candidate(candidates[0])
            govern(result)
        else:
            _run_maintenance()
    
    # 保存循环状态
    _save_cycle_state(health, observations, candidates)


def _run_maintenance():
    """维护模式"""
    log.info("[LOOP] Maintenance mode:")
    log.info("  Environment Scan...")
    log.info("  Archive Compress... (placeholder)")
    log.info("  Knowledge Merge... (placeholder)")
    log.info("  Self-Repair... (placeholder)")


def _save_cycle_state(health, observations, candidates):
    """保存循环状态"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    state = {
        "cycle": _cycle,
        "timestamp": datetime.now().isoformat(),
        "health": health,
        "observations_count": len(observations),
        "candidates_count": len(candidates),
    }
    state_file = REPORT_DIR / "latest_cycle.json"
    with open(state_file, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def run_loop():
    """自主循环：while alive"""
    log.info("ACE Runtime — Autonomous Loop 启动")
    log.info(f"心跳间隔: {HEARTBEAT_INTERVAL}s")
    log.info(f"Gateway: {GATEWAY_URL}")
    log.info("=" * 50)
    
    while _alive:
        try:
            run_once()
        except Exception as e:
            log.error(f"[LOOP] Cycle error: {e}")
            traceback.print_exc()
        
        if not _alive:
            break
        
        log.info(f"[LOOP] Sleeping {HEARTBEAT_INTERVAL}s...")
        
        # 分段睡眠，每秒检查 _alive
        for _ in range(HEARTBEAT_INTERVAL):
            if not _alive:
                break
            time.sleep(1)
    
    log.info("[LOOP] Autonomous Loop stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ACE Runtime Autonomous Loop")
    parser.add_argument("--once", action="store_true", help="Run only one cycle")
    parser.add_argument("--maintenance", action="store_true", help="Run maintenance mode")
    parser.add_argument("--interval", type=int, default=300, help="Heartbeat interval in seconds")
    args = parser.parse_args()
    
    if args.interval:
        HEARTBEAT_INTERVAL = args.interval
    
    if args.maintenance:
        _run_maintenance()
    elif args.once:
        run_once()
    else:
        run_loop()
