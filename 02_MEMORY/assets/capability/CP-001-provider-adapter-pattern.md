# CP-001 Provider Adapter Pattern（提供者适配器模式）

## Name
CP-001 — Provider Adapter Pattern

## Origin
AUM-MISSION-OPS-003 蒸馏。

## Purpose
解耦 TaskRouter 与具体 Provider 实现。

## Problem
TaskRouter 直接绑定 OneAPI，OneAPI 不可用时整个系统瘫痪。

## Core Structure
```
TaskRouter
  ↓
ProviderAdapter（抽象接口）
  ↓
具体 Provider（OneAPI / LocalMiner / OpenRouter / Ollama / GLM）
```

TaskRouter 只认识 Adapter，不认识具体 Provider。

## Constraint
- TaskRouter 不得直接调用 Provider HTTP
- Provider 切换不影响 TaskRouter
- Provider 切换不影响 Shadow Observer

## Evidence
- 2026-07-14 TaskRouter 修复：OneAPI 不可达时自动 fallback 到 local_miner
- 影子观察成功调用 4 个矿工

## Distillation
「中枢只认识接口，不认识实现」。

## Related Assets
- AR-007 Router Architecture
- PR-001 Drawer First
- CP-002 Worker Registry 动态生成

## Replaceable
可替换（Provider 实现可换）。

## Rebuildable
可重建。读「中枢认识接口」即可重建。
