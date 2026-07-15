#!/usr/bin/env python3
"""
Civilization Map Auto-Sync Daemon — 文明地图自动同步守护进程

Mission: AUM-MISSION-MAP-007
Identity: 让文明地图自我更新，不再需要人工维护
Version: v1.0 (2026-07-15)

Core Flow:
    扫描目录变化 → 检测新组件 → 生成Mermaid → 备份 → 更新地图 → TG通知

设计原则:
    1. 自我认知：系统自己更新自己的地图
    2. 可回滚：每次更新前备份
    3. 可审计：每次更新记录变更日志
    4. 事件驱动：响应 NewAssetAdmitted 事件
    5. 不打扰：只在真正有变化时更新

触发条件:
    - 每 4 小时定时扫描
    - 收到 NewAssetAdmitted 事件
    - 手动触发（--sync）
"""

import os
import sys
import json
import time
import logging
import hashlib
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional

WORKSPACE = Path(__file__).parent.parent.parent
MAP_FILE = WORKSPACE / "02_MEMORY" / "civilization_map.md"
BACKUP_DIR = WORKSPACE / "02_MEMORY" / "backups"
ASSETS_DIR = WORKSPACE / "02_MEMORY" / "civilization_assets"
PROTOCOLS_DIR = WORKSPACE / "04_PROTOCOLS"
RUNTIME_DIR = WORKSPACE / "06_RUNTIME"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

log = logging.getLogger("ACE.MapSync")
log.setLevel(logging.INFO)
fh = logging.FileHandler(WORKSPACE / "02_MEMORY" / "logs" / f"map_sync_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
log.addHandler(fh)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
log.addHandler(ch)


def hash_file(file_path: Path) -> str:
    """计算文件哈希"""
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:12]
    except:
        return ""


def scan_assets() -> Dict[str, Dict]:
    """扫描文明资产目录"""
    assets = {}
    if not ASSETS_DIR.exists():
        return assets

    for f in sorted(ASSETS_DIR.glob("*.md")):
        if f.name.startswith("_") or f.name == "ASSET_INDEX.md":
            continue
        assets[f.name] = {
            "path": str(f.relative_to(WORKSPACE)),
            "hash": hash_file(f),
            "mtime": f.stat().st_mtime
        }
    return assets


def scan_protocols() -> Dict[str, Dict]:
    """扫描协议层引擎"""
    engines = {}
    engine_patterns = ["*engine*.py", "*factory*.py", "*gate*.py", "*discovery*.py"]
    for pattern in engine_patterns:
        for f in PROTOCOLS_DIR.glob(pattern):
            engines[f.name] = {
                "path": str(f.relative_to(WORKSPACE)),
                "hash": hash_file(f),
                "mtime": f.stat().st_mtime
            }
    return engines


def scan_runtime() -> Dict[str, Dict]:
    """扫描运行时守护进程"""
    daemons = {}
    for f in RUNTIME_DIR.rglob("daemon.py"):
        name = f.parent.name + "_daemon"
        daemons[name] = {
            "path": str(f.relative_to(WORKSPACE)),
            "hash": hash_file(f),
            "mtime": f.stat().st_mtime
        }
    return daemons


def detect_changes(last_state: Dict, current_state: Dict) -> List[str]:
    """检测变化"""
    changes = []
    last_keys = set(last_state.keys())
    current_keys = set(current_state.keys())

    # 新增
    for key in current_keys - last_keys:
        changes.append(f"NEW: {key}")

    # 删除
    for key in last_keys - current_keys:
        changes.append(f"DELETED: {key}")

    # 修改
    for key in last_keys & current_keys:
        if last_state[key]["hash"] != current_state[key]["hash"]:
            changes.append(f"MODIFIED: {key}")

    return changes


def backup_map():
    """备份当前地图"""
    if MAP_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"civilization_map_{timestamp}.md"
        with open(MAP_FILE, "r", encoding="utf-8") as src:
            with open(backup_file, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        log.info(f"[BACKUP] civilization_map.md → {backup_file.name}")
        return backup_file.name
    return None


def generate_engine_section(protocols: Dict) -> str:
    """生成引擎表格"""
    lines = []
    lines.append("| 引擎 | 文件 | 行数 |")
    lines.append("|------|------|------|")

    engine_names = {
        "law_discovery.py": "Law Discovery",
        "trigger_engine.py": "Trigger Engine",
        "distillation_factory.py": "Distillation Factory",
        "smelter_gate.py": "Smelter Gate",
    }

    for name, info in sorted(protocols.items()):
        display_name = engine_names.get(name, name.replace(".py", ""))
        path = info["path"]
        try:
            line_count = sum(1 for _ in open(WORKSPACE / path, "r", encoding="utf-8"))
        except:
            line_count = "?"
        lines.append(f"| **{display_name}** | [{name}]({path}) | {line_count}+ |")

    return "\n".join(lines)


def generate_daemon_section(runtime: Dict) -> str:
    """生成守护进程表格"""
    lines = []
    lines.append("| 守护进程 | 文件 |")
    lines.append("|----------|------|")

    for name, info in sorted(runtime.items()):
        lines.append(f"| {name.replace('_daemon', '')} | [{info['path']}] |")

    return "\n".join(lines)


def generate_assets_section(assets: Dict) -> str:
    """生成资产统计"""
    return f"{len(assets)}+ 资产"


def update_map(assets: Dict, protocols: Dict, runtime: Dict) -> bool:
    """更新文明地图"""
    if not MAP_FILE.exists():
        log.warning("[UPDATE] civilization_map.md not found, skipping")
        return False

    backup_map()

    with open(MAP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新引擎表格
    engine_section = generate_engine_section(protocols)
    old_engine_table = content.find("| 引擎 | 文件 | 行数 |")
    if old_engine_table != -1:
        start = content.rfind("\n", 0, old_engine_table) + 1
        end = content.find("\n\n", old_engine_table)
        if end == -1:
            end = content.find("\n---", old_engine_table)
        if end != -1:
            content = content[:start] + engine_section + content[end:]
            log.info("[UPDATE] Engine table updated")

    # 更新守护进程表格
    daemon_section = generate_daemon_section(runtime)
    old_daemon_table = content.find("| 守护进程 | 文件 |")
    if old_daemon_table != -1:
        start = content.rfind("\n", 0, old_daemon_table) + 1
        end = content.find("\n\n", old_daemon_table)
        if end != -1:
            content = content[:start] + daemon_section + content[end:]
            log.info("[UPDATE] Daemon table updated")

    # 更新资产数量
    asset_count = generate_assets_section(assets)
    content = content.replace("28+ 资产", asset_count)
    content = content.replace("28 个资产", f"{len(assets)} 个资产")

    # 更新版本和时间戳
    content = content.replace(
        "更新时间：2026-07-15",
        f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    content = content.replace(
        "v4 (2026-07-15)",
        f"v4 ({datetime.now().strftime('%Y-%m-%d')})"
    )

    with open(MAP_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    log.info("[UPDATE] civilization_map.md updated successfully")
    return True


def send_notification(changes: List[str], stats: Dict):
    """发送TG通知"""
    bot_token = os.environ.get("TG_BOT_TOKEN_2", "")
    chat_id = "5016609451"
    if not bot_token:
        return

    message = (
        f"🗺️ ACE Map Sync Update\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Changes detected: {len(changes)}\n"
    )

    for change in changes[:10]:
        message += f"  • {change}\n"

    message += (
        f"\nAssets: {stats['assets']}\n"
        f"Engines: {stats['engines']}\n"
        f"Daemons: {stats['daemons']}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({
        "chat_id": chat_id,
        "text": message
    }).encode("utf-8")

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=15)
            log.info(f"[NOTIFY] Sent to {chat_id}")
            return
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
            else:
                log.warning(f"[NOTIFY] Failed: {e}")


def load_last_state() -> Dict:
    """加载上次扫描状态"""
    state_file = WORKSPACE / "02_MEMORY" / "map_sync_state.json"
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"assets": {}, "protocols": {}, "runtime": {}}


def save_state(state: Dict):
    """保存扫描状态"""
    state_file = WORKSPACE / "02_MEMORY" / "map_sync_state.json"
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def run_sync() -> Dict:
    """执行一次同步扫描"""
    log.info("=" * 50)
    log.info("Map Sync Scan Started")
    log.info("=" * 50)

    last_state = load_last_state()

    # 扫描当前状态
    assets = scan_assets()
    protocols = scan_protocols()
    runtime = scan_runtime()

    # 检测变化
    asset_changes = detect_changes(last_state.get("assets", {}), assets)
    protocol_changes = detect_changes(last_state.get("protocols", {}), protocols)
    runtime_changes = detect_changes(last_state.get("runtime", {}), runtime)

    all_changes = asset_changes + protocol_changes + runtime_changes

    if all_changes:
        log.info(f"[CHANGE] {len(all_changes)} changes detected")
        for change in all_changes:
            log.info(f"  • {change}")

        # 更新地图
        if update_map(assets, protocols, runtime):
            # 保存新状态
            save_state({"assets": assets, "protocols": protocols, "runtime": runtime})
            # 发送通知
            send_notification(all_changes, {
                "assets": len(assets),
                "engines": len(protocols),
                "daemons": len(runtime)
            })
    else:
        log.info("[CHANGE] No changes detected")

    log.info(f"Scan complete: {len(assets)} assets, {len(protocols)} engines, {len(runtime)} daemons")
    return {"changes": len(all_changes), "updated": len(all_changes) > 0}


def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(description="Civilization Map Auto-Sync Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (every 4 hours)")
    parser.add_argument("--sync", action="store_true", help="Run one sync and exit")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if not args.verbose:
        log.handlers = [fh]

    log.info("=" * 60)
    log.info("ACE Civilization Map Auto-Sync Daemon v1.0")
    log.info("=" * 60)

    if args.sync:
        run_sync()
        return

    if not args.daemon:
        log.info("Use --daemon for 4h mode, --sync for single sync")
        return

    log.info("[DAEMON] Cycle interval: 4 hours")

    while True:
        try:
            run_sync()
            log.info("[DAEMON] Sleeping 4 hours...")
            time.sleep(4 * 3600)
        except KeyboardInterrupt:
            log.info("[DAEMON] Interrupted, shutting down...")
            break
        except Exception as e:
            log.error(f"[DAEMON] Error: {e}")
            time.sleep(300)  # 5分钟后重试


if __name__ == "__main__":
    main()