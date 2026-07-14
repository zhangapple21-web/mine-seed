# CP-002 Worker Registry 动态生成（工人注册动态生成）

## Name
CP-002 — Worker Registry 动态生成

## Origin
AUM-MISSION-OPS-003 修复：Registry 不应是静态 JSON。

## Purpose
Registry 应是「能力快照」，不是「死人名单」。

## Problem
静态 Registry 维护成本高，新增 Provider 时容易遗漏。

## Core Structure
启动时动态生成：
```
启动
  ↓
扫描环境变量（GITHUB_PAT / ZHIPU_KEY / OPENROUTER_KEY）
  ↓
Probe（调用 /v1/models）
  ↓
生成 worker 配置
  ↓
写 Cache（worker_registry.json）
```

Registry 启动时为空 → 自动触发生成。

## Constraint
- Registry 不得手工维护
- 新增 Provider 时自动出现
- Registry 是「当前可用工人」快照

## Evidence
- 2026-07-14 WorkerRegistry 启动时从空生成 4 个 worker
- 自动注册 GLM / GitHub / Ollama / OpenRouter

## Distillation
「Registry 是能力快照，不是静态配置」。

## Related Assets
- CP-001 Provider Adapter
- GV-001 Admission Engine

## Replaceable
可替换（生成方式可调）。

## Rebuildable
可重建。读「启动时扫描+Probe」即可重建。
