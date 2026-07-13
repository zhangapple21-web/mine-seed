# Asset: Evidence Graph

**Name**: Evidence Graph（证据图谱）

**Origin Repository**: mine-seed

**Purpose**: 建立文明资产之间的证据关系网络，支持溯源和交叉验证。

**Problem It Solves**: 文明资产如果没有证据关联，会变成孤立的碎片，无法验证真伪、无法追溯来源、无法交叉校验。

**Core Structure**:
- 证据节点（EvidenceNode）
- 关系边（supports/contradicts/related_to/derived_from）
- 置信度传播
- 交叉验证引擎

**Constraint**: 每个资产必须有证据支撑；证据链必须可追溯。

**Evidence**: 04_PROTOCOLS/evidence_graph.py（mine-seed 实现）

**Can Rebuild**: ✅ 100 行可重建——图结构 + 关系定义 + 查询函数

**Can Replace**: ✅ 图存储可换（邻接表→Neo4j），接口不变

**Can Delete**: ❌ 删除会导致文明资产失去证据支撑，无法验证

**Distillation**:

EvidenceGraph 是"文明的法庭"。它把每个资产变成一个节点，证据变成边，形成一个可验证的网络。当需要验证某个结论时，不只看结论本身，还要看支持它的证据链、有没有矛盾的证据、来源是否可靠。这体现了 Axiom-02（排他优先）——先排除不可靠的，再验证可靠的。证据图谱让文明从"相信"走向"验证"。
