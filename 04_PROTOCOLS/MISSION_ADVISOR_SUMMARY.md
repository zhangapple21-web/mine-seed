# AUM-MISSION-ADVISOR-001 — 板块A' 产出汇总

> 创建时间: 2026-07-15
> 状态: **P0 全部完成，P1 完成**
> Mission 范围: 板块A' Signal Candidate 全链路 + 板块四' Capability Mapping

## 1. Deliverable 产出

| # | 名称 | 文件 | 状态 |
|---|------|------|------|
| 0 | Goal Validation Report | [GOAL_VALIDATION.md](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/GOAL_VALIDATION.md) | ✅ 完成 |
| 1 | 现有因子诊断 | [FACTOR_DIAGNOSIS.md](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/FACTOR_DIAGNOSIS.md) | ✅ 完成 |
| 2 | Signal Candidate Registry | [register_signal_candidates.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/register_signal_candidates.py) | ✅ 完成 (5个) |
| 3a | Offline Replay | [replay.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/replay.py) | ✅ 完成 |
| 3b | Replay 报告 | [REPLAY_REPORT.md](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/REPLAY_REPORT.md) | ✅ 完成 |
| 3c | Shadow Evaluation | [shadow.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/shadow.py) | ✅ 完成 |
| 4 | Law Weakening 设计 | [LAW_WEAKENING_DESIGN.md](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/LAW_WEAKENING_DESIGN.md) | ✅ 完成 |
| 板块四' | E→C 边界验证 | [E2C_BOUNDARY_VERIFICATION.md](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/E2C_BOUNDARY_VERIFICATION.md) | ✅ 完成 |
| - | 单元测试 | [test_signal_candidate_pipeline.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/test_signal_candidate_pipeline.py) | ✅ 10/10 |

## 2. 关键设计决策

### 2.1 复用 vs 重建（DFP-001）

| 决策 | 内容 |
|------|------|
| ✅ 复用 | `LawRegistry`（law_discovery.py）作为 Signal Candidate Registry |
| ✅ 复用 | `PerformanceTracker.get_factor_effectiveness` 作为因子诊断 |
| ✅ 复用 | `e2c_closure.py` 作为 E→C 框架 |
| ❌ 不重建 | 信号候选注册机制、状态机、Replay/Shadow 评估、冷却机制 |

### 2.2 边界划分

```
AdaptiveScorer (评分层)  e2c_closure (调度层)  LawRegistry (治理层)
        ↓                       ↓                    ↓
   调权因子权重            FORBID/AVOID/PREFER     注册/激活/弱化 Law
        ↓                       ↓                    ↓
   写入 adaptive_         写入 active_           写入 law_candidates/
   weights.json           constraints.json       laws.json
```

**互不引用（grep 验证通过）**：
- AdaptiveScorer ❌ e2c_closure
- e2c_closure ❌ AdaptiveScorer

### 2.3 Forbidden 遵守

| 禁止项 | 状态 |
|--------|------|
| 跳过 Goal Validation 直接诊断因子 | ❌ 已避免（先出 GOAL_VALIDATION.md） |
| 新信号未经 Replay+Shadow 直接进 AdaptiveScorer | ❌ 已避免（5个candidate全部 DRAFT，Replay 未过） |
| AdaptiveScorer 与 E2C 对同一 signal 重复调权 | ❌ 已避免（Capability Mapping 明确边界） |
| Law Candidate 直接改 Runtime | ❌ 已避免（必须经 Admission 闸门） |

## 3. Replay 真实结果

5 个 Signal Candidate **全部 INSUFFICIENT_DATA**：
- 当前数据样本仅 5 天（07-10/11/13/14/15）
- 远低于 bootstrap 门槛 30 样本
- Shadow 阶段因此**全部被正确拒绝**

**这正是 Replay 阶段的价值**：用数据说话，不让任何 signal 蒙混过关。

## 4. 单元测试

```
通过: 10/10
✓ Signal Candidate 注册正确
✓ Replay 独立运行
✓ Shadow 拒绝未通过 Replay
✓ Replay 和 Shadow 独立流程/独立目录
✓ 状态机完整
✓ E2C 与 AdaptiveScorer 边界清晰
✓ Signal Candidate 不直接修改 AdaptiveScorer
✓ Law Weakening 设计文档完整
✓ Goal Validation Report 完整
✓ 现有因子诊断报告完整
```

## 5. 待启动（P2，板块五 Law Registry MVP）

按板块五要求补充：
- Law / Status / Evidence Count / Confidence / Version / Scope 字段
- LawRegistry 现有实现已包含上述字段
- 仅需补充：版本演进机制、scope 粒度细化

## 6. 收尾事项

- [x] P0 全部完成
- [x] P1 Capability Mapping 完成
- [x] 单元测试 10/10 通过
- [ ] 板块一/二/三：维持昨日规格不变
- [ ] 板块五 MVP：P2 启动
