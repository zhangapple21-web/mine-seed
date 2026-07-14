# GV-003 Red-Blue Round Table（红蓝圆桌）

## Name
GV-003 — Red-Blue Round Table

## Origin
红蓝对抗设计（用户偏好「固定攻击链+稳定人格芯片」）。

## Purpose
建立稳定的对抗审议机制。

## Problem
随机反驳/支持无法积累经验。

## Core Structure
固定 5 步攻击链：
```
Quick Strike → Evidence Attack → Boundary Test → Stress Test → Kill Shot
```

固定 5 个人格芯片：
- **Skeptic**（怀疑者）
- **Engineer**（工程师）
- **Strategist**（战略家）
- **Economist**（经济学家）
- **Guardian**（守护者）

固定蓝队 5 问：
1. validity（有效性）
2. evidence（证据）
3. history（历史）
4. rollback（回滚）
5. side effects（副作用）

Router 决定调度策略（何时用谁），不学新攻击。

## Constraint
- 攻击链长度固定 5 步
- 攻击手法固定 3 种/人格
- 不得新增攻击手法
- 不得新增人格

## Evidence
- 多次红蓝对抗成功防御方案
- 路由器学习调度而非武器扩展

## Distillation
「系统复杂度上限是固定的」。

## Related Assets
- C-024 Testable, Iterable, Routable
- AR-007 Router Architecture

## Replaceable
不可替换（这是核心治理）。

## Rebuildable
可重建。读「5 步链 + 5 人格 + 5 问」即可重建。
