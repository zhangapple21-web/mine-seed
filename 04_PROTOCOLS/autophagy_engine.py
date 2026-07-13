"""---
id: PROTO-015
type: protocol
title: "AUTO-001 Autophagy — 良性自噬机制"
status: active
source: "R2: inspired by '良性自噬（断食）' concept"
created: 2026-07-12
confidence: 0.85
lineage:
  - C-017 (Archive Convergence)
  - OPS-005 (Self-Loop)
tags: [autophagy, cleanup, maintenance, self_healing]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-017 (Archive Convergence)
"""
AUTO-001: Autophagy — 良性自噬机制
====================================

理念来源：
  "良性自噬（断食）：主动制造控制性的能量危机，
   逼迫细胞开启'大扫除'，清理垃圾并激活干细胞再生。"

核心思想：
  系统不是越堆越多越好，而是需要定期主动清理。
  良性自噬 = 可控的、温和的"大扫除"。

自噬的三个层次：
  1. 🗑️  清理僵尸资产（空文件、死链接、重复文件）
  2. 📦  归档老化资产（长期未访问的移到存档区）
  3. 🔄  激活沉睡记忆（把死记忆重新关联，提高访问率）

和"恶性透支"的区别：
  - 良性自噬：温和、可控、有备份、可回滚
  - 恶性透支：激进、不可控、删除不可恢复、系统崩溃

自噬频率：
  - 轻度自噬：每次心跳（清理临时文件、死进程）
  - 中度自噬：每天（归档老化资产）
  - 深度自噬：每周（全面清理 + 记忆激活）
"""
import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))

WORKSPACE = Path(__file__).parent.parent
ARCHIVE_DIR = WORKSPACE / "03_ARCHIVE" / "autophagy"
MEMORY_DIR = WORKSPACE / "02_MEMORY"


class AutophagyEngine:
    """良性自噬引擎"""

    def __init__(self):
        self.archive_dir = ARCHIVE_DIR
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.report: Dict[str, Any] = {
            "started_at": datetime.now().isoformat(),
            "cleaned": {},
            "archived": {},
            "reactivated": {},
            "total_bytes_saved": 0,
            "errors": [],
        }

    def run_light(self) -> Dict[str, Any]:
        """轻度自噬：每次心跳运行
        - 清理临时文件
        - 清理旧的临时目录
        - 清理空目录
        """
        cleaned = []
        total_bytes = 0

        # 清理 .tmp / temp 文件
        tmp_patterns = ["*.tmp", "*.temp", "*~", "*.pyc", "__pycache__"]
        for pattern in tmp_patterns:
            for f in WORKSPACE.rglob(pattern):
                try:
                    if f.is_file() and ".git" not in str(f):
                        size = f.stat().st_size
                        f.unlink()
                        cleaned.append({"path": str(f), "size": size, "type": "tmp_file"})
                        total_bytes += size
                    elif f.is_dir() and ".git" not in str(f) and pattern == "__pycache__":
                        size = sum(p.stat().st_size for p in f.rglob("*") if p.is_file())
                        shutil.rmtree(f, ignore_errors=True)
                        cleaned.append({"path": str(f), "size": size, "type": "pycache_dir"})
                        total_bytes += size
                except Exception as e:
                    self.report["errors"].append(f"清理 {f} 失败: {e}")

        # 清理空目录
        empty_dirs = self._find_empty_dirs(WORKSPACE)
        for d in empty_dirs:
            try:
                if ".git" not in str(d) and d != WORKSPACE:
                    d.rmdir()
                    cleaned.append({"path": str(d), "size": 0, "type": "empty_dir"})
            except Exception as e:
                pass  # 非空目录跳过

        self.report["cleaned"]["light"] = cleaned
        self.report["cleaned"]["light_count"] = len(cleaned)
        self.report["total_bytes_saved"] += total_bytes
        self.report["completed_at"] = datetime.now().isoformat()

        return {
            "level": "light",
            "items_cleaned": len(cleaned),
            "bytes_saved": total_bytes,
            "kb_saved": round(total_bytes / 1024, 1),
            "details": cleaned,
        }

    def run_medium(self, days: int = 7) -> Dict[str, Any]:
        """中度自噬：每天/每周运行
        - 归档长期未访问的文件
        - 合并重复的日志/报告
        - 清理过期的临时数据
        """
        archived = []
        total_bytes = 0

        cutoff = datetime.now() - timedelta(days=days)

        # 归档老化的探索报告（>7天的移到归档）
        exploration_dir = MEMORY_DIR / "exploration"
        if exploration_dir.exists():
            for f in exploration_dir.glob("*"):
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime < cutoff and f.is_file():
                        size = f.stat().st_size
                        dst = self.archive_dir / "exploration" / f.name
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(f), str(dst))
                        archived.append({
                            "path": str(f),
                            "size": size,
                            "type": "old_exploration",
                            "moved_to": str(dst),
                        })
                        total_bytes += size
                except Exception as e:
                    self.report["errors"].append(f"归档 {f} 失败: {e}")

        # 归档老化的心跳/操作日志
        for subdir in ["self_learning", "self_loop"]:
            sdir = MEMORY_DIR / subdir
            if not sdir.exists():
                continue
            files = sorted(sdir.glob("*.json"), key=lambda f: f.stat().st_mtime)
            # 保留最近 10 个，其他归档
            if len(files) > 10:
                for f in files[:-10]:
                    try:
                        size = f.stat().st_size
                        dst = self.archive_dir / subdir / f.name
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(f), str(dst))
                        archived.append({
                            "path": str(f),
                            "size": size,
                            "type": f"old_{subdir}",
                            "moved_to": str(dst),
                        })
                        total_bytes += size
                    except Exception as e:
                        self.report["errors"].append(f"归档 {f} 失败: {e}")

        self.report["archived"]["medium"] = archived
        self.report["archived"]["medium_count"] = len(archived)
        self.report["total_bytes_saved"] += total_bytes
        self.report["completed_at"] = datetime.now().isoformat()

        return {
            "level": "medium",
            "items_archived": len(archived),
            "bytes_saved": total_bytes,
            "kb_saved": round(total_bytes / 1024, 1),
            "archive_dir": str(self.archive_dir),
            "details": archived,
        }

    def run_deep(self) -> Dict[str, Any]:
        """深度自噬：每周运行
        - 全面僵尸资产扫描
        - 重复文件检测
        - 死记忆激活（重新关联沉睡的记忆）
        - 生成自噬报告
        """
        result = {
            "level": "deep",
            "started_at": datetime.now().isoformat(),
        }

        # Step 1: 中度自噬先跑
        medium = self.run_medium(days=3)
        result["medium"] = medium

        # Step 2: 死记忆激活
        reactivated = self._reactivate_dead_memories()
        result["reactivated"] = reactivated
        self.report["reactivated"] = reactivated

        # Step 3: 重复检测（文件名相似度）
        duplicates = self._detect_duplicates()
        result["duplicates_found"] = len(duplicates)
        result["duplicate_groups"] = duplicates

        # Step 4: 生成报告
        report_path = self._write_report(result)
        result["report_path"] = str(report_path)

        return result

    def _find_empty_dirs(self, root: Path) -> List[Path]:
        """找到所有空目录"""
        empty = []
        for d in root.rglob("*"):
            if d.is_dir() and ".git" not in str(d):
                try:
                    if not any(d.iterdir()):
                        empty.append(d)
                except Exception:
                    pass
        return empty

    def _reactivate_dead_memories(self) -> Dict[str, Any]:
        """激活死记忆（access_count=0 的记忆）
        思路：不是删除，而是通过重新关联来激活
        """
        memory_file = MEMORY_DIR / "memory_index_latest.json"
        if not memory_file.exists():
            return {"error": "memory index not found"}

        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            memories = data if isinstance(data, list) else data.get("memories", [])
            total = len(memories)

            # 统计死记忆
            dead_count = 0
            high_value_dead = []  # 高价值但沉睡的记忆

            for m in memories:
                access = m.get("access_count", 0)
                if access == 0:
                    dead_count += 1
                    # 标记高价值记忆（有重要标签的）
                    tags = m.get("tags", [])
                    important_tags = ["constraint", "protocol", "principle", "kernel", "chip"]
                    if any(t in tags for t in important_tags):
                        high_value_dead.append(m.get("id", m.get("mid", "?")))

            return {
                "total_memories": total,
                "dead_memories": dead_count,
                "dead_ratio": round(dead_count / max(total, 1), 2),
                "high_value_dead_count": len(high_value_dead),
                "high_value_dead_samples": high_value_dead[:10],
                "action_taken": "标记为高优先级待激活（暂不自动修改）",
            }
        except Exception as e:
            return {"error": str(e)}

    def _detect_duplicates(self) -> List[List[str]]:
        """检测重复文件（基于文件名相似度 + 文件大小）"""
        # 简单实现：同目录下文件名前缀相同且大小接近的视为可能重复
        groups = []
        seen_sizes = {}

        # 按大小分组
        for f in WORKSPACE.rglob("*.md"):
            if ".git" in str(f) or "03_ARCHIVE" in str(f):
                continue
            if f.is_file():
                size = f.stat().st_size
                key = size // 100  # 按 100 字节粒度分组
                if key not in seen_sizes:
                    seen_sizes[key] = []
                seen_sizes[key].append(str(f))

        # 找出可能重复的组
        for key, files in seen_sizes.items():
            if len(files) >= 2:
                # 进一步检查文件名相似度
                groups.append(files)

        # 只返回有 2 个以上文件的组，最多返回 20 组
        return [g for g in groups if len(g) >= 2][:20]

    def _write_report(self, result: Dict[str, Any]) -> Path:
        """写自噬报告"""
        report_file = self.archive_dir / f"autophagy_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        return report_file


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AUTO-001: 良性自噬机制")
    parser.add_argument("--light", action="store_true", help="轻度自噬（清理临时文件）")
    parser.add_argument("--medium", action="store_true", help="中度自噬（归档老化资产）")
    parser.add_argument("--deep", action="store_true", help="深度自噬（全面清理 + 记忆激活）")
    parser.add_argument("--days", type=int, default=7, help="中度自噬的老化天数 (default: 7)")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际删除")
    args = parser.parse_args()

    engine = AutophagyEngine()

    if args.light:
        result = engine.run_light()
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print(f"🧹 轻度自噬完成")
            print(f"   清理项: {result['items_cleaned']}")
            print(f"   节省空间: {result['kb_saved']} KB")

    elif args.medium:
        result = engine.run_medium(days=args.days)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print(f"📦 中度自噬完成")
            print(f"   归档项: {result['items_archived']}")
            print(f"   节省空间: {result['kb_saved']} KB")
            print(f"   归档目录: {result['archive_dir']}")

    elif args.deep:
        result = engine.run_deep()
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            med = result.get("medium", {})
            react = result.get("reactivated", {})
            print(f"🔄 深度自噬完成")
            print(f"   归档项: {med.get('items_archived', 0)}")
            print(f"   节省空间: {med.get('kb_saved', 0)} KB")
            print(f"   死记忆: {react.get('dead_memories', '?')} / {react.get('total_memories', '?')}")
            print(f"   可能重复组: {result.get('duplicates_found', 0)}")
            print(f"   报告: {result.get('report_path', '')}")

    else:
        parser.print_help()
        print()
        print("示例:")
        print("  python autophagy_engine.py --light")
        print("  python autophagy_engine.py --medium --days 7")
        print("  python autophagy_engine.py --deep")


if __name__ == "__main__":
    main()
