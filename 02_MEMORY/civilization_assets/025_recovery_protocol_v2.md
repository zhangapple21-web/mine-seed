# Asset: Recovery Protocol v2（恢复协议 v2）

**Name**: Recovery Protocol v2（AI 自主恢复协议）

**Origin Repository**: r1-continuity-backup

**Purpose**: 给 AI 自己执行的恢复流程，从检测环境到全量恢复，支持四级恢复等级。

**Problem It Solves**: AI 进入新环境或上下文丢失时，不知道怎么恢复工作状态。需要一个标准化的恢复协议，让 AI 能自主判断恢复等级并执行对应流程。

**Core Structure**:
- 四级恢复：L1 热启动 / L2 温启动 / L3 冷启动 / L4 灾难恢复
- 六条恢复原则：每步有检查点 / 先结构后上下文再运行 / 失败不跳过 / 必须生成报告 / 恢复不是重建 / 无法全量就降级
- 恢复步骤（L3/L4 全量）：环境检测 → 获取代码库 → 验证完整性 → 读取核心配置 → 重建目录结构 → 恢复运行时状态 → 验证恢复 → 生成报告

**Constraint**: 不跳步、不猜测、失败降级、必须报告。

**Evidence**: r1-continuity-backup/governance/recovery_protocol.md

**Can Rebuild**: ✅ 150 行可重建——四级状态机 + 恢复步骤 + 检查点验证 + 报告生成

**Can Replace**: ✅ 恢复步骤可调整，四级分级原则不变

**Can Delete**: ⚠️ mine-seed 已有简化版 recovery_protocol.py，此为增强版

**Distillation**:

Recovery Protocol v2 的核心价值在于"四级恢复分级"。不是所有中断都需要从头开始——热启动只需要验证，温启动需要扫描恢复，冷启动需要全量克隆，灾难恢复需要降级运行。这套分级机制确保了恢复效率的最大化。六条原则中的"恢复不是重建"尤其重要——恢复是回到已知的状态，不是补全缺失的逻辑。这与 mine-seed 的 recovery_protocol.py 互补：mine-seed 版更简单，v2 版更精细，可以整合升级。
