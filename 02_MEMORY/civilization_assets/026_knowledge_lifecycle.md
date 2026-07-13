# Asset: Knowledge Lifecycle Policy（知识生命周期策略）

**Name**: Knowledge Lifecycle Policy（知识生命周期策略）

**Origin Repository**: r1-continuity-backup

**Purpose**: 管理所有概念/资产的生命周期：Draft → Active → Merge → Deprecated → Archived，防止知识膨胀。

**Problem It Solves**: 知识如果只有新增没有淘汰，会导致概念膨胀、重复、混乱。需要一个生命周期管理机制，让知识有出生、有成长、有合并、有淘汰、有归档。

**Core Structure**:
- 五级生命周期：Draft → Active → Merge → Deprecated → Archived
- Merge 规则：重复/重叠概念合并，新概念引入必须"至少减少两个旧概念"
- Deprecation 规则：被合并/无法通过现实验证/引用计数归零 → 废弃
- Archive 规则：连续两个 Sprint 无引用 + 血缘完整 → 归档
- 例外保护：core 标记的概念 / 当前 Sprint 使用的 / 与 Principle 层直接关联的 → 不允许合并或废弃

**Constraint**: 不允许直接删除仍有引用的概念；废弃前必须有替代方案。

**Evidence**: r1-continuity-backup/governance/lifecycle_policy.md

**Can Rebuild**: ✅ 80 行可重建——五级状态机 + Merge/Deprecation/Archive 规则 + 例外保护

**Can Replace**: ✅ 状态可增减，生命周期原则不变

**Can Delete**: ❌ 删除会导致知识膨胀失控（但 mine-seed 已有简化版 Admission + Mengpo）

**Distillation**:

Knowledge Lifecycle Policy 的核心洞察是"知识也有生老病死"。五级生命周期确保了知识的健康：Draft 是候选，Active 是在用，Merge 是去重，Deprecated 是淘汰，Archived 是安息。最关键的是 Merge 规则中的"新概念引入必须至少减少两个旧概念"——这条规则从根本上防止了知识膨胀，确保了系统的简洁性。它与 mine-seed 的 C-021（减法模式）、C-023（准入三问）和 Mengpo（遗忘机制）互补，共同构成了知识治理的完整闭环。
