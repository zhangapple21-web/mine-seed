# Asset: Ontology（本体论）

**Name**: Ω Runtime 本体定义（Ontology）

**Origin Repository**: r1-continuity-backup

**Purpose**: 定义 Runtime 最底层的对象、它们的唯一职责、生命周期、状态迁移、可序列化性。

**Problem It Solves**: 如果底层对象定义混乱，整个 Runtime 会混乱。需要一个统一的本体论来定义"什么是什么"，确保所有模块对同一个概念有一致的理解。

**Core Structure**:
- 12 个核心对象：Reality / Snapshot / Context / State / Judgment / Decision / Experience / Principle / Reflection / Projection / Policy / Provenance
- 4 个过程对象：Observation / Execution / Outcome / Feedback（不持久化）
- 对象间关系图：Reality→Snapshot→Context→Judgment→Decision→Execution→Feedback→State'
- 状态迁移：每个对象的生命周期明确

**Constraint**: 对象职责唯一，不重叠；过程对象不持久化。

**Evidence**: r1-continuity-backup/governance/ontology.md

**Can Rebuild**: ✅ 200 行可重建——12 个数据类 + 关系图 + 状态迁移定义

**Can Replace**: ✅ 对象可增减，本体论原则不变

**Can Delete**: ❌ 删除会导致 Runtime 失去底层定义，所有模块无法对齐

**Distillation**:

Ontology 是"Runtime 的字典"。它定义了最底层的概念，确保所有上层模块说的是同一种语言。12 个核心对象覆盖了 Runtime 的全部：从外部输入（Reality/Snapshot）到内部处理（Context/Judgment/Decision），从知识积累（Experience/Principle）到策略控制（Policy），再到溯源（Provenance）。4 个过程对象不持久化的设计很关键——它们是动作，不是状态，不需要存储。这套本体论是构建任何 Runtime 的地基。
