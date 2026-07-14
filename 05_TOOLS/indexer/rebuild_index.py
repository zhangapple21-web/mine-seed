#!/usr/bin/env python3
"""
Index Builder — 从 Repository 重建索引

职责：
1. 扫描 02_MEMORY/assets/ 下的所有资产文件
2. 提取元数据（Name、Origin、Purpose、Constraints、Evidence、Dependencies 等）
3. 写入 03_INDEX/asset_index.db（SQLite）
4. 生成 graph.json（资产依赖关系）
5. 生成 timeline.json（按创建/修改时间排序）
6. 生成 entity_map.json（将实体名映射到资产 ID）

核心原则：
- Repository 是唯一真相源
- Index 从 Repository 派生，可随时重建
- Index Builder 只读不写 Repository
"""

import os
import re
import json
import sqlite3
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Paths
BASE_DIR = Path(__file__).parent.parent.parent  # mine-seed/
REPO_DIR = BASE_DIR / "02_MEMORY" / "assets"
INDEX_DIR = BASE_DIR / "03_INDEX"

DB_PATH = INDEX_DIR / "asset_index.db"
GRAPH_PATH = INDEX_DIR / "graph.json"
TIMELINE_PATH = INDEX_DIR / "timeline.json"
ENTITY_MAP_PATH = INDEX_DIR / "entity_map.json"


def extract_metadata(content: str, filepath: Path) -> Dict:
    """从 Markdown 资产文件提取元数据"""
    metadata = {
        "id": "",
        "name": "",
        "category": "",
        "origin": "",
        "purpose": "",
        "problem": "",
        "constraint": "",
        "evidence": "",
        "distillation": "",
        "related_assets": [],
        "replaceable": "",
        "rebuildable": "",
        "importance": 0,
        "distill_score": 0,
        "filepath": str(filepath),
        "filename": filepath.name,
        "mtime": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
        "hash": hashlib.md5(content.encode()).hexdigest()[:8],
    }
    
    # Extract ID from filename (e.g., AX-001-continuity-principle.md -> AX-001)
    match = re.match(r"^([A-Z]+-\d+)", filepath.name)
    if match:
        metadata["id"] = match.group(1)
    
    # Extract category from path (e.g., axiom, principle, governance...)
    parts = filepath.parts
    if "assets" in parts:
        idx = parts.index("assets")
        if idx + 1 < len(parts):
            metadata["category"] = parts[idx + 1]
    
    # Parse Markdown sections
    sections = {}
    current_section = ""
    current_content = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = "\n".join(current_content).strip()
    
    # Map sections to metadata
    metadata["name"] = sections.get("Name", "")
    if not metadata["name"]:
        # Try to extract from first # header
        first_header = re.search(r"^# (.+)$", content, re.MULTILINE)
        if first_header:
            metadata["name"] = first_header.group(1).split("—")[0].strip()
    
    metadata["origin"] = sections.get("Origin", "")
    metadata["purpose"] = sections.get("Purpose", "")
    metadata["problem"] = sections.get("Problem", "")
    metadata["constraint"] = sections.get("Constraint", "")
    metadata["evidence"] = sections.get("Evidence", "")
    metadata["distillation"] = sections.get("Distillation", "")
    metadata["replaceable"] = sections.get("Replaceable", "")
    metadata["rebuildable"] = sections.get("Rebuildable", "")
    
    # Parse related assets
    related = sections.get("Related Assets", "")
    if related:
        # Extract asset IDs from bullet list
        for line in related.split("\n"):
            match = re.search(r"[A-Z]+-\d+", line)
            if match:
                metadata["related_assets"].append(match.group(0))
    
    # Calculate importance from name (★ count)
    importance_map = {"★★★★★": 5, "★★★★": 4, "★★★": 3, "★★": 2, "★": 1}
    importance_str = sections.get("Importance", "★★★")
    metadata["importance"] = importance_map.get(importance_str, 3)
    
    # Extract distill score if present
    distill_match = re.search(r"蒸馏分[：:]\s*(\d+)", content)
    if distill_match:
        metadata["distill_score"] = int(distill_match.group(1))
    
    return metadata


def scan_repository(repo_dir: Path) -> List[Dict]:
    """扫描 Repository 中的所有资产"""
    assets = []
    
    for filepath in repo_dir.rglob("*.md"):
        if filepath.name == "ASSET_INDEX.md":
            continue
        
        try:
            content = filepath.read_text(encoding="utf-8")
            metadata = extract_metadata(content, filepath)
            assets.append(metadata)
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
    
    return assets


def create_database(db_path: Path):
    """创建 SQLite 数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            origin TEXT,
            purpose TEXT,
            problem TEXT,
            constraint_text TEXT,
            evidence TEXT,
            distillation TEXT,
            replaceable TEXT,
            rebuildable TEXT,
            importance INTEGER,
            distill_score INTEGER,
            filepath TEXT,
            filename TEXT,
            mtime TEXT,
            hash TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS related_assets (
            source_id TEXT,
            target_id TEXT,
            PRIMARY KEY (source_id, target_id)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category)
    """)
    
    conn.commit()
    return conn


def insert_assets(conn: sqlite3.Connection, assets: List[Dict]):
    """插入资产到数据库"""
    cursor = conn.cursor()
    
    for asset in assets:
        cursor.execute("""
            INSERT OR REPLACE INTO assets (
                id, name, category, origin, purpose, problem,
                constraint_text, evidence, distillation, replaceable, rebuildable,
                importance, distill_score, filepath, filename, mtime, hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset["id"], asset["name"], asset["category"], asset["origin"],
            asset["purpose"], asset["problem"], asset["constraint"],
            asset["evidence"], asset["distillation"], asset["replaceable"],
            asset["rebuildable"], asset["importance"], asset["distill_score"],
            asset["filepath"], asset["filename"], asset["mtime"], asset["hash"]
        ))
        
        # Insert related assets
        for target_id in asset["related_assets"]:
            cursor.execute("""
                INSERT OR REPLACE INTO related_assets (source_id, target_id)
                VALUES (?, ?)
            """, (asset["id"], target_id))
    
    conn.commit()


def build_graph(assets: List[Dict]) -> Dict:
    """构建资产依赖关系图"""
    nodes = []
    edges = []
    
    for asset in assets:
        nodes.append({
            "id": asset["id"],
            "name": asset["name"],
            "category": asset["category"],
            "importance": asset["importance"],
        })
        
        for target_id in asset["related_assets"]:
            edges.append({
                "source": asset["id"],
                "target": target_id,
            })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "generated_at": datetime.now().isoformat(),
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def build_timeline(assets: List[Dict]) -> Dict:
    """构建资产时间线"""
    # Sort by mtime (most recent first)
    sorted_assets = sorted(assets, key=lambda x: x["mtime"], reverse=True)
    
    entries = []
    for asset in sorted_assets:
        entries.append({
            "id": asset["id"],
            "name": asset["name"],
            "category": asset["category"],
            "mtime": asset["mtime"],
        })
    
    return {
        "entries": entries,
        "generated_at": datetime.now().isoformat(),
        "count": len(entries),
    }


def build_entity_map(assets: List[Dict]) -> Dict:
    """构建实体→资产映射"""
    entity_map = {}
    
    for asset in assets:
        # Map by ID
        if asset["id"]:
            entity_map[asset["id"]] = asset["filepath"]
        
        # Map by name (lowercase)
        if asset["name"]:
            entity_map[asset["name"].lower()] = asset["id"]
        
        # Map by filename without extension
        entity_map[asset["filename"].replace(".md", "")] = asset["id"]
    
    return {
        "entity_map": entity_map,
        "generated_at": datetime.now().isoformat(),
        "count": len(entity_map),
    }


def full_rebuild():
    """全量重建索引"""
    print("=" * 50)
    print("Index Builder — Full Rebuild")
    print("=" * 50)
    
    # Ensure index directory exists
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    # Scan repository
    print(f"\n[1/5] Scanning Repository: {REPO_DIR}")
    assets = scan_repository(REPO_DIR)
    print(f"      Found {len(assets)} assets")
    
    # Create database
    print(f"\n[2/5] Creating Database: {DB_PATH}")
    conn = create_database(DB_PATH)
    insert_assets(conn, assets)
    conn.close()
    print(f"      Database created")
    
    # Build graph
    print(f"\n[3/5] Building Graph: {GRAPH_PATH}")
    graph = build_graph(assets)
    with open(GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    print(f"      {graph['node_count']} nodes, {graph['edge_count']} edges")
    
    # Build timeline
    print(f"\n[4/5] Building Timeline: {TIMELINE_PATH}")
    timeline = build_timeline(assets)
    with open(TIMELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
    print(f"      {timeline['count']} entries")
    
    # Build entity map
    print(f"\n[5/5] Building Entity Map: {ENTITY_MAP_PATH}")
    entity_map = build_entity_map(assets)
    with open(ENTITY_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(entity_map, f, ensure_ascii=False, indent=2)
    print(f"      {entity_map['count']} entities")
    
    print("\n" + "=" * 50)
    print("Index Build Complete")
    print("=" * 50)


def incremental_update():
    """增量更新索引"""
    print("=" * 50)
    print("Index Builder — Incremental Update")
    print("=" * 50)
    
    # Load existing hash
    existing_hashes = {}
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, hash FROM assets")
        for row in cursor.fetchall():
            existing_hashes[row[0]] = row[1]
        conn.close()
    
    # Scan repository
    print(f"\n[1/3] Scanning Repository: {REPO_DIR}")
    assets = scan_repository(REPO_DIR)
    print(f"      Found {len(assets)} assets")
    
    # Find changed assets
    changed = []
    for asset in assets:
        existing_hash = existing_hashes.get(asset["id"])
        if existing_hash != asset["hash"]:
            changed.append(asset)
    
    if not changed:
        print("\nNo changes detected. Index is up to date.")
        return
    
    print(f"\n[2/3] Changed assets: {len(changed)}")
    for asset in changed:
        print(f"      - {asset['id']}: {asset['name']}")
    
    # Update database
    print(f"\n[3/3] Updating Database")
    conn = sqlite3.connect(DB_PATH)
    insert_assets(conn, changed)
    conn.close()
    print(f"      Updated {len(changed)} assets")
    
    # Rebuild graph/timeline/entity_map (simplest approach)
    graph = build_graph(assets)
    with open(GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    
    timeline = build_timeline(assets)
    with open(TIMELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
    
    entity_map = build_entity_map(assets)
    with open(ENTITY_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(entity_map, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print("Incremental Update Complete")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Index Builder for Civilization Repository")
    parser.add_argument("--full", action="store_true", help="Full rebuild")
    parser.add_argument("--incremental", action="store_true", help="Incremental update")
    args = parser.parse_args()
    
    if args.full:
        full_rebuild()
    elif args.incremental:
        incremental_update()
    else:
        # Default: full rebuild
        full_rebuild()


if __name__ == "__main__":
    main()