# Asset: Provider Watchdog

**Name**: Provider Watchdog（Provider 健康看门狗）

**Origin Repository**: ace_core

**Purpose**: 实时监控各 Provider 健康状态，故障时自动切换到备用，记录切换事件供审计。

**Problem It Solves**: Provider 随时可能宕机，硬编码会导致整个系统崩溃。需要一个独立的健康监控层，在 Provider 失效时自动降级。

**Core Structure**:
- ProviderHealth 状态类（status/latency/failures/successes）
- SwitchEvent 切换事件记录
- 五级状态机（HEALTHY→DEGRADED→UNHEALTHY→OFFLINE→RECOVERING）
- 自动切换 + 静默降级

**Constraint**: 看门狗自身故障不得影响主循环；失败静默降级，不抛异常。

**Evidence**: ace_core/core/miner_pool/provider_watchdog.py（完整实现）

**Can Rebuild**: ✅ 100 行可重建——状态类 + 健康检查函数 + 切换逻辑

**Can Replace**: ✅ Provider 换了不影响 Watchdog，只改配置

**Can Delete**: ❌ 删除会导致 Provider 故障无法自动恢复，核心链路会断

**Distillation**:

ProviderWatchdog 的本质是"能力层的保险"——当某个 Provider 失效时，系统不会崩溃，而是自动降级到备用。核心价值不在监控本身，而在"静默降级"原则：看门狗自己出事不能影响主循环。这是 R1 时代从多次 Provider 宕机中蒸馏出的经验。100 行就能重建的原因是它只做三件事：记状态、做检查、做切换，不做任何业务逻辑。
