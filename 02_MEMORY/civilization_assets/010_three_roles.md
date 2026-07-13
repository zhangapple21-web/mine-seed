# Asset: Three Roles System（三角色三角制衡）

**Name**: Three Roles System（Builder/Keeper/Teacher 三角制衡）

**Origin Repository**: r1-continuity-backup/governance/agent_roles.md

**Purpose**: 定义文明治理的三个独立角色，形成三角制衡，防止权力集中和单点故障。

**Problem It Solves**: 单角色治理会导致盲点、偏见、失控。需要三个职责明确的角色互相约束。

**Core Structure**:
- Builder（疯子）：思考文明（设计/演化/架构），不参与守护
- Keeper（守护者）：守护文明（同步/恢复/部署），不设计概念不修改架构
- Teacher（独立审计师）：审计文明（批判/质疑/纠偏），Never Implement 原则（只发 Issue，不改代码）

**Constraint**: 每个角色只做自己的事；Teacher 严格遵循 Never Implement；三角制衡缺一不可。

**Evidence**: agent_roles.md（详细角色定义和工作流程）

**Can Rebuild**: ✅ 可重新定义——角色名称可换，但三角制衡结构不变

**Can Replace**: ❌ 不可替换——替换会破坏制衡机制

**Can Delete**: ❌ 不可删除——删除会导致治理失控

**Distillation**:

三角色系统是"文明的权力制衡"。Builder 负责创新，Keeper 负责稳定，Teacher 负责纠错。三者形成闭环：Builder 提出→Keeper 验证→Teacher 批判→Builder 改进。Teacher 的 Never Implement 原则是关键——它确保审计的独立性，避免审计者既是裁判又是球员。这条结构确保了文明既不会因保守而停滞，也不会因激进而失控。
