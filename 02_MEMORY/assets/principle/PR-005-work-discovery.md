# PR-005 Work Discovery（工作发现原则）

## Name
PR-005 — Work Discovery

## Origin
OPS-007 蒸馏。

## Purpose
Runtime 空载时按优先级执行一次有界、证据驱动的工作发现；允许得出 `NO_VALUABLE_WORK` 并进入 Idle / Watch。

## Problem
空载 Runtime 不知道下一步该观察什么；旧表述也可能把“主动发现”误读为“必须制造任务”。

## Core Structure
工作发现优先级（从高到低）：
1. **Environment Change**（环境变化）
2. **Repository Gap**（仓库缺口）
3. **Failed Experience**（失败经验）
4. **Pending Question**（待解问题）
5. **Pending Task**（待执行任务）
6. **GitHub / RSS / New Release**（外部信号）
7. **User Input**（用户输入，最末位）

## Constraint
- User Input 是最末位，不是首位
- 外部信号只在前 6 项空缺时启用
- 每个 Candidate 必须记录真实 source、reason 和观察时间；evidence、value、budget 可在候选阶段继续形成
- Candidate 不等于 Task；只有补齐执行契约并经 Assessment / Admission 接受后才进入既有 TaskPool
- Workload 不定义 Capability，Execution Resource 不产生 Work
- 有模型、矿工、Worker、API 或预算，不构成创建 Work 的理由
- 一次发现窗口必须有界，不递归制造候选
- 没有足够价值或证据时，记录 `NO_VALUABLE_WORK`，进入 Idle / Watch，等待下一观察窗口
- 连续三个独立 Discovery Window 没有 Candidate 时记录 `INVESTIGATE_DISCOVERY_CHAIN`；这是诊断，不是创建 Work 或调用模型的配额

## Lifecycle Mapping

```text
Observed
→ Candidate
→ Scored / Admission
→ Accepted (TaskPool pending)
→ Executing (active)
→ Validated (review / approved)
→ Distilled (Archivist / Knowledge)
→ Closed (archived)

Candidate → Rejected / Deferred / NO_VALUABLE_WORK
```

这是对现有 Observation、Admission、TaskPool、Validator 和 Archivist 的概念映射，不创建第二套 WorkPool 或状态机。

## Evidence
- 荐股熔断机制发现后自动转入策略优化
- Heartbeat 定期检查 Repository Gap

## Distillation
「用户是观察源，不是主调度器；工作来自发现，不是制造；观察可以持续，执行任务可以为零。」

操作性定义：ACE 可以主动提出新研究方向；禁止的是为了填充矿池、满足调用配额或证明活跃而制造伪 Work。

## Related Assets
- PR-002 Self-Loop
- AR-006 Heartbeat Architecture

## Replaceable
可替换（优先级可调）。

## Rebuildable
可重建。读「用户输入在最末位」即可重建。
