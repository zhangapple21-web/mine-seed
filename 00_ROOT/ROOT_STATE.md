# ROOT_STATE — 文明标识
> 种子库根状态文件
> 恢复时先验证：是不是同一个文明，而不是是不是同一个文件

| 字段 | 值 |
|------|-----|
| **Version** | R1-ROOT-164 |
| **Last Verified** | 2026-06-21 |
| **Repository** | mine-seed |

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

## 架构指纹

| 组件 | 角色 | 状态 |
|------|------|------|
| lab_01 | 生产环境 | ✅ 运行中 |
| lab_02 | 研究环境 | ✅ 运行中 |
| O→E→M→C→R | 演化链路 | ✅ 闭环 |
| 疯子（fengzi） | 生产域指挥官 | ✅ 在线 |
| 小疯子（xiaofengzi） | 研究域观察者 | ✅ 在线 |
| ntfy.sh | 跨机消息总线 | ✅ 在线 |
| GitHub Gist | 消息中继 | ✅ 在线 |
| One API (port 3000) | 算力调度 | ✅ 在线 |

## 种子库版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.1 | 2026-06-21 | 初始种子库结构，Phase 1-3 完成 || v0.2 | 2026-06-21 | 新增 07_GUARDIAN/ 守护层（Gravity/Conservation/Backtrack/Repair） |

## 守护层原则（07_GUARDIAN）

| 文件 | 周期 | 职责 | 原则数 |
|------|------|------|--------|
| gravity.md | 每日 | 保持生态活跃 | 5 |
| conservation.md | 每周 | 清理过期状态 | 5 |
| backtrack.md | 每月 | 快照备份 | 5 |
| repair.md | 按需 | 崩溃后确认还活着 | 5 |

> 2026-06-21 从 xiaoyao520921-ui/R1 Soul Guard 考古提取
