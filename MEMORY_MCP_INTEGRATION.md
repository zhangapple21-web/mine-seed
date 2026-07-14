# MEMORY_MCP_INTEGRATION.md — Memory MCP 接入规范

**任务**: AUM-MISSION-ARCH-022 Part C  
**日期**: 2026-07-14  
**状态**: P0 Final Bootstrap  

---

## 核心定位

> **Memory MCP = Civilization Retrieval Layer（文明检索层）**
>
> **Repository = Source of Truth（唯一真相源）**

```
Repository（真相源）
    │
    ▼
Memory MCP（检索层）
    │
    ▼
Runtime（执行层）
```

**关键规则**：
- Memory MCP 只能**读取** Repository，不能**写入** Repository。
- Memory MCP 只能**检索**已有 Asset，不能**生成**新 Asset。
- Memory MCP 是**可替换**的，Repository 是**不可替换**的。

---

## 接入流程

### 标准接入链路

```
Step 1: AGENTS.md
    │
    ├── 读取 Identity Layer
    ├── 确认系统身份
    └── 定位 Repository 路径
    │
    ▼
Step 2: ASSET_INDEX.md
    │
    ├── 读取资产索引
    ├── 确认资产清单
    └── 定位关键资产
    │
    ▼
Step 3: Repository Scan
    │
    ├── 扫描 02_MEMORY/assets/
    ├── 扫描 03_INDEX/
    └── 确认资产完整性
    │
    ▼
Step 4: Memory Index
    │
    ├── Memory MCP 建立语义索引
    ├── 关联实体关系
    └── 构建检索图谱
    │
    ▼
Step 5: Semantic Retrieval
    │
    ├── Runtime 查询 Memory MCP
    ├── Memory MCP 返回相关 Asset
    └── Runtime 基于 Asset 执行
```

### 数据流向（单向）

```
Repository ──► Memory MCP ──► Runtime
     │              │              │
     │              │              │
     ▼              ▼              ▼
  Read Only     Read Only      Read/Write
  (Asset)       (Index)        (Execution)
```

**禁止的数据流向**:
```
❌ Runtime ──► Memory MCP ──► Repository
❌ Memory MCP ──► Repository
❌ Runtime ──► Repository (直接写入)
```

---

## Memory MCP 配置

### 当前配置状态

| 配置项 | 状态 | 说明 |
|--------|------|------|
| MCP Server | ✅ 已启动 | Memory MCP 绿色运行 |
| Transport | stdio | 通过 npx 启动 |
| Registry | mcp_memory | 本地 MCP 注册 |
| Tools | search_nodes, read_graph | 语义检索工具 |

### 工具权限限制

| 工具 | 权限 | 说明 |
|------|------|------|
| `search_nodes` | ✅ Read Only | 搜索已有节点 |
| `read_graph` | ✅ Read Only | 读取关系图谱 |
| `create_entities` | ❌ 禁止 | 禁止创建新实体 |
| `create_relations` | ❌ 禁止 | 禁止创建新关系 |
| `add_observations` | ❌ 禁止 | 禁止添加观察 |
| `delete_entities` | ❌ 禁止 | 禁止删除实体 |

**原因**: Memory MCP 是检索层，不是存储层。所有文明资产的创建、修改、删除必须通过 Repository 的 Governance 流程（GV-001 Admission Engine）。

---

## 降级路径

### 场景 1：Memory MCP 不可用

```
Runtime
    │
    ├── 检测到 Memory MCP 失败
    ├── 降级到 ASSET_INDEX.md
    ├── 直接读取 Repository 文件
    └── 继续执行任务
```

**证据**: [MEMORY_MCP_CONFIG.md](file:///c:/Users/User/ace_workspace/mine-seed/03_INDEX/MEMORY_MCP_CONFIG.md#L32-L48) 已定义降级路径。

### 场景 2：Memory MCP 返回旧索引

```
Runtime
    │
    ├── 检测到索引与 Repository 不一致
    ├── 提示 "Repository Changed, Need Reindex"
    ├── 拒绝使用旧索引
    └── 要求手动刷新或等待自动同步
```

---

## 验证测试

### 测试 1：Memory MCP 读取 Repository

**目标**: 验证 Memory MCP 能正确读取 Repository 中的 Asset。

**步骤**:
1. 启动 Memory MCP
2. 查询 "Continuity"
3. 验证返回结果包含 AX-001 的内容

**预期结果**: Memory MCP 返回与 AX-001 相关的语义检索结果。

### 测试 2：Memory MCP 禁止写入

**目标**: 验证 Memory MCP 不能修改 Repository。

**步骤**:
1. 尝试通过 Memory MCP 创建新实体
2. 验证操作被拒绝

**预期结果**: Memory MCP 返回权限错误。

### 测试 3：Memory MCP 降级

**目标**: 验证 Memory MCP 不可用时能降级到 ASSET_INDEX.md。

**步骤**:
1. 关闭 Memory MCP
2. 尝试查询 "Repository"
3. 验证系统能直接读取 ASSET_INDEX.md

**预期结果**: 系统不依赖 Memory MCP，能独立完成任务。

---

## 与 LAYER_MAP 的对照

| 概念 | Layer | Memory MCP 角色 |
|------|-------|----------------|
| Repository | Implementation | 被读取的对象（Source of Truth） |
| Memory MCP | Implementation | 检索工具（Semantic Retrieval） |
| Runtime | Implementation | 执行层（TRAE） |
| Observe | Capability | Memory MCP 是 Observe 的一种实现 |
| Transform | Capability | Memory MCP 不参与 Transform |
| Act | Capability | Memory MCP 不参与 Act |

---

## 关键约束

```
Forbidden

❌ Memory MCP 写入 Repository
❌ Memory MCP 生成 Asset
❌ Memory MCP 修改 Asset
❌ Memory MCP 删除 Asset
❌ Memory MCP 替代 Repository
❌ Memory MCP 成为 Source of Truth
❌ Runtime 直接写入 Repository
❌ Repository 与 Memory MCP 双向同步
```

---

**状态**: ✅ Part C Complete — Memory MCP Integration  
**交付物**: MEMORY_MCP_INTEGRATION.md  
**下一步**: Part D — Repository Synchronization
