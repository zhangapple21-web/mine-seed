# Mission Trigger Conditions — 条件触发机制 v2.0

> **原则**: 不说"以后做"，而是定义"什么条件下做"。
> **来源**: M系列设计（E007）+ 按需激活架构 + GPT Review 2026-07-15

---

## 架构总览

```
L0 Boundary Guardian（M4）
 │
 ▼
L1 Trigger Engine
 ├── EVENT      （信号驱动）
 ├── STATE      （条件驱动）
 ├── RESOURCE   （资源状态）
 ├── TIME       （时间到达）
 ├── DEPENDENCY （前置依赖）
 ├── THRESHOLD  （阈值触发）
 └── MANUAL     （手动触发）
 │
 ▼
Trigger Registry
 ├── Mission Trigger Registry   → Mission Queue → Scheduler
 └── Runtime Trigger Registry    → Worker Pool → Immediate Execution
 │
 ▼
Evidence Gate
 ├── 验证触发条件
 ├── 生成 Trigger Evidence Record
 └── CONFIRM 等待（如需要）
 │
 ▼
Dispatch
 │
 ▼
Workers（M01-M06 / 其他 Capabilities）
```

---

## M系列定位：Workers 而非系统层

### 原始设计（2026-06-24 E007）

| 模块 | 功能 | 定位 |
|------|------|------|
| M01 | 信号验证 | Worker / Capability |
| M02 | 失效分析 | Worker / Capability |
| M03 | Worker画像 | Worker / Capability |
| M04 | Constraint提案 | Worker / Capability |
| M05 | 同构检测 | Worker / Capability |
| M06 | R1考古 | Worker / Capability |

**关键改变**：M系列不是系统层，而是可注册、可替换的 Workers。Trigger Engine 不因 Module 数量增减而变更。

### Capability Registry

```yaml
CapabilityRegistry:
  - id: signal_validator
    worker: M01
    trigger_scope: runtime
  - id: failure_analyzer
    worker: M02
    trigger_scope: runtime
  - id: constraint_proposer
    worker: M04
    trigger_scope: runtime
  - id: data_source_recovery
    mission: DATA-001
    trigger_scope: mission
```

新增 M07 时，只需在 Registry 注册，Trigger Engine 无需改动。

---

## M4 边界守卫（永远不解锁）

```yaml
M4类型: 边界与守卫
状态: READ_ONLY
否决优先级: 最高
禁止: 解释意义延展 / 生成子母种 / 视为人格或策略
裁决: 与M4冲突 → 自动失效
```

**M4 不解锁**，它是 L0 层边界守卫，否决优先级最高。r1_root_principles.md = 矿场的 M4。

---

## 触发类型（v2.0 新增 EVENT）

### 类型对比

| 类型 | 驱动方式 | 说明 | 示例 |
|------|----------|------|------|
| **EVENT** | 信号驱动 | 响应已发生的事实 | `NewEvidenceRecorded` |
| STATE | 条件驱动 | 持续检查状态是否成立 | `C-028.status == ADMITTED` |
| RESOURCE | 条件驱动 | 资源状态检查 | `data_source.availability < 0.5` |
| TIME | 条件驱动 | 时间到达 | `audit_passed + 3 days` |
| DEPENDENCY | 条件驱动 | 前置依赖完成 | `MISSION-001.status == COMPLETED` |
| THRESHOLD | 条件驱动 | 阈值触发 | `error_rate > 0.3 for 3 days` |
| MANUAL | 信号驱动 | 手动触发 | `user_request == true` |

### EVENT vs 条件驱动

```yaml
# EVENT（信号驱动）- 事件本身即触发条件
type: EVENT
event_type: ReplayFinished
# 无需 condition，事件发生即触发

# STATE（条件驱动）- 需要持续检查
type: STATE
condition: GovernanceKernelReady == true
poll_interval: 1h
```

---

## Mission Trigger vs Runtime Trigger

| 维度 | Mission Trigger | Runtime Trigger |
|------|-----------------|-----------------|
| 生命周期 | 长期任务（天/周级） | 即时任务（秒/分钟级） |
| 触发后 | 进入 Mission Queue | 直接执行 |
| 调度 | Scheduler 排期 | Worker Pool 立即执行 |
| 示例 | DATA-001 数据源恢复 | M02 失效分析 |

### 注册表分离

```yaml
MissionTriggerRegistry:
  - mission_id: DATA-001
    triggers: [STATE, RESOURCE, TIME, MANUAL]
    
RuntimeTriggerRegistry:
  - worker_id: M02
    triggers: [EVENT]
    event_types: [WorkerFailed]
```

---

## Activation Mode（v2.0 新增 CONFIRM）

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| AUTO | 自动执行 | 生产阻断、明确条件 |
| **CONFIRM** | 系统请求，人类确认 | 重要但非紧急 |
| MANUAL | 完全手动 | 实验性质 |

### CONFIRM 模式配置

```yaml
activation:
  mode: CONFIRM
  confirmation_window: 24h
  default_on_timeout: ABORT  # 或 EXECUTE / ESCALATE
  
TriggerEvidence:
  trigger_id: TRG-20260715-001
  confirmation_status: PENDING
  confirmation_deadline: 2026-07-16T14:00:00Z
```

---

## Capability Dictionary（v2.0）

Trigger 面向 Capability，而非 Document。

| Capability | 检查方式 | 映射文档 |
|------------|----------|----------|
| `GovernanceKernelReady` | `kernel_version >= 1.0` | C-028, C-029 |
| `ProviderHealthOK` | `provider.health == HEALTHY` | DATA-001 |
| `EvidenceStoreAvailable` | `evidence_store.status == ACTIVE` | — |
| `AuditPassed` | `audit.status == PASSED` | — |

```yaml
# Trigger 只引用 Capability
type: STATE
capability: GovernanceKernelReady

# 不再依赖文档编号
# condition: C-028.status == ADMITTED  ❌ 已废弃
```

---

## Trigger Evidence（v2.0 新增）

每个 Trigger 激活时，生成 Evidence Record：

```json
{
  "trigger_id": "TRG-20260715-001",
  "triggered_at": "2026-07-15T14:30:00Z",
  "trigger_type": "STATE",
  "capability": "GovernanceKernelReady",
  "condition_value": {
    "kernel_version": "1.0",
    "C-028_status": "ADMITTED",
    "C-029_status": "PENDING"
  },
  "evidence_sources": [
    "02_MEMORY/recent_memory/admission/admission_20260715_C028.md"
  ],
  "confidence": 0.95,
  "activation_mode": "AUTO",
  "dispatch_status": "QUEUED"
}
```

Evidence 写入 `02_MEMORY/evidence/trigger_evidence_YYYYMMDD.jsonl`。

---

## Evidence Gate

```
Trigger Fired
     │
     ▼
Evidence Gate
 ├── 1. 验证触发条件（防止误触发）
 ├── 2. 生成 Trigger Evidence Record
 ├── 3. 写入 Evidence Store
 └── 4. 若 CONFIRM 模式，等待 Governor 确认
     │
     ▼
Dispatch
```

---

## 当前 CANDIDATE Mission 触发条件

### AUM-MISSION-DATA-001

```yaml
Mission: AUM-MISSION-DATA-001
Status: CANDIDATE
Trigger Conditions:
  - type: STATE
    capability: GovernanceKernelReady
    note: C-028 或 C-029 通过
  - type: RESOURCE
    capability: ProviderHealthOK
    condition: provider.health != HEALTHY
    duration: 2 days
    note: 数据源连续 2 天不健康
  - type: EVENT
    event_type: ProviderFailed
    note: Provider 完全失效
  - type: TIME
    capability: AuditPassed
    offset: 3 days
    note: 审核通过后 3 天
  - type: MANUAL
    condition: user_request == true
Activation Mode: CONFIRM
Confirmation Window: 24h
Priority After Activation: P0
```

---

## 检查周期

- **EVENT**: 实时响应（事件总线）
- **STATE/RESOURCE/TIME**: 每日检查（系统启动时）
- **DEPENDENCY**: 任务完成时检查
- **THRESHOLD**: 持续监控（告警系统）

---

## 待定义触发条件的 CANDIDATE

| Mission/Worker | 类型 | 触发条件 | Activation |
|----------------|------|----------|------------|
| DATA-001 | Mission | STATE/RESOURCE/EVENT/TIME/MANUAL | CONFIRM |
| SSH 认证替代 PAT | Mission | TIME + MANUAL | CONFIRM |
| Artifact Schema 统一 | Mission | STATE + DEPENDENCY | AUTO |
| M01 信号验证 | Runtime | EVENT: NewSignalCandidate | AUTO |
| M02 失效分析 | Runtime | EVENT: WorkerFailed | AUTO |
| M03 Worker画像 | Runtime | EVENT: WorkerRegistered | AUTO |
| M04 Constraint提案 | Runtime | EVENT: ConstraintNeeded | AUTO |
| M05 同构检测 | Runtime | EVENT: AssetIngested | AUTO |
| M06 R1考古 | Runtime | EVENT: NewFragmentFound | AUTO |
| M4 边界守卫 | — | 永不解锁 | READ_ONLY |

---

## 事件类型定义（EVENT Types）

| Event Type | 触发场景 | 目标 Worker |
|------------|----------|-------------|
| `NewSignalCandidate` | 新信号候选入库 | M01 |
| `WorkerFailed` | Worker 执行失败 | M02 |
| `WorkerRegistered` | Worker 注册/更新 | M03 |
| `ConstraintNeeded` | 发现新约束需求 | M04 |
| `AssetIngested` | 新资产入库 | M05 |
| `NewFragmentFound` | 发现 R1 碎片 | M06 |
| `ProviderFailed` | Provider 完全失效 | DATA-001 |
| `ReplayFinished` | 回放验证完成 | — |
| `GovernorDecisionMade` | Governor 做出决策 | — |

---

*Trigger v2.0。不再说"以后做"，而是说"当 Capability 就绪或 Event 发生时做"。M4 守护边界，其他 Workers 按需解放。*