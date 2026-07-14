# CP-004 Smelter Gate（熔炼门）

## Name
CP-004 — Smelter Gate

## Origin
ARCH-014（用户发现 Gate 永远 passed: True）。

## Purpose
真实拦截风险内容，不是仅记录。

## Problem
原 smelter_gate.pass_through() 只记录不拒绝，名为 Gate 实为日志。

## Core Structure
5 个拒绝条件：
1. 来源异常（untrusted_source）
2. 操纵性表述（manipulative_language）
3. 反馈过短（feedback_too_short）
4. 评分极端 + 反馈不匹配（score_feedback_mismatch）
5. 评分偏差（score_deviation）

```python
result = gate.pass_through(content, context)
if not result["passed"]:
    return {"audit_status": "rejected", "reject_reason": result["reason"]}
```

## Constraint
- 单纯评分极端只标记不拒绝
- 必须有反馈不匹配时才拒绝
- 必须有真实拒绝分支（不能总 passed: True）

## Evidence
- 14 个单元测试全部通过
- 异常测试用例正确触发拒绝

## Distillation
「Gate 必须真有拒绝能力」。

## Related Assets
- C-019 Compression Gate
- GV-001 Admission Engine

## Replaceable
可替换（拒绝条件可调）。

## Rebuildable
可重建。读「Gate 必须真有拒绝」即可重建。
