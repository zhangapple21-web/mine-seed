# Asset: Energy Budget（能量预算）

**Name**: Energy Budget（能量预算）

**Origin Repository**: mine-seed

**Purpose**: 监控和管理系统的四种能量（API 调用/Token/磁盘 IO/网络请求），实现四级降级。

**Problem It Solves**: 系统运行会消耗资源，如果不限制，会导致成本失控、资源耗尽、服务中断。

**Core Structure**:
- 四级降级：green→yellow→orange→red
- 四种能量类型：API 调用/Token/磁盘 IO/网络请求
- 每日/每小时/心跳预算
- 优先级门控（低优先级任务在 orange/red 时暂停）

**Constraint**: 能量耗尽前必须降级；降级策略必须可配置。

**Evidence**: 04_PROTOCOLS/energy_budget.py（完整实现）

**Can Rebuild**: ✅ 100 行可重建——四级状态机 + 四种能量计数器 + 优先级门控

**Can Replace**: ✅ 预算值可调整，框架不变

**Can Delete**: ⚠️ 删除会导致资源不受限制，但不影响核心链路运行（短期）

**Distillation**:

Energy Budget 的核心洞察是"系统需要像生物体一样管理能量"。四级降级确保了系统在资源紧张时优雅降级，而不是突然崩溃。优先级门控确保了核心任务总能获得资源，非核心任务在资源紧张时自动暂停。这体现了 C-021（减法/稳定模式）——新增任何东西之前，先问"移除它会不会影响核心链路"。
