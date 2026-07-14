# Memory MCP Configuration Guide

> Memory MCP 作为 Knowledge Service 的检索前端，读取 `03_INDEX/` 数据，不写入 Repository。

---

## Configuration

在 TRAE 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "C:/Users/User/ace_workspace/mine-seed/03_INDEX/entity_map.json"
      }
    }
  }
}
```

---

## Usage

Memory MCP 提供以下工具：

| Tool | Purpose |
|------|---------|
| `search_nodes` | 搜索资产实体 |
| `open_nodes` | 打开资产详情 |
| `read_graph` | 读取整个图谱 |

---

## Boundary

- ✅ Memory MCP 读取 `03_INDEX/` 数据
- ✅ Memory MCP 提供检索能力
- ❌ Memory MCP 不写入 `02_MEMORY/assets/`
- ❌ Memory MCP 不修改 Repository

---

## Fallback

如果 Memory MCP 不可用，Agent 应自动降级到：
- 读取 `ASSET_INDEX.md`
- 直接调用 `KnowledgeService` (Python API)

---

## Notes

Memory MCP 是 Knowledge Service 的可选前端，不是必需。Repository 是唯一真相源。