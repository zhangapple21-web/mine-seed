# CIVILIZATION.md — Civilization Layer

> **文明层总纲。** 身份层（AGENTS.md）只回答「我是谁」，本文件回答「文明是什么 / 怎么运转 / 资产放哪里」。
> 任何 Agent 在读 AGENTS.md 之后、下一步是读这份文件。

---

## Civilization Vision

ACE 的目标不是让一个 AI 记住东西，而是建立一个 **Civilization Repository**——一个 **任何 LLM** 都能读懂、5 个月后重启仍能继续工作的文明仓库。

| 维度 | 状态 |
|------|------|
| 主体 | Civilization Repository（仓库） |
| 运行时 | Runtime（可换、可重启、可丢失） |
| Agent | 可换（Trae / GPT / Claude / Gemini / 未来任何 LLM） |
| 身份入口 | AGENTS.md（极简） |
| 文明目录 | 本文件 |
| 资产清单 | `02_MEMORY/assets/ASSET_INDEX.md` |

---

## Repository Architecture — 四层结构

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 0 — Identity                                         │
│  ┌────────────────┬──────────────────┐                      │
│  │ AGENTS.md      │ CIVILIZATION.md  │  ← 任何 Agent 必读    │
│  └────────────────┴──────────────────┘                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 1 — Civilization Repository                          │
│  02_MEMORY/                                                 │
│    ├── assets/      ← 蒸馏后的文明资产（>=20）               │
│    ├── principles/  ← 核心原则                              │
│    ├── constraints/ ← 硬约束                                │
│    ├── missions/    ← Mission 记录                          │
│    ├── protocols/   ← 协议                                  │
│    ├── evidence/    ← 证据                                  │
│    ├── distillation/← 蒸馏产物                              │
│    ├── blueprints/  ← 架构蓝图                              │
│    └── history/     ← 文明史                                │
├─────────────────────────────────────────────────────────────┤
│  Layer 2 — Runtime State (06_RUNTIME/)                      │
│  ├── ROOT_STATE       ← 当前运行指纹                        │
│  ├── ACTIVE_MISSION   ← 进行中的 Mission                    │
│  ├── QUEUE            ← 任务队列                            │
│  ├── SESSION          ← 当前 Session                        │
│  └── TODAY            ← 今日工作日志                        │
├─────────────────────────────────────────────────────────────┤
│  Layer 3 — Session Logs (08_SESSIONS/)                      │
│  仅作历史。不可被运行时自动覆盖到 Layer 1。                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Asset Categories

| 类别 | 目录 | 含义 |
|------|------|------|
| 📐 Axiom | `assets/axiom/` | 文明公理，最高约束 |
| 📋 Principle | `assets/principle/` | 核心原则 |
| 🗂️ Governance | `assets/governance/` | 治理协议 |
| 🔌 Capability | `assets/capability/` | 能力契约 |
| 👤 Role | `assets/role/` | 角色系统 |
| 📊 Protocol | `assets/protocol/` | 协议 |
| 🧠 Cognition | `assets/cognition/` | 认知引擎 |
| 🏗️ Architecture | `assets/architecture/` | 架构蓝图 |

---

## Evolution Workflow（资产准入）

```
观察（Observation）
    ↓
问题（Question）
    ↓
假设（Hypothesis）
    ↓
实验（Experiment）
    ↓
证据（Evidence）
    ↓
决策（Decision — 经 Admission Engine）
    ↓
蒸馏（Distillation）
    ↓
Admission（进入 Civilization Layer）
```

---

## Admission Workflow（资产准入引擎）

任何新增资产在写入 `02_MEMORY/assets/` 前，必须经三问审查：

1. **它是 Runtime 状态，还是 Civilization 资产？**
   - Runtime 状态 → `06_RUNTIME/`
   - Civilization 资产 → `02_MEMORY/assets/`
2. **五个月后，新的 Agent 是否还能理解并继续使用？**
   - 否 → 拒绝（Reject List）
3. **如果删除当前 LLM，仅保留 Repository，是否还能重建这一能力？**
   - 否 → 拒绝（说明资产未蒸馏，只依赖 LLM 知识）

只有三问全过，才允许进入 Civilization Repository。

---

## Distillation Workflow

```
原始素材（聊天 / 源码 / 报告）
    ↓
压缩（提取关键事实 / 数字 / 结论）
    ↓
抽象（提炼为原则 / 公理 / 协议）
    ↓
结构化（按模板写为 Asset）
    ↓
索引（写入 ASSET_INDEX）
```

每条 Asset 模板：

```
Name / Origin / Purpose / Problem
Core Structure / Constraint / Evidence
Distillation / Related Assets / Replaceable / Rebuildable
```

---

## Recovery Workflow

| 触发条件 | 动作 |
|----------|------|
| 找不到 README | 报错 + 提示运行 EFP |
| 找不到 AGENTS.md | 报错 + 提示完整 Bootstrap |
| Runtime 状态为空 | 从 06_RUNTIME/ 上次快照恢复 |
| Civilization 资产缺失 | 报错 + 提示资产丢失（非可恢复） |
| Agent 上下文丢失 | 重新执行 BOOTSTRAP_FLOW |

---

## Continuity Principle（连续性公理）

> **Civilization Repository 是连续性的主体。**
>
> Runtime 是生命，Repository 是文明。
> 生命可以死，文明必须活。
> 当一个 Runtime 死掉，下一个 Runtime 应当能从同一份 Repository 复活。

---

## P0 总闸门（三问）

任何新增内容，在写入 Repository 前必须回答：

1. **它是 Runtime 状态，还是 Civilization 资产？**
2. **五个月后，新的 Agent 是否还能理解并继续使用？**
3. **如果删除当前 LLM，仅保留 Repository，是否还能重建这一能力？**

**只有三问全过，才允许进入 Civilization Repository。**

---

*文明层总纲。变更需经 C-018（Asset Creation Gate）审核。*
