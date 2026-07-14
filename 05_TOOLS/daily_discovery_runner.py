#!/usr/bin/env python3
"""
Daily Discovery Runner — 每日发现协议自动化执行器

DAILY-001 协议：三方向扫描
1. TG收藏夹增量
2. 仓库未开采部分
3. 本地文件

用法:
  python daily_discovery_runner.py           # 立即执行
  python daily_discovery_runner.py --schedule  # 注册 Windows 定时任务
  python daily_discovery_runner.py --check    # 检查上次运行状态
"""

import os
import sys
import json
import subprocess
import argparse
import time
import traceback
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
DISCOVERY_DIR = WORKSPACE / "02_MEMORY" / "discovery_queue"
LOG_FILE = WORKSPACE / "05_TOOLS" / "mine_output" / "discovery" / "daily_discovery.log"
STATUS_FILE = WORKSPACE / "05_TOOLS" / "mine_output" / "discovery" / "discovery_status.json"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


class RunnerLogger:
    def __init__(self, log_file: Path):
        self.log_file = log_file

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"
        print(log_line.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)


class RunnerStatus:
    def __init__(self, status_file: Path):
        self.status_file = status_file
        self.status = self._load_status()

    def _load_status(self) -> dict:
        if self.status_file.exists():
            try:
                return json.loads(self.status_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {
            "last_run_time": "",
            "last_run_success": False,
            "discoveries": [],
            "error_message": "",
        }

    def save_status(self, success: bool, discoveries: list = None, error_message: str = ""):
        self.status = {
            "last_run_time": datetime.now().isoformat(),
            "last_run_success": success,
            "discoveries": discoveries or [],
            "error_message": error_message,
        }
        self.status_file.write_text(json.dumps(self.status, ensure_ascii=False, indent=2), encoding='utf-8')

    def get_status(self) -> dict:
        return self.status


def run_discovery(logger: RunnerLogger) -> tuple[bool, list]:
    """运行每日发现协议"""
    logger.log("[DAILY-001] 开始每日发现扫描...")

    discoveries = []

    # 方向1: TG收藏夹增量扫描
    logger.log("[1/3] 扫描 TG 收藏夹增量...")
    try:
        tg_discoveries = scan_tg_favorites()
        discoveries.extend(tg_discoveries)
        logger.log(f"  ✓ TG收藏夹扫描完成，发现 {len(tg_discoveries)} 项")
    except Exception as e:
        logger.log(f"  ⚠ TG收藏夹扫描失败: {e}", "WARNING")

    # 方向2: 仓库未开采部分扫描
    logger.log("[2/3] 扫描仓库未开采部分...")
    try:
        repo_discoveries = scan_repository()
        discoveries.extend(repo_discoveries)
        logger.log(f"  ✓ 仓库扫描完成，发现 {len(repo_discoveries)} 项")
    except Exception as e:
        logger.log(f"  ⚠ 仓库扫描失败: {e}", "WARNING")

    # 方向3: 本地文件扫描
    logger.log("[3/3] 扫描本地文件...")
    try:
        local_discoveries = scan_local_files()
        discoveries.extend(local_discoveries)
        logger.log(f"  ✓ 本地文件扫描完成，发现 {len(local_discoveries)} 项")
    except Exception as e:
        logger.log(f"  ⚠ 本地文件扫描失败: {e}", "WARNING")

    # 保存发现清单
    if discoveries:
        save_discovery_report(discoveries)
        logger.log(f"  ✓ 发现清单已保存，共 {len(discoveries)} 项")
    else:
        logger.log(f"  ⚠ 未发现任何新内容")

    return len(discoveries) > 0, discoveries


def scan_tg_favorites() -> list:
    """扫描 TG 收藏夹增量"""
    discoveries = []
    
    # 检查上次扫描时间
    last_scan_file = WORKSPACE / "02_MEMORY" / "environment" / "latest_scan.json"
    if last_scan_file.exists():
        try:
            scan_data = json.loads(last_scan_file.read_text(encoding='utf-8'))
            last_tg_time = scan_data.get("tg_favorites_last_update", "")
            discoveries.append({
                "type": "tg_favorites",
                "title": "TG收藏夹状态",
                "description": f"上次扫描时间: {last_tg_time}",
                "evidence_level": "Partial",
                "action": "记录状态",
            })
        except Exception:
            pass

    return discoveries


def scan_repository() -> list:
    """扫描仓库未开采部分"""
    discoveries = []

    # 检查 02_MEMORY 目录下未被索引的文件
    memory_dir = WORKSPACE / "02_MEMORY"
    index_file = WORKSPACE / "03_INDEX" / "ASSET_INDEX.md"
    
    indexed_files = set()
    if index_file.exists():
        try:
            content = index_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if 'file:///' in line or '.md' in line or '.json' in line:
                    import re
                    match = re.search(r'([a-zA-Z0-9_.-]+\.(md|json|py))', line)
                    if match:
                        indexed_files.add(match.group(1))
        except Exception:
            pass

    # 扫描 memory 目录
    for filepath in memory_dir.rglob('*.md'):
        filename = filepath.name
        if filename not in indexed_files:
            discoveries.append({
                "type": "repository",
                "title": f"未索引文件: {filename}",
                "description": f"路径: {filepath.relative_to(WORKSPACE)}",
                "evidence_level": "Partial",
                "action": "评估是否需要索引",
            })
            if len(discoveries) >= 10:
                break

    return discoveries


def scan_local_files() -> list:
    """扫描本地文件"""
    discoveries = []

    # 检查文明地图和工具清单
    files_to_check = [
        ("civilization_map.md", "文明地图"),
        ("TOOLS.md", "工具清单"),
        ("AGENTS.md", "代理清单"),
        ("CIVILIZATION.md", "文明宣言"),
    ]

    for filename, name in files_to_check:
        filepath = WORKSPACE / filename
        if filepath.exists():
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            discoveries.append({
                "type": "local_file",
                "title": f"{name} 状态",
                "description": f"最后修改: {mtime}, 大小: {filepath.stat().st_size} bytes",
                "evidence_level": "Verified",
                "action": "记录状态",
            })

    return discoveries


def save_discovery_report(discoveries: list):
    """保存发现清单"""
    today = datetime.now().strftime('%Y%m%d')
    today_full = datetime.now().strftime('%Y-%m-%d')
    
    report = f"""# 每日发现清单 — {today_full}

> **Mission**: AUM-MISSION-DAILY-001（每日有限考古协议）
> **运行者**: Daily Discovery Runner
> **运行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **发现数量**: {len(discoveries)}

---

## 扫描结果

"""

    for i, disc in enumerate(discoveries, 1):
        report += f"""### 发现 {i}: {disc.get('title', '未知')}

| 字段 | 值 |
|------|-----|
| **类型** | {disc.get('type', 'unknown')} |
| **描述** | {disc.get('description', '-')} |
| **证据等级** | {disc.get('evidence_level', 'Unknown')} |
| **建议动作** | {disc.get('action', '记录')} |

"""

    report += """---

## 后续处理

- 发现仅记录，不直接实现
- 值得升级的发现会在后续 Mission 中处理
- 重复发现会被标记为 Duplicate

---

> **免责声明**: 本报告由AI自动生成，仅供参考。

"""

    output_file = DISCOVERY_DIR / f"daily_discovery_{today}.md"
    output_file.write_text(report, encoding='utf-8')


def run_all(logger: RunnerLogger, status_manager: RunnerStatus):
    """执行完整流程"""
    logger.log("=" * 60)
    logger.log(f"每日发现协议启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.log("=" * 60)

    start_time = time.time()
    success = False
    discoveries = []

    try:
        success, discoveries = run_discovery(logger)
    except Exception as e:
        success = False
        logger.log(f"  ✗ 执行异常: {e}", "ERROR")
        logger.log(f"  异常详情: {traceback.format_exc()[:500]}", "DEBUG")

    elapsed = time.time() - start_time
    logger.log(f"\n{'='*60}")
    logger.log(f"执行完成，耗时 {elapsed:.1f} 秒")
    logger.log(f"整体状态: {'✓ 成功' if success else '✗ 失败'}")
    logger.log(f"发现数量: {len(discoveries)}")
    logger.log(f"{'='*60}")

    status_manager.save_status(success=success, discoveries=discoveries)


def schedule_task():
    """注册 Windows 定时任务（每日收盘后 16:30 执行）"""
    print("注册每日发现协议定时任务...")

    task_name = "ACE_DailyDiscovery"
    script_path = Path(__file__).resolve()
    python_path = sys.executable

    cmd = (
        f'schtasks /create /tn "{task_name}" '
        f'/tr "\\"{python_path}\" \\"{script_path}\"" '
        f'/sc daily /st 16:30 '
        f'/f /ru SYSTEM'
    )

    print(f"\n命令: {cmd}")
    print("\n请手动以管理员身份运行以下命令:")
    print(cmd)
    print("\n或者使用 Windows Task Scheduler GUI 创建任务:")
    print(f"  程序: {python_path}")
    print(f"  参数: {script_path}")
    print(f"  触发器: 每天 16:30")
    print(f"  运行身份: SYSTEM")


def check_status():
    """检查上次运行状态"""
    status_manager = RunnerStatus(STATUS_FILE)
    status = status_manager.get_status()

    print("\n上次运行状态:")
    print(f"  时间: {status.get('last_run_time', '未运行')}")
    print(f"  结果: {'✓ 成功' if status.get('last_run_success') else '✗ 失败'}")

    if status.get('error_message'):
        print(f"  错误: {status['error_message']}")

    if status.get('discoveries'):
        disc_count = len(status['discoveries'])
        print(f"  发现数量: {disc_count}")
        for i, disc in enumerate(status['discoveries'][:5], 1):
            print(f"    {i}. {disc.get('title', '未知')}")
        if disc_count > 5:
            print(f"    ... 还有 {disc_count - 5} 项")


def main():
    parser = argparse.ArgumentParser(description="Daily Discovery Runner")
    parser.add_argument("--schedule", action="store_true", help="Show schedule command")
    parser.add_argument("--check", action="store_true", help="Check last run status")
    args = parser.parse_args()

    logger = RunnerLogger(LOG_FILE)
    status_manager = RunnerStatus(STATUS_FILE)

    if args.schedule:
        schedule_task()
    elif args.check:
        check_status()
    else:
        run_all(logger, status_manager)


if __name__ == "__main__":
    main()