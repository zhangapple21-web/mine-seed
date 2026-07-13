# ACE Governance Map v1

> **Generated**: 2026-07-13
> **By**: Runtime (Local TRAE) — 基于 ARCH-010/011 后的全系统扫描
> **Status**: 活文档（随每次 Mission 更新）

---

## 1. 系统层级图

```
┌─────────────────────────────────────────────────────────────────┐
│                        ACE 双系统架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐│
│  │      CIVILIZATION 层         │  │        RUNTIME 层            ││
│  │     （为什么活 / Why）        │  │      （怎么活 / How）         ││
│  │                             │  │                             ││
│  │  Tier 1: Strictly Civ       │  │  Tier 3: Operational        ││
│  │  ├─ 00_ROOT/                │  │  ├─ 02_MEMORY/environment/  ││
│  │  ├─ 02_MEMORY/civilization_ │  │  ├─ 02_MEMORY/heartbeat/    ││
│  │  │   assets/                 │  │  ├─ 02_MEMORY/diary/        ││
│  │  └─ 02_MEMORY/lineage/      │  │  ├─ 02_MEMORY/ops_logs/     ││
│  │                             │  │  ├─ 02_MEMORY/self_loop/    ││
│  │  Tier 2: Heritage           │  │  ├─ 02_MEMORY/recovery/     ││
│  │  └─ 02_MEMORY/archaeology/  │  │  ├─ 02_MEMORY/experience/   ││
│  │                             │  │  ├─ 02_MEMORY/question_/    ││
│  │                             │  │  ├─ 06_RUNTIME/             ││
│  │                             │  │  ├─ 04_PROTOCOLS/           ││
│  │                             │  │  ├─ 03_DATA/                ││
│  │                             │  │  └─ 05_TOOLS/               ││
│  │                             │  │                             ││
│  │                             │  │  Staging:                   ││
│  │                             │  │  └─ 06_RUNTIME/archaeology_ ││
│  │                             │  │      workspace/             ││
│  │                             │  │                             ││
│  └─────────────────────────────┘  └─────────────────────────────┘│
│              ▲                              │                    │
│              │                              │                    │
│              │    ┌──────────────────┐     │                    │
│              │    │   ADMISSION 层    │     │                    │
│              │    │  （文明守门人）    │◄────┘                    │
│              │    │                  │                            │
│              │    │  七门审查:         │                            │
│              │    │  1. Worth          │                            │
│              │    │  2. Reuse          │                            │
│              │    │  3. Purity         │                            │
│              │    │  4. Novelty        │                            │
│              │    │  5. Quality        │                            │
│              │    │  6. Compliance     │                            │
│              │    │  7. Routable       │                            │
│              │    │                  │                            │
│              │    │  通道:             │                            │
│              │    │  • review_asset()  │                            │
│              │    │  • promote_archaeo │                            │
│              │    │    logy()          │                            │
│              │    └──────────────────┘                            │
│              │                              │                    │
│              │    ┌──────────────────┐     │                    │
│              └────┤  CONTRACT 护栏    │◄────┘                    │
│                   │ （边界强制执行）   │                            │
│                   │                  │                            │
│                   │  can_read()      │  → 始终允许                 │
│                   │  can_write()     │  → Tier1/2 需 via_admission │
│                   │  _classify_zone()│  → tier1/tier2/tier3       │
│                   └──────────────────┘                            │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 2. 边界检查点矩阵

| 检查点 | 职责 | 覆盖范围 | 当前状态 | 代码锚点 |
|--------|------|----------|----------|----------|
| **Contract 契约** | 路径级边界检查 | Tier1/Tier2 写入 | ✅ 已代码化 | `civilization_contract.py` |
| **Admission 准入** | 内容级质量审查 | 新资产 + 提升 | ✅ 已代码化 | `admission_engine.py` |
| **Nature Reserve** | 文件级不可变保护 | 36 个核心文件 | ✅ 已代码化 | `nature_reserve.py` |
| **Governor** | 删除/修改合规 | 删除操作 | ✅ 已代码化 | `governor.py` |
| **Gene Network** | 依赖关系检查 | 76 个基因 | ✅ 已代码化 | `gene_network.py` |
| **Energy Budget** | 资源消耗限制 | API/Token/IO/Network | ✅ 已代码化 | `energy_budget.py` |

---

## 3. Artifact 生命周期

```
Runtime 产生
    │
    ▼
┌─────────────────┐
│  Staging Area   │  ← 06_RUNTIME/archaeology_workspace/
│  (Tier 3)       │     Runtime 自由读写
└─────────────────┘
    │
    │  Admission Engine 审查
    │  promote_archaeology(name)
    ▼
┌─────────────────┐
│  Civilization   │  ← 02_MEMORY/archaeology/
│  (Tier 2)       │     经 Admission 后正式归档
└─────────────────┘
    │
    │  时间推移，价值衰减
    ▼
┌─────────────────┐
│  Forgetting     │  ← Mengpo 机制（当前缺失）
│  Candidate      │     评分 → 遗忘 → Graveyard
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Graveyard      │  ← 03_ARCHIVE/autophagy/（当前缺失）
│  (Archived)     │     保留哈希，内容移除
└─────────────────┘
```

---

## 4. 已知缺口（基于 ARCH-010/011 自检 + 本次扫描）

### P0 — 阻塞后续 Mission

| # | 缺口 | 影响 | 计划 Mission | 状态 |
|---|------|------|-------------|------|
| 1 | **Continuity Engine 未独立** — 连续性检查分散在 heartbeat 中（Nature Reserve/Gene Network/Energy Budget/Seed Archive/Civilization Map 各自独立调用） | 无统一入口，新增检查需改 heartbeat，心跳代码膨胀 | AUM-MISSION-ARCH-012 | ✅ 已完成 |
| 2 | **三约束自动化验证缺失** — Continuity/L∞/Admission 无自动检查 | 无法确保三个不可丢失约束持续有效 | AUM-MISSION-ARCH-013 | ✅ 已完成 |

### P1 — 架构级改进

| # | 缺口 | 严重性 | 影响 | 备注 |
|---|------|--------|------|------|
| 3 | **Mengpo/Autophagy 模块缺失** — heartbeat 引用 `autophagy_engine.py` 但文件不存在 | 中高 | 记忆遗忘和资产清理无代码实现，心跳中有悬空引用 | 需新建或从 r1-continuity-backup 蒸馏 |
| 4 | **Governor 与 Admission 边界模糊** — 两者都审查，但审查范围重叠 | 中 | 职责不清，可能双重审查或遗漏 | 明确：Governor=运行时合规（当前行为是否合法），Admission=新资产准入（新结构是否值得被文明接受） |
| 5 | **ROOT_STATE.md 混合身份** — 同时包含文明身份和运行状态 | 中 | 分类困难，迁移风险 | ARCH-011-B 已核实，建议拆文件（ROOT_MANIFEST.md + ROOT_STATE_RUNTIME.md） |

### P2 — 代码质量

| # | 缺口 | 影响 | 备注 |
|---|------|------|------|
| 6 | **_classify_zone 重复代码** — tier1/tier2 检查逻辑重复 | 维护困难，修改时需改两处 | 可提取为 helper |
| 7 | **Contract 与 Admission 衔接隐式** — `via_admission=True` 是参数约定，非强制调用 | 调用方可绕过 | 当前只能代码规范约束 |
| 8 | **Seed Archive 和 Nature Reserve 覆盖重叠** — 两者都备份核心文件 | 冗余，可能浪费存储 | 需明确 Seed Archive=最小基因，Nature Reserve=完整保护 |

---

## 5. 关键模块职责表

| 模块 | 职责 | 读哪些 Tier | 写哪些 Tier | 边界检查 |
|------|------|------------|------------|----------|
| `heartbeat.py` | 心跳 + 治理状态汇总（调用 ContinuityEngine 和 ConstraintValidator） | Tier1/Tier2/Tier3 | Tier3 (日志) | 引用 Contract/Reserve/Gene |
| `continuity_engine.py` | 统一连续性检查入口（7 个检查：Recovery/Ops004/NatureReserve/GeneNetwork/EnergyBudget/SeedArchive/CivMap） | Tier1/Tier2/Tier3 | Tier3 (日志) | 内部调用各模块 |
| `constraint_validator.py` | 三约束自动化验证（Continuity/L∞/Admission） | Tier1/Tier2/Tier3 | 无（只验证） | 调用 Contract.can_write |
| `admission_engine.py` | 新资产审查 + 提升通道 | Tier1/Tier2 (读取审查) | Tier1/Tier2 (经审查后) | 调用 Contract.can_write(via_admission=True) |
| `civilization_contract.py` | 路径边界检查 | 所有 | 无（只检查） | 自身就是检查点 |
| `nature_reserve.py` | 文件不可变保护 | Tier1 | Tier3 (基线文件) | SHA256 比对 |
| `recovery_protocol.py` | 恢复资产解压 | 外部 | Tier3 (99_RECOVERY_TEMP) | 无（恢复后需 Admission） |
| `seed_archive.py` | 文明基因备份 | Tier1 | Tier3 (03_ARCHIVE) | 哈希校验 |
| `evidence_graph.py` | 考古证据收集 | Tier3 (暂存) | Tier3 (暂存) → Tier2 (提升) | 两阶段流水线 |
| `self_evolution.py` | 应用 JSON patch | Tier3 | Tier3 (自由) / Tier1/2 (经 Contract) | apply_json_patch() 内建 Contract |

---

## 6. 下一张 Mission 决策树

```
Governance Map v1 (updated 2026-07-13)
    │
    ├─► ARCH-012: Continuity Engine 整合 ✅ 已完成
    │     • 统一连续性检查入口
    │     • 整合 heartbeat 中的连续性逻辑
    │     • 优先级: P0（地基，ARCH-013 依赖它）
    │
    ├─► ARCH-013: 三约束自动化验证 ✅ 已完成
    │     • 在 heartbeat 中自动化检查 Continuity/L∞/Admission
    │     • 依赖 ARCH-012 的 Continuity Engine
    │     • 优先级: P0（安全底线）
    │
    └─► ARCH-014: Mengpo/Autophagy 模块实现
          • 实现记忆遗忘机制（Mengpo）
          • 实现资产清理机制（Autophagy）
          • 修复 heartbeat 中的悬空引用
          • 优先级: P1（中高）— 遗忘机制缺失导致资产无限增长
```

**建议顺序**: ARCH-014（P1 中高，修复悬空引用 + 完成遗忘机制）
