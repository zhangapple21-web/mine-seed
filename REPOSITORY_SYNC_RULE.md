# REPOSITORY_SYNC_RULE.md — Repository 与 Memory MCP 同步规则

**任务**: AUM-MISSION-ARCH-022 Part D  
**日期**: 2026-07-14  
**状态**: P0 Final Bootstrap  

---

## 核心原则

> **Repository 是唯一的 Asset Source。**  
> **Memory MCP 永远不会成为 Asset Source。**  
> **同步是单向的：Repository → Memory MCP。**

```
Repository（真相源）
    │
    ├── Asset Created
    ├── Asset Modified
    ├── Asset Deleted
    │
    ▼
Index Refresh（索引刷新）
    │
    ├── 扫描变更文件
    ├── 更新 asset_index.db
    ├── 更新 graph.json
    └── 更新 timeline.json
    │
    ▼
Memory MCP Reindex（语义重索引）
    │
    ├── 读取更新后的索引
    ├── 重建语义图谱
    └── 更新检索缓存
    │
    ▼
Memory MCP（检索层）
```

---

## 同步触发条件

### 触发条件 1：Asset 创建

```
新 Asset 写入 Repository
    │
    ▼
触发 Index Refresh
    │
    ▼
触发 Memory MCP Reindex
```

**证据**: [GV-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-001-admission-engine.md#L19): "evolve() → apply_constraint_patch() → Admission Engine → Repository"

### 触发条件 2：Asset 修改

```
Asset 被修改
    │
    ▼
触发 Index Refresh
    │
    ▼
触发 Memory MCP Reindex
```

**注意**: 修改必须通过 Admission Engine（GV-001），不能直接修改。

### 触发条件 3：Asset 删除

```
Asset 被删除
    │
    ▼
触发 Index Refresh
    │
    ▼
触发 Memory MCP Reindex
```

**注意**: 删除必须通过 Civilization Freeze（GV-002）或 Round Table（GV-003）。

### 触发条件 4：定期同步

```
Heartbeat（每 5-10 分钟）
    │
    ▼
检查 Repository 变更
    │
    ▼
如有变更，触发 Index Refresh + Memory MCP Reindex
```

**证据**: [PR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-002-self-loop.md#L26): "Heartbeat 必须每 5-10 分钟一次"

---

## 禁止的同步方向

```
❌ 禁止：Memory MCP → Repository

Memory MCP 检测到新信息
    │
    ❌ 禁止写入 Repository
    │
    ✅ 正确做法：通过 Admission Engine 提交
```

```
❌ 禁止：Runtime → Repository（直接写入）

Runtime 执行任务
    │
    ❌ 禁止直接修改 Repository
    │
    ✅ 正确做法：通过 Act（GitHub MCP / Shell）提交，再触发同步
```

```
❌ 禁止：Memory MCP ↔ Repository（双向同步）

Repository 和 Memory MCP 永远保持单向关系。
双向同步会导致 Source of Truth 混淆。
```

---

## 同步流程详细步骤

### 步骤 1：Repository 变更检测

```python
# 伪代码
def detect_repository_changes():
    """检测 Repository 变更"""
    last_sync = read_last_sync_timestamp()
    current_files = scan_repository_files()
    
    changes = []
    for file in current_files:
        if file.mtime > last_sync:
            changes.append(file)
    
    return changes
```

### 步骤 2：Index Refresh

```python
def refresh_index(changes):
    """刷新索引"""
    for change in changes:
        if change.type == "created":
            add_to_asset_index(change)
            add_to_graph(change)
            add_to_timeline(change)
        elif change.type == "modified":
            update_asset_index(change)
            update_graph(change)
            update_timeline(change)
        elif change.type == "deleted":
            remove_from_asset_index(change)
            remove_from_graph(change)
            remove_from_timeline(change)
    
    save_index()
```

**证据**: [rebuild_index.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/indexer/rebuild_index.py#L1) 已实现索引重建逻辑。

### 步骤 3：Memory MCP Reindex

```python
def reindex_memory_mcp():
    """触发 Memory MCP 重索引"""
    # 读取更新后的索引
    index = read_asset_index()
    graph = read_graph()
    timeline = read_timeline()
    
    # 通过 Memory MCP API 更新语义索引
    memory_mcp.update_index(index, graph, timeline)
    
    # 记录同步时间戳
    save_sync_timestamp()
```

**注意**: Memory MCP Reindex 是异步操作，可能需要几秒到几分钟。在此期间，Runtime 仍可使用旧的 Memory MCP 索引，但应提示 "Indexing in progress"。

---

## 冲突处理

### 场景：Repository 更新时 Memory MCP 正在查询

```
Repository 更新
    │
    ├── Memory MCP 正在处理查询
    │
    ▼
处理策略：
    ├── 1. 允许查询完成（使用旧索引）
    ├── 2. 在查询结果中附加 "索引可能已过期" 警告
    └── 3. 下次查询使用新索引
```

### 场景：Memory MCP 返回的结果与 Repository 不一致

```
Runtime 发现 Memory MCP 结果与 Repository 文件不一致
    │
    ▼
处理策略：
    ├── 1. 以 Repository 文件为准（Source of Truth）
    ├── 2. 提示 "Memory Index 可能已过期"
    └── 3. 触发 Index Refresh + Memory MCP Reindex
```

---

## 同步状态监控

### 状态指标

| 指标 | 正常值 | 异常值 | 处理方式 |
|------|--------|--------|---------|
| 最后同步时间 | < 10 分钟 | > 10 分钟 | 触发紧急同步 |
| 索引一致性 | 100% | < 100% | 触发完整重建 |
| Memory MCP 可用性 | 可用 | 不可用 | 降级到 ASSET_INDEX.md |
| Repository 变更数 | 0~10/小时 | > 100/小时 | 检查是否有异常写入 |

### 监控日志

```
[2026-07-14 10:00:00] Repository Scan: 25 assets, 0 changes
[2026-07-14 10:05:00] Repository Scan: 25 assets, 1 change (AX-001 modified)
[2026-07-14 10:05:01] Index Refresh: Updated asset_index.db
[2026-07-14 10:05:02] Memory MCP Reindex: Started
[2026-07-14 10:05:05] Memory MCP Reindex: Completed
[2026-07-14 10:10:00] Repository Scan: 25 assets, 0 changes
```

---

## 故障恢复

### 故障 1：Index Refresh 失败

```
Index Refresh 失败
    │
    ▼
恢复策略：
    ├── 1. 保留上次成功的索引
    ├── 2. 记录失败原因
    ├── 3. 下次 Heartbeat 重试
    └── 4. 连续失败 3 次，触发告警
```

### 故障 2：Memory MCP Reindex 失败

```
Memory MCP Reindex 失败
    │
    ▼
恢复策略：
    ├── 1. Memory MCP 继续使用旧索引
    ├── 2. 标记索引为 "stale"
    ├── 3. 下次同步时重试
    └── 4. 连续失败 5 次，降级到 ASSET_INDEX.md
```

### 故障 3：Repository 损坏

```
Repository 损坏
    │
    ▼
恢复策略：
    ├── 1. 停止所有同步
    ├── 2. 从 Git 历史恢复
    ├── 3. 验证恢复后的完整性
    └── 4. 触发完整重建
```

---

## 与 LAYER_MAP 的对照

| 概念 | Layer | 同步角色 |
|------|-------|---------|
| Repository | Implementation | Source of Truth，唯一变更源 |
| Index | Implementation | Repository 的镜像，加速读取 |
| Memory MCP | Implementation | 语义检索层，基于 Index 构建 |
| Runtime | Implementation | 执行层，触发同步查询 |

---

## 关键约束

```
Forbidden

❌ Memory MCP → Repository（任何写入）
❌ Runtime → Repository（直接写入）
❌ Repository ↔ Memory MCP（双向同步）
❌ Memory MCP 成为 Asset Source
❌ 静默使用旧索引（必须提示）
❌ 绕过 Admission Engine 直接修改 Repository
```

---

**状态**: ✅ Part D Complete — Repository Synchronization  
**交付物**: REPOSITORY_SYNC_RULE.md  
**下一步**: Part E — Integration Test
