# CP-003 Shadow Observer（影子观察）

## Name
CP-003 — Shadow Observer

## Origin
AUM-MISSION-EXP-001（用户偏好「可退出的实验」）。

## Purpose
多模型审计的零风险观察机制。

## Problem
直接接入矿工裁判风险高（影响主流程）。

## Core Structure
严格只读约束：
```
Shadow Observer
  ↓
读取主流程产物（advisor/*.md）
  ↓
调用 TaskRouter.call_worker()
  ↓
写入 03_DATA/shadow_audit/
  ↓
❌ 不得写入 audit_results.json
❌ 不得修改 StockAdvisor
❌ 不得影响 Admission
```

## Constraint
- 7 天观察期
- 3 个升级问题，2 个证据支持才能升级
- 中途发现主流程污染立刻停止

## Evidence
- 2026-07-14 第一次影子观察成功（GLM 70 + GitHub 65 → 共识 67）
- 2026-07-14 第二次影子观察（中芯国际共识 72）

## Distillation
「实验不应该影响生产」。

## Related Assets
- CP-001 Provider Adapter
- AR-007 Router Architecture

## Replaceable
可替换（观察策略可调）。

## Rebuildable
可重建。读「只读影子 + 7 天实验」即可重建。
