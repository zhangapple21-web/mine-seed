#!/usr/bin/env python3
"""
24小时矿场 v6 — free_llm 兼容版（并行化）

原 miner_24h.py 的 Gateway 依赖太重（Registry/Observation/Router/Judge），
此版本提供轻量级兼容层：
- 保持相同的任务列表和输出格式
- 使用 free_llm 替代 Gateway 路由
- 保留约束规则（AVOID/PREFER）作为纯数据
- 输出兼容 observation_log.json 格式
- 并行化：ThreadPoolExecutor(max_workers=4)
- log() 改用 logging 模块消除竞态
- observation_log.json 保持串行写入

用法：
  python3 miner_24h_free.py [task_name]
  # task_name: market_sentiment | tech_analysis | sector_rotation | risk_assessment
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

# logging 配置（消除竞态）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(OUTPUT_DIR / "miner_free.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ],
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

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

# 任务定义（从原 TASK_PROFILES 简化）
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
    """运行单个任务"""
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

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        outfile = OUTPUT_DIR / f"{task_name}_{ts}.md"
        content = f"# {task_name}\n\n渠道: {result['channel']} | 模型: {result['model']} | 耗时: {elapsed:.1f}s\n\n{result['content']}"
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write(content)

        CLOUD_DIR.mkdir(parents=True, exist_ok=True)
        cloud_file = CLOUD_DIR / f"{task_name}_{ts}.md"
        with open(cloud_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"  OK: {result['channel']}/{result['model']} {elapsed:.1f}s -> {cloud_file.name}")

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
        logger.error(f"  FAIL: {e}")
        return {"success": False, "task": task_name, "error": str(e), "elapsed": elapsed}


def run_all():
    """运行所有任务（并行化）"""
    t0_total = time.time()
    logger.info("=" * 50)
    logger.info("24h矿场 v6 (free_llm) 启动 [并行模式]")
    logger.info("=" * 50)

    results = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_task = {executor.submit(run_task, task_name): task_name for task_name in TASKS}
        
        for future in as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"任务 {task_name} 异常: {e}")
                results.append({"success": False, "task": task_name, "error": str(e)})

    elapsed_total = time.time() - t0_total
    success = sum(1 for r in results if r["success"])
    logger.info(f"\n矿场完成: {success}/{len(results)} 任务成功 | 总耗时: {elapsed_total:.1f}s")

    # observation_log.json 保持串行写入
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
            json.dump({"observations": observations}, f, ensure_ascii=False, indent=2)
        logger.info(f"observation_log 已保存: {obs_file}")
    except Exception as e:
        logger.warning(f"observation_log 保存失败: {e}")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="24h矿场 free_llm 版")
    parser.add_argument("task", nargs="?", default="all", help="任务名或 'all'")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.task == "all":
        run_all()
    else:
        result = run_task(args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
