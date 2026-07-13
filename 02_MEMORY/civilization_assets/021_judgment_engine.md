# Asset: Judgment Engine（判断引擎）

**Name**: Judgment Engine（判断引擎）

**Origin Repository**: r1-continuity-backup

**Purpose**: 填补 Observation → Decision 之间的认知评估缺口，通过双层校验提升判断可信度。

**Problem It Solves**: 直接从观察跳到决策会导致误判。需要一个中间层对观察做认知评估，考虑多种假设、依赖假设、外部校验。

**Core Structure**:
- 双层校验：内部推导（assumptions + alternatives + evidence）+ 外部独立校验（Teacher 反向验证）
- Multi-Hypothesis Ranking：多假设排序，每个假设含正反证据
- Assumption 显式化：区分显式/隐含假设，支持递归追问
- Confidence 核定：双层验证均通过才能 > 0.5

**Constraint**: 任何 Judgment 必须考虑替代解释；隐含假设必须显式化。

**Evidence**: r1-continuity-backup/governance/judgment_engine.md

**Can Rebuild**: ✅ 100 行可重建——Judgment 数据类 + 内部推导 + 外部校验钩子 + 置信度计算

**Can Replace**: ✅ 校验策略可调整，框架不变

**Can Delete**: ⚠️ 删除会导致决策质量下降，但不影响核心链路运行

**Distillation**:

Judgment Engine 的核心原则是"不要轻易相信第一解释"。双层校验确保了判断的可靠性：内部推导列出所有可能的解释和依赖假设，外部校验（Teacher 角色）从反面验证。Multi-Hypothesis Ranking 避免了"确认偏误"——不只找支持的证据，也找反对的证据。Assumption 显式化则防止了"隐含假设导致的错误"——很多决策错误不是因为推理错了，而是因为隐含的假设有问题。
