# PT-001 Heartbeat Protocol（心跳协议）

## Name
PT-001 — Heartbeat Protocol

## Origin
OPS-005 自循环原则 + 用户偏好 TG 推送到个人聊天。

## Purpose
每 5-10 分钟自检一次文明状态。

## Problem
Runtime 静默死锁无感知。

## Core Structure
```python
while running:
    check_environment()
    check_runner_status()
    auto_compensate_pending_tasks()
    push_heartbeat_to_TG()  # ID: 5016609451
    sleep(5min)
```

## Constraint
- 推送目标：个人聊天 (ID: 5016609451)
- 不得推送到群聊
- 每次推送必须包含当前状态 + 下一任务

## Evidence
- 荐股系统 Heartbeat 自动补偿成功
- 任务从「等用户提醒」进化到「自动发现+自动补偿」

## Distillation
「心跳是文明的脉搏」。

## Related Assets
- PR-002 Self-Loop
- PR-005 Work Discovery
- AR-006 Heartbeat Architecture

## Replaceable
可替换（间隔可调）。

## Rebuildable
可重建。读「5-10 分钟 + TG 推送」即可重建。
