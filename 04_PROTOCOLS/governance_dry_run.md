# Event-Sourced Governance — Minimal Dry Run

> 创建时间: 2026-07-15
> 状态: EXPERIMENTAL
> 范围: 仅用于验证模型，不产生真实治理效力
> 对应原则: C-029 ~ C-033 (CANDIDATE)

## 目的

用最小事件集验证 Event-Sourced 治理模型的可行性，不修改任何现有治理记录。

## 最小事件集（v0.1）

仅定义 4 种核心事件，其余全部作为 Payload：

| Event Type | 含义 | 改变状态? |
|------------|------|-----------|
| `ArtifactRegistered` | 治理对象注册 | ✅ 建立身份 |
| `ArtifactAppended` | 追加证据/记录 | ❌ 只追加事实 |
| `DecisionRecorded` | 记录治理决定 | ✅ 改变规范效力 |
| `ArtifactMigrated` | 表示方式迁移 | ❌ 不改语义 |

## Event Envelope（最小版）

```yaml
EventId: <uuid>
EventType: ArtifactRegistered | ArtifactAppended | DecisionRecorded | ArtifactMigrated
EventSchemaVersion: 1
SubjectId: <artifact-id>
StreamSequence: <int>
OccurredAt: <timestamp>
RecordedAt: <timestamp>
EffectiveFrom: <timestamp>
Payload: <object>
```

## Payload 定义

### ArtifactRegistered

```yaml
Payload:
    ObjectType: PRINCIPLE | CONSTRAINT | PROTOCOL | ADR
    StableName: <human-readable name>
    InitialStatus: DRAFT | CANDIDATE
```

### ArtifactAppended

```yaml
Payload:
    AppendType: EVIDENCE | AMENDMENT | COMMENT
    ArtifactRef: <reference to appended content>
    AppendedBy: <actor>
```

### DecisionRecorded

```yaml
Payload:
    DecisionId: <decision-id>
    Outcome: ADMIT | ADMIT_PROVISIONALLY | REJECT | REQUEST_REVISION
    DecidedBy: <authority>
    Reason: <rationale>
    EffectiveUntil: <timestamp or null>
    Scope: <scope or null>
```

### ArtifactMigrated

```yaml
Payload:
    MigrationType: REPRESENTATION | SCHEMA
    FromSchema: <old-schema-version>
    ToSchema: <new-schema-version>
    SemanticChange: false
    MigrationRef: <migration record reference>
```

## Dry Run — C-028 Persistence Independence

### 事件流

```
0001 ArtifactRegistered
     SubjectId: C-028
     ObjectType: CONSTRAINT
     StableName: Persistence Independence Principle
     InitialStatus: CANDIDATE

0002 ArtifactAppended
     SubjectId: C-028
     AppendType: EVIDENCE
     ArtifactRef: user-proposal-20260715

0003 ArtifactAppended
     SubjectId: C-028
     AppendType: EVIDENCE
     ArtifactRef: admission-record-20260715-C028

0004 DecisionRecorded
     SubjectId: C-028
     Outcome: ADMIT_PROVISIONALLY
     DecidedBy: user
     Reason: 内容合理，补 Admission Record 后临时生效
     EffectiveUntil: 2026-08-15
     Scope: repository-governance
```

### 生成的 Projection

```yaml
SubjectId: C-028
ObjectType: CONSTRAINT
StableName: Persistence Independence Principle
CurrentStatus: PROVISIONAL
EffectiveDecision: DEC-C028-001
EvidenceCount: 2
MigrationCount: 0
LastEvent: 0004
```

## Dry Run — C-029 Admission Separation

### 事件流

```
0001 ArtifactRegistered
     SubjectId: C-029
     ObjectType: CONSTRAINT
     StableName: Admission Separation Principle
     InitialStatus: CANDIDATE

0002 ArtifactAppended
     SubjectId: C-029
     AppendType: EVIDENCE
     ArtifactRef: user-proposal-20260715
```

### 生成的 Projection

```yaml
SubjectId: C-029
ObjectType: CONSTRAINT
StableName: Admission Separation Principle
CurrentStatus: CANDIDATE
EffectiveDecision: null
EvidenceCount: 1
MigrationCount: 0
LastEvent: 0002
```

## 验证点

1. ✅ 删除 Projection 后可从事件流重建
2. ✅ DecisionRecorded 是唯一改变规范效力的事件
3. ✅ ArtifactMigrated 不改变语义
4. ✅ 没有 Pending Decision 这种东西，无 Decision 就是 CANDIDATE
5. ✅ Kernel 只认识 4 种事件，不知道 Admission/Review/Replay 等业务概念

## 下一步

- [ ] 观察 1-2 个月真实治理事件
- [ ] 确认哪些事件类型真正频繁发生
- [ ] 从实际使用中"考古"出稳定的 Kernel v1
- [ ] Bootstrap Charter 仅在 Kernel v1 正式化时使用一次

---

*Status: EXPERIMENTAL — Dry Run Only*
