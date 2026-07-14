# PR-005 Work Discovery（工作发现原则）

## Name
PR-005 — Work Discovery

## Origin
OPS-007 蒸馏。

## Purpose
Runtime 空载时按优先级寻找工作。

## Problem
空载 Runtime 不知道下一步该做什么。

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
- 每项发现都必须有可执行任务

## Evidence
- 荐股熔断机制发现后自动转入策略优化
- Heartbeat 定期检查 Repository Gap

## Distillation
「用户是观察源，不是主调度器」。

## Related Assets
- PR-002 Self-Loop
- AR-006 Heartbeat Architecture

## Replaceable
可替换（优先级可调）。

## Rebuildable
可重建。读「用户输入在最末位」即可重建。
