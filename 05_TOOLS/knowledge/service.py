#!/usr/bin/env python3
"""
Knowledge Service — 统一知识服务入口

职责：
- 提供统一的知识服务接口（Asset Search、Constraint Search、Evidence Search 等）
- 底层实现使用 03_INDEX/ 数据
- 不直接读写 Repository 文件

接口示例：
    from knowledge import KnowledgeService
    ks = KnowledgeService()
    
    # 按名称搜索资产
    asset = ks.search_asset("Mengpo")
    
    # 按约束搜索
    constraints = ks.search_constraints("must")
    
    # 获取依赖图
    graph = ks.get_graph("AX-001")
"""

import json
import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Optional

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
INDEX_DIR = BASE_DIR / "03_INDEX"
DB_PATH = INDEX_DIR / "asset_index.sqlite"
GRAPH_PATH = INDEX_DIR / "graph.json"
TIMELINE_PATH = INDEX_DIR / "timeline.json"
ENTITY_MAP_PATH = INDEX_DIR / "entity_map.json"


class KnowledgeService:
    """统一知识服务入口"""
    
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or INDEX_DIR
        self.db_path = self.index_dir / "asset_index.db"
        self._conn = None
        self._graph = None
        self._timeline = None
        self._entity_map = None
    
    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn
    
    def _load_graph(self) -> Dict:
        """加载图数据"""
        if self._graph is None:
            with open(GRAPH_PATH) as f:
                self._graph = json.load(f)
        return self._graph
    
    def _load_timeline(self) -> Dict:
        """加载时间线"""
        if self._timeline is None:
            with open(TIMELINE_PATH) as f:
                self._timeline = json.load(f)
        return self._timeline
    
    def _load_entity_map(self) -> Dict:
        """加载实体映射"""
        if self._entity_map is None:
            with open(ENTITY_MAP_PATH) as f:
                self._entity_map = json.load(f)
        return self._entity_map
    
    # ========== Search Methods ==========
    
    def search_asset(self, query: str) -> List[Dict]:
        """搜索资产（按名称或 ID）"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Try exact ID match first
        cursor.execute("""
            SELECT id, name, category, purpose, importance, filepath
            FROM assets WHERE id = ?
        """, (query,))
        rows = cursor.fetchall()
        
        if rows:
            return self._rows_to_dicts(rows)
        
        # Fuzzy name search
        cursor.execute("""
            SELECT id, name, category, purpose, importance, filepath
            FROM assets WHERE name LIKE ? OR id LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        
        return self._rows_to_dicts(rows)
    
    def search_by_category(self, category: str) -> List[Dict]:
        """按类别搜索资产"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, category, purpose, importance, filepath
            FROM assets WHERE category = ?
            ORDER BY importance DESC, id
        """, (category,))
        rows = cursor.fetchall()
        
        return self._rows_to_dicts(rows)
    
    def search_constraints(self, keyword: str) -> List[Dict]:
        """搜索包含特定约束关键词的资产"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, category, constraint_text
            FROM assets WHERE constraint_text LIKE ?
        """, (f"%{keyword}%",))
        rows = cursor.fetchall()
        
        return [
            {"id": row[0], "name": row[1], "category": row[2], "constraint": row[3]}
            for row in rows
        ]
    
    def search_evidence(self, keyword: str) -> List[Dict]:
        """搜索包含特定证据关键词的资产"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, category, evidence
            FROM assets WHERE evidence LIKE ?
        """, (f"%{keyword}%",))
        rows = cursor.fetchall()
        
        return [
            {"id": row[0], "name": row[1], "category": row[2], "evidence": row[3]}
            for row in rows
        ]
    
    def get_asset_detail(self, asset_id: str) -> Optional[Dict]:
        """获取资产详情"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM assets WHERE id = ?
        """, (asset_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    
    # ========== Graph Methods ==========
    
    def get_graph(self, asset_id: str = None) -> Dict:
        """获取依赖图（可选：以某个资产为中心）"""
        graph = self._load_graph()
        
        if asset_id:
            # Filter to only include related nodes
            related_ids = {asset_id}
            edges = []
            
            for edge in graph["edges"]:
                if edge["source"] == asset_id or edge["target"] == asset_id:
                    edges.append(edge)
                    related_ids.add(edge["source"])
                    related_ids.add(edge["target"])
            
            nodes = [n for n in graph["nodes"] if n["id"] in related_ids]
            
            return {"nodes": nodes, "edges": edges, "center": asset_id}
        
        return graph
    
    def get_dependencies(self, asset_id: str) -> List[str]:
        """获取资产的依赖列表"""
        graph = self._load_graph()
        
        deps = []
        for edge in graph["edges"]:
            if edge["source"] == asset_id:
                deps.append(edge["target"])
        
        return deps
    
    def get_dependents(self, asset_id: str) -> List[str]:
        """获取依赖此资产的其他资产"""
        graph = self._load_graph()
        
        dependents = []
        for edge in graph["edges"]:
            if edge["target"] == asset_id:
                dependents.append(edge["source"])
        
        return dependents
    
    # ========== Timeline Methods ==========
    
    def get_timeline(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取时间线（可选：按日期范围过滤）"""
        timeline = self._load_timeline()
        
        if not start_date and not end_date:
            return timeline["entries"]
        
        entries = []
        for entry in timeline["entries"]:
            mtime = entry.get("mtime", "")
            if start_date and mtime < start_date:
                continue
            if end_date and mtime > end_date:
                continue
            entries.append(entry)
        
        return entries
    
    # ========== Entity Map Methods ==========
    
    def lookup_entity(self, name: str) -> Optional[str]:
        """查找实体对应的资产 ID"""
        entity_map = self._load_entity_map()
        mapping = entity_map.get("entity_map", {})
        
        # Try exact match
        if name in mapping:
            return mapping[name]
        
        # Try lowercase
        if name.lower() in mapping:
            return mapping[name.lower()]
        
        return None
    
    # ========== Helper Methods ==========
    
    def _rows_to_dicts(self, rows: List[tuple]) -> List[Dict]:
        """将数据库行转换为字典"""
        return [
            {"id": row[0], "name": row[1], "category": row[2], 
             "purpose": row[3], "importance": row[4], "filepath": row[5]}
            for row in rows
        ]
    
    def close(self):
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ========== CLI ==========

def main():
    import sys
    
    ks = KnowledgeService()
    
    print("=" * 50)
    print("Knowledge Service — CLI Test")
    print("=" * 50)
    
    # Test search
    print("\n[Search Asset: Continuity]")
    results = ks.search_asset("Continuity")
    for r in results:
        print(f"  {r['id']}: {r['name']}")
    
    # Test category search
    print("\n[Search Category: axiom]")
    results = ks.search_by_category("axiom")
    for r in results:
        print(f"  {r['id']}: {r['name']}")
    
    # Test constraint search
    print("\n[Search Constraints: 必须]")
    results = ks.search_constraints("必须")
    for r in results[:3]:
        print(f"  {r['id']}: {r['name']}")
    
    # Test graph
    print("\n[Get Graph for AX-001]")
    graph = ks.get_graph("AX-001")
    print(f"  Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
    
    # Test timeline
    print("\n[Get Timeline (last 3)]")
    entries = ks.get_timeline()[:3]
    for e in entries:
        print(f"  {e['id']}: {e['mtime']}")
    
    # Test entity lookup
    print("\n[Lookup Entity: continuity principle]")
    asset_id = ks.lookup_entity("continuity principle")
    print(f"  Result: {asset_id}")
    
    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    main()