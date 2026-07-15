# AUM-MISSION-DATA-001 — Knowledge Shift 数据源恢复（Candidate）

> **状态**: CANDIDATE — Waiting Review After Audit
> **优先级**: P0 (Production Blocker) — 但在审核后执行
> **创建时间**: 2026-07-15

---

## 背景

Baostock 已无法稳定使用，AkShare 亦受到反爬限制，导致 Knowledge Shift 连续多个班次无法正常产出。

这是生产环境阻断事件，不属于架构优化，而属于生产恢复任务。

---

## Mission

恢复 Knowledge Shift 数据流水线，并完成数据源抽象，为未来 Provider 切换建立统一接口。

---

## Scope

**仅涉及**:
- Observation Layer
- MarketData Provider
- Knowledge Shift

**不修改**:
- Evidence Layer
- Roundtable
- Replay
- Governance

---

## Deliverables

| ID | 名称 | 优先级 |
|----|------|--------|
| D1 | Provider Adapter | P0 |
| D2 | Mootdx Provider | P0 |
| D3 | normalize_dataframe | P0 |
| D4 | Provider Health Check | P0 |
| D5 | Provider Observation | P0 |

---

## Validation

| ID | 验证项 | 必须提交 |
|----|--------|----------|
| V1 | 成交量单位 | comparison.csv |
| V2 | 市场编码 | Market Mapping Table |
| V3 | 日期格式 | 统一 YYYY-MM-DD |

---

## Architecture Constraints

1. 业务层不得依赖具体 Provider
2. Provider 输出必须经过 normalize_dataframe()
3. Provider 不得直接修改 Evidence/Replay/Roundtable
4. Knowledge Shift 面向 MarketDataProvider 接口
5. 任何单位转换必须具有验证 Evidence

---

## Acceptance Criteria

- ✅ Knowledge Shift 正常恢复
- ✅ 600519、000001 全流程运行
- ✅ Provider 可切换，业务代码零修改
- ✅ Health Check 输出 HEALTHY/DEGRADED
- ✅ Volume 单位具有验证 Evidence

---

## Non-Goals

- ❌ Tick 数据
- ❌ Level2
- ❌ 北交所专项支持
- ❌ 高频优化
- ❌ 数据缓存重构
- ❌ Replay 重构

---

## Evidence Required

- Provider Comparison Report
- Market Mapping Table
- Volume Validation
- Health Check Report
- Knowledge Shift Recovery Log

---

## Distillation

**Kernel**: Business depends on capability, not implementation.

**Blueprint**:
```
Knowledge Shift
        │
        ▼
MarketDataProvider
        │
 ┌──────┼─────────┐
 ▼      ▼         ▼
Baostock Mootdx AKShare
```

**Protocol**:
```
Provider → normalize_dataframe → Observation → Knowledge Shift
```

**Constraint**:
- Provider 可替换
- Output 必须标准化
- Evidence First
- Observation Before Production

**Experience**: 真正需要高可用的不是某一个数据源，而是数据获取能力本身。

**Identity**: ACE 不绑定任何单一 Provider，而是维护一层可验证、可观测、可替换的数据获取能力。

---

## Timeline

- **创建**: 2026-07-15
- **状态**: CANDIDATE
- **复审时间**: 审核通过后（约 2026-08-05）

---

*This is a Mission Candidate. No execution until Governor Decision on C-028/C-029 and Audit completion.*