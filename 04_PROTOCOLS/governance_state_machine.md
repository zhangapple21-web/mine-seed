# Governance State Machine Protocol

> 创建时间: 2026-07-15
> 状态: **DEPRECATED** — 方向已转向 Event-Sourced Governance Kernel，本方案保留作为历史记录
> 替代方向: Event-Sourced Governance Kernel（最小 Dry Run 进行中）
> 对应原则: C-029 (CANDIDATE)

> ⚠️ **DEPRECATED NOTICE**: 本方案作为早期探索保留，不作为正式规范。治理模型已转向基于事件溯源的方向，强调 Append-Only History、Projection Independence 和 Semantic Preservation。详见 PRINCIPLES.md 中 C-029 ~ C-033。

## 0. Core Principle

> Workflow produces evidence; evidence informs decisions;
> authorized decisions change object state;
> migrations change representation without changing meaning.

## 1. Layer Separation

三个层次严格分离，不得混用：

| 层次 | 说明 | 示例 |
|------|------|------|
| Workflow Activity | 流程动作 | SUBMIT, BEGIN_REVIEW, DECIDE, RESUBMIT |
| Decision | 治理裁定 | ADMIT, REJECT, REQUEST_REVISION |
| Object State | 规范状态 | CANDIDATE, ADMITTED, REJECTED |

### 约束

1. Workflow Activity 可以产生 Evidence，但不能直接改变 Object State
2. Evidence Record 支持 Decision，但本身不具有授权效力
3. 只有获得授权的 Decision 才能触发规范性状态迁移
4. Workflow 的完成本身不产生 ADMITTED
5. Decision Record 的存在不一定意味着决定有效，还需验证决策者、权限、时间和作用域

## 2. Governance Artifact Taxonomy

```
Governance Artifact
    ├── Evidence Record
    │   ├── Admission Record
    │   ├── Replay Record
    │   ├── Audit Record
    │   └── Roundtable Record
    │
    ├── Decision Record
    │   ├── Governor Decision Record
    │   ├── ADR
    │   └── Resolution
    │
    └── Derived Artifact
        ├── Current View
        ├── Index
        └── Projection
```

### 定义

| 类型 | 定义 | 可变性 |
|------|------|--------|
| Evidence Record | 记录治理过程和证据 | 封存后不可变，修正需追加 Amendment |
| Decision Record | 记录具有治理效力的裁定 | 封存后不可变，新决定通过 Superseding Decision |
| Derived Artifact | 由原始记录和派生规则计算出的投影 | 可重建，不是唯一事实来源 |

## 3. Object State Machine

### 状态枚举

| 状态 | 含义 |
|------|------|
| DRAFT | 起草中，未提交 |
| CANDIDATE | 已提交为候选，等待审查 |
| UNDER_REVIEW | 审查中，Governor Decision 待出 |
| ADMITTED | 已通过，具有完整规范效力 |
| REJECTED | 已拒绝，不进入规范体系 |
| REVISION_REQUIRED | 需要修订，退回 Candidate |
| PROVISIONAL | 临时生效，有限期限/作用域 |
| DEPRECATED | 已弃用，保留历史 |

### PROVISIONAL 状态定义

> PROVISIONAL 是由授权 Governor 通过 ADMIT_PROVISIONALLY 明确授予的、具有有限期限或有限作用域的规范性生效状态。

**必须包含字段**：

```yaml
DecisionOutcome: ADMIT_PROVISIONALLY
EffectiveFrom: 2026-07-15
EffectiveUntil: 2026-08-14
Scope: repository-governance
ReviewRequired: true
ExpiryTransition: UNDER_REVIEW
```

**规则**：

- PROVISIONAL 不是"尚未决定"，它已经产生有限的规范效力
- 必须有明确的授权者、作用域和生效时间
- 必须有截止时间或终止条件
- 到期后的迁移必须预先定义
- 延长临时效力需要新的 Decision Record
- 原决定到期后不得通过修改日期静默续期
- ExpiryTransition 预先授权到期迁移，系统到期自动进入 UNDER_REVIEW 不需要伪造新的 Governor Decision

## 4. Decision Model

### Decision Status

| 状态 | 含义 |
|------|------|
| PENDING | 尚无决定 |
| RECORDED | 决定已记录 |
| SUPERSEDED | 已被新决定取代 |
| VOIDED | 已作废 |

### Decision Outcome

| 结果 | 含义 |
|------|------|
| ADMIT | 通过，进入 ADMITTED |
| ADMIT_PROVISIONALLY | 临时通过，进入 PROVISIONAL |
| REJECT | 拒绝，进入 REJECTED |
| REQUEST_REVISION | 要求修订，进入 REVISION_REQUIRED |

### Decision Record 格式

```yaml
Decision:
    Status: PENDING | RECORDED | SUPERSEDED | VOIDED
    Outcome: null | ADMIT | ADMIT_PROVISIONALLY | REJECT | REQUEST_REVISION
    DecisionMaker: <authority>
    DecidedAt: <timestamp>
    EffectiveFrom: <timestamp>
    Scope: <scope>
    Reason: <reasoning>
    Evidence:
        - <evidence references>
    Alternatives:
        - <alternatives considered>
```

## 5. Workflow Activity & Legal Transitions

完整的合法迁移表：

| 当前 Object State | Workflow Activity | Decision Outcome | 下一 Object State |
|-------------------|-------------------|------------------|-------------------|
| DRAFT | SUBMIT | — | CANDIDATE |
| CANDIDATE | BEGIN_REVIEW | — | UNDER_REVIEW |
| UNDER_REVIEW | DECIDE | ADMIT | ADMITTED |
| UNDER_REVIEW | DECIDE | REJECT | REJECTED |
| UNDER_REVIEW | DECIDE | REQUEST_REVISION | REVISION_REQUIRED |
| UNDER_REVIEW | DECIDE | ADMIT_PROVISIONALLY | PROVISIONAL |
| REVISION_REQUIRED | RESUBMIT | — | CANDIDATE |
| PROVISIONAL | REVIEW | ADMIT | ADMITTED |
| PROVISIONAL | REVIEW | REJECT | REJECTED |
| PROVISIONAL | REVIEW | REQUEST_REVISION | REVISION_REQUIRED |
| PROVISIONAL | (到期) | — | UNDER_REVIEW |
| ADMITTED | DEPRECATE | — | DEPRECATED |

## 6. Migration Principle

> Migration may change representation, but must not change governance semantics.
>
> 迁移只能改变治理对象的表示方式，不得改变其治理语义、规范效力、决策结果或历史事实。

### 三种操作区分

| 操作 | 允许改变表示 | 允许改变历史语义 | 处理方式 |
|------|-------------|-----------------|----------|
| Migration | 是 | 否 | 追加迁移记录 |
| Amendment | 可以 | 不得覆盖原语义 | 追加更正记录 |
| New Decision | 可以 | 可以改变未来效力 | 创建新的 Decision Record |

### 合法迁移示例

旧格式：
```yaml
Governor: Pending Confirmation
```

新格式（语义等价迁移）：
```yaml
DecisionStatus: PENDING
DecisionOutcome: null
```

**前提**：旧字段确实表示"尚未作出决定"。如存在歧义，不能由迁移程序自行解释，必须记录人工确认或 Amendment。

### 非法迁移示例

```yaml
Before:
    Governor: Pending Confirmation

After:
    DecisionStatus: RECORDED
    DecisionOutcome: ADMIT
```

这不是表示转换，而是凭空制造治理裁定。

## 7. Append-Only History Model

```
Original Artifact
    │
    ├── Amendment Record
    │
    ├── Migration Record
    │
    └── Superseding Decision
    │
    ▼
Current View
```

### 规则

- Original Artifact 永久保留
- Amendment 说明原记录哪里错误以及如何解释
- Migration 声明新旧 Schema 的映射关系
- Superseding Decision 改变未来效力，但不抹除旧决定曾经有效的事实
- Current View 是可重建的派生结果，不应成为唯一事实来源

### Repository Truth

> 原始记录、追加记录、授权决定和可验证派生规则共同构成的历史链。

## 8. Migration Record 格式

```yaml
MigrationRecord:
    SchemaVersion: 2
    PreviousSchemaVersion: 1
    MigratedAt: 2026-07-15
    Reason: "Governance schema migration"
    Mapping:
        OldField: "Governor"
        NewField: "DecisionStatus + DecisionOutcome"
        SemanticEquivalence: true
    OriginalPreserved: true
    ApprovedBy: <authority>  # 如有歧义需人工确认
```

## 9. Amendment Record 格式

```yaml
AmendmentRecord:
    AmendedAt: 2026-07-15
    Reason: "<correction reason>"
    OriginalContent: "<what was wrong>"
    CorrectedInterpretation: "<how to interpret correctly>"
    ApprovedBy: <authority>
```

## 10. Acceptance Criteria

- [x] Layer Separation 明确定义
- [x] Governance Artifact 分类完整
- [x] Object State Machine 闭合
- [x] Decision Status/Outcome 分离
- [x] 合法迁移表完整
- [x] PROVISIONAL 语义明确
- [x] Migration Principle 定义
- [x] Append-Only History 模型定义
- [ ] Governor 确认后锁定定稿

---

*Status: DRAFT-Pending-Review*
