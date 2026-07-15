# Deliverable 1 — 现有因子诊断报告

> 创建时间: 2026-07-15
> 数据范围: 最近 7 天（2026-07-10 ~ 2026-07-15）
> 样本数: 12 条推荐
> 评估目标: Goal D（稳定 3-5 日收益） + Goal B（胜率）

## 1. 因子诊断结果

通过 `PerformanceTracker.get_factor_effectiveness()` 复用的诊断结果：

| 因子 | 样本数 | 胜率 | 平均收益 | Goal D 匹配 | 处置 |
|------|--------|------|----------|------------|------|
| price_range | 12 | 33% | -2.1% | ❌ 偏离 | 待 Replay 验证 |
| change_moderate | 12 | 50% | -0.5% | ⚠ 中性 | 保留 |
| change_small | 8 | 25% | -3.2% | ❌ 不达标 | 待 Replay |
| turnover_healthy | 12 | 50% | -1.0% | ⚠ 中性 | 保留 |
| cap_mid_large | 12 | 50% | -0.8% | ⚠ 中性 | 保留 |
| pe_reasonable | 10 | 40% | -1.5% | ⚠ 临界 | 保留但降权 |
| liquidity_ok | 12 | 50% | -1.0% | ⚠ 中性 | 保留 |

## 2. 与 Goal D 匹配度评估

**Primary Goal D（稳定 T+3 收益）** 当前表现：
- T+3 胜率 50%（达标 ≥ 40%）
- T+3 平均收益 -1.02%（**未达标**）
- T+3 周期内最大亏损 4.76%（金山办公）

**问题**：
1. **T+1 表现糟糕**（胜率 20%，收益 -2.42%）—— 印证用户判断"不能因单日亏损定好坏"
2. **T+3 仍负收益** —— 现有 6 个因子在 T+3 周期内**整体打不出正收益**
3. **样本严重不足** —— 12 条样本 < MIN_EVIDENCE_FOR_PATTERN(30) —— 任何"调整"都属过度拟合

## 3. 结论

### 3.1 现有因子不能直接证明有效

- ❌ **不能基于 12 样本调权**：触发 `AdaptiveScorer.analyze_and_adjust` 的 T+1/T+5 通路，但样本不足会导致 `factor_perf` 噪声大
- ❌ **不能基于此添加新因子**：必须先经 Replay 证明现有因子的统计价值

### 3.2 需要做的

1. **停止 AdaptiveScorer 调权**，直到样本达到 30+ 再开启
2. **启动 Replay 2 个月数据**，补全证据
3. **新增 5 个 Signal Candidate 走 Replay+Shadow 完整链路**

### 3.3 现有因子 vs Signal Candidate 边界

| 类别 | 来源 | 行为 | 是否进 AdaptiveScorer |
|------|------|------|---------------------|
| 现有 6 因子 | 静态权重 | 由 Goal D 反推 | ❌ **暂不调权**（样本不足）|
| 5 个 Signal Candidate | 新引入 | 必须 Replay+Shadow+Admission | ❌ **必须走完链路** |

## 4. 下游动作

- [ ] 启动 Replay 阶段（Deliverable 3）—— 2 个月历史数据回放
- [ ] 注册 5 个 Signal Candidate 到 LawRegistry（Deliverable 2）
- [ ] Law Weakening 触发规则（Deliverable 4）
