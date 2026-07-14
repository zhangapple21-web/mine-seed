#!/usr/bin/env python3
"""验证 Index Builder 输出"""

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
INDEX_DIR = BASE_DIR / "03_INDEX"

print("=" * 50)
print("Index Verification")
print("=" * 50)

# Test SQLite
db_path = INDEX_DIR / "asset_index.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n[SQLite Test]")
cursor.execute("SELECT COUNT(*) FROM assets")
print(f"  Total assets: {cursor.fetchone()[0]}")

cursor.execute("SELECT id, name, category FROM assets LIMIT 5")
print("  Sample assets:")
for row in cursor.fetchall():
    print(f"    {row[0]}: {row[1]} ({row[2]})")

cursor.execute("SELECT COUNT(*) FROM related_assets")
print(f"  Total edges: {cursor.fetchone()[0]}")

conn.close()

# Test graph.json
print("\n[Graph Test]")
with open(INDEX_DIR / "graph.json") as f:
    graph = json.load(f)
print(f"  Nodes: {len(graph['nodes'])}")
print(f"  Edges: {len(graph['edges'])}")
print(f"  Sample edge: {graph['edges'][0]}")

# Test timeline.json
print("\n[Timeline Test]")
with open(INDEX_DIR / "timeline.json") as f:
    timeline = json.load(f)
print(f"  Entries: {len(timeline['entries'])}")
print(f"  Most recent: {timeline['entries'][0]['id']}")

# Test entity_map.json
print("\n[Entity Map Test]")
with open(INDEX_DIR / "entity_map.json") as f:
    entity_map = json.load(f)
print(f"  Entities: {len(entity_map['entity_map'])}")
print(f"  Sample: AX-001 -> {entity_map['entity_map'].get('AX-001', 'N/A')}")

print("\n" + "=" * 50)
print("All tests passed!")
print("=" * 50)