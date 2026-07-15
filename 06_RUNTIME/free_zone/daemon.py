#!/usr/bin/env python3
"""
ACE Free Zone Daemon — 自由区 24h 持续学习守护进程

Mission: AUM-MISSION-FREEZONE-001
Identity: 自由区副本，24小时持续产出 Observation 和 Hypothesis
Version: v1.0 (2026-07-15)

Core Loop:
    每 30 分钟 → 调用免费 LLM → 产出 Observation → 孟婆过滤 → 存储

设计原则:
    1. 零成本：只用免费 API（GLM/NIM/GitHub）
    2. 独立运行：不影响主系统，输出到 free_zone/ 目录
    3. 文明加工：产出经过 DistillationFactory 处理
    4. 心跳通知：每 8 小时 TG 心跳

Never Rules:
    - 修改生产资产（civilization_assets / constraint / world_models）
    - 跳过孟婆直接写入 Repository
    - 使用付费 API
"""

import os
import sys
import json
import time
import logging
import importlib.util
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256

# ── 路径设置 ──
WORKSPACE = Path(__file__).parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "05_TOOLS" / "miner"))

# ── 配置 ──
CONFIG_PATH = WORKSPACE / "06_RUNTIME" / "free_zone" / "config.json"
OUTPUT_DIR = WORKSPACE / "02_MEMORY" / "free_zone"
LOG_DIR = WORKSPACE / "02_MEMORY" / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ── 日志 ──
log = logging.getLogger("ACE.FreeZone")
log.setLevel(logging.INFO)

log_file = LOG_DIR / f"free_zone_{datetime.now().strftime('%Y%m%d')}.log"
fh = logging.FileHandler(log_file, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
log.addHandler(ch)


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def import_module(path: Path):
    """动态导入模块"""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_free_llm():
    """加载 free_llm 库"""
    return import_module(WORKSPACE / "05_TOOLS" / "miner" / "free_llm.py")


def load_distillation_factory():
    """加载孟婆"""
    return import_module(WORKSPACE / "04_PROTOCOLS" / "distillation_factory.py")


def generate_observation_id(content: str) -> str:
    """生成 Observation ID"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    h = sha256(content.encode()).hexdigest()[:8]
    return f"OBS-FZ-{ts}-{h}"


def run_task(free_llm, task: dict) -> dict:
    """运行单个学习任务"""
    task_id = task["id"]
    log.info(f"[TASK] {task_id} → prefer: {task.get('prefer', 'auto')}")

    t0 = time.time()
    try:
        result = free_llm.call(
            prompt=task["prompt"],
            system=task.get("system", ""),
            max_tokens=task.get("max_tokens", 500),
            temperature=0.4,
            prefer=task.get("prefer")
        )

        elapsed = time.time() - t0
        content = result["content"]
        channel = result["channel"]
        model = result["model"]

        # 生成 Observation
        obs_id = generate_observation_id(content)
        observation = {
            "observation_id": obs_id,
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "channel": channel,
            "model": model,
            "content": content,
            "elapsed_seconds": round(elapsed, 1),
            "metadata": {}
        }

        # 写入自由区输出
        outfile = OUTPUT_DIR / f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(observation, f, ensure_ascii=False, indent=2)

        log.info(f"[OK] {task_id}: {channel}/{model} {elapsed:.1f}s → {obs_id}")
        return observation

    except Exception as e:
        elapsed = time.time() - t0
        log.error(f"[FAIL] {task_id}: {e} ({elapsed:.1f}s)")
        return {"task_id": task_id, "error": str(e), "elapsed": elapsed}


def distill_observation(distillation_factory, observation: dict) -> dict:
    """通过孟婆处理 Observation"""
    try:
        # 转换为孟婆输入格式
        experience = {
            "core_features": {
                "task_id": observation.get("task_id"),
                "channel": observation.get("channel"),
                "content_summary": observation["content"][:200]
            },
            "metadata": observation.get("metadata", {})
        }

        record = distillation_factory.process(experience)
        if record:
            log.info(f"[DISTILL] {observation['observation_id']} → pollution: {record.pollution_detected}, pattern: {'yes' if record.pattern_extracted else 'no'}")
            return record.to_dict()
        return {"skipped": True}
    except Exception as e:
        log.warning(f"[DISTILL] Error: {e}")
        return {"error": str(e)}


def send_heartbeat(config: dict, cycle_count: int, stats: dict):
    """发送 TG 心跳"""
    tg_config = config.get("tg_heartbeat", {})
    if not tg_config.get("enabled"):
        return

    bot_token = os.environ.get(tg_config.get("bot_token_env", "TG_BOT_TOKEN_2"), "")
    chat_id = tg_config.get("chat_id", "")
    if not bot_token or not chat_id:
        log.warning("[HEARTBEAT] Missing TG config, skipping")
        return

    uptime_hours = (stats.get("total_cycles", 0) * config.get("cycle_interval_seconds", 1800)) / 3600
    message = (
        f"🧪 ACE Free Zone Heartbeat\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Cycles: {stats['total_cycles']} ({uptime_hours:.1f}h)\n"
        f"Observations: {stats['total_observations']}\n"
        f"Distilled: {stats['total_distilled']}\n"
        f"Errors: {stats['total_errors']}\n"
        f"Last run: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"Status: {'HEALTHY' if stats['total_errors'] < 5 else 'DEGRADED'}"
    )

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = json.dumps({
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
        log.info(f"[HEARTBEAT] Sent to {chat_id}")
    except Exception as e:
        log.warning(f"[HEARTBEAT] Failed: {e}")


def run_cycle(free_llm, distillation_factory, config: dict) -> dict:
    """运行一个学习周期"""
    cycle_start = time.time()
    log.info(f"{'='*50}")
    log.info(f"Free Zone Cycle Started")
    log.info(f"{'='*50}")

    observations = []
    distilled = 0
    errors = 0

    for task in config.get("tasks", []):
        obs = run_task(free_llm, task)
        if "error" in obs:
            errors += 1
            continue

        observations.append(obs)

        # 孟婆处理
        distill_result = distill_observation(distillation_factory, obs)
        if distill_result and not distill_result.get("skipped"):
            distilled += 1

    elapsed = time.time() - cycle_start
    log.info(f"Cycle complete: {len(observations)} observations, {distilled} distilled, {errors} errors, {elapsed:.1f}s")

    return {
        "observations": len(observations),
        "distilled": distilled,
        "errors": errors,
        "elapsed": round(elapsed, 1)
    }


def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(description="ACE Free Zone Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run as 24h daemon")
    parser.add_argument("--once", action="store_true", help="Run single cycle and exit")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if not args.verbose:
        # 静默模式：只保留文件日志
        log.handlers = [fh]

    log.info("=" * 60)
    log.info("ACE Free Zone Daemon v1.0 — 24h Continuous Learning")
    log.info("=" * 60)

    # 加载组件
    try:
        free_llm = load_free_llm()
        distillation_factory = load_distillation_factory()
        factory = distillation_factory.DistillationFactory(
            store_path=str(OUTPUT_DIR / "distilled")
        )
        log.info("[INIT] free_llm loaded")
        log.info("[INIT] DistillationFactory (孟婆) loaded")
    except Exception as e:
        log.error(f"[INIT] Failed to load components: {e}")
        sys.exit(1)

    config = load_config()
    cycle_interval = config.get("cycle_interval_seconds", 1800)
    heartbeat_interval = config.get("heartbeat_interval_cycles", 16)

    stats = {
        "total_cycles": 0,
        "total_observations": 0,
        "total_distilled": 0,
        "total_errors": 0
    }

    # 单次模式
    if args.once:
        result = run_cycle(free_llm, factory, config)
        stats["total_cycles"] = 1
        stats["total_observations"] = result["observations"]
        stats["total_distilled"] = result["distilled"]
        stats["total_errors"] = result["errors"]
        send_heartbeat(config, 1, stats)
        return

    # Daemon 模式
    if not args.daemon:
        log.info("Use --daemon for 24h mode, --once for single cycle")
        return

    log.info(f"[DAEMON] Cycle interval: {cycle_interval}s ({cycle_interval//60}min)")
    log.info(f"[DAEMON] Heartbeat: every {heartbeat_interval} cycles ({heartbeat_interval * cycle_interval // 3600}h)")

    while True:
        try:
            result = run_cycle(free_llm, factory, config)

            stats["total_cycles"] += 1
            stats["total_observations"] += result["observations"]
            stats["total_distilled"] += result["distilled"]
            stats["total_errors"] += result["errors"]

            # 心跳
            if stats["total_cycles"] % heartbeat_interval == 0:
                send_heartbeat(config, stats["total_cycles"], stats)

            # 等待下一个周期
            sleep_time = max(60, cycle_interval - int(result["elapsed"]))
            log.info(f"[DAEMON] Sleeping {sleep_time}s until next cycle...")
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            log.info("[DAEMON] Interrupted by user, shutting down...")
            send_heartbeat(config, stats["total_cycles"], stats)
            break
        except Exception as e:
            log.error(f"[DAEMON] Cycle error: {e}")
            time.sleep(60)  # 出错后等 1 分钟


if __name__ == "__main__":
    main()