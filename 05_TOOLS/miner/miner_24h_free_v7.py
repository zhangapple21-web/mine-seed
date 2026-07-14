#!/usr/bin/env python3
"""
24小时矿场 v7 — 并行版

v6 → v7 改进：
- 4 个子任务并行执行（ThreadPoolExecutor, max_workers=4）
- log() 改用 logging 模块（线程安全，消除竞态）
- observation_log.json 保持最后统一串行写入
- 耗时从 ~4 分钟降到 ~60 秒

用法：
  python3 miner_24h_free_v7.py [task_name]
  # task_name: market_sentiment | tech_analysis | sector_rotation | risk_assessment | all
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 加载 free_llm
sys.path.insert(0, str(Path(__file__).parent))
from free_llm import call

# 配置
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/tmp/mine_output"))
CLOUD_DIR = Path(os.environ.get("CLOUD_DIR", "/workspace/fengzi-repos/mine-seed/cloud/miner"))
LOG_FILE = OUTPUT_DIR / "miner_free_v7.log"

# 线程安全的 logging 配置
logger = logging.getLogger("miner_v7")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)

# 约束规则（从原 miner_24h.py 迁移）
AVOID_RULES = [
    ("*", "gh_r1"),
    ("*", "nim_ultra_550b"),
    ("*", "gh_4o"),
    ("persona_deep", "nim_mistral_675b"),
    ("canonical_v2", "gh_r1"),
    ("canonical_v2", "nim_ultra_550b"),
    ("persona_deep", "nim_ultra_550b"),
    ("signal_mean_reversion", "glm_4_flash"),
    ("signal_volume_price_divergence", "glm_4_flash"),
]

PREFER_RULES = [
    ("signal_mean_reversion", "nim_deepseek"),
]

# 任务定义
TASKS = {
    "market_sentiment": {
        "prompt": "你是疯子矿场的市场分析师。简短分析当前A股市场情绪（100字以内）。格式：[情绪] [方向] [建议]",
        "system": "你是专业的A股市场情绪分析师。",
        "prefer": "glm",
        "max_tokens": 500,
    },
    "tech_analysis": {
        "prompt": "用100字分析当前A股技术面走势。关注沪指和创业板。",
        "system": "你是专业的A股技术分析师。",
        "prefer": "nim",
        "max_tokens": 500,
    },
    "sector_rotation": {
        "prompt": "分析当前A股板块轮动趋势，列出3个强势板块和3个弱势板块。",
        "system": "你是专业的A股板块轮动分析师。",
        "prefer": "glm",
        "max_tokens": 600,
    },
    "risk_assessment": {
        "prompt": "评估当前A股市场风险等级（低/中/高），给出理由。",
        "system": "你是专业的A股市场风险评估师。",
        "prefer": "github",
        "max_tokens": 400,
    },
}


def run_task(task_name: str) -> dict:
    """运行单个任务（线程安全）"""
    task = TASKS.get(task_name)
    if not task:
        logger.error(f"未知任务: {task_name}")
        return {"success": False, "error": "unknown task"}

    logger.info(f"[TASK] {task_name} -> {task['prefer']}")

    t0 = time.time()
    try:
        result = call(
            task["prompt"],
            system=task["system"],
            max_tokens=task["max_tokens"],
            temperature=0.3,
            prefer=task["prefer"]
        )
        elapsed = time.time() - t0

        # 每个任务独立的输出文件（无共享写入冲突）
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        outfile = OUTPUT_DIR / f"{task_name}_{ts}.md"
        content = f"# {task_name}\n\n渠道: {result['channel']} | 模型: {result['model']} | 耗时: {elapsed:.1f}s\n\n{result['content']}"
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write(content)

        # 复制到 cloud/
        CLOUD_DIR.mkdir(parents=True, exist_ok=True)
        cloud_file = CLOUD_DIR / f"{task_name}_{ts}.md"
        with open(cloud_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"[OK] {task_name}: {result['channel']}/{result['model']} {elapsed:.1f}s")

        return {
            "success": True,
            "task": task_name,
            "channel": result["channel"],
            "model": result["model"],
            "elapsed": elapsed,
            "file": str(cloud_file),
        }

    except Exception as e:
        elapsed = time.time() - t0
        logger.error(f"[FAIL] {task_name}: {e}")
        return {"success": False, "task": task_name, "error": str(e), "elapsed": elapsed}


def run_all_parallel():
    """并行运行所有任务"""
    logger.info("=" * 50)
    logger.info("24h矿场 v7 (并行版) 启动")
    logger.info("=" * 50)

    t_start = time.time()
    results = []

    # 4 个子任务并行执行
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 提交所有任务
        future_to_task = {
            executor.submit(run_task, task_name): task_name
            for task_name in TASKS
        }

        # 收集结果（按完成顺序）
        for future in as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"[EXCEPTION] {task_name}: {e}")
                results.append({"success": False, "task": task_name, "error": str(e)})

    total_elapsed = time.time() - t_start
    success = sum(1 for r in results if r.get("success"))
    logger.info(f"矿场完成: {success}/{len(results)} 任务成功, 总耗时: {total_elapsed:.1f}s")

    # observation_log.json 最后统一串行写入（避免并行写入冲突）
    obs_file = OUTPUT_DIR / "observation_log.json"
    observations = []
    for r in results:
        observations.append({
            "timestamp": datetime.now().isoformat(),
            "task": r.get("task", "unknown"),
            "worker_id": r.get("channel", "free_llm"),
            "model": r.get("model", "unknown"),
            "corps": "FREE",
            "success": r.get("success", False),
            "elapsed": r.get("elapsed", 0),
        })

    try:
        with open(obs_file, 'w', encoding='utf-8') as f:
            json.dump({"observations": observations, "total_elapsed": total_elapsed}, f, ensure_ascii=False, indent=2)
        logger.info(f"[OBS] observation_log 已保存: {obs_file}")
    except Exception as e:
        logger.error(f"[WARN] observation_log 保存失败: {e}")

    return results, total_elapsed


def run_all_serial():
    """串行运行（用于对比测试）"""
    logger.info("=" * 50)
    logger.info("24h矿场 v7 (串行对比版) 启动")
    logger.info("=" * 50)

    t_start = time.time()
    results = []
    for task_name in TASKS:
        result = run_task(task_name)
        results.append(result)
        time.sleep(1)

    total_elapsed = time.time() - t_start
    success = sum(1 for r in results if r.get("success"))
    logger.info(f"矿场完成: {success}/{len(results)} 任务成功, 总耗时: {total_elapsed:.1f}s")

    return results, total_elapsed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="24h矿场 v7 并行版")
    parser.add_argument("task", nargs="?", default="all", help="任务名或 'all'")
    parser.add_argument("--serial", action="store_true", help="串行模式（用于对比测试）")
    parser.add_argument("--benchmark", action="store_true", help="跑并行+串行对比测试")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.benchmark:
        # 先跑串行
        logger.info("\n>>> 基准测试: 串行模式 <<<\n")
        _, serial_time = run_all_serial()

        # 再跑并行
        logger.info("\n>>> 基准测试: 并行模式 <<<\n")
        _, parallel_time = run_all_parallel()

        # 对比报告
        logger.info("\n" + "=" * 50)
        logger.info("基准测试报告")
        logger.info("=" * 50)
        logger.info(f"串行耗时: {serial_time:.1f}s")
        logger.info(f"并行耗时: {parallel_time:.1f}s")
        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        logger.info(f"加速比: {speedup:.1f}x")
        logger.info(f"节省时间: {serial_time - parallel_time:.1f}s")
        return

    if args.task == "all":
        if args.serial:
            run_all_serial()
        else:
            run_all_parallel()
    else:
        result = run_task(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
