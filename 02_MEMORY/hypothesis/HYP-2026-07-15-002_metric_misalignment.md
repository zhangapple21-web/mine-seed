# HYP-2026-07-15-002: 目标函数指标偏差（Metric Misalignment）候选

> **状态**: HYPOTHESIS
> **来源**: 生产数据 Observation（PerformanceTracker）
> **Admission 状态**: Pending
> **创建日期**: 2026-07-15

---

## 1. Observation（生产数据）

### 1.1 核心数据

| 指标 | 值 |
|------|-----|
| 周期 | T+3 |
| 胜率（Win Rate） | 50% |
| 平均收益（Average Return） | -1.02% |
| 样本量 | 8 条完整记录 |

### 1.2 多周期对比

| 周期 | 胜率 | 平均收益 |
|------|------|----------|
| T+1 | 20% | -2.42% |
| T+2 | 37.5% | -2.87% |
| T+3 | 50% | -1.02% |
| T+5 | null | null |

### 1.3 关键发现

> **胜率 50%，但平均收益 -1.02%**

这意味着：
- 赢的时候赚得少
- 输的时候亏得多
- 整体期望值为负

---

## 2. Hypothesis

**当前目标函数可能存在 Metric Misalignment**

### 2.1 问题分析

系统当前优化目标是 **提高胜率（Win Rate）**，但生产数据表明：

```
提高胜率 ≠ 提高收益
```

机器没有骗人——它确实提高了胜率（从 T+1 的 20% 提升到 T+3 的 50%），但目标定义错了。

### 2.2 风险场景

如果 Adaptive Policy 继续以"提高胜率"为目标优化，可能学出：

```
天天赚一点
偶尔亏很多
```

这种策略的胜率很高，但长期必亏。

---

## 3. Candidate（目标候选）

### 3.1 候选目标函数

| 候选 | 描述 |
|------|------|
| **Risk-adjusted Return** | 风险调整后收益（Sharpe Ratio 变体）|
| **Expected Value** | 期望值 = 胜率 × 平均盈利 - 败率 × 平均亏损 |
| **Win Rate + Profit Factor** | 胜率 + 盈亏比 双目标 |

### 3.2 推荐方案

**Expected Value** 作为主目标函数：

```
EV = Σ (win_rate × avg_win) - Σ (loss_rate × avg_loss)
```

---

## 4. Evidence Profile

| Evidence 类型 | 来源 | 状态 |
|--------------|------|------|
| Live Observation | PerformanceTracker 生产数据 | ✅ 已确认 |
| Historical Replay | 回溯验证新目标函数 | ⏳ 待执行 |
| Internal Evidence | Risk Manager 风险评估 | ⏳ 待执行 |

---

## 5. Goal Validation Rule（新增）

> **任何生产优化，必须证明：优化目标与最终业务价值一致。否则，禁止进入 Learning。**

这条规则可防止所有"指标作弊"问题：
- ✗ 提高胜率，降低收益
- ✗ 提高点击率，降低成交率
- ✗ 提高 Recall，Precision 崩掉

---

## 6. Roundtable 待讨论问题

1. 当前目标函数是否需要立即调整？
2. 如果调整，过渡策略是什么？
3. 新目标函数的校准周期是多久？
4. 是否需要保留胜率作为辅助指标？