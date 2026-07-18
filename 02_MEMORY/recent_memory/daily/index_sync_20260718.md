# Civilization Index Sync Report — 2026-07-18

> 扫描时间: 2026-07-18 06:53:20

---

## 缺失资产（3 个）

| ID | 名称 | 类别 | Source | 问题 |
|----|------|------|--------|------|
| E-001 | sandbox_reset_kills_cron | experience | `多次验证` | 文件不存在 |
| E-003 | adata_eastmoney_blocked | experience | `多次验证` | 文件不存在 |
| E-005 | github_pat_lacks_repo_scope | experience | `多次验证` | 文件不存在 |

## 新发现资产（47 个）

| 名称 | 类别 | Source | 大小 | 描述 |
|------|------|--------|------|------|
| tg_download_r1_files | blueprint | `05_TOOLS/miner/tg_download_r1_files.py` | 2.0KB | !/usr/bin/env python3 |
| discovery_scan | blueprint | `05_TOOLS/miner/discovery_scan.py` | 6.7KB | !/usr/bin/env python3 |
| civilization_index_sync | blueprint | `05_TOOLS/miner/civilization_index_sync.py` | 16.0KB | !/usr/bin/env python3 |
| tg_civilization_scanner | blueprint | `05_TOOLS/miner/tg_civilization_scanner.py` | 14.5KB | !/usr/bin/env python3 |
| civilization_daily | blueprint | `05_TOOLS/miner/civilization_daily.py` | 16.6KB | !/usr/bin/env python3 |
| signal_discovery | blueprint | `05_TOOLS/signals/signal_discovery.py` | 27.6KB | !/usr/bin/env python3 |
| README | blueprint | `04_PROTOCOLS/README.md` | 5.9KB | 04_PROTOCOLS - 协议层 |
| first_day | blueprint | `04_PROTOCOLS/first_day.md` | 5.3KB | First Day Protocol — 新 AI 第一天行动指南 |
| mission_protocol | blueprint | `04_PROTOCOLS/mission_protocol.py` | 22.0KB |  |
| environment_first | blueprint | `04_PROTOCOLS/environment_first.py` | 11.4KB | !/usr/bin/env python3 |
| ops_000_asset_first | blueprint | `04_PROTOCOLS/ops_000_asset_first.py` | 14.9KB | !/usr/bin/env python3 |
| repository | blueprint | `04_PROTOCOLS/repository.py` | 8.2KB |  |
| evidence_graph | blueprint | `04_PROTOCOLS/evidence_graph.py` | 40.8KB |  |
| RUNTIME_BOUNDARY | blueprint | `06_RUNTIME/RUNTIME_BOUNDARY.md` | 2.8KB | RUNTIME_BOUNDARY.md — Runtime 与 Civilization 职责边界 |
| tg_pusher | blueprint | `06_RUNTIME/connectors/tg_pusher.py` | 10.4KB | !/usr/bin/env python3 |
| fitness_tracker | constraint | `05_TOOLS/signals/fitness_tracker.py` | 3.7KB | !/usr/bin/env python3 |
| constraint_validator | constraint | `04_PROTOCOLS/constraint_validator.py` | 13.7KB |  |
| CONSTRAINT_LEDGER | constraint | `06_RUNTIME/CONSTRAINT_LEDGER.md` | 4.9KB | Constraint Ledger | 矿场v5 约束账本 |
| constraint_proposer | constraint | `06_RUNTIME/constraint_proposer.py` | 13.9KB | !/usr/bin/env python3 |
| constraint_injector | constraint | `06_RUNTIME/constraint_injector.py` | 4.5KB | !/usr/bin/env python3 |
| deploy_constraints | constraint | `06_RUNTIME/deploy_constraints.py` | 5.8KB | !/usr/bin/env python3 |
| sync_constraints | constraint | `06_RUNTIME/sync_constraints.py` | 4.2KB | !/usr/bin/env python3 |
| USER | constraint | `01_AGENTS/USER.md` | 0.8KB | 基本信息 |
| USER | constraint | `01_AGENTS/xiaofengzi/USER.md` | 0.8KB | 基本信息 |
| tasks | constraint | `01_AGENTS/xiaofengzi/research/tasks.md` | 5.3KB | 研究域任务清单 |
| task_router_v2 | experience | `05_TOOLS/miner/task_router_v2.py` | 21.2KB | !/usr/bin/env python3 |
| miner_cron | experience | `05_TOOLS/miner/miner_cron.sh` | 1.5KB | !/bin/bash |
| experience_engine | experience | `05_TOOLS/memory/experience_engine.py` | 36.8KB | !/usr/bin/env python3 |
| civilization_map | experience | `04_PROTOCOLS/civilization_map.py` | 12.0KB | !/usr/bin/env python3 |
| PROFILE | experience | `01_AGENTS/PROFILE.md` | 0.6KB | 小疯子（研究域） |
| PROFILE | experience | `01_AGENTS/xiaofengzi/PROFILE.md` | 0.6KB | 小疯子（研究域） |
| MANIFESTO | identity | `00_ROOT/MANIFESTO.md` | 2.1KB | 矿场宣言 — MANIFESTO.md |
| SOUL | identity | `01_AGENTS/SOUL.md` | 2.5KB |  |
| SOUL | identity | `01_AGENTS/xiaofengzi/SOUL.md` | 2.5KB |  |
| principles | identity | `01_AGENTS/xiaofengzi/research/principles.md` | 6.5KB | 研究域原则库（Principles） |
| SOUL | identity | `01_AGENTS/fengzi/SOUL.md` | 4.4KB |  |
| task_router | kernel | `05_TOOLS/miner/task_router.py` | 39.6KB | !/usr/bin/env python3 |
| model_router | kernel | `05_TOOLS/miner/model_router.py` | 10.7KB | !/usr/bin/env python3 |
| GOVERNANCE | protocol | `00_ROOT/GOVERNANCE.md` | 1.3KB | Governance v1 |
| CONTRACT | protocol | `04_PROTOCOLS/CONTRACT.md` | 6.4KB | CONTRACT-001: Runtime-Civilization Interface Contr |
| recovery_protocol | protocol | `04_PROTOCOLS/recovery_protocol.py` | 11.0KB | !/usr/bin/env python3 |
| civilization_contract | protocol | `04_PROTOCOLS/civilization_contract.py` | 13.7KB |  |
| RECOVERY_CHECKLIST | protocol | `06_RUNTIME/RECOVERY_CHECKLIST.md` | 3.6KB | 恢复检查清单 |
| CRONTAB | protocol | `06_RUNTIME/CRONTAB.md` | 1.8KB | CRONTAB 配置说明 |
| RECOVERY_PLAN | protocol | `06_RUNTIME/RECOVERY_PLAN.md` | 4.7KB | RECOVERY_PLAN.md — 恢复验证计划 |
| PROTOCOLS | protocol | `01_AGENTS/PROTOCOLS.md` | 0.9KB | 双Agent协作协议 |
| PROTOCOLS | protocol | `01_AGENTS/xiaofengzi/PROTOCOLS.md` | 0.9KB | 双Agent协作协议 |

## 分类统计

- **kernel**: 2 个
- **blueprint**: 15 个
- **protocol**: 9 个
- **constraint**: 10 个
- **experience**: 6 个
- **identity**: 5 个

---

*本报告由 Civilization Index Sync 自动生成。*