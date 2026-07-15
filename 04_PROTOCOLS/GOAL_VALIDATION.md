# Goal Validation Report — 荐股系统优化目标

> 创建时间: 2026-07-15
> Mission: AUM-MISSION-ADVISOR-001 第二阶段
> 状态: **DRAFT-Pending-Review**（待用户确认权重分配和目标定义后转正）

---

## 0. Goal Validation Rule（核心原则）

> **任何生产优化，必须证明：优化目标与最终业务价值一致。否则，禁止进入 Learning。**

这条规则可防止所有"指标作弊"问题：
- ✗ 提高胜率，降低收益
- ✗ 提高点击率，降低成交率
- ✗ 提高 Recall，Precision 崩掉

**Observation 支撑**: T+3 胜率 50% 但平均收益 -1.02%（见 HYP-2026-07-15-002）

**实施位置**: AdaptiveScorer 进入 Learning 前的前置检查点

---

## 1. 优化目标四选一

根据现有数据状态和宿主(个人投资者)特征，选择 **D. 追求稳定 3-5 日收益** 作为主目标，**B. 追求胜率** 作为次要目标。

| 候选 | 适配性 | 原因 |
|------|-------|------|
| A. 最高收益 | ❌ 不选 | 推荐给客户最高收益容易引导追高/题材股，与"中短线稳健"不符 |
| B. 最高胜率 | ✅ 次目标 | 胜率是稳健性最直接表征，配合止损/止盈使用 |
| C. 最佳 Risk-Reward | ❌ 暂不选 | 当前样本不足，RR 计算依赖更完整的最大回撤/持仓数据 |
| **D. 稳定 3-5 日收益** | ✅ **主目标** | 与 T+2/T+3 判定周期契合，与中短线持仓周期匹配 |

**组合定义**：

- **Primary Goal**: 最大化 T+3 周期内的**期望收益**（average return），同时控制 T+3 胜率 ≥ 40%
- **Secondary Goal**: 提升 T+5 周期的**胜率**（≥ 50% 视为健康）
- **Constraint**: 单只最大回撤 < 15%，单日健康度不熔断

## 2. Evaluation Metrics 集合

| 指标 | 公式 | 权重 | 来源 |
|------|------|------|------|
| **Win Rate T+3** | T+3 收益>0 / 总样本 | 30% | PerformanceTracker |
| **Average Return T+3** | Σreturn_t3 / n | 30% | PerformanceTracker |
| **Max Drawdown T+5** | min(period_low) / recommend_price - 1 | 15% | PerformanceTracker |
| **Sharpe T+5** | (avg_t5 - rf) / std_t5 | 10% | PerformanceTracker |
| **Holding Days** | 实际持仓中位数 | 5% | PerformanceTracker |
| **Publication Score** | 健康度 * gate_pass | 10% | AdaptiveScorer |

> **重要**：所有 Signal Candidate 必须能用上述指标评估，否则不能进入 Shadow Evaluation。
> 任何因子有效性判断必须先匹配到上述指标中的至少一项，否则该因子无意义。

## 3. Capability Mapping（关键）

> **目的**：明确 AdaptiveScorer / e2c_closure / LawRegistry 边界，**避免双重学习**。

| 模块 | 层级 | 职责 | 输入 | 输出 | 副作用 |
|------|------|------|------|------|--------|
| **AdaptiveScorer** | 评分层 | 根据历史胜率调整 layer1-3 因子权重 | PerformanceTracker.get_factor_effectiveness | adjusted_weights | 修改 adaptive_weights.json |
| **e2c_closure** | 调度层 | 失败模式生成 FORBID/AVOID/PREFER 约束 | observation_log.json | active_constraints.json | 拒绝/降级/提升 task_dispatch |
| **LawRegistry** | 治理层 | 注册/激活/弱化 Law Candidate | Pattern→Hypothesis→Law | laws.json / law_candidates.json | 仅在 Admission 通过后改 Policy |
| **PolicyManager** | 治理层 | 候选策略 → Roundtable → Admission | adjusted_weights + audit_evidence | active_policy | 修改 policy.json |

### 3.1 边界规则（重要）

1. **AdaptiveScorer 只调权，不调调度**：降权一个因子 ≠ 禁止使用该因子
2. **E2C 触发 AVOID 时，AdaptiveScorer 应跳过该 target**：避免双重学习
3. **LawCandidate 不直接进 AdaptiveScorer**：必须经过 Replay + Shadow + Roundtable + Admission 全链
4. **Shadow Evaluation 期间 AdaptiveScorer 不动**：观察真实表现，不混入已有调整

### 3.2 禁止事项

- ❌ 跳过 Goal Validation 直接加因子
- ❌ 新信号未经 Replay+Shadow 直接进 AdaptiveScorer
- ❌ AdaptiveScorer 与 E2C 对同一 signal 重复调权
- ❌ Law Candidate 直接改 Runtime

## 4. Acceptance Criteria

- [x] 优化目标明确定义（Primary: 稳定 T+3 收益；Secondary: T+5 胜率）
- [x] 评估指标集合定义（6 项 + 权重）
- [x] Capability Mapping 明确四层边界
- [x] 禁止事项明确

**待确认项**：
- [ ] 用户确认权重分配（WinRate 30% + AvgReturn 30% + MaxDrawdown 15% + Sharpe 10% + PublicationScore 10%）
- [ ] 用户确认目标定义（Primary: T+3 期望收益最大化，T+3 胜率 ≥ 40%；Secondary: T+5 胜率 ≥ 50%）

**当前状态**：本报告为 **DRAFT-Pending-Review**，待用户确认后锁定为定稿，下游 Deliverable 1-4 方可启动。
**关键提醒**：当前 T+3 胜率已达标（50%），但 T+3 平均收益为负（-1.02%），按本报告定义的 Primary Goal（收益最大化），系统目前不达标。
