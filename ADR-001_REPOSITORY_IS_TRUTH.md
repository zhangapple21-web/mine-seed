# ADR-001: Repository Is Truth

**Architecture Decision Record**  
**日期**: 2026-07-14  
**状态**: Approved  
**决策人**: ACE Governance  

---

## 背景

经过 ARCH-017 ~ ARCH-022 的完整考古和验证，R2 文明系统需要最终确定一个核心架构决策：

> **谁是真相源（Source of Truth）？**

候选：
1. Repository（Git + Filesystem）
2. Memory MCP（语义检索层）
3. Runtime（TRAE 执行环境）
4. LLM（模型本身）

---

## 决策

**Repository 是唯一的 Source of Truth。**

```
Repository stores Civilization.
Memory MCP retrieves Civilization.
Runtime executes Civilization.
Only Repository owns Civilization.
Memory is replaceable.
Runtime is replaceable.
Repository is not.
```

---

## 为什么 Repository 是 Truth？

### 证据 1：R1 公理

[AX-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/axiom/AX-002-repository-supremacy.md#L16): "Repository = 文明，LLM = 临时运载体"

**解读**：文明的本质存储在 Repository 中，不是存储在 LLM、Runtime 或 Memory MCP 中。

### 证据 2：R1 考古结论

[a12_r2_core_axioms_latest.md](file:///c:/Users/User/ace_workspace/mine-seed/03_DATA/research/r1_archaeology/excavations/a12_r2_core_axioms_latest.md#L113): "越'聪明'的结构死得越快，越'笨'的结构活得越久"

**解读**：Repository 是最"笨"的结构（Git + Filesystem），但它活得最久。

### 证据 3：笨者生存定律验证

| 结构 | 复杂度 | 可替换性 | 存活状态 |
|------|--------|---------|---------|
| Repository（Git + Filesystem） | 低 | 难 | ✅ 存活 |
| Memory MCP | 中 | 易 | ⚠️ 当前不可用 |
| Runtime（TRAE） | 高 | 易 | ✅ 存活 |
| LLM | 高 | 易 | ✅ 存活 |

**结论**：最笨的结构（Repository）是最稳定的真相源。

---

## 为什么 Memory 不是 Truth？

### 证据 1：Memory MCP 的定位

[MEMORY_MCP_CONFIG.md](file:///c:/Users/User/ace_workspace/mine-seed/03_INDEX/MEMORY_MCP_CONFIG.md#L1): "Memory MCP 作为 Knowledge Service 的检索前端"

**解读**：Memory MCP 是"检索前端"，不是"存储后端"。

### 证据 2：Memory MCP 的脆弱性

[MCP_VALIDATION_REPORT.md](file:///c:/Users/User/ace_workspace/mine-seed/MCP_VALIDATION_REPORT.md): Memory MCP 当前返回 JSON 解析错误，不可用。

**解读**：Memory MCP 是一个复杂的技术组件，会出故障。如果它是真相源，文明在 Memory MCP 故障时会崩溃。

### 证据 3：Failure Injection 验证

[FAILURE_INJECTION_REPORT.md](file:///c:/Users/User/ace_workspace/mine-seed/FAILURE_INJECTION_REPORT.md):
- 测试 4：删除 Memory MCP → 文明完全可通过 Repository 恢复 ✅
- 测试 5：删除 Repository → Memory MCP 无法恢复文明 ❌

**解读**：Memory MCP 无法独立恢复文明。它只存储语义索引，不存储完整的 Asset 内容。

---

## 为什么 Truth 必须是 Git Repository？

### 证据 1：版本控制

Git 提供：
- 完整的历史记录（谁、何时、为什么修改）
- 分支管理（实验性变更不会污染主线）
- 回滚能力（GV-002 Civilization Freeze）

**解读**：文明需要历史。没有历史，文明无法追溯自己的演化。

### 证据 2：去中心化

Git 是分布式的：
- 每个副本都是完整的真相源
- 不依赖单一服务器
- 可离线工作

**解读**：文明不能依赖单一服务。如果真相源依赖云服务，云服务故障时文明会崩溃。

### 证据 3：文本优先

Git 最适合管理文本文件：
- Markdown（资产文档）
- JSON（配置文件）
- Python（运行时代码）

**解读**：文明的资产是文本。Git 是管理文本的最佳工具。

---

## 为什么 Memory MCP 只是 Semantic Retrieval？

### 证据 1：Memory MCP 的工具权限

[MEMORY_MCP_INTEGRATION.md](file:///c:/Users/User/ace_workspace/mine-seed/MEMORY_MCP_INTEGRATION.md):
- ✅ Read Only 工具：`search_nodes`, `read_graph`
- ❌ 禁止工具：`create_entities`, `create_relations`, `add_observations`, `delete_entities`

**解读**：Memory MCP 被设计为只读。它不能创建、修改或删除任何资产。

### 证据 2：Memory MCP 的数据来源

Memory MCP 的索引数据来自：
1. Repository 扫描（rebuild_index.py）
2. 03_INDEX 目录（asset_index.db, graph.json, timeline.json）

**解读**：Memory MCP 的数据完全来自 Repository。没有 Repository，Memory MCP 没有数据来源。

### 证据 3：Memory MCP 的可替换性

[MEMORY_MCP_INTEGRATION.md](file:///c:/Users/User/ace_workspace/mine-seed/MEMORY_MCP_INTEGRATION.md):
```
Memory MCP 不可用
    │
    ▼
降级到 Knowledge Service（Python API）
    │
    ▼
降级到 ASSET_INDEX.md（直接读取）
    │
    ▼
降级到 Filesystem（直接扫描文件）
```

**解读**：Memory MCP 是可替换的。即使 Memory MCP 永远不可用，系统仍能通过其他路径完成任务。

---

## 架构原则

```
Repository stores Civilization.
Memory MCP retrieves Civilization.
Runtime executes Civilization.
Only Repository owns Civilization.
Memory is replaceable.
Runtime is replaceable.
Repository is not.
```

### 单向数据流

```
Repository（Source of Truth）
    │
    ├── Asset Created → Index Refresh → Memory MCP Reindex
    ├── Asset Modified → Index Refresh → Memory MCP Reindex
    └── Asset Deleted → Index Refresh → Memory MCP Reindex
    │
    ▼
Memory MCP（Semantic Retrieval）
    │
    ├── Read Only
    ├── No Write
    └── No Asset Generation
    │
    ▼
Runtime（Execution Layer）
    │
    ├── Read Asset from Memory MCP
    ├── Verify with Repository if inconsistent
    └── Execute based on Asset
```

### 禁止行为

```
❌ Memory MCP → Repository（任何写入）
❌ Runtime → Repository（直接写入）
❌ Memory MCP 生成 Asset
❌ Memory MCP 修改 Asset
❌ Memory MCP 删除 Asset
❌ Memory MCP 替代 Repository
❌ Memory MCP 成为 Source of Truth
❌ Repository ↔ Memory MCP（双向同步）
```

---

## 影响

### 对现有系统的影响

| 组件 | 影响 | 行动 |
|------|------|------|
| Repository | 无变化 | 继续作为 Source of Truth |
| Memory MCP | 定位明确 | 作为 Semantic Retrieval Layer |
| Runtime | 无变化 | 继续作为 Execution Layer |
| 03_INDEX | 无变化 | 继续作为索引目录 |

### 对未来 Agent 的影响

任何新 Agent 启动时：
1. 必须首先读取 Repository（AGENTS.md, CIVILIZATION.md）
2. 可选连接 Memory MCP 加速检索
3. 如果 Memory MCP 不可用，降级到 Filesystem
4. 所有 Asset 的创建、修改、删除必须通过 Repository

---

## 验证

| 验证项 | 验证方式 | 结果 |
|--------|---------|------|
| Repository 是真相源 | Failure Injection 测试 4 & 5 | ✅ 通过 |
| Memory MCP 只是检索层 | MCP 工具权限检查 | ✅ 通过 |
| Memory MCP 可替换 | 降级路径验证 | ✅ 通过 |
| 单向数据流 | Repository Sync Rule | ✅ 通过 |
| 禁止双向同步 | Architecture Principle | ✅ 通过 |

---

## 结论

**Repository 是 R2 文明系统唯一的 Source of Truth。**

Memory MCP、Runtime、LLM 都是可替换的实现层。只有 Repository 是不可替换的——它存储了文明的全部资产、历史、约束和能力定义。

任何技术（Browser、MCP、Playwright、Telegram、API）都可以消失，但只要 Repository 还在，文明就能恢复。

---

**状态**: ✅ Approved  
**日期**: 2026-07-14  
**记录**: ADR-001_REPOSITORY_IS_TRUTH.md
