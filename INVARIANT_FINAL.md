# Invariant Layer — 最终定义 (v1.0)

> **Status**: ARCH-024 板块一交付物
> **Created**: 2026-07-15
> **Source**: ARCH-020 Red Team Review + ARCH-024 裁定

---

## 定义

**Invariant（不变量）**：系统运行过程中不可违反的约束条件。它们不是"系统能做什么"（Capability），而是"系统不可违背什么"——是比 Goal 更底层的存在性前提。

---

## Invariant 层成员

| ID | Name | 定义 | 来源 |
|----|------|------|------|
| INV-001 | Continuity | 系统的身份和状态不可漂移，运行不可中断 | AX-001 |
| INV-002 | Boundary | 系统的行动边界，不可越界执行 | ARCH-020 |
| INV-003 | Observation | 所有决策必须有观察证据支撑 | ARCH-020 |
| INV-004 | Risk Conversion | 风险必须在可控范围内转换，不允许风险累积 | ARCH-020（补回） |

---

## 各 Invariant 详细说明

### INV-001 — Continuity

**定义**：系统的身份和状态不可漂移，运行不可中断。Runtime 可以死，Repository 必须活。

**验证方式**：
- Repository 是否持续存在且可访问
- 系统重启后是否能从 Repository 恢复完整状态
- 身份（Identity）是否在重启前后保持一致

**违反后果**：
- 触发 Recovery Protocol（RP）
- 标记为 `CRITICAL` 级别告警
- 暂停所有非核心操作，优先恢复连续性

**关联约束**：
- AX-001 Continuity Principle
- OPS-004 Recovery First
- PR-002 Self-Loop

---

### INV-002 — Boundary

**定义**：系统的行动边界，任何操作都不得越过预设的权限和范围。

**验证方式**：
- 每个操作执行前检查是否在允许范围内
- 越界操作必须被拦截并记录

**违反后果**：
- 操作被拒绝
- 触发审计告警
- 记录到 violation_log

**关联约束**：
- C-018 Asset Creation Gate
- ARCH-011 Admission Engine

---

### INV-003 — Observation

**定义**：所有决策必须有观察证据支撑，禁止无证据决策。

**验证方式**：
- 每个决策必须能追溯到 observation_log 中的记录
- 无法追溯的决策标记为 `evidence_missing`

**违反后果**：
- 决策降级为 `hypothesis`（假设），不作为最终决策执行
- 触发 Red Team 审计

**关联约束**：
- OPS-006 Search Policy（证据层级）
- C-024 Civilization Quality Traits（testable）

---

### INV-004 — Risk Conversion

**定义**：风险必须在可控范围内转换，不允许风险累积。当检测到风险累积时，系统必须主动降低风险敞口。

**验证方式**：
- 风险事件触发后，检查是否有对应的降险动作
- 连续 N 次失败后，必须有约束生成（E→C 闭环）

**违反后果**：
- 强制触发约束生成
- 暂停相关操作，待风险评估通过后恢复

**关联约束**：
- CP-005 T+N Multi-Period Feedback
- E→C Closure Protocol

---

## 与其他层的关系

```
Goal Layer（目标层）
    └── [待定义] —— 系统存在的根本目的
         │
         ▼
Invariant Layer（不变量层）
    ├── Continuity   —— 身份和状态不可漂移，运行不可中断
    ├── Boundary     —— 行动边界
    ├── Observation  —— 证据约束
    └── Risk Conversion —— 风险约束
         │
         ▼
Capability Layer（能力层）
    ├── Observe  —— 观察能力
    ├── Transform —— 变换能力
    └── Act      —— 执行能力
         │
         ▼
Implementation Layer（实现层）
    └── 具体模块、脚本、工具
```

---

## 为什么 Risk Conversion 被补回

在 ARCH-020 Red Team Review 中，Risk Conversion 被明确列为 5 个 Invariant 之一。但在后续的 ARCH-021/022 中，该 Invariant 未出现，且没有任何解释说明其被移除或合并。

**裁定依据**：
1. Red Team 明确列过 Risk Conversion
2. 后续文档没提 ≠ 被推翻
3. 风险约束是系统稳定性的关键组成部分

因此，按 ARCH-024 裁定1，将 Risk Conversion 补回 Invariant 层。

---

## 变更记录

| 日期 | 变更内容 | 触发来源 |
|------|---------|---------|
| 2026-07-15 | 创建 INVARIANT_FINAL.md，包含 Boundary/Observation/Risk Conversion | ARCH-024 裁定1 |
| 2026-07-15 | 补入 Continuity 为 INV-001；确认 Continuity 属于 Invariant 而非 Goal | ARCH-024 用户裁定（选B） |

---

## 待决策项

- [x] Continuity 保持 Invariant 层，不升级为 Goal（ARCH-024 用户裁定，选B）
- [ ] Evolution 作为 System Property 单独记录（已决策，待创建文档）

---

*此文档为 ARCH-024 板块一交付物，经用户裁定后创建。*