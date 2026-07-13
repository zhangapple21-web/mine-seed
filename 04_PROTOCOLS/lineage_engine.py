"""
Lineage Engine - 文明资产血缘追踪引擎（最小实现）

功能：
- 给定 asset_id，返回完整血缘链
- 检测孤儿资产（无 origin_mission 记录的）
- 检测断链（parent_asset 指向不存在的资产）

设计原则：
- 轻量：不引入图数据库，纯 JSON + 内存
- 只读：不修改 lineage 数据
- 最小：只做查询和检测，不做写入
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class LineageEngine:
    def __init__(self, index_path: str = None):
        if index_path is None:
            index_path = Path(__file__).parent.parent / "02_MEMORY" / "lineage" / "lineage_index.json"
        self.index_path = Path(index_path)
        self._data: Dict[str, Any] = {}
        self._assets: Dict[str, Any] = {}
        self._load()

    def _load(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        self._assets = self._data.get("assets", {})

    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self._assets.get(asset_id)

    def get_lineage_chain(self, asset_id: str) -> List[Dict[str, Any]]:
        chain = []
        current_id = asset_id
        visited = set()

        while current_id and current_id not in visited:
            visited.add(current_id)
            asset = self._assets.get(current_id)
            if not asset:
                break
            chain.append({
                "asset_id": asset.get("asset_id"),
                "name": asset.get("name"),
                "origin_mission": asset.get("origin_mission"),
                "origin_repository": asset.get("origin_repository"),
                "distillation_date": asset.get("distillation_date"),
                "parent_asset": asset.get("parent_asset"),
                "status": asset.get("status"),
            })
            current_id = asset.get("parent_asset")

        return chain

    def find_orphans(self) -> List[Dict[str, Any]]:
        orphans = []
        for asset_id, asset in self._assets.items():
            origin_mission = asset.get("origin_mission", "")
            if origin_mission and origin_mission.lower().startswith("unknown"):
                orphans.append({
                    "asset_id": asset_id,
                    "name": asset.get("name"),
                    "reason": f"origin_mission = {origin_mission}",
                })
        return orphans

    def find_broken_chains(self) -> List[Dict[str, Any]]:
        broken = []
        for asset_id, asset in self._assets.items():
            parent_id = asset.get("parent_asset")
            if parent_id and parent_id not in self._assets:
                broken.append({
                    "asset_id": asset_id,
                    "name": asset.get("name"),
                    "parent_asset": parent_id,
                    "reason": f"parent_asset '{parent_id}' 不存在",
                })
        return broken

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._assets)
        orphans = len(self.find_orphans())
        broken = len(self.find_broken_chains())

        by_status = {}
        for asset in self._assets.values():
            status = asset.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

        by_category = {}
        for asset in self._assets.values():
            cat = asset.get("category", "unknown")
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_assets": total,
            "orphan_count": orphans,
            "broken_chain_count": broken,
            "by_status": by_status,
            "by_category": by_category,
        }

    def query_by_origin(self, repository: str) -> List[Dict[str, Any]]:
        results = []
        for asset_id, asset in self._assets.items():
            origin = asset.get("origin_repository", "")
            if repository.lower() in origin.lower():
                results.append({
                    "asset_id": asset_id,
                    "name": asset.get("name"),
                    "category": asset.get("category"),
                })
        return results


def main():
    engine = LineageEngine()

    print("=" * 60)
    print("Lineage Engine — Continuity 自检")
    print("=" * 60)

    stats = engine.get_stats()
    print(f"\n[Stats]")
    print(f"  总资产数: {stats['total_assets']}")
    print(f"  孤儿资产: {stats['orphan_count']}")
    print(f"  断链数: {stats['broken_chain_count']}")
    print(f"  按状态分布: {stats['by_status']}")
    print(f"  按类别分布: {stats['by_category']}")

    print(f"\n[Orphan Detection]")
    orphans = engine.find_orphans()
    if orphans:
        for o in orphans:
            print(f"  ⚠ {o['asset_id']} ({o['name']}) — {o['reason']}")
    else:
        print("  ✅ 无孤儿资产")

    print(f"\n[Broken Chain Detection]")
    broken = engine.find_broken_chains()
    if broken:
        for b in broken:
            print(f"  ⚠ {b['asset_id']} ({b['name']}) — {b['reason']}")
    else:
        print("  ✅ 无断链")

    print(f"\n[Sample Lineage Chain]")
    chain = engine.get_lineage_chain("028_ace_civilization_os")
    for i, node in enumerate(chain):
        indent = "  " * i
        print(f"{indent}└─ {node['asset_id']} ({node['name']})")
        print(f"{indent}   Mission: {node['origin_mission']} | Repo: {node['origin_repository']} | Status: {node['status']}")

    print(f"\n[Assets from mine-seed]")
    mine_seed_assets = engine.query_by_origin("mine-seed")
    print(f"  共 {len(mine_seed_assets)} 个")

    print(f"\n[Assets from r1-continuity-backup]")
    r1_assets = engine.query_by_origin("r1-continuity-backup")
    print(f"  共 {len(r1_assets)} 个")

    print("\n" + "=" * 60)
    print("自检完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
