# ASSET_INDEX.md — Civilization Asset Index

> **所有 Civilization Asset 的总索引。**
> Agent 读 `CIVILIZATION.md` 后，下一步是读本文件。
> 本文件**只索引，不复制**——所有详情在 `02_MEMORY/assets/*/*.md`。

---

## 总览

| 类别 | 数量 | 目录 |
|------|------|------|
| Axiom（公理） | 2 | `02_MEMORY/assets/axiom/` |
| Principle（原则） | 5 | `02_MEMORY/assets/principle/` |
| Governance（治理） | 3 | `02_MEMORY/assets/governance/` |
| Capability（能力） | 5 | `02_MEMORY/assets/capability/` |
| Role（角色） | 2 | `02_MEMORY/assets/role/` |
| Protocol（协议） | 2 | `02_MEMORY/assets/protocol/` |
| Cognition（认知） | 2 | `02_MEMORY/assets/cognition/` |
| Architecture（架构） | 2 | `02_MEMORY/assets/architecture/` |
| **合计** | **23** | — |

---

## Axiom（公理 — 不可替换）

| ID | 名称 | 重要性 | 蒸馏分 | 依赖 |
|----|------|--------|--------|------|
| [AX-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/axiom/AX-001-continuity-principle.md) | Continuity Principle | ★★★★★ | 10 | — |
| [AX-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/axiom/AX-002-repository-supremacy.md) | Repository Supremacy | ★★★★★ | 10 | AX-001 |

## Principle（原则 — 可替换实现）

| ID | 名称 | 重要性 | 蒸馏分 | 依赖 |
|----|------|--------|--------|------|
| [PR-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-001-drawer-first.md) | Drawer First | ★★★★★ | 9 | AX-002 |
| [PR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-002-self-loop.md) | Self-Loop | ★★★★★ | 9 | AX-001 |
| [PR-003](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-003-distill-before-archive.md) | Distill Before Archive | ★★★★★ | 9 | AX-002 |
| [PR-004](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-004-repository-is-the-bus.md) | Repository Is the Bus | ★★★★ | 8 | AX-002 |
| [PR-005](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/principle/PR-005-work-discovery.md) | Work Discovery | ★★★★ | 8 | PR-002 |

## Governance（治理）

| ID | 名称 | 重要性 | 蒸馏分 | 依赖 |
|----|------|--------|--------|------|
| [GV-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-001-admission-engine.md) | Admission Engine | ★★★★★ | 10 | AX-002, C-016 |
| [GV-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-002-civilization-freeze.md) | Civilization Freeze | ★★★★ | 9 | PR-002 |
| [GV-003](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/governance/GV-003-red-blue-round-table.md) | Red-Blue Round Table | ★★★★★ | 10 | C-024 |

## Capability（能力）

| ID | 名称 | 重要性 | 蒸馏分 | 依赖 |
|----|------|--------|--------|------|
| [CP-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-001-provider-adapter-pattern.md) | Provider Adapter Pattern | ★★★★ | 9 | PR-001 |
| [CP-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-002-worker-registry-dynamic.md) | Worker Registry 动态生成 | ★★★ | 8 | CP-001 |
| [CP-003](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-003-shadow-observer.md) | Shadow Observer | ★★★★ | 9 | CP-001 |
| [CP-004](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-004-smelter-gate.md) | Smelter Gate | ★★★★★ | 9 | C-019, GV-001 |
| [CP-005](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/capability/CP-005-multi-period-feedback.md) | T+N Multi-Period Feedback | ★★★ | 8 | — |

## Role（角色）

| ID | 名称 | 重要性 | 蒸馏分 | 依赖 |
|----|------|--------|--------|------|
| [RL-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/role/RL-001-red-team-roles.md) | Red Team Roles（5 人格） | ★★★★★ | 10 | GV-003 |
| [RL-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/role/RL-002-blue-team-defense.md) | Blue Team Defense（5 问） | ★★★★★ | 10 | GV-003 |

## Protocol（协议）

| ID | 名称 | 重要性 | 蒸馏分 | 依赖 |
|----|------|--------|--------|------|
| [PT-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/protocol/PT-001-heartbeat-protocol.md) | Heartbeat Protocol | ★★★★★ | 9 | PR-002 |
| [PT-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/protocol/PT-002-dual-trigger.md) | Dual-Trigger Mechanism | ★★★★ | 8 | PT-001 |

## Cognition（认知）

| ID | 名称 | 重要性 | 蒸馏分 | 依赖 |
|----|------|--------|--------|------|
| [CG-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/cognition/CG-001-question-first-cognition.md) | Question-First Cognition | ★★★★★ | 9 | CG-002 |
| [CG-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/cognition/CG-002-environmental-awareness.md) | Environmental Awareness | ★★★★★ | 9 | EFP-001 |

## Architecture（架构）

| ID | 名称 | 重要性 | 蒸馏分 | 依赖 |
|----|------|--------|--------|------|
| [AR-001](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/architecture/AR-001-four-layer-architecture.md) | Four-Layer Architecture | ★★★★★ | 10 | AX-001, AX-002 |
| [AR-002](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/assets/architecture/AR-002-asset-template.md) | Asset Template | ★★★★ | 8 | — |

---

## 评分说明

- **重要性**（★ 1-5）：该资产对文明连续性的影响
- **蒸馏分**（1-10）：从原始素材中提取的纯粹度（10=完全无原始依赖）
- **依赖**：必须先读的其他资产 ID

---

## P0 总闸门 — 任何新增资产必须通过三问

1. **它是 Runtime 状态，还是 Civilization 资产？**
2. **五个月后，新的 Agent 是否还能理解并继续使用？**
3. **如果删除当前 LLM，仅保留 Repository，是否还能重建这一能力？**

三问全过才可入本索引。

---

*索引由 AUM-MISSION-ARCH-017 建立（2026-07-14）。变更需经 Admission Engine。*
