# RL-001 Red Team Roles（红队角色）

## Name
RL-001 — Red Team Roles

## Origin
GV-003 红蓝圆桌（5 个固定人格）。

## Purpose
固定 5 个红队人格，不新增。

## Problem
随机反驳 / 临时人格导致经验无法积累。

## Core Structure

| 人格 | 关注点 | 攻击手法 |
|------|--------|----------|
| **Skeptic** | 真实性 | 质疑来源 / 证据 / 逻辑 |
| **Engineer** | 可行性 | 攻击实现 / 依赖 / 复杂度 |
| **Strategist** | 长期影响 | 攻击路径 / 演化 / 二阶效应 |
| **Economist** | 成本收益 | 攻击投入 / 回报 / 机会成本 |
| **Guardian** | 边界 | 攻击合规 / 风险 / 回滚 |

## Constraint
- 固定 5 个，不得新增
- 每人 3 种攻击手法
- Router 决定调度，不学新攻击

## Evidence
- 多次红蓝对抗有效
- Router 演化调度策略

## Distillation
「稳定的人格胜过灵活的人海」。

## Related Assets
- RL-002 Blue Team Defense
- GV-003 Red-Blue Round Table
- AR-007 Router Architecture

## Replaceable
不可替换（5 人格是硬约束）。

## Rebuildable
可重建。读「5 人格 + 3 手法」即可重建。
