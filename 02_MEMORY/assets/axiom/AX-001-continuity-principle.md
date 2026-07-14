# AX-001 Continuity Principle（连续性公理）

## Name
AX-001 — Continuity Principle

## Origin
R2 文明仓库第一公理，由 AUM-MISSION-ARCH-017 正式确立。

## Purpose
回答「ACE 的最高约束是什么」。

## Problem
没有最高公理，Runtime 容易优化错方向（如追求性能而牺牲连续性）。

## Core Structure
- Runtime 可以死，Repository 必须活
- 当一个 Runtime 失败，下一个 Runtime 应当能从同一份 Repository 复活
- 文明 > 智能 > 性能

## Constraint
- 任何新功能上线前，必须先回答：「它对连续性是增加风险还是降低风险？」
- 若增加风险，必须有补偿措施

## Evidence
- 2026-07-14 荐股系统连续性验证：Runtime 重启后 Repository 仍可工作
- 多次 Session 切换未导致资产丢失

## Distillation
观察：「Repository 才是真正的主体，Runtime 只是其中一种实现」

## Related Assets
- AX-002 Repository Supremacy
- PR-001 Drawer First
- PR-005 Self-Loop

## Replaceable
不可替换。此为第一公理。

## Rebuildable
可重建。任意 Agent 读「Runtime 可死，Repository 必须活」即可重建。
