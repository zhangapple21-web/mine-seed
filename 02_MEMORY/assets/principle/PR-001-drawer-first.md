# PR-001 Drawer First Protocol（抽屉优先原则）

## Name
PR-001 — Drawer First Protocol

## Origin
OPS-001 / OPS-002 蒸馏合并。

## Purpose
确保任何动作前先翻 6 层抽屉，避免重复造轮子。

## Problem
经常在「已经有现成资产」时新增功能，造成冗余与冲突。

## Core Structure
6 层抽屉（按数据新鲜度排序）：
1. **Layer 0 — Runtime**（运行态，最新）
2. **Layer 1 — Workspace**（本地文件）
3. **Layer 2 — GitHub**（文明地图）
4. **Layer 3 — Telegram**（收藏夹）
5. **Layer 4 — Archive**（ZIP / Snapshot）
6. **Layer 5 — Internet**（最后手段）

## Constraint
- Internet 是最后手段，不是第一手段
- Runtime 永远比 GitHub 新
- GitHub 永远比 TG 新
- 若仓库已有设计，不得重做

## Evidence
- 荐股定时任务修复中，发现已有 heartbeat.py 可用作补偿机制
- TaskRouter 修复中，发现 local_miner.py 已有完整 Provider 实现

## Distillation
「先翻抽屉，再造轮子」。

## Related Assets
- PR-002 Asset Before Action
- PR-003 Find Before Build
- PR-004 Recovery First

## Replaceable
可替换（抽屉分层方式可调整）。

## Rebuildable
可重建。读「Internet 是最后手段」即可重建。
