# CP-005 T+N Multi-Period Feedback（T+N 多周期反馈）

## Name
CP-005 — T+N Multi-Period Feedback

## Origin
P0 修复（用户诊断 T+5 死循环）。

## Purpose
打破「没 T+5 → 不调整 → 没 T+5」死循环。

## Problem
原 performance_tracker.get_factor_effectiveness() 只看 T+5，导致长期无数据无调整。

## Core Structure
多周期支持：
```python
def get_factor_effectiveness(period="T+5"):
    return_field = "return_t1" if period == "T+1" else "return_t5"
    min_samples = 2 if period == "T+1" else 3
```

优先级：T+1 → T+3 → T+5 → T+10。

## Constraint
- T+1 样本阈值 2
- T+5 样本阈值 3
- 自适应：哪个周期先到样本量用哪个

## Evidence
- 2026-07-14 策略从 POLICY-001 升级到 POLICY-002（基于 T+1 证据）
- T+1 反馈跑通，策略进入自动调整

## Distillation
「反馈不应被时间卡死」。

## Related Assets
- CP-006 Adaptive Scorer
- GV-001 Admission Engine

## Replaceable
可替换（周期组合可调）。

## Rebuildable
可重建。读「T+1 优先 + 样本阈值自适应」即可重建。
