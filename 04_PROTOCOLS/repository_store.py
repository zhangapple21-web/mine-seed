"""---
id: PROTO-022
type: protocol
title: "Repository Store — 持久化层"
status: active
source: "R2: Repository Runtime"
created: 2026-07-13
tags: [repository, store, persistence, backup]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
"""
Repository Store — 持久化层
============================

职责：
  - Repository 数据的保存和加载
  - 备份和恢复
  - 兼容旧格式迁移

不处理：
  - 业务逻辑
  - 去重/搜索
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from repository import Repository

WORKSPACE = Path(__file__).parent.parent


class RepositoryStore:
    """仓库持久化器"""

    def __init__(self, repo: Repository, data_dir: Optional[Path] = None):
        self.repo = repo
        self.data_dir = data_dir or (WORKSPACE / "03_DATA" / "CIV_REPOSITORY")
        self.index_file = self.data_dir / "index.json"
        self.backup_dir = self.data_dir / "backups"

    # --------------------------------------------------
    # 保存
    # --------------------------------------------------
    def save(self) -> bool:
        """保存当前仓库数据到磁盘"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            assets = self.repo.dump_batch()
            by_type: Dict[str, int] = {}
            for a in assets:
                t = a.get("type", "unknown")
                by_type[t] = by_type.get(t, 0) + 1

            data = {
                "version": "2.0.0",
                "updated_at": datetime.now().isoformat(),
                "total_assets": len(assets),
                "by_type": by_type,
                "assets": assets,
            }
            self.index_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            return True
        except Exception:
            return False

    # --------------------------------------------------
    # 加载
    # --------------------------------------------------
    def load(self) -> int:
        """从磁盘加载数据到仓库

        返回加载的资产数量
        兼容旧格式（version 1.0.0）
        """
        if not self.index_file.exists():
            return 0
        try:
            data = json.loads(self.index_file.read_text(encoding="utf-8"))
            assets_data = data.get("assets", [])
            return self.repo.load_batch(assets_data)
        except Exception:
            return 0

    # --------------------------------------------------
    # 备份
    # --------------------------------------------------
    def backup(self, name: Optional[str] = None) -> Optional[Path]:
        """创建备份"""
        if not self.index_file.exists():
            return None
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = name or f"repo_backup_{timestamp}"
            backup_path = self.backup_dir / f"{name}.json"
            shutil.copy2(self.index_file, backup_path)
            return backup_path
        except Exception:
            return None

    # --------------------------------------------------
    # 恢复
    # --------------------------------------------------
    def restore(self, backup_name: str) -> bool:
        """从备份恢复"""
        backup_path = self.backup_dir / f"{backup_name}.json"
        if not backup_path.exists():
            return False
        try:
            # 先备份当前状态
            self.backup(name="auto_before_restore")
            # 恢复
            shutil.copy2(backup_path, self.index_file)
            # 重新加载
            self.repo._assets.clear()
            self.load()
            return True
        except Exception:
            return False

    # --------------------------------------------------
    # 列表
    # --------------------------------------------------
    def list_backups(self) -> List[str]:
        """列出所有备份"""
        if not self.backup_dir.exists():
            return []
        return sorted([f.stem for f in self.backup_dir.glob("*.json")])
