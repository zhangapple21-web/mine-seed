# PR-002 Self-Loop（自循环原则）

## Name
PR-002 — Self-Loop

## Origin
OPS-005 + 用户偏好「用户不是任务分发者」。

## Purpose
确保系统空载时主动寻找工作，不等待用户输入。

## Problem
空载 Runtime 静默等待用户指令，浪费时间与机会。

## Core Structure
每日自循环：
```
Environment → Observe → Audit → Recovery
    → Discovery → Candidate → Seed
    → Task → Validator → Governor
    → Archive → Evolution → Heartbeat
    → Repeat
```

## Constraint
- Heartbeat 必须每 5-10 分钟一次
- Discovery 优先于 User Input
- 用户是文明观察源之一，不是唯一驱动

## Evidence
- 荐股定时任务从「等用户提醒」进化到「Heartbeat 自动补偿」
- TaskRouter 修复中发现 06_RUNTIME 已存在 14+ 个自动触发点

## Distillation
「让 Runtime 主动工作，不是让用户主动指挥」。

## Related Assets
- PR-001 Drawer First
- PR-005 Work Discovery
- PR-006 Self-Loop Mandate

## Replaceable
可替换（自循环顺序可调）。

## Rebuildable
可重建。读「空载必须主动寻找工作」即可重建。
