# HYP-2026-07-15-001: 治理规范 v1.0 候选

> **状态**: HYPOTHESIS（不是 ADR，不是 v1.0）
> **修订**: v0.2 (2026-07-15) — 反映 GPT 第二次评审 + 拍板 C-027
> **来源**: GPT-4 两次一致性评审（External Review，已归档）
> **Admission 状态**: Pending
> **创建日期**: 2026-07-15

## 1. Hypothesis 描述

基于 GPT-4 两次对板块0（C-026/C-027）+ 板块A'（Signal Candidate 链路）的一致性评审：

> 5个维度（一致性/可演化/治理闭环/命名统一/可追溯/可验证）均评为 5/5
> 四条链路（Mission/治理/Signal/External）现在是同一个治理模式 O→E→C→A→K
> 建议视为统一治理协议 v1.0

**Hypothesis**: 现有治理体系（Observation→Evidence→Candidate→Admission→Knowledge/Policy）已收敛为统一治理协议，可正式定为 ACE 治理规范 v1.0。

## 2. v0.2 重大修正（采纳 GPT 第二次评审）

### 2.1 术语边界修正

| 旧 | 新 | 修正原因 |
|----|-----|---------|
| External Knowledge | External Observation | Knowledge 保留给已通过治理的内容（GPT 评审）|
|  | + External Review（子类） | LLM 评审/同行评议 |

### 2.2 Evidence Profile 替代硬四类齐

新治理原则、交易策略、Bug 修复、文档修订等不同 Candidate 适用不同 Evidence Profile。

**禁止**: 固定模板硬套所有 Candidate。

### 2.3 新增 C-027（更重要）

**C-027 — Governance as Governance Object** 拍板写入 PRINCIPLES.md（PROVISIONAL，30 天复审）

> **Governance 不拥有豁免权。**
> 任何治理规则（含 C-026/C-027/未来 v1.0）的提出、修改、废弃必须走 Admission 流程。

**重要性**: C-027 比 v1.0 标签**更重要**——v1.0 是收敛动作，C-027 是收敛前提。

## 3. 为什么是 Hypothesis 不是 ADR

按 C-026（External Observation Principle）+ C-027（Governance as Governance Object）：

1. **GPT 评审是 External Review**，按 C-026 硬约束永远不能成 Knowledge
2. v1.0 是**文明资产级别变更**，必须经 C-027 规定的 Admission 流程
3. 评审本身给出"建议"而非"决策"——决策权在治理层
4. C-027 自身是 v0.1 PROVISIONAL——v1.0 派单前 C-027 必须先通过 Admission

## 4. 走 Admission 流程需要的证据（按 Evidence Profile）

C-027 类治理变更的 Evidence Profile：

| 维度 | 当前状态 | 缺口 |
|------|----------|------|
| External Review | ✅ 已归档（GPT 两次评审） | 充分 |
| Internal Discussion | 部分（执行者判断 + 用户对话） | 缺其他治理层成员参与 |
| Live Observation | 无 | 需 30 天内观察 C-026/C-027 实际运行情况 |

**结论**: **当前 evidence 不够**——Internal Discussion 不完整，Live Observation 缺失。

## 5. v1.0 派单的前置条件（已写进 C-027 配套 Evidence Profile）

| 阶段 | 状态 | 触发条件 |
|------|------|----------|
| 现状 | C-024/C-025/C-026/C-027 全部 PROVISIONAL | 已存在 |
| Hypothetical v1.0 | 本文档（HYP-2026-07-15-001）| 由 External Review 触发 |
| 实际 v1.0 | 需 C-027 通过 Admission + Internal Discussion 完整 + Live Observation ≥ 30 天 | 等待 |

## 6. GPT 评审归档

详见：
- [evidence_20260715_external.jsonl](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/evidence/evidence_20260715_external.jsonl) - 第一次评审：5/5 一致性结论
- [evidence_20260715_external_v2.jsonl](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/evidence/evidence_20260715_external_v2.jsonl) - 第二次评审：三条实质修正（已全部采纳）
- [evidence_index.json](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/evidence/evidence_index.json) - 已索引

## 7. 采纳的 GPT 全部建议

| ID | 建议 | 采纳 | 写入位置 |
|----|------|------|---------|
| S1 | External Knowledge → External Observation/Review | ✅ | C-026 v0.2 |
| S2 | Evidence Profile 替代硬四类齐 | ✅ | Evidence Classification v0.2 |
| S3 | Governance 不拥有豁免权 | ✅ | C-027 新增 |
| 另 | 不加 Evidence Capture 阶段 | ✅ | 维持现状 |
| 另 | 治理 v1.0 派单 | ❌ 等 evidence 充分 | 本文档 |

## 8. 下一步

- [ ] 等待 C-027 30 天 PROVISIONAL 复审
- [ ] 等待 Internal Discussion 完整（其他治理层成员参与）
- [ ] 等待 Live Observation ≥ 30 天
- [ ] 现状：所有 PROVISIONAL 保持原状

**演化日志**:
- 2026-07-15 v0.1 (HYPOTHESIS) — 由第一次 GPT 评审触发。不派单 v1.0。
- 2026-07-15 v0.2 (HYPOTHESIS) — 反映 GPT 第二次评审：采纳术语修正 + Evidence Profile + C-027 拍板。
