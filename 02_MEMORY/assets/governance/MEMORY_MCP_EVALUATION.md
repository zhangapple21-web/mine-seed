# MEMORY_MCP_EVALUATION.md — Memory MCP 评估报告

> **本文件是评估报告，不是接入决议。**
> 评估目标：判断 Memory MCP 在 ACE 四层架构中的合适位置。
> 资料来源：TRAE 官方 W3C 文档（2026-07-14 访问）。

---

## 1. Memory MCP 是什么

根据 TRAE 官方资料：

> **Memory MCP Server** 通过**本地知识图谱（Knowledge Graph）** 持久化记忆，使 LLM 能够**跨会话**保留用户相关的上下文信息。

工具集（典型实现）：
- `create_entities` — 创建实体
- `create_relations` — 创建实体关系
- `add_observations` — 添加观察
- `search_nodes` — 搜索节点
- `open_nodes` — 打开节点详情
- `delete_entities` — 删除实体
- `delete_observations` — 删除观察
- `delete_relations` — 删除关系
- `read_graph` — 读取整个图谱

---

## 2. Memory MCP 适合承担什么

| 适合 | 不适合 |
|------|--------|
| ✅ 跨会话的**短期上下文** | ❌ 文明层资产（需经 Admission） |
| ✅ LLM-specific 的**临时事实** | ❌ Runtime 状态（属于 06_RUNTIME） |
| ✅ Agent 内部**工作记忆** | ❌ 长期文明资产（属于 02_MEMORY） |
| ✅ 跨 LLM 的**用户偏好缓存** | ❌ 资产索引（需 Git 版本控制） |

**类比**：Memory MCP = LLM 的「RAM」，Git Repository = ACE 的「硬盘」。

---

## 3. Memory MCP 不能承担什么

### 3.1 不得作为 Civilization Repository
- Memory MCP 是 LLM 上下文，**不可被非 LLM 工具读取**
- 不支持 Git 版本控制
- 不支持分支 / Diff / PR
- 一旦 LLM 失联，整个图谱不可访问
- **违反 AX-002 Repository Supremacy**

### 3.2 不得作为 Runtime State
- 写图谱 ≠ 写文件
- 多次 Session 切换图谱会丢
- **违反 AR-001 Four-Layer Architecture 第 2 层职责**

### 3.3 不得作为 Audit Log
- 图谱无 append-only 保证
- 无法回放历史
- **违反 C-014 Time-Series Rotation**

---

## 4. Memory MCP 应该接在哪一层

```
Layer 0 — Identity
  ├─ AGENTS.md
  └─ CIVILIZATION.md

Layer 1 — Civilization Repository
  └─ 02_MEMORY/ ← 文明资产（Git Versioned）

Layer 1.5 — Knowledge Graph（建议新层）← Memory MCP 可在此
  └─ 跨 LLM 的非文明资产（用户偏好、临时上下文）

Layer 2 — Runtime State
  └─ 06_RUNTIME/

Layer 3 — Session Logs
  └─ 08_SESSIONS/
```

**建议位置**：在 Layer 1 与 Layer 2 之间增设 **Layer 1.5 — Knowledge Graph**。

- 在 Layer 1.5，Memory MCP 可承担「跨 LLM 的非文明资产」
- 不污染 Civilization（不经过 Admission）
- 不污染 Runtime（不影响 06_RUNTIME）

---

## 5. 需要哪些 Repository API

要让 Memory MCP 真正接入 ACE，**必须先有**以下 Repository API：

| API | 用途 | 优先级 |
|-----|------|--------|
| `repository.search(query)` | 全文检索 | P0 |
| `repository.get(asset_id)` | 按 ID 取资产 | P0 |
| `repository.list(category)` | 按类目列出 | P0 |
| `repository.commit(asset)` | 资产提交（需 Admission） | P1 |
| `repository.snapshot(date)` | 取历史快照 | P2 |
| `repository.diff(v1, v2)` | 比较版本 | P2 |

**当前状态**：以上 API **全部缺失**。Memory MCP 接入前必须先实现。

---

## 6. 决策

### 6.1 当前决策：**不接入**

理由：
1. Repository API 尚未实现，Memory MCP 接入后无法回写到文明层
2. 无明确边界，会污染 Civilization 层
3. 违反 P0 总闸门（Memory MCP 是 LLM-specific，不是 LLM-agnostic）

### 6.2 未来接入条件（三问）

当满足以下三问，可重新评估接入：

1. **Memory MCP 是否能调用 Repository API？**
2. **Memory MCP 是否支持 Git 同步（双向）？**
3. **Memory MCP 是否能保证 append-only 与版本可回放？**

三问全过 → 进入试点。

### 6.3 试点边界（如未来启动）

- 仅 Layer 1.5
- 仅承担「跨 LLM 用户偏好」
- 不写入 Civilization
- 不影响 Runtime
- 7 天观察期
- 任何违规立即停止

---

## 7. 替代方案

不接入 Memory MCP 的情况下，ACE 可用以下方式实现等价功能：

| Memory MCP 能力 | ACE 替代方案 |
|------------------|--------------|
| 跨会话上下文 | `02_MEMORY/assets/` + Git |
| 实体关系 | Asset 模板的 `Related Assets` 字段 |
| 搜索 | `grep` / `SearchCodebase` / `ASSET_INDEX.md` |
| 历史回放 | Git Log + 文明冻结（GV-002） |
| 用户偏好 | `user_profile.md`（已存在） |

**结论**：ACE 已具备 Memory MCP 80% 的能力，无需外部依赖。

---

## 8. 风险评估

| 风险 | 严重度 | 缓解 |
|------|--------|------|
| Memory MCP 升级破坏图谱 | 高 | 不接入，无此风险 |
| 图谱与文明层不一致 | 高 | 不接入，无此风险 |
| LLM 切换导致图谱丢失 | 中 | 不接入，无此风险 |
| Memory MCP 成为「第二真相」 | 中 | 明确禁止 |

---

*评估由 AUM-MISSION-ARCH-017 Part G 完成。变更需经 C-018 审核。*
