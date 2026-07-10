# V6-RFC-004: Constraint自动注入

**状态**: Draft  
**作者**: 疯子(CCO)  
**日期**: 2026-06-16  
**依赖**: RFC-001, RFC-002, RFC-003

---

## 1. 设计哲学

矿场V6的核心不是代码，是**约束的自动生成**。

```
Observation → Experience → Constraint
```

当系统检测到异常模式时，自动生成约束，无需人工干预。

## 2. 第一条约束（已生成）

```json
{
  "id": "constraint_scheduler_001",
  "type": "FORBID",
  "target": "direct_spawn",
  "scope": ["sub_session", "computer_use"],
  "reason": "session_explosion_20260616",
  "evidence": "80_sessions_accumulated",
  "rule": "所有执行权必须经过Scheduler，禁止直接spawn/抢占云电脑",
  "created": "2026-06-16T14:46:00+08:00",
  "status": "active"
}
```

## 3. 约束触发器

| 触发条件 | 约束类型 | 动作 |
|----------|----------|------|
| 活跃Session > 50 | FORBID | 禁止新的B类spawn |
| 活跃Session > 30 | THROTTLE | 禁止新的C类spawn |
| A类任务延迟 > 5min | PREEMPT | 终止所有B/C类任务 |
| 同类型任务重复创建 | DEDUP | 拒绝重复Session |
| 云电脑占用 > 10min | TIMEOUT | 强制释放 |
| 连续3次同任务失败 | COOLDOWN | 该任务冷却1h |

## 4. 约束生命周期

```
DETECTED → DRAFT → ACTIVE → SUPERSEDED → ARCHIVED
```

| 状态 | 含义 |
|------|------|
| DETECTED | Scheduler检测到异常模式 |
| DRAFT | 自动生成约束草案，需CCO确认 |
| ACTIVE | 约束生效，所有执行必须遵守 |
| SUPERSEDED | 被新约束替代 |
| ARCHIVED | 历史约束，仅供参考 |

## 5. 约束生成流程

```
1. Scheduler检测异常（如Session > 50）
2. 自动生成约束草案（type + scope + rule）
3. 通知CCO确认
4. CCO确认 → ACTIVE
5. 所有后续执行必须检查约束
6. 如果约束不再需要 → SUPERSEDED → ARCHIVED
```

### 5.1 自动确认规则

以下条件满足时，约束可自动激活（无需CCO确认）：
- 触发条件是数值阈值（如Session > 50）
- 同类型约束已有先例（如之前生成过类似FORBID）
- A类任务受阻

### 5.2 必须CCO确认

- 约束影响A类任务
- 约束类型为FORBID（禁止类）
- 新型约束（无先例）

## 6. 约束存储

所有约束存放在 `ACTIVE_WORKERS.md` 的 `active_constraints` 区域：

```json
{
  "active_constraints": [
    {
      "id": "constraint_scheduler_001",
      "type": "FORBID",
      "target": "direct_spawn",
      "status": "active"
    }
  ],
  "superseded_constraints": [],
  "constraint_log": [
    {
      "id": "constraint_scheduler_001",
      "activated": "2026-06-16T14:46:00",
      "evidence": "80_sessions"
    }
  ]
}
```

## 7. 与O→E→C闭环的关系

约束不是凭空设计的，是从经验中压缩出来的：

```
Observation: 80个Session堆积，云电脑被锁
    ↓
Experience: 允许直接spawn = 资源竞争 = 瘫痪
    ↓
Constraint: FORBID direct_spawn, 所有执行权经过Scheduler
```

这是矿场第一次把**真实撞墙事件**压缩成协议。以后每次撞墙都应该走同样的闭环。

## 8. 未来约束预测

基于当前系统演化方向，预计会触发的约束：

| 预测约束 | 触发条件 | 概率 |
|----------|----------|------|
| 禁止同任务并发 | Cron撞车频繁 | 高 |
| Session配额制 | 资源持续紧张 | 中 |
| 自动降级策略 | 云电脑长期不可用 | 中 |
| 跨环境调度 | 需要多台云电脑 | 低 |

---

**总结**: Constraint自动注入 = V6的"免疫系统"。不是等病了再治，而是检测到异常模式就自动生成抗体。
