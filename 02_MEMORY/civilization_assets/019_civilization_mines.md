# Asset: Civilization Mine System（文明矿山体系）

**Name**: Civilization Mine System（文明矿山体系）

**Origin Repository**: mine-seed（自我总结）

**Purpose**: 将外部 Repository 定义为"矿山"而非"运行时依赖"，建立 矿山 → 资产库 → Runtime 三层架构，确保 Runtime 只依赖蒸馏后的文明资产。

**Problem It Solves**: 如果 Runtime 直接依赖外部仓库代码，会导致：1）仓库更新影响 Runtime 稳定性；2）代码重复、维护成本高；3）文明资产分散在十几个仓里找不到；4）丢了一个仓库就丢了一切。

**Core Structure**:
- Mine Layer（矿山层）：10 个仓库，只读，原材料
- Asset Layer（资产层）：Civilization Asset Library，蒸馏后，可复用
- Runtime Layer（运行层）：实际运行代码，只依赖资产层
- 开采规范：DFP-001 适配版（扫描→考古→对比→蒸馏→准入→资产库）
- 矿山分类：富矿/深矿/贫矿/废矿

**Constraint**: Runtime 不得直接 import 矿山代码；矿山只读，不得修改；资产必须经过蒸馏和准入才能入库。

**Evidence**: civilization_mines.md + civilization_map.md v2 + 18 个已蒸馏资产

**Can Rebuild**: ✅ 200 行可重建——矿山索引 + 三层架构定义 + 开采规范

**Can Replace**: ✅ 矿山来源可换（GitHub→本地→其他），架构不变

**Can Delete**: ❌ 删除会导致 Runtime 直接依赖矿山，失去架构边界

**Distillation**:

文明矿山体系的核心洞察是"别人的代码永远是别人的，蒸馏了才是自己的"。三层架构划出了清晰的边界：矿山是原材料来源（可以丢、可以换），资产库是文明的结晶（真正的小世界），Runtime 是运行的载体（只认识资产库）。这条边界确保了：1）文明不依赖任何具体仓库；2）资产可复用、可迁移、可重建；3）知识膨胀可控（有蒸馏过程过滤）。它体现了 P-006（沉淀是价值跃迁）——从 117K LOC 的矿石，到 18 个文明资产的钢材，价值密度提升了几个数量级。
