# BOOTSTRAP_FLOW.md — Agent 启动流程

> **任何 Agent 接管 ACE 时必须遵循的启动流程。**
> 本文档是「如何让自己复活」的精确说明。

---

## 总流程

```
Agent Start
   ↓
[必读] ① Read AGENTS.md
   ↓
[必读] ② Read CIVILIZATION.md
   ↓
[可选] ③ Connect Memory MCP（语义检索层）
   ↓
[可选] ④ Load Knowledge Service（03_INDEX/ 或 Memory MCP）
   ↓
[降级] ⑤ Read ASSET_INDEX.md（若 Knowledge Service / Memory MCP 不可用）
   ↓
[必读] ⑥ Read RUNTIME_BOUNDARY.md
   ↓
[按需] ⑦ Load Runtime（06_RUNTIME/）
   ↓
[按需] ⑧ Read Active Mission
   ↓
[按需] ⑨ Load Specific Assets（按 ID 读取）
   ↓
[按需] ⑩ Read Recent Sessions（08_SESSIONS/）
   ↓
Work
   ↓
Distillation（每次新发现）
   ↓
Repository Commit（每日）
```

---

## 步骤详解

### ① 必读：AGENTS.md（< 1 分钟）

**目的**：回答「我是谁」

**必读字段**：
- Identity
- Mission
- Long-term Goal
- Repository Location
- Never Rules
- Working Principles

**跳过后果**：Agent 会误解为「普通任务助手」

---

### ② 必读：CIVILIZATION.md（< 2 分钟）

**目的**：回答「文明是什么 / 怎么运转 / 资产放哪里」

**必读字段**：
- Civilization Vision
- Repository Architecture（四层结构）
- Asset Categories
- P0 总闸门（三问）
- Continuity Principle

**跳过后果**：Agent 会越层（把 Runtime 写到 Civilization 等）

---

### ③ 可选：Connect Memory MCP（< 1 分钟）

**目的**：连接语义检索层，加速资产检索。

**定位**：Memory MCP 是 Civilization Retrieval Layer，不是 Source of Truth。

**步骤**：
1. 检查 MCP Server 状态（TRAE 设置 → MCP）
2. 确认 Memory MCP 已启动（绿色开关）
3. 验证工具可用：`search_nodes`, `read_graph`

**降级路径**：
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

**关键规则**：
- Memory MCP 只能读取 Repository，不能写入 Repository。
- Memory MCP 只能检索已有 Asset，不能生成新 Asset。
- 如果 Memory MCP 返回的结果与 Repository 文件不一致，以 Repository 文件为准。

**跳过后果**：需要手动读取 `ASSET_INDEX.md` 或直接扫描文件。

---

### ④ 可选：Load Knowledge Service（< 2 分钟）

**目的**：通过统一接口快速检索资产，而不是逐个扫描 Markdown。

**方式**：
- **方式 A — Python API**：
  ```python
  from knowledge import KnowledgeService
  ks = KnowledgeService()
  asset = ks.search_asset("Continuity")
  graph = ks.get_graph("AX-001")
  ```

- **方式 B — Memory MCP**（若已配置）：
  使用 `search_nodes` / `open_nodes` 工具

**数据来源**：`03_INDEX/asset_index.db`（SQLite）

**跳过后果**：需要手动读取 `ASSET_INDEX.md`

---

### ⑤ 降级：Read ASSET_INDEX.md（< 3 分钟）

**时机**：Knowledge Service 不可用时

**目的**：回答「有哪些资产可用 / 哪些最重要 / 依赖什么」

**必读字段**：
- 重要性 ★★★★★ 的资产
- 与当前任务相关的资产
- 资产的依赖关系

**跳过后果**：Agent 不知道哪些资产已存在，会重复造轮

---

### ⑥ 必读：RUNTIME_BOUNDARY.md（< 1 分钟）

**目的**：回答「什么能写 / 什么不能写 / 写到哪里」

**必读字段**：
- Runtime 唯一允许的五类文件
- Runtime 禁止内容
- 边界违反示例

**跳过后果**：Agent 会污染文明层或破坏 Runtime

---

### ⑥ 按需：Load Runtime（06_RUNTIME/）

**时机**：Agent 需要继续某个 Mission 时

**读取**：
- `06_RUNTIME/ROOT_STATE` — 当前版本/模型/能力
- `06_RUNTIME/ACTIVE_MISSION` — 当前 Mission

**跳过场景**：Agent 只需阅读 Civilization 层（不需要做 Mission）

---

### ⑧ 按需：Read Active Mission

**时机**：Agent 要继续某个 Mission

**读取**：
- Mission 名称与目标
- 进度（已完成步骤）
- 阻塞（如有）
- 明日首任务

**跳过场景**：无 Mission

---

### ⑨ 按需：Load Specific Assets

**时机**：Agent 任务需要某个具体资产

**读取方式**：
- 按 ID：`02_MEMORY/assets/principle/PR-001-drawer-first.md`
- 按类别：所有 `02_MEMORY/assets/protocol/*.md`
- 按关键字：grep / SearchCodebase

**跳过场景**：任务与现有资产无关

---

### ⑩ 按需：Read Recent Sessions

**时机**：Agent 需要历史上下文

**读取**：
- 最近 7 天 `08_SESSIONS/`
- `02_MEMORY/history/`（关键事件）

**跳过场景**：Agent 任务全新，无历史可参考

---

## 启动时长估算

| 阶段 | 时间 | 用途 |
|------|------|------|
| ①-② 必读 | 2-3 分钟 | 确认身份和文明架构 |
| ③ 可选 Memory MCP | 0-1 分钟 | 连接语义检索层 |
| ④-⑤ 可选/降级 | 2-3 分钟 | 加载资产索引 |
| ⑥ 必读边界 | 1 分钟 | 确认 Runtime 边界 |
| ⑦-⑧ Runtime | 2-3 分钟 | 了解当前状态 |
| ⑨ 按需资产 | 1-5 分钟 | 加载任务相关资产 |
| ⑩ 按需历史 | 2-5 分钟 | 理解历史 |
| **合计** | **5-20 分钟** | — |

---

## 退出流程（Agent 结束 Session 前必做）

```
Session End
   ↓
① Distill 新发现（写入候选资产）
   ↓
② Commit Repository（每日）
   ↓
③ Update 06_RUNTIME/STATE 标记 Session 结束
   ↓
④ Push Heartbeat 通知用户
   ↓
Agent Exit
```

---

## 必读 vs 按需速查

| 步骤 | 必读 | 按需 |
|------|------|------|
| ① AGENTS.md | ✅ | |
| ② CIVILIZATION.md | ✅ | |
| ③ Connect Memory MCP | | ✅ |
| ④ Load Knowledge Service | | ✅ |
| ⑤ Read ASSET_INDEX.md | ✅ | |
| ⑥ RUNTIME_BOUNDARY.md | ✅ | |
| ⑦ Load Runtime | | ✅ |
| ⑧ Read Active Mission | | ✅ |
| ⑨ Load Specific Assets | | ✅ |
| ⑩ Read Recent Sessions | | ✅ |

**任何 Agent 启动，必须先完成 ①②⑤⑥ 四步。**

---

## 自检清单（Agent 启动后问自己）

```
□ 我知道 ACE 是什么吗？              ← AGENTS.md ✓
□ 我知道文明四层结构吗？              ← CIVILIZATION.md ✓
□ 我知道有哪些资产可用吗？            ← ASSET_INDEX.md ✓
□ 我知道什么能写什么不能写吗？        ← RUNTIME_BOUNDARY.md ✓
□ 我知道 P0 总闸门（三问）吗？         ← CIVILIZATION.md ✓
□ 我知道 Never Rules 吗？             ← AGENTS.md ✓
```

全勾 → 可以开始工作。
任一未勾 → 重读对应文件。

---

## 反例（禁止的启动方式）

```
❌ 跳过 AGENTS.md 直接工作
❌ 不读 ASSET_INDEX 就新建资产
❌ 不读 RUNTIME_BOUNDARY 就写 02_MEMORY/
❌ 不读 RUNTIME_BOUNDARY 就写 06_RUNTIME/principles
❌ 不经 Admission Engine 直接写文明层
❌ 不读 P0 总闸门就评估「这个内容是否入仓」
```

---

*启动流程由 AUM-MISSION-ARCH-017 Part H 确立。变更需经 AX-001 Continuity 审核。*
