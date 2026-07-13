# Asset: Nature Reserve（自然保护区）

**Name**: Nature Reserve（自然保护区）

**Origin Repository**: mine-seed

**Purpose**: 保护核心文明资产不被修改，建立 SHA256 基线，与自演化引擎集成。

**Problem It Solves**: 核心资产（公理、约束、协议）如果被随意修改，会导致文明身份漂移、规则混乱、系统崩溃。

**Core Structure**:
- 三层保护：Core Genes（核心基因）/ Core Constraints（核心约束）/ Core Protocols（核心协议）
- SHA256 基线检查
- 与自演化引擎集成，阻止违反保护区规则的修改

**Constraint**: 保护区内的资产只能通过 Admission 进入，不能直接修改。

**Evidence**: 04_PROTOCOLS/nature_reserve.py（完整实现）

**Can Rebuild**: ✅ 80 行可重建——文件列表 + SHA256 计算 + 基线检查 + 集成钩子

**Can Replace**: ✅ 保护范围可调整，机制不变

**Can Delete**: ❌ 删除会导致核心资产失去保护

**Distillation**:

Nature Reserve 的核心类比是"自然保护区"——核心基因、约束、协议就像濒危物种，需要特殊保护。SHA256 基线确保了资产的完整性，任何未经授权的修改都会被检测到。这体现了 L∞ 本源层的"自我校验"原则——系统必须能够验证自己的核心资产是否被篡改。
