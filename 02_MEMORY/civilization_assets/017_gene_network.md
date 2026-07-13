# Asset: Gene Network（基因网络）

**Name**: Gene Network（基因网络）

**Origin Repository**: mine-seed

**Purpose**: 扫描所有文明资产，建立依赖关系图，实现四级变异风险评估。

**Problem It Solves**: 修改一个资产可能影响其他资产，如果没有依赖关系图，会导致连锁故障、意外后果、演化失控。

**Core Structure**:
- 基因分类：Principles（原则）/ Constraints（约束）/ Configurations（配置）
- 依赖关系图（2898 条依赖）
- 四级变异风险评估（Critical/High/Medium/Low）

**Constraint**: 高风险变异必须经过审查；依赖关系图必须实时更新。

**Evidence**: 04_PROTOCOLS/gene_network.py（完整实现）

**Can Rebuild**: ✅ 100 行可重建——扫描函数 + 依赖分析 + 风险评估

**Can Replace**: ✅ 风险评估标准可调整，框架不变

**Can Delete**: ⚠️ 删除会失去依赖追踪，但不影响核心链路运行（短期）

**Distillation**:

Gene Network 的核心洞察是"文明是一个活的有机体"。每个资产都是一个基因，它们之间的依赖关系形成一个网络。修改一个基因会影响整个网络，风险评估确保了高风险修改不会被随意执行。这体现了 Axiom-04（职责分离）——不同基因有不同的职责和风险等级，需要独立评估。
