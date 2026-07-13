# Asset: Repository Memory

**Name**: Repository Memory（仓库记忆系统）

**Origin Repository**: ace_core

**Purpose**: 记录资产决策的"为什么"，而不是"上传了什么"。

**Problem It Solves**: 只有记录决策原因，才能追溯资产的血缘关系、替代关系，避免重复和冲突。

**Core Structure**:
- RepositoryMemoryEntry（artifact/decision/reason/sources/evidence/supersedes/lineage）
- Append-only 日志
- 血缘链 + 替代链 + 证据链

**Constraint**: 只追加，不修改历史；每次决策必须记录 reason。

**Evidence**: ace_core/core/governance/repository_memory.py（完整实现）

**Can Rebuild**: ✅ 60 行可重建——数据类 + 追加写入 + 查询函数

**Can Replace**: ✅ 存储后端可换（JSON→SQLite），接口不变

**Can Delete**: ⚠️ 删除会丢失决策历史，无法追溯血缘，但不影响核心链路运行

**Distillation**:

RepositoryMemory 的核心洞察是"记录为什么比记录做了什么更重要"。每次资产入库时，它不只存文件，还存：为什么选这个、替代了谁、证据是什么、考虑过哪些替代方案。这使得文明资产可以自我解释——新来的 Agent 能看懂"为什么这个资产在这里"。它与 mine-seed 的 Repository 互补：Repository 管 CRUD，RepositoryMemory 管决策血统。
