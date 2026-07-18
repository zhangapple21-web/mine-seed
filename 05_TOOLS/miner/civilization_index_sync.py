#!/usr/bin/env python3
"""
Civilization Index Sync — 文明索引同步校验器

功能：
1. 扫描实际文件系统，找出 CIVILIZATION_INDEX.json 中未收录的资产
2. 校验已收录资产的 source 文件是否仍然存在
3. 自动提议新资产分类（基于启发式规则）
4. 输出同步报告，列出需新增 / 需移除 / 需更新的条目

用法：
  python3 civilization_index_sync.py           # 全量扫描
  python3 civilization_index_sync.py --fix      # 自动修复（仅添加确认的资产）
  python3 civilization_index_sync.py --dry-run  # 只报告不同步
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# 日志
LOG_DIR = Path(__file__).parent / ".." / "mine_output" / "index_sync"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "index_sync.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("index_sync")

# 路径
MINE_SEED = Path(os.environ.get("MINE_SEED", "/workspace/fengzi-repos/mine-seed"))
INDEX_FILE = MINE_SEED / "00_ROOT" / "CIVILIZATION_INDEX.json"

# 权重
CATEGORY_WEIGHTS = {
    "kernel": 5,
    "blueprint": 4,
    "protocol": 3,
    "constraint": 2,
    "experience": 1,
    "identity": 8,
}

# 已知的"非资产"目录/文件（工具代码、测试、配置、日志、临时文件等）
SKIP_PATTERNS = [
    "__pycache__",
    ".git",
    "node_modules",
    ".DS_Store",
    "*.pyc",
    "*.log",
    "*.env",
    "*.flag",
    "mine_output",
    "tg_output",
    "free_api.env",
    "tg_login_state.json",
    "worker_registry.json",
    "observation_log.json",
    "session_validation_",
    "recent_memory/daily/",
    "recent_memory/daily_summary/",
    "recent_memory/experience/",
    "recent_memory/recovery/",
    "recent_memory/ops_logs/",
    "recent_memory/self_loop/",
    "recent_memory/evolution/",
    "recent_memory/environment/",
    "discovery_queue/",
    "advisor_tracker/",
    "archaeology/",
    "exploration/",
    "knowledge/",
    "lineage/",
    "question_center/",
    "civilization_assets/",
    "civilization_audit/",
    "superseded_archive",
]

# 候选目录（包含资产概率高的目录）
ASSET_SCAN_DIRS = [
    "00_ROOT",
    "01_AGENTS",
    "04_PROTOCOLS",
    "05_TOOLS/miner",
    "05_TOOLS/advisor",
    "05_TOOLS/signals",
    "05_TOOLS/memory",
    "05_TOOLS/gateway",
    "06_RUNTIME",
    "07_GUARDIAN",
]

# 候选文件扩展名
ASSET_EXTENSIONS = {".py", ".md", ".sh"}

# 文件大小阈值（小于此值可能不是有意义的资产）
MIN_SIZE_BYTES = 200


def load_index() -> dict:
    """加载文明索引"""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": "1.0", "categories": {}, "score": {}, "missions": {}}


def save_index(index: dict):
    """保存文明索引"""
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    logger.info(f"[SAVE] 索引已保存: {INDEX_FILE}")


def is_skip_path(rel_path: str) -> bool:
    """判断是否跳过"""
    for pattern in SKIP_PATTERNS:
        if pattern.startswith("*"):
            if rel_path.endswith(pattern[1:]):
                return True
        elif pattern.endswith("/"):
            if pattern in rel_path:
                return True
        elif pattern in rel_path:
            return True
    return False


def scan_existing_sources(index: dict) -> Dict[str, str]:
    """收集索引中所有 source 路径"""
    sources = {}
    for cat, data in index.get("categories", {}).items():
        for asset in data.get("assets", []):
            src = asset.get("source", "")
            if src:
                sources[src] = asset.get("id", "")
    return sources


def check_source_exists(source: str) -> Tuple[bool, str]:
    """检查 source 文件是否存在"""
    full_path = MINE_SEED / source
    if full_path.exists():
        return True, ""
    return False, f"文件不存在: {source}"


def classify_file(f: Path, rel_path: str, content: str) -> Optional[str]:
    """启发式分类文件"""
    name_lower = f.stem.lower()

    # Kernel：核心能力模块
    if "free_llm" in name_lower or "stock_query" in name_lower or "model_router" in name_lower:
        return "kernel"
    if "class" in content and "def call" in content and "llm" in content.lower():
        return "kernel"
    if "def call(" in content and "fallback" in content.lower():
        return "kernel"

    # Blueprint：架构模式、Pipeline
    if "blueprint" in content.lower() or "pipeline" in content.lower():
        return "blueprint"
    if "signal_discovery" in name_lower:
        return "blueprint"
    if "triple_fallback" in content.lower() or "三" in content and "降级" in content:
        return "blueprint"

    # Protocol：协议、部署规范
    if "protocol" in name_lower:
        return "protocol"
    if "contract" in name_lower or "governance" in name_lower:
        return "protocol"
    if "recovery" in name_lower and f.suffix == ".md":
        return "protocol"
    if "crontab" in name_lower:
        return "protocol"

    # Constraint：约束、规则
    if "constraint" in name_lower:
        return "constraint"
    if "avoid" in content.lower()[:500] and "forbid" in content.lower()[:500]:
        return "constraint"
    if "不得" in content[:500] or "禁止" in content[:500]:
        return "constraint"

    # Experience：经验、报告
    if "experience" in content.lower()[:300] or "经验" in content[:300]:
        return "experience"
    if "discovery_scan" in name_lower:
        return "blueprint"
    if "civilization_daily" in name_lower:
        return "blueprint"

    # Identity：人格、原则
    if name_lower in ("principles", "soul", "manifesto", "governance", "architecture"):
        return "identity"
    if "SOUL" in content[:200] or "PRINCIPLES" in content[:200]:
        return "identity"
    if "文明核心原则" in content[:500]:
        return "identity"

    return None


def scan_new_assets(index: dict) -> List[dict]:
    """扫描文件系统找新资产"""
    existing_sources = scan_existing_sources(index)
    new_assets = []

    def scan_dir(scan_dir: str):
        """并行扫描单个目录"""
        full_dir = MINE_SEED / scan_dir
        if not full_dir.exists():
            return []

        found = []
        for ext in ASSET_EXTENSIONS:
            for f in full_dir.rglob(f"*{ext}"):
                rel_path = str(f.relative_to(MINE_SEED))

                if is_skip_path(rel_path):
                    continue

                if f.stat().st_size < MIN_SIZE_BYTES:
                    continue

                if rel_path in existing_sources:
                    continue

                try:
                    content = f.read_text(encoding='utf-8', errors='ignore')[:2000]
                except:
                    continue

                cat = classify_file(f, rel_path, content)
                if cat:
                    desc_hint = ""
                    first_line = content.strip().split('\n')[0] if content else ""
                    if first_line.startswith('#'):
                        desc_hint = first_line.lstrip('#').strip()[:80]

                    found.append({
                        "name": f.stem,
                        "category": cat,
                        "source": rel_path,
                        "desc_hint": desc_hint,
                        "size": f.stat().st_size,
                    })

        return found

    # 并行扫描所有目录
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(scan_dir, d): d for d in ASSET_SCAN_DIRS}
        for future in as_completed(futures):
            scan_dir_name = futures[future]
            try:
                results = future.result()
                new_assets.extend(results)
            except Exception as e:
                logger.error(f"[SCAN] {scan_dir_name} 扫描失败: {e}")

    # 去重
    seen = set()
    unique = []
    for a in new_assets:
        if a["source"] not in seen:
            seen.add(a["source"])
            unique.append(a)

    return unique


def verify_existing_assets(index: dict) -> List[dict]:
    """验证已有资产的 source 文件是否存在"""
    missing = []
    for cat, data in index.get("categories", {}).items():
        for asset in data.get("assets", []):
            source = asset.get("source", "")
            if source and not (MINE_SEED / source).exists():
                missing.append({
                    "id": asset.get("id", "?"),
                    "name": asset.get("name", "?"),
                    "category": cat,
                    "source": source,
                    "issue": "文件不存在",
                })
    return missing


def generate_next_id(index: dict, category: str) -> str:
    """生成下一个 ID"""
    cat_data = index.get("categories", {}).get(category, {})
    existing = cat_data.get("assets", [])
    max_num = 0
    for asset in existing:
        aid = asset.get("id", "")
        parts = aid.split("-")
        if len(parts) >= 2:
            try:
                num = int(parts[1])
                max_num = max(max_num, num)
            except ValueError:
                pass

    prefix_map = {
        "kernel": "K",
        "blueprint": "B",
        "protocol": "P",
        "constraint": "C",
        "experience": "E",
        "identity": "I",
    }
    prefix = prefix_map.get(category, "X")
    return f"{prefix}-{max_num + 1:03d}"


def fix_index(index: dict, new_assets: List[dict], missing: List[dict]) -> dict:
    """修复索引：添加新资产 + 标记缺失资产"""
    # 1. 标记缺失资产
    for m in missing:
        for cat, data in index.get("categories", {}).items():
            for asset in data.get("assets", []):
                if asset.get("id") == m["id"]:
                    asset["status"] = "missing"
                    logger.warning(f"[FIX] 标记缺失: {m['id']} {m['name']} ({m['source']})")

    # 2. 添加新资产
    added = 0
    for a in sorted(new_assets, key=lambda x: x["category"]):
        cat = a["category"]
        if cat not in index["categories"]:
            index["categories"][cat] = {"count": 0, "assets": []}

        cat_data = index["categories"][cat]
        new_id = generate_next_id(index, cat)

        new_entry = {
            "id": new_id,
            "name": a["name"],
            "desc": a.get("desc_hint", "") or f"自动发现的 {cat} 资产",
            "source": a["source"],
            "added": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
        }

        cat_data["assets"].append(new_entry)
        cat_data["count"] = len(cat_data["assets"])
        added += 1
        logger.info(f"[FIX] 新增资产: {new_id} {a['name']} ({cat}) <- {a['source']}")

    # 3. 重算分数
    index["score"] = {}
    total = 0
    for cat, weight in CATEGORY_WEIGHTS.items():
        count = index.get("categories", {}).get(cat, {}).get("count", 0)
        score = count * weight
        index["score"][cat] = score
        total += score
    index["score"]["total"] = total

    index["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"[FIX] 新增 {added} 个资产，总分: {total}")
    return index


def generate_report(new_assets: List[dict], missing: List[dict]) -> str:
    """生成同步报告"""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# Civilization Index Sync Report — {today}",
        "",
        f"> 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
    ]

    # 缺失资产
    lines.extend([
        f"## 缺失资产（{len(missing)} 个）",
        "",
    ])
    if missing:
        lines.append("| ID | 名称 | 类别 | Source | 问题 |")
        lines.append("|----|------|------|--------|------|")
        for m in missing:
            lines.append(f"| {m['id']} | {m['name']} | {m['category']} | `{m['source']}` | {m['issue']} |")
    else:
        lines.append("无缺失资产。")

    # 新发现资产
    lines.extend([
        "",
        f"## 新发现资产（{len(new_assets)} 个）",
        "",
    ])
    if new_assets:
        lines.append("| 名称 | 类别 | Source | 大小 | 描述 |")
        lines.append("|------|------|--------|------|------|")
        for a in sorted(new_assets, key=lambda x: x["category"]):
            size_kb = a["size"] / 1024
            lines.append(f"| {a['name']} | {a['category']} | `{a['source']}` | {size_kb:.1f}KB | {a.get('desc_hint', '')[:50]} |")
    else:
        lines.append("未发现新资产。")

    # 统计
    cat_counts = {}
    for a in new_assets:
        cat = a["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    lines.extend([
        "",
        "## 分类统计",
        "",
    ])
    for cat in ["kernel", "blueprint", "protocol", "constraint", "experience", "identity"]:
        count = cat_counts.get(cat, 0)
        if count > 0:
            lines.append(f"- **{cat}**: {count} 个")

    lines.extend([
        "",
        "---",
        "",
        "*本报告由 Civilization Index Sync 自动生成。*",
    ])

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="文明索引同步校验器")
    parser.add_argument("--fix", action="store_true", help="自动修复索引（添加新资产）")
    parser.add_argument("--dry-run", action="store_true", help="只报告，不修改")
    parser.add_argument("--all", action="store_true", help="全量扫描（包括 .json、.sh 等）")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("Civilization Index Sync 启动")
    logger.info("=" * 50)

    t0 = time.time()

    # 加载索引
    index = load_index()
    current_total = index.get("score", {}).get("total", 0)
    logger.info(f"[INDEX] 当前总分: {current_total}, 上次更新: {index.get('last_updated', 'unknown')}")

    # 1. 验证已有资产
    logger.info("[STEP 1] 验证已有资产...")
    missing = verify_existing_assets(index)
    if missing:
        logger.warning(f"[VERIFY] 发现 {len(missing)} 个缺失资产")
    else:
        logger.info("[VERIFY] 所有资产 source 文件存在")

    # 2. 扫描新资产
    logger.info("[STEP 2] 扫描新资产...")
    new_assets = scan_new_assets(index)
    if new_assets:
        logger.info(f"[SCAN] 发现 {len(new_assets)} 个潜在新资产")
        for a in new_assets:
            logger.info(f"  + [{a['category']}] {a['name']} <- {a['source']}")
    else:
        logger.info("[SCAN] 未发现新资产")

    # 3. 生成报告
    report_md = generate_report(new_assets, missing)
    report_dir = MINE_SEED / "02_MEMORY" / "recent_memory" / "daily"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"index_sync_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_md)
    logger.info(f"[REPORT] {report_file}")

    # 4. 修复
    if args.fix and new_assets:
        logger.info("[FIX] 开始修复索引...")
        index = fix_index(index, new_assets, missing)
        save_index(index)
        new_total = index.get("score", {}).get("total", 0)
        logger.info(f"[FIX] 索引已更新: {current_total} -> {new_total} (+{new_total - current_total})")
    elif args.dry_run:
        logger.info("[DRY-RUN] 跳过修复")
    elif new_assets:
        logger.info(f"[INFO] 发现 {len(new_assets)} 个新资产，使用 --fix 自动修复")

    elapsed = time.time() - t0
    logger.info(f"[DONE] 耗时: {elapsed:.1f}s")
    print(f"\n索引同步完成: {len(new_assets)} 个新发现, {len(missing)} 个缺失, 报告: {report_file}")


if __name__ == "__main__":
    main()
