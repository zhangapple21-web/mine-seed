# PT-002 Dual-Trigger Mechanism（双触发机制）

## Name
PT-002 — Dual-Trigger Mechanism

## Origin
荐股定时任务修复（用户 9:00 开机，原任务 8:15）。

## Purpose
定时任务 + Heartbeat 自动补偿的双保险。

## Problem
单一定时任务容易因系统休眠/关机错过。

## Core Structure
```
触发路径 1：Windows Task Scheduler
  - 每周一-五 9:20
  - SYSTEM 用户
  - 任务名：ACE_StockAdvisor_Daily

触发路径 2：Heartbeat 自动补偿
  - 9:20-11:30 每 15 分钟检查
  - 验证 advisor_YYYYMMDD.md 与 runner_status.json
  - 发现未完成则自动补偿
```

## Constraint
- 两个触发器互不冲突
- 校验机制必须防重复
- 用户开机时间波动时要兜底

## Evidence
- 2026-07-14 任务成功注册 + Heartbeat 兜底
- 系统从「8:15 错过」进化到「9:20 必达」

## Distillation
「关键任务必须有兜底」。

## Related Assets
- PT-001 Heartbeat Protocol
- CP-006 Adaptive Scorer

## Replaceable
可替换（具体时间可调）。

## Rebuildable
可重建。读「定时 + Heartbeat 双保险」即可重建。
