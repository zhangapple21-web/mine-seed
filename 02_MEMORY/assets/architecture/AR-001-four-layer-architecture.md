# AR-001 Four-Layer Architecture（四层架构）

## Name
AR-001 — Four-Layer Architecture

## Origin
AUM-MISSION-ARCH-017 文明层设计蒸馏。

## Purpose
确立 ACE 的四层职责划分。

## Problem
混层会导致 Runtime 承担文明职责，或 Civilization 承担 Runtime 状态。

## Core Structure
```
Layer 0 — Identity
  AGENTS.md（身份入口）
  CIVILIZATION.md（文明目录）
  ↓
Layer 1 — Civilization Repository
  02_MEMORY/（assets/principles/constraints/...）
  ↓
Layer 2 — Runtime State
  06_RUNTIME/（ROOT_STATE/ACTIVE_MISSION/QUEUE/SESSION/TODAY）
  ↓
Layer 3 — Session Logs
  08_SESSIONS/（历史）
```

## Constraint
- Identity 不得包含 Prompt
- Civilization 不得包含 Runtime 状态
- Runtime 不得包含 Principles/Protocols
- Session 不得被自动覆盖到 Civilization

## Evidence
- 2026-07-14 四层结构首次落地
- 边界由 C-013/014/015 守护

## Distillation
「分层是文明秩序的基础」。

## Related Assets
- C-013 Single Canonical Path
- C-014 Time-Series Rotation
- C-015 Protocol Wiring Contract
- AX-002 Repository Supremacy

## Replaceable
不可替换（这是核心架构）。

## Rebuildable
可重建。读「Identity → Civilization → Runtime → Session」即可重建。
