# Artifact Inventory — 2026-07-15

> **只统计，不改。识别重复，标记待统一项。**

---

## 统计概览

| Artifact 类型 | 文件数 | 主要位置 | 重复/碎片问题 |
|---------------|--------|----------|---------------|
| Protocol | 84 | 04_PROTOCOLS/ | 部分概念重叠 |
| ADR | 1 | 根目录 | 无 |
| Constraint | 7+ | 03_DATA/CONSTRAINTS/, 02_miner_config/ | ⚠️ Schema 重复 |
| Evidence | 9 | 02_MEMORY/evidence/ | 无 |
| Decision | 2 | 02_MEMORY/recent_memory/admission/ | 无 |
| Replay | 6 | 02_MEMORY/evidence/replay/ + replay.py | 无 |
| Roundtable | 2 | 02_MEMORY/roundtable_rfc.json + roundtable.py | 无 |
| Migration | 4 | 多处 | ⚠️ 文件重复 |
| Mission | 7 | 03_DATA/MISSIONS/ | 无 |

---

## 详细分析

### Protocol (84 个)

**Python 引擎**: 70 个 .py 文件
- 核心引擎: `law_discovery.py`, `admission_engine.py`, `roundtable.py`, `replay.py`
- 运维协议: `ops_000_asset_first.py` ~ `ops_005_self_loop.py`
- 辅助工具: `test_*.py`, `register_*.py`

**Markdown 文档**: 14 个 .md 文件
- 治理文档: `governance_state_machine.md`, `governance_dry_run.md`
- 验证报告: `E2C_BOUNDARY_VERIFICATION.md`, `REPLAY_REPORT.md`
- 设计文档: `LAW_WEAKENING_DESIGN.md`, `PUBLICATION_PRINCIPLE.md`

**观察**: Protocol 层文件数量庞大，部分功能可能重叠（如 `repository.py` / `repository_manager.py` / `repository_store.py`）。

---

### Constraint (7+ 个)

| 文件 | 位置 | 说明 |
|------|------|------|
| C-025-law-discovery.md | 02_MEMORY/assets/constraint/ | 约束资产 |
| CONSTRAINT_LEDGER.md | 03_DATA/CONSTRAINTS/ | 约束总账 |
| routing_constraints.json | 03_DATA/CONSTRAINTS/ | ⚠️ 与 02_miner_config/ 重复 |
| signal_registry.json | 03_DATA/CONSTRAINTS/ | ⚠️ 与 02_miner_config/ 重复 |
| signal_taxonomy.json | 03_DATA/CONSTRAINTS/ | 信号分类 |
| routing_constraints.json | 02_miner_config/ | ⚠️ 与 03_DATA/CONSTRAINTS/ 重复 |
| signal_registry.json | 02_miner_config/ | ⚠️ 与 03_DATA/CONSTRAINTS/ 重复 |

**Schema 重复**: `routing_constraints.json` 和 `signal_registry.json` 在两个目录中同时存在。

---

### Evidence (9 个)

| 文件 | 位置 | 说明 |
|------|------|------|
| evidence_index.json | 02_MEMORY/evidence/ | 证据索引 |
| evidence_20260714.jsonl | 02_MEMORY/evidence/ | 证据日志 |
| evidence_20260715_external.jsonl | 02_MEMORY/evidence/ | 外部证据 |
| evidence_20260715_external_v2.jsonl | 02_MEMORY/evidence/ | 外部证据 v2 |
| replay_sig_candidate_*.json (x5) | 02_MEMORY/evidence/replay/ | 回放验证结果 |

**状态**: 结构统一（jsonl append-only），无重复问题。

---

### Decision (2 个)

| 文件 | 位置 | 状态 |
|------|------|------|
| admission_20260715_C028.md | 02_MEMORY/recent_memory/admission/ | Pending |
| admission_20260715_C029.md | 02_MEMORY/recent_memory/admission/ | Pending |

**观察**: 当前只有 Admission Record，无独立的 Governor Decision 文件。Decision 嵌入在 Record 中。

---

### Migration (4 个)

| 文件 | 位置 |
|------|------|
| data_source_migration_plan.md | r1_archaeology/ |
| data_source_migration_plan.md | 02_MEMORY/recent_memory/research/ |
| data_source_migration_plan.md | research/ |
| data_source_migration_plan.md | recent_memory/research/ |

**问题**: 同一文件在 4 个位置存在，内容可能相同或不同步。

---

### Mission (7 个)

| 文件 | 类型 |
|------|------|
| AUM-MISSION-ARCH-003.json | Architecture |
| AUM-MISSION-ARCH-004.json | Architecture |
| AUM-MISSION-ARCH-006.json | Architecture |
| AUM-MISSION-OPS-005.json | Operations |
| AUM-MISSION-RES-001.json | Research |
| AUM-MISSION-RES-002.json | Research |
| AUM-MISSION-RES-007.json | Research |

---

## 重复 Schema 清单

| Schema | 重复位置 | 建议 |
|--------|----------|------|
| routing_constraints.json | 03_DATA/CONSTRAINTS/ + 02_miner_config/ | 统一为单一源 |
| signal_registry.json | 03_DATA/CONSTRAINTS/ + 02_miner_config/ | 统一为单一源 |
| worker_registry.json | 03_DATA/WORKERS/ + 02_miner_config/ | 统一为单一源 |
| data_source_migration_plan.md | 4 个位置 | 保留唯一源，其余改为链接 |

---

## 天然同类项

以下 Artifact 已经共享相似的 Schema 或语义，未来统一时优先合并：

1. **Admission + Roundtable + Replay** — 均为治理证据，共享 `timestamp`, `status`, `evidence_ids` 字段
2. **Constraint + Policy** — 均定义系统边界，Constraint 是禁止，Policy 是允许
3. **Mission + Protocol** — Mission 是"做什么"，Protocol 是"怎么做"，边界需明确

---

## 今日结论

- **不改任何东西**
- **识别了 4 组重复 Schema**
- **识别了 3 组天然同类项**
- **等待 Governance Kernel 验证通过后，再进入 Artifact 统一阶段**

---

*Inventory only. No migration. Frozen until Governor Decision.*
