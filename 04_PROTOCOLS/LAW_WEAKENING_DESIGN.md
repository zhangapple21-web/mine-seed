# Policy Lifecycle — 退出机制（板块A' Deliverable 4）

> 创建时间: 2026-07-15
> 更新时间: 2026-07-15
> 状态: **已替换为通用 Policy 生命周期（板块0 产出）**
> 关联: AUM-MISSION-ADVISOR-001, C-026

## 重要说明

本文件原为板块A'局部定义的 Law Weakening 退出机制。
**已被板块0产出的通用 Policy 生命周期替代**，不再独立维护。

通用定义见：**`00_ROOT/PRINCIPLES.md` → "Policy Lifecycle — 通用 Policy 生命周期"**

## 状态映射

| 本文件旧定义 | 通用生命周期 | LawStatus 枚举 |
|-------------|------------|---------------|
| DRAFT | Candidate | `DRAFT` |
| ACTIVE | Active | `ACTIVE` |
| — | Monitoring | `MONITORING` (新增) |
| — | Challenged | `CHALLENGED` (新增) |
| WEAKENING | Weakening | `WEAKENING` |
| INVALID | Deprecated | `INVALID` |
| ARCHIVED | Archived | `ARCHIVED` |

## 关键变更

1. **新增 Challenged 状态**: 贡献度下降但不确定时暂停判断（最长10天），避免直接跳 Weakening 误杀
2. **新增 Monitoring 状态**: 激活后进入监控期收集贡献度数据
3. **Roundtable 介入点明确**: Candidate→Active / Challenged→Weakening / Weakening→Deprecated 必须经过
4. **统一适用**: 不仅限于 Law/Signal Candidate，所有 Policy 均使用此生命周期

## 触发规则（保留，与通用生命周期兼容）

| 条件 ID | 名称 | 阈值 | 对应状态转换 |
|---------|------|------|-------------|
| W-001 | 连续贡献下降 | consecutive_decline_days = 20 | Monitoring → Challenged → Weakening |
| W-002 | 胜率跌破地板 | win_rate_floor < 0.40 | Monitoring → Challenged |
| W-003 | 负收益持续 | avg_return_5d < 0% | Challenged → Weakening |
| W-004 | 最大回撤超标 | max_drawdown > 阈值 | Challenged → Weakening |
| W-005 | E2C AVOID 触发 ≥ 5 次 | 来自 active_constraints.json | Monitoring → Challenged |

## E2C 与 Weakening 边界（保留）

| 机制 | 层级 | 行为 |
|------|------|------|
| E2C (e2c_closure) | **调度层** | 短期：失败 → 约束 → 降级/拒绝 |
| Weakening Monitor | **生命周期层** | 长期：贡献度持续下降 → 退场 |

两者唯一交集：W-005（E2C AVOID 触发 ≥ 5 次作为 Challenged 触发条件之一）
