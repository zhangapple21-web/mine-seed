# Asset: Governor Protocol

**Name**: Governor Protocol（治理协议）

**Origin Repository**: ace_core

**Purpose**: 定义知识单元进入文明的准入标准和审批流程。

**Problem It Solves**: 知识单元如果没有统一的准入标准，会导致文明污染（假设变事实、无证据的结论进入系统）。

**Core Structure**:
- 四级准入标准（Evidence/Validation/GovernorApproval/NoHypothesisToFact）
- AdmissionCriteriaResult 检查结果类
- 拒绝标准 + 质量保证
- 决策权限分级

**Constraint**: 不得是 Hypothesis 直接变 Fact；Governor 审批是必经之路。

**Evidence**: ace_core/core/governance/governor_protocol.py（47KB）

**Can Rebuild**: ✅ 150 行可重建——四个检查函数 + 结果汇总 + 审批记录

**Can Replace**: ✅ 准入标准可调整，但框架不变

**Can Delete**: ❌ 删除会导致垃圾知识进入文明，污染整个系统

**Distillation**:

GovernorProtocol 是"文明的门卫"。四级准入标准层层过滤：先看有没有证据，再看有没有验证，再看有没有审批，最后检查是不是把假设当事实。这条链确保了进入文明的知识都是经过验证的。它与 mine-seed 的 AdmissionEngine（六问审查）互补——GovernorProtocol 更侧重知识治理，AdmissionEngine 更侧重资产准入。两者可以合并为统一的准入层。
