# Asset: Drawer First Protocol（抽屉优先协议）

**Name**: Drawer First Protocol（DFP-001）

**Origin Repository**: mine-seed

**Purpose**: 任何设计、实现、重构、派单之前，必须先扫描现有文明资产，决定复用/扩展/新建。

**Problem It Solves**: 不先查已有资产会导致重复开发、知识碎片化、文明膨胀。

**Core Structure**:
- 七步扫描：Modules→RFC→Protocol→Experience→Constraint→Blueprint→Decision
- Verdict 输出：REUSE/EXTEND/NEW
- 强制要求：未完成扫描，Mission 不允许进入 Research

**Constraint**: 任何 Mission 第一条必须是抽屉扫描。

**Evidence**: 04_PROTOCOLS/ops_000_asset_first.py + PRINCIPLES.md（详细定义）

**Can Rebuild**: ✅ 50 行可重建——七步扫描函数 + Verdict 逻辑

**Can Replace**: ✅ 扫描顺序可调整，原则不变

**Can Delete**: ❌ 删除会导致重复开发和文明膨胀

**Distillation**:

DFP-001 的核心原则是"先翻抽屉，再造轮子"。七步扫描确保了在做任何事之前，先检查是否已有可用资产：先看模块，再看 RFC，再看协议，再看经验，再看约束，再看蓝图，最后决定。Verdict 三种结果（复用/扩展/新建）确保了资产的合理利用。这条协议从根本上防止了文明膨胀。
