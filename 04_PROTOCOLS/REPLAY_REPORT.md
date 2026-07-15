# Deliverable 3 — Offline Replay 报告

> 创建时间: 2026-07-15
> 回放窗口: 60 天（实际可用数据 5 天）
> 状态: **5 个 candidate 全部 INSUFFICIENT_DATA**

## 1. 回放结果总览

| Candidate | 状态 | 匹配样本 | 评估样本 | T+3 胜率 | T+3 收益 |
|-----------|------|----------|----------|----------|----------|
| capital_dominance | INSUFFICIENT_DATA | 0 | 0 | N/A | N/A |
| fund_type_quality | INSUFFICIENT_DATA | 0 | 0 | N/A | N/A |
| limit_up_timing | INSUFFICIENT_DATA | 0 | 0 | N/A | N/A |
| seal_quality | INSUFFICIENT_DATA | 0 | 0 | N/A | N/A |
| auction_premium | INSUFFICIENT_DATA | 0 | 0 | N/A | N/A |

## 2. 原因分析

**为什么全部 INSUFFICIENT_DATA？**

1. **样本时间不足**：仅 5 个交易日（07-10/11/13/14/15）的 trace.json，远低于 bootstrap 门槛的 30 样本
2. **匹配关键词缺失**：当前 layer1/layer2/layer3 reasons 中没有 5 个新 signal 的特征关键词（北向资金/涨停时机/封单/竞价等）
3. **数据源缺失**：5 个 signal 需要的数据源（北向资金/分时成交/集合竞价）尚未接入

## 3. 结论

### 3.1 Replay 阶段产出（按"先回放再说"原则）

- ✅ **Replay 框架已就绪**：`04_PROTOCOLS/replay.py` 可执行，可回放任意 candidate
- ✅ **判定逻辑已就绪**：通过/失败/样本不足三态明确
- ❌ **5 个 candidate 均未通过 Replay 验证**：不能进入 Shadow Evaluation

### 3.2 不能跳过 Replay 直接进 Shadow

按板块A' Forbidden：
> ❌ 跳过 Replay 直接进 Shadow → 5 天时间浪费

**当前 5 个 candidate 必须先解决以下问题才能重跑 Replay**：

1. 接入北向资金数据源（fund_type_quality 需要）
2. 接入分时成交数据（limit_up_timing / seal_quality 需要）
3. 接入集合竞价数据（auction_premium 需要）
4. 等历史数据积累到 30+ 样本

### 3.3 不阻断现有 6 因子的运行

Replay 失败**不影响**：
- 现有 stock_advisor.run() 继续按 6 因子运行
- 现有 AdaptiveScorer 调权逻辑（虽然样本不足，已建议暂停）
- 现有 E2C 闭环

## 4. 下游

- [ ] **Shadow Evaluation 框架就绪但暂不执行**（`04_PROTOCOLS/shadow.py`）
- [ ] 等 Replay 通过后再启动 Shadow
- [ ] 决定是先补数据源（4 个新数据源）还是等 2 个月数据自然积累
