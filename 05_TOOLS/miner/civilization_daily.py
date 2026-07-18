#!/usr/bin/env python3
"""
Civilization Daily — 文明日报生成器

每日凌晨自动执行：
1. Runtime Health Check（API / Provider / Worker / Heartbeat / Cron）
2. Civilization Distillation（扫描今日产出 → 6 类资产）
3. Admission Review（提交到 admission/ 等待 Governor）
4. 生成 Civilization Daily 报告

用法：
  python3 civilization_daily.py
  python3 civilization_daily.py --dry-run  # 测试模式
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# 日志
LOG_DIR = Path(__file__).parent / ".." / "mine_output" / "civilizer"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "civilizer.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("civilizer")

# 路径
MINE_SEED = Path(os.environ.get("MINE_SEED", "/workspace/fengzi-repos/mine-seed"))
INDEX_FILE = MINE_SEED / "00_ROOT" / "CIVILIZATION_INDEX.json"
DAILY_DIR = MINE_SEED / "02_MEMORY" / "recent_memory" / "daily"
ADMISSION_DIR = MINE_SEED / "02_MEMORY" / "recent_memory" / "admission"
CLOUD_DIR = Path(os.environ.get("CLOUD_DIR", MINE_SEED / "cloud"))

# 权重
CATEGORY_WEIGHTS = {
    "kernel": 5,
    "blueprint": 4,
    "protocol": 3,
    "constraint": 2,
    "experience": 1,
    "identity": 8,
}


class CivilizationDaily:
    """文明日报生成器"""

    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.index = self._load_index()
        self.health = {}
        self.new_assets = []
        self.daily_score = 0

    def _load_index(self) -> dict:
        """加载文明索引"""
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0", "categories": {}, "score": {}}

    def step1_health_check(self) -> dict:
        """① Runtime 健康检查（并行化）"""
        logger.info("[Step 1] Runtime Health Check (parallel)")
        health = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }

        # 1.1 free_llm API 检查（并行 ping 3 个渠道）
        sys.path.insert(0, str(MINE_SEED / "05_TOOLS" / "miner"))
        try:
            from free_llm import call

            def _ping_channel(ch):
                try:
                    t0 = time.time()
                    r = call("ping", max_tokens=5, prefer=ch)
                    return ch, {
                        "status": "ALIVE",
                        "latency": round(time.time() - t0, 2),
                        "model": r.get("model", "unknown")
                    }
                except Exception as e:
                    return ch, {"status": "DEAD", "error": str(e)[:80]}

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(_ping_channel, ch): ch for ch in ["glm", "nim", "github"]}
                for future in as_completed(futures):
                    ch, result = future.result()
                    health["checks"][ch] = result
        except Exception as e:
            health["checks"]["free_llm"] = {"status": "ERROR", "error": str(e)[:80]}

        # 1.2 cron 检查
        try:
            import subprocess
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            lines = [l for l in result.stdout.split('\n') if l.strip() and not l.startswith('#')]
            health["checks"]["cron"] = {
                "status": "ALIVE",
                "tasks": len(lines)
            }
        except Exception as e:
            health["checks"]["cron"] = {"status": "DEAD", "error": str(e)[:80]}

        # 1.3 adata 检查
        try:
            import adata
            df = adata.stock.info.all_code()
            health["checks"]["adata"] = {
                "status": "ALIVE",
                "stocks": len(df)
            }
        except Exception as e:
            health["checks"]["adata"] = {"status": "DEAD", "error": str(e)[:80]}

        # 1.4 磁盘空间
        try:
            import shutil
            stat = shutil.disk_usage("/tmp")
            health["checks"]["disk"] = {
                "status": "ALIVE",
                "free_gb": round(stat.free / (1024**3), 1)
            }
        except:
            pass

        self.health = health
        logger.info(f"[Health] {sum(1 for v in health['checks'].values() if v.get('status') == 'ALIVE')}/{len(health['checks'])} OK")
        return health

    def step2_distillation(self) -> List[dict]:
        """② 文明蒸馏：扫描今日产出"""
        logger.info("[Step 2] Civilization Distillation")
        new_assets = []

        # 扫描今日修改的文件
        today_str = self.today.replace("-", "")
        yesterday_ts = (datetime.now() - timedelta(days=1)).timestamp()

        scan_dirs = [
            MINE_SEED / "05_TOOLS",
            MINE_SEED / "04_PROTOCOLS",
            MINE_SEED / "00_ROOT",
        ]

        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            for f in scan_dir.rglob("*.py"):
                if f.stat().st_mtime > yesterday_ts:
                    # 这是一个今日修改的 Python 文件
                    # 检查是否已经在索引中
                    rel_path = str(f.relative_to(MINE_SEED))
                    if not self._asset_exists(rel_path):
                        asset = self._classify_asset(f, rel_path)
                        if asset:
                            new_assets.append(asset)

            for f in scan_dir.rglob("*.md"):
                if f.stat().st_mtime > yesterday_ts:
                    rel_path = str(f.relative_to(MINE_SEED))
                    if not self._asset_exists(rel_path):
                        asset = self._classify_asset(f, rel_path)
                        if asset:
                            new_assets.append(asset)

        # 扫描 cloud/ 目录下的今日产出
        if CLOUD_DIR.exists():
            for f in CLOUD_DIR.rglob(f"*{today_str}*.md"):
                rel_path = str(f.relative_to(MINE_SEED))
                if not self._asset_exists(rel_path):
                    new_assets.append({
                        "name": f"Cloud output: {f.name}",
                        "type": "experience",
                        "source": rel_path,
                        "reason": "Runtime 产出"
                    })

        self.new_assets = new_assets
        logger.info(f"[Distillation] 发现 {len(new_assets)} 个潜在新资产")
        return new_assets

    def _asset_exists(self, source: str) -> bool:
        """检查资产是否已在索引中"""
        for cat_data in self.index.get("categories", {}).values():
            for asset in cat_data.get("assets", []):
                if asset.get("source") == source:
                    return True
        return False

    def _classify_asset(self, f: Path, rel_path: str) -> dict:
        """尝试自动分类资产"""
        name = f.stem
        content = f.read_text(encoding='utf-8', errors='ignore')[:2000]

        # 简单的启发式分类
        if "class" in content and "def call" in content and "llm" in content.lower():
            return {"name": name, "type": "kernel", "source": rel_path, "reason": "核心能力模块"}
        elif "Blueprint" in content or "Pipeline" in content or "模式" in content:
            return {"name": name, "type": "blueprint", "source": rel_path, "reason": "架构模式"}
        elif "Protocol" in content or "protocol" in content.lower():
            return {"name": name, "type": "protocol", "source": rel_path, "reason": "协议约定"}
        elif "Constraint" in content or "不得" in content or "禁止" in content:
            return {"name": name, "type": "constraint", "source": rel_path, "reason": "约束规则"}
        elif "Experience" in content or "经验" in content:
            return {"name": name, "type": "experience", "source": rel_path, "reason": "经验沉淀"}
        elif "Identity" in content or "SOUL" in content or "PRINCIPLES" in content:
            return {"name": name, "type": "identity", "source": rel_path, "reason": "文明人格"}

        # 默认：不自动分类，标记为待审查
        return {"name": name, "type": "pending", "source": rel_path, "reason": "需人工分类"}

    def step3_admission_review(self) -> str:
        """③ 提交 Admission Review"""
        logger.info("[Step 3] Admission Review")
        ADMISSION_DIR.mkdir(parents=True, exist_ok=True)

        admission_file = ADMISSION_DIR / f"admission_{self.today.replace('-', '')}.md"

        lines = [
            f"# Admission Review — {self.today}",
            "",
            "> 由 Civilization Daily 自动生成，等待 Governor 审查。",
            "",
            "---",
            "",
            "## 今日提议资产",
            "",
        ]

        for i, asset in enumerate(self.new_assets, 1):
            lines.extend([
                f"### {i}. {asset['name']}",
                "",
                f"- **提议类型**: {asset['type']}",
                f"- **来源**: `{asset['source']}`",
                f"- **理由**: {asset['reason']}",
                "",
                "#### Governor 决策",
                "",
                "- [ ] PASS — 进入 Repository",
                "- [ ] REJECT — 丢弃",
                "- [ ] MERGE — 与已有资产合并",
                "- [ ] SUPERSEDE — 替代旧资产",
                "- [ ] ARCHIVE — 归档",
                "",
                "#### 决策理由",
                "",
                "（Governor 填写）",
                "",
                "---",
                "",
            ])

        if not self.new_assets:
            lines.append("今日无新资产提议。\n")

        with open(admission_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        logger.info(f"[Admission] 提交: {admission_file}")
        return str(admission_file)

    def step4_generate_daily(self) -> str:
        """④ 生成 Civilization Daily"""
        logger.info("[Step 4] Generate Civilization Daily")
        DAILY_DIR.mkdir(parents=True, exist_ok=True)

        # 计算分数变化
        yesterday_score = self.index.get("score", {}).get("total", 0)

        # 统计各类别新增
        category_changes = {cat: 0 for cat in CATEGORY_WEIGHTS}
        for asset in self.new_assets:
            cat = asset.get("type", "pending")
            if cat in category_changes:
                category_changes[cat] += 1

        score_change = sum(
            category_changes[cat] * weight
            for cat, weight in CATEGORY_WEIGHTS.items()
        )
        today_score = yesterday_score + score_change

        # 统计 Repository 总数
        repo_totals = {}
        for cat, data in self.index.get("categories", {}).items():
            repo_totals[cat] = data.get("count", 0)
        # 加上今日新增（预估）
        for cat, count in category_changes.items():
            if cat in repo_totals:
                repo_totals[cat] += count

        # 健康检查摘要
        alive = sum(1 for v in self.health.get("checks", {}).values() if v.get("status") == "ALIVE")
        total_checks = len(self.health.get("checks", {}))

        lines = [
            f"# Civilization Daily — {self.today}",
            "",
            f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> 来源: Architecture Brain (云端)",
            "",
            "---",
            "",
            "## ① Runtime Health Check",
            "",
            f"**状态**: {alive}/{total_checks} 项正常",
            "",
        ]

        for check_name, check_data in self.health.get("checks", {}).items():
            status = check_data.get("status", "UNKNOWN")
            icon = "🟢" if status == "ALIVE" else "🔴" if status == "DEAD" else "🟡"
            extra = ""
            if "latency" in check_data:
                extra = f" ({check_data['latency']}s)"
            elif "stocks" in check_data:
                extra = f" ({check_data['stocks']} stocks)"
            elif "tasks" in check_data:
                extra = f" ({check_data['tasks']} tasks)"
            lines.append(f"- {icon} **{check_name}**: {status}{extra}")

        lines.extend([
            "",
            "---",
            "",
            "## ② Civilization Distillation",
            "",
            f"今日发现 **{len(self.new_assets)}** 个潜在新资产",
            "",
        ])

        if self.new_assets:
            lines.append("| # | 名称 | 提议类型 | 来源 |")
            lines.append("|---|------|----------|------|")
            for i, asset in enumerate(self.new_assets, 1):
                lines.append(f"| {i} | {asset['name']} | {asset['type']} | `{asset['source']}` |")
        else:
            lines.append("今日无新资产。")

        lines.extend([
            "",
            "---",
            "",
            "## ③ Admission Review",
            "",
            f"提交文件: `02_MEMORY/recent_memory/admission/admission_{self.today.replace('-', '')}.md`",
            "",
            "等待 Governor 审查。",
            "",
            "---",
            "",
            "## ④ Repository 总览",
            "",
            "| 类别 | 总数 | 较昨日 | 权重 | 分数贡献 |",
            "|------|------|--------|------|----------|",
        ])

        for cat in ["kernel", "blueprint", "protocol", "constraint", "experience", "identity"]:
            total = repo_totals.get(cat, 0)
            change = category_changes.get(cat, 0)
            weight = CATEGORY_WEIGHTS.get(cat, 1)
            score_contrib = total * weight
            change_str = f"+{change}" if change > 0 else str(change) if change < 0 else "0"
            lines.append(f"| {cat.capitalize()} | {total} | {change_str} | {weight} | {score_contrib} |")

        lines.extend([
            "",
            "---",
            "",
            "## 文明评分",
            "",
            f"昨日: **{yesterday_score}**",
            f"今日: **{today_score}**",
            f"变化: **{'+' if score_change >= 0 else ''}{score_change}**",
            "",
        ])

        # 评分变化趋势
        if score_change > 5:
            lines.append("📈 文明快速增长")
        elif score_change > 0:
            lines.append("📊 文明稳步增长")
        elif score_change == 0:
            lines.append("➖ 文明无变化")
        else:
            lines.append("📉 文明资产减少")

        lines.extend([
            "",
            "---",
            "",
            "## 下一步建议",
            "",
            "（Governor 填写）",
            "",
            "---",
            "",
            "*本报告由云端 Architecture Brain 自动生成。*",
        ])

        daily_file = DAILY_DIR / f"civilization_daily_{self.today.replace('-', '')}.md"
        with open(daily_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        logger.info(f"[Daily] 生成: {daily_file}")
        return str(daily_file)

    def run(self):
        """完整运行 4 步"""
        logger.info("=" * 50)
        logger.info("Civilization Daily 启动")
        logger.info("=" * 50)

        self.step1_health_check()
        self.step2_distillation()
        self.step3_admission_review()
        daily_file = self.step4_generate_daily()

        logger.info("=" * 50)
        logger.info(f"Civilization Daily 完成: {daily_file}")
        logger.info("=" * 50)

        return {
            "health": self.health,
            "new_assets": self.new_assets,
            "daily_file": daily_file,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="文明日报生成器")
    parser.add_argument("--dry-run", action="store_true", help="测试模式，不写入文件")
    args = parser.parse_args()

    daily = CivilizationDaily()

    if args.dry_run:
        print("=== 测试模式 ===")
        daily.step1_health_check()
        print(f"\n健康检查: {daily.health}")
        daily.step2_distillation()
        print(f"\n新资产: {len(daily.new_assets)}")
        for a in daily.new_assets:
            print(f"  - {a['name']} ({a['type']})")
        return

    result = daily.run()
    print(f"\n文明日报生成完成: {result['daily_file']}")


if __name__ == "__main__":
    main()
