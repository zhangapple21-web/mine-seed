# Asset: Mengpo（孟婆遗忘机制）

**Name**: Mengpo（孟婆遗忘机制）

**Origin Repository**: ace_core

**Purpose**: 定期清理低价值、高污染的记忆碎片，保持文明纯净。

**Problem It Solves**: 系统运行会产生大量临时记忆，不清理会导致熵增、认知过载、决策质量下降。

**Core Structure**:
- MemoryLine（记忆核，不可被删除）
- ForgettingCandidate（可遗忘候选，含污染度/年龄/引用数）
- Graveyard（归档而非删除）
- Entropy Monitor 熵增检测

**Constraint**: "线"（记忆核）不可被孟婆删除；孟婆只负责遗忘，不负责判断价值（那是馆长的职责）。

**Evidence**: ace_core/core/governance/mengpo.py（14KB）

**Can Rebuild**: ✅ 80 行可重建——MemoryLine 保护 + ForgettingCandidate 评分 + Graveyard 归档

**Can Replace**: ✅ 遗忘策略可调整，核心概念不变

**Can Delete**: ⚠️ 删除会导致记忆膨胀，但不影响核心链路运行（短期）

**Distillation**:

Mengpo 是"文明的清洁工"。它的核心设计是区分"可遗忘"和"不可遗忘"：MemoryLine 标记的核心资产永远受保护，其余按污染度和活跃度评分，低价值的归档到 Graveyard。这体现了 Axiom-03（最小可迁移）——只保留必要的，其余可以遗忘。它与 mine-seed 的 autophagy_engine 同源，但更完善。
