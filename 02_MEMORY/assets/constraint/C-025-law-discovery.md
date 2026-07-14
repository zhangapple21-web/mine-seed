# C-025: Law Discovery Constraint

> Mission: AUM-MISSION-LAW-001
> Status: ACTIVE
> Created: 2026-07-15

## Constraint Statement

**Learning 不得直接修改 Recommendation Engine。Law 不得绕过治理链直接成为 Policy。**

## Principles

### P-025-01: Evidence First
任何规律必须来自 Evidence，不得人为指定规律。

**禁止：**
- 人工写死"规律因子"
- 丁元英评分
- 强势文化评分
- 情绪因子=20

### P-025-02: Pattern ≠ Law
Pattern 只是重复现象，Law 必须经过 Validation。

**阈值：**
- `MIN_EVIDENCE_FOR_PATTERN = 30`（形成 Pattern 的最小 Evidence 数量）
- `MIN_SAMPLE_FOR_VALIDATION = 50`（验证 Hypothesis 的最小样本量）
- `P_VALUE_THRESHOLD = 0.05`（统计显著性阈值）

### P-025-03: Law ≠ Policy
规律不是策略，一个 Law 可以生成多个 Policy。

**流程：**
```
Law → Roundtable → Policy Candidate → Admission → Approved Policy → Runtime
```

### P-025-04: Admission Is The Only Gate
任何 Policy 更新必须经过：
- Roundtable（评估）
- Admission（批准）
- Policy Update（执行）

**禁止：**
- Law 直接进入 Runtime
- 未验证规律进入 Policy

### P-025-05: Evidence Immutable
Evidence 不允许修改，只能追加。

**数据结构：**
- 存储：`02_MEMORY/evidence/evidence_YYYYMMDD.jsonl`
- 索引：`02_MEMORY/evidence/evidence_index.json`
- 格式：JSONL（append-only）

### P-025-06: Law Evolves
Law 可以：
- 新增（从 Evidence 发现）
- 强化（更多 Evidence 支持）
- 弱化（Evidence 反证）
- 废弃（长期无效）

**状态机：**
```
DRAFT → ACTIVE → WEAKENING → INVALID → ARCHIVED
         ↓
      REJECTED (Roundtable 拒绝)
```

## Architecture

```
Observation (市场新异动)
      │
      ▼
Evidence (高密度事实) — immutable, append-only
      │
      ▼
Pattern Mining (统计学模式) — MIN_EVIDENCE_FOR_PATTERN = 30
      │
      ▼
Hypothesis (规律假设) — Pattern → Hypothesis
      │
      ▼
Evidence Validation (严苛推演) — MIN_SAMPLE = 50, p < 0.05
      │
      ▼
Law (市场新规律) — Law Registry
      │
      ▼
Roundtable (红蓝对抗) — 评估收益/风险/副作用/覆盖范围
      │
      ▼
Policy Candidate (策略候选) — Policy Candidate Store
      │
      ▼
Admission (唯一准入) — 批准或拒绝
      │
      ▼
Approved Policy (全新交易边界) — 进入 Runtime
```

## Component Responsibilities

| Component | 职责 | 输出 |
|-----------|------|------|
| Observation | 收集事实，不做分析 | Observation |
| Evidence | 整理为不可变证据 | Evidence (immutable) |
| Pattern Mining | 发现重复模式 | Pattern |
| Hypothesis | 转化为规律假设 | Hypothesis |
| Evidence Validation | 统计检验验证 | Pass/Fail + Stats |
| Law Registry | 管理规律生命周期 | Law (DRAFT/ACTIVE/INVALID) |
| Roundtable | 红蓝对抗评估 | Policy Candidate |
| Admission | 唯一准入闸门 | Approved Policy |
| Policy Update | Runtime 加载策略 | Policy (versioned) |

## Code References

- **Law Discovery Protocol**: [law_discovery.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/law_discovery.py)
- **Evidence Store**: `02_MEMORY/evidence/`
- **Law Registry**: `02_MEMORY/law_registry/`
- **Policy Candidates**: `02_MEMORY/policy_candidates/`

## Never Rules

```
❌ 人工写死"规律因子"
❌ 丁元英评分
❌ 强势文化评分
❌ 情绪因子=20
❌ Miner 修改 Recommendation
❌ Law 直接进入 Runtime
❌ 未验证规律进入 Policy
❌ 修改历史 Evidence
```

## Audit Checklist

每次 Law Discovery 运行时，检查：

- [ ] Evidence 是否只追加不修改
- [ ] Pattern 是否满足最小 Evidence 数量
- [ ] Hypothesis 是否经过统计检验
- [ ] Law 是否进入 Registry 而非直接进入 Runtime
- [ ] Policy Candidate 是否经过 Roundtable
- [ ] Policy 是否经过 Admission 批准

## Distillation Target

本约束对应以下文明资产：

| 类型 | 资产 |
|------|------|
| Kernel | Law Discovery Kernel |
| Blueprint | Evidence → Pattern → Hypothesis → Law → Policy |
| Protocol | Law Discovery Protocol |
| Constraint | C-025 (本约束) |
| Experience | 哪类 Pattern 容易形成稳定 Law |

## Related Constraints

- C-003: Evidence First
- C-019: compress_audit_results() for recommendation decisions
- C-020: FA模式仅限内部推理层
- ARCH-011: Admission Engine for Tier 1/2 assets

---

*Last verified: 2026-07-15*