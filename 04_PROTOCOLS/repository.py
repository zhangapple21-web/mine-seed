"""---
id: PROTO-021
type: protocol
title: "AUM-003 Civilization Repository — 文明仓库运行时"
status: active
source: "R2: Repository 独立为 Runtime"
created: 2026-07-13
confidence: 0.95
lineage:
  - PROTO-019 (Mission Protocol)
  - PROTO-020 (Admission Engine)
tags: [repository, runtime, asset, civilization]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
"""
AUM-003: Civilization Repository — 文明仓库运行时
=================================================

设计原则：
  Repository 是唯一的文明资产入口。
  任何模块不得绕过 Repository 写入资产。

职责边界：
  repository.py       — 核心模型 + 统一接口
  repository_store.py — 持久化/备份/恢复
  repository_manager.py — 去重/搜索/统计/关系

资产模型（CivilizationAsset）：
  六种类型：Kernel / Blueprint / Protocol / Constraint / Experience / Identity
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


@dataclass
class CivilizationAsset:
    """文明资产 — 统一资产对象"""

    # 标识
    id: str                     # 资产唯一 ID (如 ASSET-KER-0001)
    type: str                   # 资产类型 (kernel/blueprint/protocol/constraint/experience/identity)
    title: str                  # 资产标题

    # 来源
    source_mission: str = ""    # 来源 Mission ID

    # 时间
    created: str = ""           # 创建时间
    updated: str = ""           # 更新时间

    # 版本
    version: str = "1.0.0"      # 版本号

    # 状态
    status: str = "active"      # active / archived / deprecated

    # 内容
    content: str = ""           # 资产内容/描述
    content_hash: str = ""      # 内容哈希（用于去重）

    # 谱系
    lineage: List[str] = field(default_factory=list)  # 父资产 ID 链

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    # 准入信息（保留，用于追溯）
    gates: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "source_mission": self.source_mission,
            "created": self.created,
            "updated": self.updated,
            "version": self.version,
            "status": self.status,
            "content": self.content,
            "content_hash": self.content_hash,
            "lineage": self.lineage,
            "metadata": self.metadata,
            "tags": self.tags,
            "gates": self.gates,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CivilizationAsset":
        """从字典创建资产，兼容旧格式"""
        # 兼容旧格式字段名映射
        asset_id = data.get("id") or data.get("aid", "")
        asset_type = data.get("type") or data.get("asset_type", "")
        title = data.get("title") or data.get("name", "")
        content = data.get("content") or data.get("description", "")
        created = data.get("created") or data.get("admitted_at", "")

        return cls(
            id=asset_id,
            type=asset_type,
            title=title,
            source_mission=data.get("source_mission", ""),
            created=created,
            updated=data.get("updated", created),
            version=data.get("version", "1.0.0"),
            status=data.get("status", "active"),
            content=content,
            content_hash=data.get("content_hash", ""),
            lineage=data.get("lineage", []),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            gates=data.get("gates", {}),
        )


class Repository:
    """文明仓库 — 唯一资产入口

    职责：
      - 提供统一的资产增删改查接口
      - 不处理业务逻辑（去重/搜索由 Manager 处理）
      - 不处理持久化（由 Store 处理）
      - 内存中的资产索引
    """

    def __init__(self):
        self._assets: Dict[str, CivilizationAsset] = {}

    # --------------------------------------------------
    # 核心 CRUD
    # --------------------------------------------------
    def add(self, asset: CivilizationAsset) -> bool:
        """添加资产"""
        if asset.id in self._assets:
            return False
        asset.created = asset.created or datetime.now().isoformat()
        asset.updated = asset.updated or asset.created
        self._assets[asset.id] = asset
        return True

    def remove(self, asset_id: str) -> bool:
        """移除资产"""
        if asset_id not in self._assets:
            return False
        del self._assets[asset_id]
        return True

    def update(self, asset_id: str, changes: Dict[str, Any]) -> bool:
        """更新资产字段"""
        if asset_id not in self._assets:
            return False
        asset = self._assets[asset_id]
        for key, value in changes.items():
            if hasattr(asset, key) and key != "id":
                setattr(asset, key, value)
        asset.updated = datetime.now().isoformat()
        return True

    def get(self, asset_id: str) -> Optional[CivilizationAsset]:
        """获取单个资产"""
        return self._assets.get(asset_id)

    # --------------------------------------------------
    # 查询
    # --------------------------------------------------
    def query(self, **filters) -> List[CivilizationAsset]:
        """条件查询

        支持的过滤条件：
          type=xxx, status=xxx, source_mission=xxx, tag=xxx
        """
        results = list(self._assets.values())
        if "type" in filters:
            results = [a for a in results if a.type == filters["type"]]
        if "status" in filters:
            results = [a for a in results if a.status == filters["status"]]
        if "source_mission" in filters:
            results = [a for a in results if a.source_mission == filters["source_mission"]]
        if "tag" in filters:
            tag = filters["tag"]
            results = [a for a in results if tag in a.tags]
        return results

    def search(self, keyword: str) -> List[CivilizationAsset]:
        """关键词搜索（标题 + 内容）"""
        keyword = keyword.lower()
        results = []
        for asset in self._assets.values():
            if keyword in asset.title.lower() or keyword in asset.content.lower():
                results.append(asset)
        return results

    # --------------------------------------------------
    # 统计
    # --------------------------------------------------
    def stats(self) -> Dict[str, Any]:
        """仓库统计"""
        by_type: Dict[str, int] = {}
        for a in self._assets.values():
            by_type[a.type] = by_type.get(a.type, 0) + 1

        return {
            "total": len(self._assets),
            "by_type": by_type,
            "active": len([a for a in self._assets.values() if a.status == "active"]),
            "archived": len([a for a in self._assets.values() if a.status == "archived"]),
        }

    def lineage(self, asset_id: str) -> List[str]:
        """获取资产谱系（父资产链）"""
        asset = self._assets.get(asset_id)
        if not asset:
            return []
        return asset.lineage

    # --------------------------------------------------
    # 批量操作
    # --------------------------------------------------
    def load_batch(self, assets: List[Dict[str, Any]]) -> int:
        """批量加载资产（用于 Store 恢复数据）"""
        count = 0
        for data in assets:
            try:
                asset = CivilizationAsset.from_dict(data)
                if self.add(asset):
                    count += 1
            except Exception:
                continue
        return count

    def dump_batch(self) -> List[Dict[str, Any]]:
        """批量导出资产（用于 Store 持久化）"""
        return [a.to_dict() for a in self._assets.values()]

    # --------------------------------------------------
    # 内部接口（供 Manager 使用）
    # --------------------------------------------------
    def _all(self) -> Dict[str, CivilizationAsset]:
        """返回全部资产（Manager 专用）"""
        return self._assets
