# Continuity 升级联动影响分析报告

> **Status**: 仅分析，不执行
> **Created**: 2026-07-15
> **Trigger**: ARCH-024 裁定3

---

## 背景

在 ARCH-020 Red Team Review 中，Continuity 被列为 5 个 Invariant 之一：
- Continuity（连续性）
- Boundary（边界）
- Observation（观察）
- Evolution（演化）
- Risk Conversion（风险转换）

在后续的 ARCH-021/022 中，Continuity 被升级为 Goal Layer（目标层），成为系统存在的根本目的。

本报告分析这个改动与"三个不可丢失约束（Continuity / L∞ / Admission）"提法之间的关系，以及是否需要联动调整。

---

## 分析

### 1. Continuity 的原始定义

在 `project_memory.md` 中，Continuity 被定义为：

> ACE (Autonomous Civilization Engine) operates on the 'Continuity Principle' as its core axiom.

这是一个存在性前提——没有连续性，系统就不存在。

### 2. "三个不可丢失约束"的原始语境

"三个不可丢失约束（Continuity / L∞ / Admission）"出现在多个治理文档中，包括：
- ROOT_STATE.md（已归档）
- ARCH-011 Admission Engine 设计
- C-011 ~ C-020 系列约束

它们的含义：

| 约束 | 含义 | 层级 |
|------|------|------|
| Continuity | 系统必须持续运行，不可中断 | Goal / Invariant? |
| L∞ | 无限记忆，不可丢失 | Capability（Memory） |
| Admission | 所有写入必须经过准入审查 | Governance |

### 3. 问题：Continuity 属于 Goal 还是 Invariant？

**Goal Layer**：系统的目的——"我们为什么存在"
**Invariant Layer**：系统不可违背的约束——"我们必须遵守什么"

Continuity 可以同时满足两种定义：
- 作为 Goal：系统的目的是持续运行
- 作为 Invariant：系统不可中断运行

**区别在于视角**：
- Goal 视角：Continuity 是我们要实现的目标
- Invariant 视角：Continuity 是我们不可违反的约束

### 4. 联动影响分析

如果 Continuity 升级为 Goal：

| 影响项 | 当前状态 | 需要调整? |
|--------|---------|-----------|
| "三个不可丢失约束"提法 | Continuity / L∞ / Admission | 需要重新表述，Continuity 不再与其他两项并列 |
| INVARIANT_FINAL.md | 不包含 Continuity | 无需调整 |
| Governance 文档 | Admission 作为约束 | 无需调整，Admission 仍属于 Governance |
| L∞ 记忆约束 | L∞ 作为 Capability | 无需调整 |

**关键问题**：
"三个不可丢失约束"原本是三个并列项，但如果 Continuity 升级为 Goal，它就不再是与其他两项并列的约束，而是更高层级的目的。

**建议表述调整**：
- 原表述："三个不可丢失约束（Continuity / L∞ / Admission）"
- 新表述："一个根本目标（Continuity）+ 两个核心约束（L∞ / Admission）"

### 5. 与 ARCH-022 v1.0 冻结的关系

ARCH-022 将 Continuity 归入 Goal Layer，但没有更新"三个不可丢失约束"的表述。

**如果接受这个升级**：
1. 需要更新相关文档中的表述
2. 需要在 Goal Layer 定义中明确 Continuity 的位置
3. 需要确认 L∞ 和 Admission 是否也属于 Goal Layer 还是保持在其他层级

**如果不接受这个升级**：
1. Continuity 应保持在 Invariant Layer
2. 需要修正 ARCH-022 的 Goal Layer 定义
3. "三个不可丢失约束"表述保持不变

---

## 结论

**问题本质**：Continuity 的层级归属是一个定义问题，不是技术问题。

**两个选项**：

| 选项 | 含义 | 联动影响 |
|------|------|---------|
| **A: 升级为 Goal** | Continuity 是系统目的，高于 Invariant | 需要更新"三个不可丢失约束"表述；需要在 Goal Layer 明确定义 |
| **B: 保持为 Invariant** | Continuity 是约束，与其他 Invariant 并列 | 需要修正 ARCH-022；"三个不可丢失约束"表述保持不变 |

**本报告不做出推荐**——这需要用户显式决策。

---

## 待决策

- [ ] Continuity 应该属于 Goal Layer 还是 Invariant Layer？
- [ ] 如果升级为 Goal，是否更新"三个不可丢失约束"表述？
- [ ] L∞ 和 Admission 是否也需要重新定级？

---

*此文档为 ARCH-024 板块一交付物，响应裁定3（仅分析，不执行）。*