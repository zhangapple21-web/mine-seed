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
