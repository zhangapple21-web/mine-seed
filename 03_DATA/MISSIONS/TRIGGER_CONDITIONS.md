# Mission Trigger Conditions — 条件触发机制 v2.1

> **原则**: 不说"以后做"，而是定义"什么条件下做"。
> **来源**: M系列设计（E007）+ 按需激活架构 + GPT Review 2026-07-15
> **参考**: Temporal Signal / AWS EventBridge / Dify 1.10 Event-Driven Workflows

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
 ├── 1. 验证触发条件（防止误触发）
 ├── 2. 生成 Trigger Evidence Record
 ├── 3. 写入 Evidence Store
 └── 4. 若 CONFIRM 模式，等待 Governor 确认
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

## 触发类型（v2.1 完善检查调度）

### 类型对比

| 类型 | 驱动方式 | 说明 | 检查方式 |
|------|----------|------|----------|
| **EVENT** | 信号驱动 | 响应已发生的事实 | 实时（事件总线） |
| STATE | 条件驱动 | 持续检查状态是否成立 | check_schedule（默认 daily） |
| RESOURCE | 条件驱动 | 资源状态检查 | check_schedule（默认 daily） |
| TIME | 条件驱动 | 时间到达 | check_schedule（默认 hourly） |
| DEPENDENCY | 条件驱动 | 前置依赖完成 | 事件触发（DEPENDENCY_COMPLETED） |
| THRESHOLD | 条件驱动 | 阈值触发 | 持续监控（告警系统） |
| MANUAL | 信号驱动 | 手动触发 | 实时 |

### check_schedule 字段（v2.1 新增）

```yaml
# STATE 触发器示例
type: STATE
capability: GovernanceKernelReady
check_schedule:
  frequency: daily          # daily / hourly / cron
  time: "09:00"             # 每天固定时间（可选）
  timezone: "Asia/Shanghai"
```

### EVENT vs 条件驱动

```yaml
# EVENT（信号驱动）- 事件本身即触发条件
type: EVENT
event_type: ReplayFinished
# 无需 condition，事件发生即触发

# STATE（条件驱动）- 需要持续检查
type: STATE
condition: GovernanceKernelReady == true
check_schedule:
  frequency: hourly
```

---

## Mission Trigger vs Runtime Trigger

| 维度 | Mission Trigger | Runtime Trigger |
|------|-----------------|-----------------|
| 生命周期 | 长期任务（天/周级） | 即时任务（秒/分钟级） |
| 触发后 | 进入 Mission Queue | 直接执行 |
| 调度 | Scheduler 排期 | Worker Pool 立即执行 |
| 示例 | DATA-001 数据源恢复 | M02 失效分析 |

### 注册表分离（v2.1 引用配置 ID）

```yaml
MissionTriggerRegistry:
  - mission_id: DATA-001
    trigger_configs:
      - cfg_id: TC-STATE-001
        type: STATE
        capability: GovernanceKernelReady
      - cfg_id: TC-RESOURCE-001
        type: RESOURCE
        capability: ProviderHealthOK
        condition: "!= HEALTHY"
        duration_type: continuous  # continuous | cumulative
        duration: 2 days
      - cfg_id: TC-EVENT-001
        type: EVENT
        event_type: ProviderFailed
      - cfg_id: TC-TIME-001
        type: TIME
        capability: AuditPassed
        offset: 3 days
    activation_mode: CONFIRM
    confirmation_window: 24h
    
RuntimeTriggerRegistry:
  - worker_id: M02
    trigger_configs:
      - cfg_id: TC-EVENT-M02
        type: EVENT
        event_type: WorkerFailed
    activation_mode: AUTO
```

---

## Activation Mode（v2.1 新增 ESCALATE）

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| AUTO | 自动执行 | 生产阻断、明确条件 |
| **CONFIRM** | 系统请求，人类确认 | 重要但非紧急 |
| **ESCALATE** | 超时未确认，升级处理 | 关键任务超时 |
| MANUAL | 完全手动 | 实验性质 |

### CONFIRM 模式配置（v2.1 完善）

```yaml
activation:
  mode: CONFIRM
  confirmation_window: 24h
  default_on_timeout: ESCALATE  # ABORT / EXECUTE / ESCALATE
  
  # ESCALATE 配置
  escalation:
    target: governor+1          # 升级到上一级
    notify_channel: telegram    # 通知渠道
    auto_execute_after: 48h     # 最终兜底自动执行
```

### ESCALATE 流程

```
CONFIRM 触发
     │
     ▼
等待 Governor 确认（24h 窗口）
     │
     ├── 确认 → 执行
     │
     └── 超时 → ESCALATE
                 │
                 ▼
         升级到 governor+1
         通知到 Telegram
         再等待 24h
                 │
                 ├── 确认 → 执行
                 │
                 └── 超时 → 自动执行（兜底）
```

---

## Capability Dictionary（v2.1）

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

## Trigger Evidence（v2.1 新增 duration 字段）

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
  "dispatch_status": "QUEUED",
  "trigger_evaluation_duration_ms": 23,
  "duration_type": "continuous"
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
  - cfg_id: TC-STATE-001
    type: STATE
    capability: GovernanceKernelReady
    check_schedule:
      frequency: daily
      time: "09:00"
    note: C-028 或 C-029 通过
    
  - cfg_id: TC-RESOURCE-001
    type: RESOURCE
    capability: ProviderHealthOK
    condition: provider.health != HEALTHY
    duration_type: continuous
    duration: 2 days
    check_schedule:
      frequency: hourly
    note: 数据源连续 2 天不健康
    
  - cfg_id: TC-EVENT-001
    type: EVENT
    event_type: ProviderFailed
    note: Provider 完全失效
    
  - cfg_id: TC-TIME-001
    type: TIME
    capability: AuditPassed
    offset: 3 days
    check_schedule:
      frequency: daily
      time: "00:00"
    note: 审核通过后 3 天
    
  - cfg_id: TC-MANUAL-001
    type: MANUAL
    condition: user_request == true
    
Activation Mode: CONFIRM
Confirmation Window: 24h
Default on Timeout: ESCALATE
Escalation Target: governor+1
Priority After Activation: P0
```

**duration_type 说明**：
- `continuous`: 连续不健康（每天检查都失败）
- `cumulative`: 累计不健康（总共 X 天失败）

---

## 检查周期（v2.1 完善）

| 类型 | 检查方式 | 默认频率 | 可配置 |
|------|----------|----------|--------|
| EVENT | 实时响应 | 事件总线 | — |
| STATE | 定时检查 | daily 09:00 | check_schedule |
| RESOURCE | 定时检查 | daily 09:00 | check_schedule |
| TIME | 定时检查 | hourly | check_schedule |
| DEPENDENCY | 事件触发 | 任务完成时 | — |
| THRESHOLD | 持续监控 | 告警系统 | — |

---

## 待定义触发条件的 CANDIDATE

| Mission/Worker | 类型 | 触发条件 | Activation |
|----------------|------|----------|------------|
| DATA-001 | Mission | STATE/RESOURCE/EVENT/TIME/MANUAL | CONFIRM+ESCALATE |
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

## 事件类型定义（v2.1 新增 purpose）

| Event Type | 触发场景 | 目标 Worker | Purpose |
|------------|----------|-------------|---------|
| `NewSignalCandidate` | 新信号候选入库 | M01 | 验证信号质量 |
| `WorkerFailed` | Worker 执行失败 | M02 | 失效分析与重试 |
| `WorkerRegistered` | Worker 注册/更新 | M03 | 画像更新 |
| `ConstraintNeeded` | 发现新约束需求 | M04 | 约束提案 |
| `AssetIngested` | 新资产入库 | M05 | 同构检测 |
| `NewFragmentFound` | 发现 R1 碎片 | M06 | 考古整理 |
| `ProviderFailed` | Provider 完全失效 | DATA-001 | 数据源恢复 |
| `ReplayFinished` | 回放验证完成 | — | 作为 DEPENDENCY 触发条件 |
| `GovernorDecisionMade` | Governor 做出决策 | — | 触发 STATUS 变更通知 |

**Purpose 字段说明**：
- 明确事件被谁引用、为什么存在
- 避免后续维护时遗忘

---

## 业界参考

### Temporal（Event Sourcing + Signal）

- **Signal**: 外部事件注入 Workflow
- **Event Sourcing**: 所有状态变更记录为事件
- **Workflow vs Activity**: 长期编排 vs 即时执行

**借鉴**：Mission = Workflow，Worker = Activity

### AWS EventBridge（Pattern Matching）

- **Rule**: 事件模式匹配
- **Target**: 目标服务
- **enabled**: 规则开关

**借鉴**：check_schedule.enabled、pattern matching

### Dify 1.10（Event-Driven Workflows）

- **Trigger**: 工作流启动条件
- **Event**: 外部事件触发

**借鉴**：EVENT 作为第一类 Trigger

---

*Trigger v2.1。参考 Temporal/AWS EventBridge/Dify 最佳实践。不说"以后做"，只说"什么条件下做"。M4 守护边界，其他 Workers 按需解放。*