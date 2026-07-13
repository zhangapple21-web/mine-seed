# Asset: Recovery Protocol（恢复协议）

**Name**: Recovery Protocol（恢复协议）

**Origin Repository**: mine-seed

**Purpose**: 发现恢复资产时不等待用户，先恢复，恢复失败再汇报。

**Problem It Solves**: 如果等待用户确认再恢复，可能错过最佳恢复时机；如果恢复失败不汇报，用户不知道系统状态。

**Core Structure**:
- 七步恢复：发现→读README→找关联压缩包→建依赖图→解压→建索引→报告
- 触发条件：EFP 扫到 backup/README/snapshot/archive/seed/recovery 等关键词

**Constraint**: 恢复失败必须汇报；恢复过程必须建索引。

**Evidence**: 04_PROTOCOLS/recovery_protocol.py（完整实现）

**Can Rebuild**: ✅ 80 行可重建——七步流程 + 依赖图 + 索引

**Can Replace**: ✅ 恢复策略可调整，框架不变

**Can Delete**: ⚠️ 删除会导致无法自动恢复，但不影响核心链路运行（短期）

**Distillation**:

Recovery Protocol 的核心原则是"恢复第一"。发现恢复资产时不等待用户，直接执行恢复流程。这体现了 Axiom-03（最小可迁移）——核心状态可以压缩到最小单元，恢复就是重建这个单元。七步流程确保了恢复的完整性：从发现到报告，每一步都有明确的目标和产出。
