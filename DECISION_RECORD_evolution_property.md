# Decision Record: Evolution as System Property

**ID**: DR-001  
**Date**: 2026-07-14  
**Status**: Approved  
**Decision Maker**: ACE Governance  

---

## 背景

在 ARCH-024 架构缺口补正中，需要明确 Evolution 的层级归属：

**问题**: Evolution 应该属于哪一层？

**候选**:
1. **Goal Layer**: 系统的根本目的是进化
2. **Invariant Layer**: 进化是不可违背的约束
3. **Capability Layer**: 进化是系统的一种能力
4. **System Property**: 进化是系统整体行为的涌现属性

---

## 决策

**Evolution 降级为 System Property。**

```
Evolution is not what the system does.
Evolution is what happens when the system does what it does.
```

---

## 为什么不是 Goal？

**Goal** 回答"系统存在的根本目的是什么"。

Evolution 不是目的，它是过程的副产品。系统的目的是维护文明（Continuity），进化是维护过程中自然产生的结果。

---

## 为什么不是 Invariant？

**Invariant** 回答"系统不可违背什么"。

Evolution 不是约束。即使系统停止进化（例如冻结状态），系统仍然是有效的文明系统。进化是期望行为，不是必需条件。

---

## 为什么不是 Capability？

**Capability** 回答"系统能做什么"。

Evolution 不是系统的能力。系统的能力是 Observe、Transform、Act。Evolution 是这些能力共同作用的结果——它是涌现属性。

---

## 为什么是 System Property？

**System Property** 是系统整体行为的涌现属性，不属于系统的四层架构。

| 特征 | 说明 |
|------|------|
| **涌现性** | 进化不是单一模块的功能，而是 Observe→Transform→Act→Observe 闭环的整体结果 |
| **非必要性** | 系统可以在不进化的状态下正常运行（如冻结状态） |
| **不可直接控制** | 不能通过调用"进化接口"来触发进化，只能通过优化各个能力层来促进进化 |

---

## 与其他概念的关系

```
Goal（目标层）
    │
    ▼
Invariant（不变量层）
    ├── Continuity   — 身份和状态不可漂移
    ├── Boundary     — 行动边界
    ├── Observation  — 证据约束
    └── Risk Conversion — 风险约束
    │
    ▼
Capability（能力层）
    ├── Observe
    ├── Transform
    └── Act
    │
    ▼
Implementation（实现层）
    └── 具体模块、脚本、工具
    │
    ▼
System Property（涌现属性）
    ├── Evolution — 闭环运行的自然结果
    └── Compression — 信息处理的自然结果
```

---

## 影响

| 组件 | 影响 | 行动 |
|------|------|------|
| LAYER_MAP.md | Evolution 从 Invariant/Capability 移至 System Property | 更新文档 |
| INVARIANT_FINAL.md | Evolution 不再作为 Invariant | 无需修改（未列入） |
| ADR-001 | 四层架构不包含 System Property | 无需修改 |

---

## 结论

Evolution 是系统运行过程中自然产生的涌现属性，不是系统的目的、约束或能力。

**记录**: DECISION_RECORD_evolution_property.md  
**状态**: ✅ Approved  
**日期**: 2026-07-14