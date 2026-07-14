import json
from pathlib import Path

def convert_to_jsonl_format():
    """将 graph.json 转换为 @modelcontextprotocol/server-memory 期望的 JSONL 格式"""
    
    base_dir = Path("c:/Users/User/ace_workspace/mine-seed")
    graph_path = base_dir / "03_INDEX" / "graph.json"
    output_path = base_dir / "03_INDEX" / "memory.jsonl"
    
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)
    
    node_map = {}
    for node in graph.get("nodes", []):
        node_map[node["id"]] = node["name"]
    
    lines = []
    
    for node in graph.get("nodes", []):
        entity = {
            "type": "entity",
            "name": node["name"],
            "entityType": node.get("category", "asset"),
            "observations": [
                f"ID: {node['id']}",
                f"Category: {node.get('category', 'unknown')}",
                f"Importance: {node.get('importance', 1)}"
            ]
        }
        lines.append(json.dumps(entity, ensure_ascii=False))
    
    for edge in graph.get("edges", []):
        source_name = node_map.get(edge["source"], edge["source"])
        target_name = node_map.get(edge["target"], edge["target"])
        relation = {
            "type": "relation",
            "from": source_name,
            "to": target_name,
            "relationType": "depends_on"
        }
        lines.append(json.dumps(relation, ensure_ascii=False))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        f.write('\n')
    
    print(f"Converted {len(graph.get('nodes', []))} entities and {len(graph.get('edges', []))} relations")
    print(f"Output: {output_path}")

if __name__ == "__main__":
    convert_to_jsonl_format()
