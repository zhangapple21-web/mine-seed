# Constraint Ledger | 矿场v5 约束账本

**日期**: 2026-06-20
**版本**: v3.0-deployed
**状态**: 🟢 **v5 Monkey Patch已部署** — 9 AVOID + 1 PREFER 运行时注入miner_24h.py

## 部署历史

| 版本 | 策略 | 结果 |
|---|---|---|
| v1 | 写routing_constraints.json | PermissionError (root创建) |
| v2 | 在miner_24h.py找return best_worker | 函数不存在 |
| v3 | 自动检测return语句 | 基于错误假设，未执行 |
| v4 | task_router.py加装饰器 | PermissionError (root创建) |
| **v5** | **Monkey Patch miner_24h.py** | **✅ 部署成功 (15:18)** |

## v5部署详情

- **策略**: 在miner_24h.py的`from task_router import ...`行之后插入monkey patch代码
- **注入方式**: `router.get_fallback_chain = types.MethodType(_constrained_get_fallback_chain, router)`
- **备份**: `/home/coze/miner_24h.py.bak_v5`
- **验证命令**: `grep CONSTRAINT /home/coze/mine_output/cron.log`
- **回滚**: `cp /home/coze/miner_24h.py.bak_v5 /home/coze/miner_24h.py`

## 约束列表

| ID | Constraint | Source | Owner | Status |
|---|---|---|---|---|
| RC-001 | *→gh_r1 AVOID | manual | 疯子 | ✅ ACTIVE |
| RC-002 | *→nim_ultra_550b AVOID | manual | 疯子 | ✅ ACTIVE |
| RC-003 | *→gh_4o AVOID | manual | 疯子 | ✅ ACTIVE |
| RC-004 | persona_deep→nim_mistral_675b AVOID | manual | 疯子 | ✅ ACTIVE |
| RC-005 | canonical_v2→gh_r1 AVOID | manual | 疯子 | ✅ ACTIVE |
| RC-006 | canonical_v2→nim_ultra_550b AVOID | manual | 疯子 | ✅ ACTIVE |
| RC-007 | persona_deep→nim_ultra_550b AVOID | manual | 疯子 | ✅ ACTIVE |
| RC-014 | signal_mean_reversion→glm_4_flash AVOID | auto_oec | auto | ✅ ACTIVE |
| RC-015 | signal_volume_price_divergence→glm_4_flash AVOID | auto_oec | auto | ✅ ACTIVE |
| RC-016 | signal_mean_reversion→nim_deepseek PREFER | auto_oec | auto | ✅ ACTIVE |
| RC-008 | slice_mining→? AVOID | manual/auto | 待确认 | 📝 TEXT_ONLY |
| RC-009 | routing_analysis→? AVOID | manual/auto | 待确认 | 📝 TEXT_ONLY |
| RC-010 | shadow_analysis→? AVOID(3条) | manual/auto | 待确认 | 📝 TEXT_ONLY |
| RC-011 | signal_mean_reversion→? AVOID | manual | 待确认 | 📝 TEXT_ONLY |
| RC-012 | slice_classification→? AVOID | manual | 待确认 | 📝 TEXT_ONLY |
| RC-013 | signal_volume_price_divergence→? AVOID | manual | 待确认 | 📝 TEXT_ONLY |
| RC-017 | 待确认 | ? | ? | 📝 TEXT_ONLY |
| RC-018 | 待确认 | ? | ? | 📝 TEXT_ONLY |

## 约束代码化状态

| 状态 | 含义 |
|---|---|
| 📝 TEXT_ONLY | 仅存在于文档，无代码读取 |
| ⚙️ CODED | 已写入代码/配置，未被生产调用 |
| ✅ ACTIVE | 在生产中被代码读取并执行 |

## 待办

- [x] 部署约束代码化 (v5 Monkey Patch)
- [ ] **20:00班次后验证cron.log出现[CONSTRAINT]日志** ← 下一步
- [ ] 确认8条pending约束的target worker
- [ ] 反永久化规则：7天后review AVOID约束成功率

---

## 流程约束 (Process Constraints)

> 由 Admission Engine / Mission Distillation 沉淀的流程类约束，非路由约束。

| ID | Constraint | Source | Status |
|---|---|---|---|
| C-019 | 审计链路禁止绕过压缩机制直接生效：下游消费者禁止直接读 audit_results.json，必须通过 ExperienceEngine.get_audit_compression_latest() 获取审计摘要 | AUM-MISSION-ARCH-013 子任务1 | ✅ ACTIVE |

**C-019 判据**:
- ✅ 合规：调用 `ExperienceEngine.get_audit_compression_latest()` 获取审计摘要
- ❌ 违规：直接 `json.load(open(audit_results.json))` 用于决策

**C-019 例外**:
- 审计模块自身（post_recommendation_auditor.py）读写原始文件属于正常操作
- 压缩模块自身（experience_engine.compress_audit_results）读原始文件属于正常操作
- 仅"下游消费者"受此约束限制

详见：[arch013_distillation_20260713.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_audit/arch013_distillation_20260713.md)

---

## 范围约束 (Scope Constraints)

| ID | Constraint | Source | Status |
|---|---|---|---|
| C-020 | FA模式（Full Access Mode）仅限内部推理层，不得用于任何直接触发真实动作的路径（推送给用户的最终输出、交易相关动作、触发通知/推送等） | AUM-MISSION-ARCH-014 子任务1 | ✅ ACTIVE |

**C-020 适用范围**:

| ✅ 适用 | ❌ 不适用 |
|---------|----------|
| Ollama 本地模型的推理过程 | 任何直接触发真实动作的路径 |
| 矿工对推荐质量的内部评估 | 推送给用户的最终输出 |
| 红蓝对抗中的推理环节 | 交易相关动作 |
| 经验压缩的模式提取 | 触发通知/推送 |

**C-020 执行机制**:
- smelter_gate 强制标记所有 FA 模式产出
- 日志可追溯，便于审计
- 违反此约束的代码不允许通过 Admission Engine 审批

详见：[arch014_distillation_20260713.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_audit/arch014_distillation_20260713.md)
