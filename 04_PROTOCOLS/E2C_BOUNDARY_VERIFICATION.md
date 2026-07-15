# E→C Boundary Verification — 板块四' 验证

> 创建时间: 2026-07-15
> 验证方法: 抽屉扫描 + Capability Mapping
> 结论: **e2c_closure 现有实现已满足板块四'全部要求**

## 1. Capability Mapping 验证表

| 板块四' 要求 | e2c_closure 现状 | 状态 |
|--------------|------------------|------|
| 禁止重复实现 AdaptiveScorer | 完全独立，无任何 import adaptive_scorer | ✅ |
| 明确 AdaptiveScorer 边界 | 作用域 scope='scheduler/routing/fallback'，不涉及 'scoring' | ✅ |
| 失败自动生成约束 | Observation→ConstraintEntry 自动转换 | ✅ |
| 冷却机制替代硬删 | CoolingManager.is_in_cooling 完整实现 | ✅ |
| 调度前置检查 | check_pre_schedule / apply_constraints 已实现 | ✅ |

## 2. 边界规则（验证）

| 模块 | 层级 | 不允许做的 |
|------|------|----------|
| AdaptiveScorer | 评分层 | ❌ 修改约束 |
| e2c_closure | 调度层 | ❌ 修改因子权重 |
| LawRegistry | 治理层 | ❌ 直接调 Runtime |

**验证方法**：grep 搜索跨层引用，结果为 0。

## 3. 复用决策

| 决策 | 内容 |
|------|------|
| ✅ 复用 | `04_PROTOCOLS/e2c_closure.py` 全部已实现 |
| ❌ 不新建 | E2C 框架/约束生成/冷却/调度前置 |
| 📝 补文档 | 本文件 + Capability Mapping 已在 GOAL_VALIDATION.md |

## 4. 联动关系（避免双重学习）

```
AdaptiveScorer (评分层)    E2C (调度层)    LawRegistry (治理层)
       │                       │                  │
       │ 降权 1 个因子         │ AVOID 调度某 worker │  升级 law status
       │                       │                  │
       └─────── 通知 ─────────→│                  │
                               │                  │
                               └───── W-005 触发 ─→│  Weakening 评估
```

**避免双重学习的关键**：
- AdaptiveScorer 调权后，E2C 不再针对该 target 生成 AVOID
- E2C AVOID 触发后，AdaptiveScorer 不再对该 target 调权
- 两者由 evidence_coupling 联动（写入 audit_evidence.json）

## 5. Acceptance

- [x] e2c_closure 完整实现已存在
- [x] 与 AdaptiveScorer 边界清晰（grep 验证）
- [x] 不需要重复实现
- [x] Capability Mapping 文档化
- [ ] audit_evidence.json 联动文件**尚未实现**（联动仅在文档中声明）

## 6. 下游

- 等 audit_evidence.json 联动文件实现后，E2C 与 AdaptiveScorer 才能真正去重
- 当前 P1 任务边界已完成
