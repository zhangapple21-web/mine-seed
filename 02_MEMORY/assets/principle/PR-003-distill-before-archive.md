# PR-003 Distill Before Archive（蒸馏优先原则）

## Name
PR-003 — Distill Before Archive

## Origin
用户偏好「文件须经压缩、审视、圆桌讨论后才能上传」。

## Purpose
确保文明资产是「蒸馏后」的事实，不是原始数据。

## Problem
原始数据（聊天、源码、报告）直接上传会造成仓库膨胀与噪声。

## Core Structure
蒸馏流程：
```
原始素材
  ↓
压缩（提取关键事实 / 数字 / 结论）
  ↓
抽象（提炼为原则 / 公理 / 协议）
  ↓
结构化（按模板写为 Asset）
  ↓
索引（写入 ASSET_INDEX）
```

## Constraint
- 禁止「聊天记录当文明资产」
- 禁止「复制源码代替蒸馏」
- 禁止「未压缩直接入仓」

## Evidence
- 28+ 已蒸馏的 civilization_assets 文档（2026-07-14）
- MissionReport.md 经多次压缩后才入仓

## Distillation
「不蒸馏的素材是噪声，不是资产」。

## Related Assets
- PR-001 Drawer First
- AR-002 Asset Template
- GV-001 Admission Engine

## Replaceable
可替换（蒸馏流程可调）。

## Rebuildable
可重建。读「不蒸馏就是噪声」即可重建。
