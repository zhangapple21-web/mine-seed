# AUM-MISSION-EXP-001 — Shadow Audit Report

> **Mission ID**: AUM-MISSION-EXP-001
> **Role**: Shadow Observer (影子观察员)
> **Period**: 7天 (2026-07-14 至 2026-07-21)
> **Status**: 进行中

---

## 0. Mission 身份

| 项目 | 内容 |
|------|------|
| 身份 | Shadow Observer |
| 职责 | 对推荐进行多模型审计，输出Evidence，不参与决策 |
| 权限 | 只读，不写Repository，不写Runtime State |
| 存储 | `03_DATA/shadow_audit/`（独立目录） |
| 周期 | 7天 |
| 升级条件 | 3个问题，至少2个证据支持才能升级 |

---

## 1. 严格数据流分离

```
StockAdvisor (主流程)
    │
    ├──→ mine_output/advisor/advisor_YYYYMMDD.md  ← 主流程产物（只读）
    │                                                       │
    │                                                       │【只读，不修改】
    │                                                       ↓
    └──→ Shadow Observer (影子线) → 03_DATA/shadow_audit/   ← 影子产物
                                        ↓
                                   7天后汇总
                                        ↓
                              SHADOW_AUDIT_REPORT.md（本文件）
```

**主流程**：StockAdvisor → Policy Manager → Admission → Output（保持不变）
**影子线**：只读主流程产物 → 矿工审计 → 写入 03_DATA/shadow_audit/

---

## 2. 每日观察记录

### Day 1 (2026-07-14)

- **状态**: ✅ 影子观察员上线
- **观察对象**: 待记录
- **矿工池可用性**: 待记录
- **矿工共识分**: 待记录
- **影子 vs 主线 一致性**: 待记录

---

## 3. 7天汇总

待 7 天观察完成后填写。

---

## 4. 升级判断（7天后填写）

### 问题1：是否提供新信息？

- 证据1: 待记录
- 证据2: 待记录
- **判断**: 待记录

### 问题2：是否提高预测质量？

- 证据1: 待记录
- 证据2: 待记录
- **判断**: 待记录

### 问题3：关闭后是否明显下降？

- 证据1: 待记录
- 证据2: 待记录
- **判断**: 待记录

---

## 5. 退出机制

至少 2 个证据支持，才能升级进入正式决策链路。
否则实验结束，Miner 保持影子身份。

---

## 6. 严格边界（再次确认）

✅ DO:
- 读取主流程产物
- 调用矿工做多模型评估
- 写入 03_DATA/shadow_audit/

❌ DON'T:
- 接入 daily_runner.py 主流程
- 修改 StockAdvisor / Policy Manager / Admission
- 把矿工输出写入 audit_results.json
- 用矿工输出调整策略
- 让矿工调用影响主流程开关

---

**Mission 启动时间**: 2026-07-14
**Mission 负责人**: TRAE Agent
**下次更新**: 每日追加观察记录