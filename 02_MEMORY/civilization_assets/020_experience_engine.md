# Asset: Experience Engine（经验引擎）

**Name**: Experience Engine（经验引擎）

**Origin Repository**: r1-continuity-backup

**Purpose**: 将事件提炼为可迁移的经验，保存"为什么这次有效"而不是"发生了什么"。

**Problem It Solves**: Memory 只记录事件，不提炼因果。如果没有经验提炼，系统只会重复犯错，不会从历史中学习。

**Core Structure**:
- Experience = Reflection 提炼的可迁移认知
- 四种类型：positive（有效）/ negative（有害）/ boundary（边界）/ pattern（模式）
- 因果结构：cause → effect → mechanism
- 适用边界：context_pattern + confidence + scope + time_bound
- 验证状态：support_cases / contradict_cases / validation_status
- Lineage：来源 + 相关经验 + 替代关系

**Constraint**: 经验不是事实，是有适用边界的假设；必须经过验证才能提升可信度。

**Evidence**: r1-continuity-backup/governance/experience_engine.md

**Can Rebuild**: ✅ 120 行可重建——Experience 数据类 + generate() + validate() + query()

**Can Replace**: ✅ 存储后端可换，经验结构不变

**Can Delete**: ⚠️ 删除会导致系统无法从历史中学习，但不影响核心链路运行（短期）

**Distillation**:

Experience Engine 的核心洞察是"经验不是事件的拷贝，而是因果结构的压缩"。Memory 记"发生了什么"，Experience 记"为什么有效/无效"。四种类型覆盖了学习的所有维度：正面经验（做什么有效）、负面经验（做什么有害）、边界经验（什么时候适用）、模式经验（跨场景规律）。最关键的是"适用边界"——任何经验都有适用范围，知道什么时候不适用比知道什么时候适用更重要。
