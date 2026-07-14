# RL-002 Blue Team Defense（蓝队防御）

## Name
RL-002 — Blue Team Defense

## Origin
GV-003 红蓝圆桌（5 问结构化防御）。

## Purpose
替代「简单支持」的盲点。

## Problem
传统蓝队只说「支持」，无证据、无回滚、无副作用分析。

## Core Structure
结构化 Defense Case，5 问必答：

```
1. Validity（有效性）— 这个提案在逻辑上成立吗？
2. Evidence（证据）— 有哪些数据/历史/先例支持？
3. History（历史）— 类似情况在过去如何演化？
4. Rollback（回滚）— 如果失败，如何回滚？回滚成本？
5. Side Effects（副作用）— 二阶效应？边界情况？长期影响？
```

## Constraint
- 不得只回答「支持」而不答 5 问
- 每问必须给出可验证的回答
- 任何「我看不到风险」的回答视为未防御

## Evidence
- ARCH-014 修复中蓝队成功识别「Gate 仅记录不拒绝」漏洞
- T+5 死循环诊断中蓝队要求先答 T+1 备选

## Distillation
「结构化防御胜过直觉支持」。

## Related Assets
- RL-001 Red Team Roles
- GV-003 Red-Blue Round Table

## Replaceable
不可替换（5 问是硬约束）。

## Rebuildable
可重建。读「5 问结构化」即可重建。
