# Asset: CSP Registry（三级能力架构）

**Name**: CSP Registry（Capability → Service → Provider 三级架构）

**Origin Repository**: r1-continuity-backup + mine-seed

**Purpose**: 定义稳定的能力抽象层，解耦 Runtime 与 Provider 实现。

**Problem It Solves**: Provider 每天都在变（GPT-4→Claude→本地模型），如果 Runtime 直接绑 Provider，每次换 Provider 都要改代码。

**Core Structure**:
- Capability 层（8 个永久定义：Reason/Retrieve/Generate/Transform/Observe/Execute/Persist/Notify）
- Service 层（具体服务：LLM.Chat/Image.Generate/Vector.Retrieve）
- Provider 层（实现者：OpenAI/Claude/Ollama）
- Routing Rules（按条件路由到 Provider）

**Constraint**: Capability 层十年不变；Provider 替换不修改 Runtime 代码。

**Evidence**: 04_PROTOCOLS/csp_registry.py（mine-seed 实现）

**Can Rebuild**: ✅ 150 行可重建——三个数据类 + 路由函数 + Registry 持久化

**Can Replace**: ✅ Provider 随便换，Capability/Service 不动

**Can Delete**: ❌ 删除会导致 Runtime 直接绑 Provider，失去抽象层

**Distillation**:

CSP 三级架构的核心类比是"电源插座标准"：Capability 是"需要电"（永远不变），Service 是"220V 交流"（接口标准不变），Provider 是"国家电网/发电机/太阳能"（可以换）。这条原则确保了 Runtime 的稳定性——无论 Provider 怎么变，调用代码不变。它是 R1 时代从多次 Provider 切换中蒸馏出的架构智慧。
