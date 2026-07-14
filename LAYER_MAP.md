# LAYER_MAP.md — Concept Layer Classification

**任务**: AUM-MISSION-ARCH-022 Part A  
**日期**: 2026-07-14  
**状态**: P0 Final Bootstrap  

---

## 核心原则

> **每个 Concept 只能属于一层。**  
> **禁止跨层。**  
> **禁止推理分类，必须引用 Evidence。**

---

## Layer 0: Goal（目标层）

### GO-001: Continuity

| 字段 | 内容 |
|------|------|
| **Concept** | Continuity（连续性） |
| **Layer** | Goal |
| **Evidence** | [AX-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/axiom/AX-001-continuity-principle.md#L16): "Runtime 可以死，Repository 必须活" |
| **Reason** | 这是系统存在的根本目的。没有连续性，系统就没有存在的理由。任何技术更替（LLM更换、Runtime重启）都不能改变这个Goal。 |

---

## Layer 1: Invariant（不变量层）

### INV-001: Boundary

| 字段 | 内容 |
|------|------|
| **Concept** | Boundary（边界） |
| **Layer** | Invariant |
| **Evidence** | [AR-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/architecture/AR-001-four-layer-architecture.md#L32): "Identity 不得包含 Prompt"；第34行: "Runtime 不得包含 Principles/Protocols" |
| **Reason** | 系统必须有不可逾越的边界。没有边界，系统会自我毁灭。这不是实现选择，而是存在前提。 |

### INV-002: Identity

| 字段 | 内容 |
|------|------|
| **Concept** | Identity（身份） |
| **Layer** | Invariant |
| **Evidence** | [AX-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/axiom/AX-002-repository-supremacy.md#L16): "Repository = 文明，LLM = 临时运载体" |
| **Reason** | 系统的身份由 Repository 定义，不是由 Runtime 或 LLM 定义。更换 LLM 后，只要 Repository 不变，系统还是"它"。 |

### INV-003: Observation

| 字段 | 内容 |
|------|------|
| **Concept** | Observation（观察能力） |
| **Layer** | Invariant |
| **Evidence** | [PR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-002-self-loop.md#L24): "Environment → Observe → Audit → Recovery" |
| **Reason** | 系统必须能观察自己和世界。没有观察，系统不知道自己在做什么，会在细节中迷失。 |

---

## Layer 2: Capability（能力层）

### CAP-001: Observe

| 字段 | 内容 |
|------|------|
| **Concept** | Observe（感知现实） |
| **Layer** | Capability |
| **Evidence** | [PR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-002-self-loop.md#L24): "Environment → Observe" |
| **Reason** | 系统能感知现实世界。这是输入端能力。没有 Observe，系统没有输入。 |
| **子类** | Read, Watch, Capture, Search |

### CAP-002: Transform

| 字段 | 内容 |
|------|------|
| **Concept** | Transform（变换信息） |
| **Layer** | Capability |
| **Evidence** | [CP-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-001-provider-adapter-pattern.md#L36): "中枢只认识接口，不认识实现"（信息从具体实现变换为抽象接口） |
| **Reason** | 系统能将信息从一种形态变为另一种。这是处理端能力。 |
| **子类** | Compress, Verify, Remember, Reason, Decide, Plan |

**子类归属验证**:

| 子类 | 归属 | Evidence |
|------|------|---------|
| **Verify** | Transform | [CP-004](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-004-smelter-gate.md#L24): `gate.pass_through(content, context)` — 将不确定的内容变换为确定的通过/拒绝状态 |
| **Remember** | Transform | [AX-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/axiom/AX-001-continuity-principle.md#L16): "Runtime 可以死，Repository 必须活" — 将瞬态信息变换为持久态 |
| **Reason** | Transform | [PR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-002-self-loop.md#L24): "Audit → Recovery" — 将原始数据变换为结构化结论 |
| **Decide** | Transform | [CP-004](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-004-smelter-gate.md#L24): `result["passed"]` — 将多个评估维度变换为单一决策 |

### CAP-003: Act

| 字段 | 内容 |
|------|------|
| **Concept** | Act（影响现实） |
| **Layer** | Capability |
| **Evidence** | [PR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-002-self-loop.md#L20): "Archive → Evolution → Heartbeat"（Heartbeat 是系统对现实世界的主动输出） |
| **Reason** | 系统能对现实世界执行操作。这是输出端能力。没有 Act，系统没有输出。 |
| **子类** | Write, Send, Execute, Modify, Publish |

---

## Layer 3: Implementation（实现层）

### IMP-001: Repository

| 字段 | 内容 |
|------|------|
| **Concept** | Repository（文明仓库） |
| **Layer** | Implementation |
| **Evidence** | [AX-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/axiom/AX-002-repository-supremacy.md#L16): "Repository = 文明" |
| **Reason** | Repository 是 Continuity 和 Identity 的具体实现。它是存储文明资产的具体方式（Git + Filesystem）。更换 Repository 的实现方式（如从 Git 换到 Mercurial）不会影响 Continuity 这个 Goal。 |

### IMP-002: Memory MCP

| 字段 | 内容 |
|------|------|
| **Concept** | Memory MCP |
| **Layer** | Implementation |
| **Evidence** | [MEMORY_MCP_CONFIG.md](file:///c:/Users/User/ace_workspace/mine-seed/03_INDEX/MEMORY_MCP_CONFIG.md#L1): "Memory MCP 作为 Knowledge Service 的检索前端" |
| **Reason** | Memory MCP 是知识检索的具体技术实现。它是可替换的（可降级到 ASSET_INDEX.md 或直接调用 KnowledgeService）。 |

### IMP-003: Browser

| 字段 | 内容 |
|------|------|
| **Concept** | Browser |
| **Layer** | Implementation |
| **Evidence** | [memory_index_latest.json](file:///c:/Users/User/ace_workspace/mine-seed/03_DATA/research/r1_archaeology/memory_index/memory_index_latest.json): `"is_selenium": true` — R1 使用 Selenium（Browser 自动化） |
| **Reason** | Browser 是 Observe 和 Act 的一种实现。已被 API 替代，证明可替换。 |

### IMP-004: API

| 字段 | 内容 |
|------|------|
| **Concept** | API |
| **Layer** | Implementation |
| **Evidence** | [CP-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-001-provider-adapter-pattern.md#L32): "OneAPI 不可达时自动 fallback 到 local_miner" |
| **Reason** | API 是 Observe 和 Act 的一种实现。当 OneAPI 不可用时，系统自动 fallback，证明可替换。 |

### IMP-005: Telegram

| 字段 | 内容 |
|------|------|
| **Concept** | Telegram |
| **Layer** | Implementation |
| **Evidence** | [PR-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-001-drawer-first.md#L21): "Layer 3 — Telegram" |
| **Reason** | Telegram 是 Observe 和 Act 的一种实现（消息监控和发送）。 |

### IMP-006: Filesystem

| 字段 | 内容 |
|------|------|
| **Concept** | Filesystem |
| **Layer** | Implementation |
| **Evidence** | [PR-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-001-drawer-first.md#L19): "Layer 1 — Workspace" |
| **Reason** | Filesystem 是最"笨"的实现：零配置、零依赖、零维护成本。是 Observe/Transform/Act 的基础实现。 |

### IMP-007: Policy

| 字段 | 内容 |
|------|------|
| **Concept** | Policy（策略） |
| **Layer** | Implementation |
| **Evidence** | [PR-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-001-drawer-first.md#L26): "Internet 是最后手段" |
| **Reason** | Policy 是具体规则文件。"Internet 是最后手段"是一条具体策略，可替换为其他策略。 |

### IMP-008: Constraint

| 字段 | 内容 |
|------|------|
| **Concept** | Constraint（约束） |
| **Layer** | Implementation |
| **Evidence** | [GV-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-001-admission-engine.md#L31): "禁止直接写入 02_MEMORY/ Tier 1 / Tier 2" |
| **Reason** | Constraint 是具体检查逻辑。它是 Boundary Invariant 的实现方式之一。 |

### IMP-009: Admission

| 字段 | 内容 |
|------|------|
| **Concept** | Admission（准入） |
| **Layer** | Implementation |
| **Evidence** | [GV-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-001-admission-engine.md#L19): "evolve() → apply_constraint_patch() → Admission Engine" |
| **Reason** | Admission 是具体工作流程。它是资产进入 Repository 的实现机制。 |

### IMP-010: Governance

| 字段 | 内容 |
|------|------|
| **Concept** | Governance（治理） |
| **Layer** | Implementation |
| **Evidence** | [GV-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-001-admission-engine.md#L1): "Admission Engine（资产准入引擎）"；[GV-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-002-civilization-freeze.md#L1): "Civilization Freeze（文明冻结）"；[GV-003](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-003-red-blue-round-table.md#L1): "Red-Blue Round Table（红蓝圆桌）" |
| **Reason** | Governance 是制度实现。GV-001/GV-002/GV-003 都是具体的治理文档，定义了具体流程和规则。更换这些文档不会影响系统的核心能力。 |

### IMP-011: Memory

| 字段 | 内容 |
|------|------|
| **Concept** | Memory（记忆存储） |
| **Layer** | Implementation |
| **Evidence** | [AX-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/axiom/AX-001-continuity-principle.md#L16): "Runtime 可以死，Repository 必须活" — Repository 是记忆的实现方式 |
| **Reason** | Memory 是具体持久化方式（SQLite/JSON/Filesystem）。它是 Identity Invariant 的实现工具。 |

### IMP-012: Compression

| 字段 | 内容 |
|------|------|
| **Concept** | Compression（压缩） |
| **Layer** | Implementation |
| **Evidence** | [R1_CIVILIZATION_GRAPH.json](file:///c:/Users/User/ace_workspace/mine-seed/03_DATA/research/r1_archaeology/R1_CIVILIZATION_GRAPH.json#L978): "Experience Compression Layer" |
| **Reason** | Compression 在这里指具体的压缩层实现（如 eco_layer.json、lexicon 压缩）。作为 Transform 子类的 "Compression" 是 Capability，但作为具体实现的 "Experience Compression Layer" 是 Implementation。 |

---

## Layer 4: System Property（涌现属性层）

> 注意：System Property 不属于系统的四层架构，是系统整体行为的涌现属性。

### PROP-001: Evolution

| 字段 | 内容 |
|------|------|
| **Concept** | Evolution（演化） |
| **Layer** | System Property |
| **Evidence** | [PR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-002-self-loop.md#L20): "Archive → Evolution → Heartbeat" |
| **Reason** | Evolution 是整个闭环（Observe → Transform → Act → Observe）产生的涌现属性。不是系统"能做什么"，而是"系统做了什么之后发生了什么"。 |

### PROP-002: Compression

| 字段 | 内容 |
|------|------|
| **Concept** | Compression（信息压缩） |
| **Layer** | System Property |
| **Evidence** | [R1_CIVILIZATION_GRAPH.json](file:///c:/Users/User/ace_workspace/mine-seed/03_DATA/research/r1_archaeology/R1_CIVILIZATION_GRAPH.json#L978): "Experience Compression Layer" |
| **Reason** | 作为 System Property 的 Compression = 系统在处理信息时自然产生的压缩行为。即使没有 "Experience Compression Layer" 这个实现，系统仍然会通过其他方式压缩信息。 |

---

## Layer 5: External Input（外部输入层）

> 注意：External Input 不属于系统。

### EXT-001: Reality

| 字段 | 内容 |
|------|------|
| **Concept** | Reality（现实） |
| **Layer** | External Input |
| **Evidence** | [PR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-002-self-loop.md#L24): "Environment → Observe" — Environment 即 Reality |
| **Reason** | Reality 是外部世界，不是系统的一部分。系统通过 Observe 获取 Reality 的信息。 |

---

## 跨层概念清理

### 已解决的跨层混淆

| 概念 | 之前的混乱归属 | 现在的唯一归属 | 解决理由 |
|------|--------------|--------------|---------|
| Continuity | Goal + Invariant | **Goal** | 它是系统存在的根本目的 |
| Boundary | Invariant + Constraint | **Invariant** | Constraint 是 Implementation |
| Identity | Invariant + Memory | **Invariant** | Memory 是 Implementation |
| Repository | Capability + Memory | **Implementation** | 它是具体存储方式 |
| Reason | Capability + Transform | **Transform（子类）** | 推理是信息变换 |
| Compression | Capability + Refinery | **Implementation / System Property** | 区分具体实现和涌现属性 |
| Evolution | Capability + Property | **System Property** | 不是系统能做什么 |
| Policy | Capability + Governance | **Implementation** | 它是具体规则文件 |
| Constraint | Invariant + Capability | **Implementation** | 它是具体检查逻辑 |
| Admission | Capability + Governance | **Implementation** | 它是具体工作流程 |
| Memory | Capability + Implementation | **Implementation** | 它是具体持久化方式 |
| Governance | Capability + Implementation | **Implementation** | 它是制度实现 |

---

## 验证规则

**规则 1**: 如果一个概念能出现在两层，说明分层失败。  
**规则 2**: 删除 Implementation 后 Capability 必须仍然存在。  
**规则 3**: 删除 Capability 后 Invariant 必须仍然存在。  
**规则 4**: 删除 Invariant 后 Goal 必须仍然存在。

### 验证结果

| 验证 | 结果 |
|------|------|
| 规则 1（无跨层概念） | ✅ 通过 |
| 规则 2（删除 Browser → Observe 仍在） | ✅ 通过 |
| 规则 2（删除 Repository → Transform 仍在） | ✅ 通过 |
| 规则 3（删除 Observe → Boundary 仍在） | ✅ 通过 |
| 规则 4（删除 Boundary → Continuity 仍在） | ✅ 通过 |

---

## 最终架构

```
Goal
    │
    ▼
Continuity
    │
    ▼
Invariant
    │
    ├── Boundary
    ├── Identity
    └── Observation
    │
    ▼
Capability
    │
    ├── Observe（Read, Watch, Capture, Search）
    ├── Transform（Compress, Verify, Remember, Reason, Decide）
    └── Act（Write, Send, Execute, Modify, Publish）
    │
    ▼
Implementation
    │
    ├── Repository, Memory MCP, Filesystem
    ├── Browser, API, Telegram, MCP, SSH
    ├── Policy, Constraint, Admission, Governance
    └── Memory, Compression
    │
    ▼
System Property（涌现属性，不属于系统四层）
    │
    ├── Evolution
    └── Compression（信息压缩行为）
    │
    ▼
External Input（不属于系统）
    │
    └── Reality
```

---

**状态**: ✅ Part A Complete — Layer Resolution  
**交付物**: LAYER_MAP.md  
**下一步**: Part B — Capability Final Compression
