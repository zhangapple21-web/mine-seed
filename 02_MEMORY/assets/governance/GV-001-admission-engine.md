# GV-001 Admission Engine（资产准入引擎）

## Name
GV-001 — Admission Engine

## Origin
ARCH-011 + 多次 Admission 失误蒸馏。

## Purpose
Tier 1 / Tier 2 资产写入的强制路径。

## Problem
直接写入文明层会导致：
- 资产未经蒸馏
- 资产分类错误
- 资产可追溯性丢失

## Core Structure
唯一合规路径：
```
evolve()
  ↓
apply_constraint_patch()
  ↓
Admission Engine
  ↓
02_MEMORY/assets/
```

## Constraint
- 禁止直接写入 02_MEMORY/ Tier 1 / Tier 2
- 禁止不经过 evolve() 的「野写入」
- 任何写入必须留下约束追溯

## Evidence
- 2026-07-14 多个 Mission 资产通过 evolve() 路径沉淀
- 2026-07-13 文明冻结通过 Admission 完成

## Distillation
「文明层不接受野写入」。

## Related Assets
- C-013 Single Canonical Path
- C-016 Constraint Traceability
- PR-003 Distill Before Archive

## Replaceable
不可替换（这是核心治理）。

## Rebuildable
可重建。读「Tier 1 必须经 evolve()」即可重建。
