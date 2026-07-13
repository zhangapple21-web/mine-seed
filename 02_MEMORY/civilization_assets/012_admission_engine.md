# Asset: Admission Engine（文明准入引擎）

**Name**: Admission Engine（文明准入引擎）

**Origin Repository**: mine-seed

**Purpose**: 审查资产是否满足准入条件，确保只有高质量、有价值、不污染文明的资产才能进入仓库。

**Problem It Solves**: 如果没有准入审查，文明仓库会被垃圾填满，导致知识膨胀、决策质量下降。

**Core Structure**:
- 准入六问：Worth（值得吗）/ Reuse（会复用吗）/ Purity（会污染吗）/ Novelty（重复吗）/ Quality（有更好的吗）/ Compliance（合规吗）
- 审查通过后调用 Repository.add() 写入
- 不负责持久化（RepositoryStore 处理）

**Constraint**: 审查不通过的资产不得进入仓库；审查记录必须保留。

**Evidence**: 04_PROTOCOLS/admission_engine.py（完整实现）

**Can Rebuild**: ✅ 100 行可重建——六个检查函数 + 结果汇总 + Repository 调用

**Can Replace**: ✅ 审查标准可调整，框架不变

**Can Delete**: ❌ 删除会导致垃圾资产进入仓库，污染文明

**Distillation**:

Admission Engine 是"文明的守门人"。六问覆盖了资产价值的所有维度：是否值得保存、是否会被复用、是否会污染文明、是否重复、质量是否达标、是否合规。它与 ace_core 的 GovernorProtocol 互补——GovernorProtocol 侧重知识治理（证据/验证/审批），AdmissionEngine 侧重资产准入（价值/复用/纯净）。两者可以合并为统一的准入层。
