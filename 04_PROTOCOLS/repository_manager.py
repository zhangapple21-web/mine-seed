"""---
id: PROTO-023
type: protocol
title: "Repository Manager — 管理层"
status: active
source: "R2: Repository Runtime"
created: 2026-07-13
tags: [repository, manager, dedup, search, index]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
"""
Repository Manager — 管理层
============================

职责：
  - 去重
  - 版本升级
  - 搜索增强
  - 索引构建
  - 统计聚合
  - 资产关系

不处理：
  - 持久化（Store 处理）
  - 基础 CRUD（Repository 处理）
"""
from datetime import datetime
from typing import Dict, Any, List, Optional, Set

from repository import Repository, CivilizationAsset


class RepositoryManager:
    """仓库管理器"""

    def __init__(self, repo: Repository):
        self.repo = repo

    # --------------------------------------------------
    # 去重
    # --------------------------------------------------
    def find_duplicates(self) -> List[List[str]]:
        """查找重复资产（按 content_hash）

        返回重复资产 ID 的分组列表
        """
        hash_map: Dict[str, List[str]] = {}
        for aid, asset in self.repo._all().items():
            h = asset.content_hash
            if h:
                hash_map.setdefault(h, []).append(aid)

        return [group for group in hash_map.values() if len(group) > 1]

    def is_duplicate(self, asset: CivilizationAsset) -> bool:
        """判断资产是否已存在"""
        if not asset.content_hash:
            return False
        for existing in self.repo._all().values():
            if existing.content_hash == asset.content_hash:
                return True
            if existing.type == asset.type and existing.title == asset.title:
                return True
        return False

    # --------------------------------------------------
    # 版本升级
    # --------------------------------------------------
    def bump_version(self, asset_id: str) -> bool:
        """升级资产版本号（patch +1）"""
        asset = self.repo.get(asset_id)
        if not asset:
            return False
        try:
            parts = asset.version.split(".")
            parts[2] = str(int(parts[2]) + 1)
            new_version = ".".join(parts)
            self.repo.update(asset_id, {"version": new_version})
            return True
        except Exception:
            return False

    # --------------------------------------------------
    # 搜索增强
    # --------------------------------------------------
    def search_by_type(self, keyword: str, asset_type: str) -> List[CivilizationAsset]:
        """按类型搜索"""
        results = self.repo.search(keyword)
        return [a for a in results if a.type == asset_type]

    def search_by_mission(self, keyword: str, mission_id: str) -> List[CivilizationAsset]:
        """按 Mission 搜索"""
        results = self.repo.search(keyword)
        return [a for a in results if a.source_mission == mission_id]

    # --------------------------------------------------
    # 统计聚合
    # --------------------------------------------------
    def stats_by_mission(self) -> Dict[str, int]:
        """按 Mission 统计资产数"""
        counts: Dict[str, int] = {}
        for asset in self.repo._all().values():
            mid = asset.source_mission or "unknown"
            counts[mid] = counts.get(mid, 0) + 1
        return counts

    def stats_by_tag(self) -> Dict[str, int]:
        """按标签统计资产数"""
        counts: Dict[str, int] = {}
        for asset in self.repo._all().values():
            for tag in asset.tags:
                counts[tag] = counts.get(tag, 0) + 1
        return counts

    def timeline(self) -> List[Dict[str, Any]]:
        """按时间线排列资产"""
        assets = sorted(
            self.repo._all().values(),
            key=lambda a: a.created or "",
        )
        return [
            {
                "id": a.id,
                "type": a.type,
                "title": a.title,
                "created": a.created,
                "mission": a.source_mission,
            }
            for a in assets
        ]

    # --------------------------------------------------
    # 资产关系
    # --------------------------------------------------
    def get_related(self, asset_id: str) -> List[CivilizationAsset]:
        """获取相关资产（同 Mission 或同类型）"""
        asset = self.repo.get(asset_id)
        if not asset:
            return []

        related: List[CivilizationAsset] = []
        for a in self.repo._all().values():
            if a.id == asset_id:
                continue
            # 同 Mission
            if a.source_mission and a.source_mission == asset.source_mission:
                related.append(a)
            # 同类型且有共同标签
            elif a.type == asset.type:
                if set(a.tags) & set(asset.tags):
                    related.append(a)

        return related

    def build_type_index(self) -> Dict[str, List[str]]:
        """构建按类型索引"""
        index: Dict[str, List[str]] = {}
        for aid, asset in self.repo._all().items():
            t = asset.type
            index.setdefault(t, []).append(aid)
        return index

    def build_mission_index(self) -> Dict[str, List[str]]:
        """构建按 Mission 索引"""
        index: Dict[str, List[str]] = {}
        for aid, asset in self.repo._all().items():
            mid = asset.source_mission or "unknown"
            index.setdefault(mid, []).append(aid)
        return index

    # --------------------------------------------------
    # 健康检查
    # --------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """仓库健康检查"""
        duplicates = self.find_duplicates()
        assets = self.repo._all()

        # 检查空内容
        empty_content = [a.id for a in assets.values() if not a.content]

        # 检查缺失来源
        missing_source = [a.id for a in assets.values() if not a.source_mission]

        return {
            "total_assets": len(assets),
            "duplicate_groups": len(duplicates),
            "duplicates": duplicates,
            "empty_content": empty_content,
            "missing_source": missing_source,
            "healthy": len(duplicates) == 0 and len(empty_content) == 0,
        }
