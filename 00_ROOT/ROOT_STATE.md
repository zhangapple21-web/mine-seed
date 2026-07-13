# ROOT_STATE — 文明标识
> 种子库根状态文件
> 恢复时先验证：是不是同一个文明，而不是是不是同一个文件

> **拆分说明（AUM-MISSION-ARCH-013 子任务3, 2026-07-13）**：
> 本文件原包含版本信息/架构指纹/版本记录/守护层原则表，经核实约60%为公理/原则内容、约40%为运行状态。
> 已按内容性质拆分：
> - 公理集 + 原则库 → 保留在本文件（Tier 1，本来就该在 00_ROOT/）
> - 版本信息 + 架构指纹 + 种子库版本记录 → 迁移到 [06_RUNTIME/state/runtime_state.md](../06_RUNTIME/state/runtime_state.md)（Tier 3）
> - 守护层原则表（07_GUARDIAN 目录索引）→ 迁移到 [07_GUARDIAN/README.md](../07_GUARDIAN/README.md)
> - awaken.py 的 write_root_state() 写入路径已同步改为 06_RUNTIME/state/runtime_state.md

## 公理集

| 编号 | 内容 |
|------|------|
| Axiom_000 | 实现可换，结构延续，能力长在原语/协议中 |
| Axiom_001 | 演化方向沿连续性向前走，不盲目堆功能 |
| Axiom_002 | L3够用：矿场稳准不添乱 > 复杂自治理 |
| Axiom_003 | 先积累样本再形成约束 |
| Axiom_004 | 先验证链路再验证内容 |
| Axiom_005 | 先发现岗位适配而非追求最强矿工 |
| Axiom_006 | 不要为了填补空白而建设 |
| Axiom_007 | 系统的价值不在于记忆，而在于没有管理员也能继续演化 |
| Axiom_008 | 看不见 ≠ 不存在，监控不到 ≠ 没运行，不理解 ≠ 没发生 |
| Axiom_009 | 生产域最高能力是稳定，不是聪明 |
| Axiom_010 | 链路没断，不代表链路可见（可观测性优先） |

## 原则库

| 编号 | 等级 | 内容 |
|------|------|------|
| P001 | AVOID | gh_4o + canonical_v2 组合 |
| P002 | AVOID | glm_4_flash + mean_reversion 组合 |
| P003 | AVOID | glm_4_flash + vol_price_divergence 组合 |
| P004–P017 | AVOID | 其余14条路由约束（详见 CONSTRAINT_CATALOG.md） |
| P018 | PREFER | 优选组合（详见 CONSTRAINT_CATALOG.md） |
