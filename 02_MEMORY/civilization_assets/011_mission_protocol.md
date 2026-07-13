# Asset: Mission Protocol（文明任务协议）

**Name**: Mission Protocol（文明任务协议）

**Origin Repository**: mine-seed

**Purpose**: 将任务从"做什么"升级为"为什么做/做到什么程度/不能做什么/最后要沉淀什么"。

**Problem It Solves**: 普通 TODO 只说做什么，没有目标、验收、禁止、沉淀，做完就忘，无法积累文明资产。

**Core Structure**:
- 八层结构：Header→Mission→Scope→Deliverables→Acceptance→Forbidden→Distillation→Admission
- Drawer Scan 强制要求（Phase 0）
- Distillation 六资产：Kernel/Blueprint/Protocol/Constraint/Experience/Identity

**Constraint**: 未完成 Drawer Scan，Mission 不允许进入 Research 阶段。

**Evidence**: 04_PROTOCOLS/mission_protocol.py（完整实现）

**Can Rebuild**: ✅ 200 行可重建——数据类 + 创建逻辑 + 状态机 + 持久化

**Can Replace**: ✅ 存储后端可换，结构不变

**Can Delete**: ❌ 删除会导致任务失去目标和沉淀机制

**Distillation**:

Mission Protocol 的核心洞察是"任务只是触发器，文明资产才是终点"。八层结构确保每个任务都有明确的目标（Mission）、范围（Scope）、产出（Deliverables）、验收标准（Acceptance）、禁止事项（Forbidden）、蒸馏目标（Distillation）和准入审查（Admission）。Drawer Scan 强制要求确保了"先翻抽屉，再造轮子"——在做任何事之前先检查已有资产。这是 mine-seed 最核心的协议创新。
