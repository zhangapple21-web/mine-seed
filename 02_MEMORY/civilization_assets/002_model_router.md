# Asset: Model Router

**Name**: Model Router（模型路由器）

**Origin Repository**: ace_core

**Purpose**: 根据任务类型和策略，选择最合适的模型/Provider。

**Problem It Solves**: 不同任务需要不同模型（复杂推理要贵的，简单问答要快的），硬编码模型选择会导致成本失控或质量下降。

**Core Structure**:
- ModelSpec 模型规格（provider/model/tier）
- 四种路由策略（quality_first/cost_effective/latency_first/diverse）
- TaskProfile 任务画像
- 健康状态跟踪 + 自动降级

**Constraint**: 不负责实际调用模型（MinerPool 处理）；不维护模型健康状态（ProviderWatchdog 处理）。

**Evidence**: ace_core/core/miner_pool/model_router.py（完整实现）

**Can Rebuild**: ✅ 80 行可重建——策略枚举 + 任务画像映射 + 优先队列

**Can Replace**: ✅ Provider 增减不影响路由逻辑，只改配置

**Can Delete**: ❌ 删除会导致所有任务使用默认模型，无法优化成本/延迟

**Distillation**:

ModelRouter 的核心洞察是"路由不是找最好的，是找最适合的"。四种策略覆盖了生产场景的所有需求：质量优先用于复杂决策，成本优先用于批量处理，延迟优先用于实时交互，多样性优先用于多模型辩论。它体现了 CSP 三级架构的 Service→Provider 路由原则——Runtime 只关心要什么能力（推理），不关心用哪个 Provider（GPT-4 还是 Claude）。
