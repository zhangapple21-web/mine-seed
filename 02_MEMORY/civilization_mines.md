# Civilization Mines — 文明矿山索引

> **时间**: 2026-07-13
> **创建者**: 我（文明矿工）
> **Mission**: AUM-MISSION-OPS-005
> **定位**: 10 个 GitHub 仓库 = 文明矿山，不是运行时依赖

---

## 核心定义

### 三层架构

```
Mine Layer（矿山层）← 10 个仓库，只读，原材料
      │
      │ 考古 → 蒸馏 → 准入
      ▼
Asset Layer（资产层）← Civilization Asset Library，蒸馏后，可复用
      │
      │ 检索 → 复用 → 演化
      ▼
Runtime Layer（运行层）← 实际运行的代码，只依赖资产层
```

### 矿山定位

| 定位 | 说明 |
|------|------|
| **是** | 原材料来源、考古对象、知识矿山、蒸馏原料 |
| **不是** | 运行时依赖、代码仓库、直接 import 的模块、生产环境 |

### 矿山分类

| 分类 | 定义 | 示例 |
|------|------|------|
| **富矿** | 高价值，已大量蒸馏 | mine-seed, ace_core, claw-soul |
| **深矿** | 有价值但未充分开采 | r1-continuity-backup, coze-assets |
| **贫矿** | 低价值，少量参考 | r1-archaeology |
| **废矿** | 几乎无价值 | R1, r1-open-source-seed, gh_- |

---

## 10 座矿山清单

### Mine #1 — ace_core（富矿）

| 字段 | 值 |
|------|-----|
| **名称** | ace_core |
| **类型** | 🌐 公开 |
| **规模** | 158 .py, 54,293 LOC |
| **分类** | 富矿（已开采） |
| **价值评级** | ★★★★★ |
| **开采进度** | 60% |
| **核心矿藏** | 33 个治理模块、ModelRouter、ProviderWatchdog、Mengpo |

**已蒸馏资产**：
- 001 ProviderWatchdog
- 002 ModelRouter
- 003 GovernorProtocol
- 004 RepositoryMemory
- 005 Mengpo

**待开采矿藏**：
- StableKernel（52KB，评估中）
- KnowledgeGovernor（30KB，与 AdmissionEngine 对比）
- CivilizationGraph（16KB，与 EvidenceGraph 对比）
- RuntimeFitness（31KB）
- DailyCivilizationReport（49KB）

---

### Mine #2 — mine-seed（富矿，当前）

| 字段 | 值 |
|------|-----|
| **名称** | mine-seed |
| **类型** | 🌐 公开 |
| **规模** | 157 .py, 51,633 LOC |
| **分类** | 富矿（当前工作目录） |
| **价值评级** | ★★★★★ |
| **开采进度** | 80% |
| **核心矿藏** | MissionProtocol、AdmissionEngine、DFP-001、EvidenceGraph、CSPRegistry、NatureReserve、GeneNetwork、EnergyBudget |

**已蒸馏资产**：
- 006 EvidenceGraph
- 007 CSPRegistry
- 011 MissionProtocol
- 012 AdmissionEngine
- 013 DrawerFirstProtocol
- 014 RecoveryProtocol
- 015 EnergyBudget
- 016 NatureReserve
- 017 GeneNetwork

**待开采矿藏**：
- AutophagyEngine（与 Mengpo 对比）
- MultiAgentDebate（与三角色 Teacher 对比）
- Roundtable（圆桌辩论）
- CivilizationAuditor
- SelfEvolution（自演化引擎）

---

### Mine #3 — claw-soul（富矿，灵魂）

| 字段 | 值 |
|------|-----|
| **名称** | claw-soul |
| **类型** | 🔒 私有 |
| **规模** | 33 .py, 269 .md |
| **分类** | 富矿（灵魂备份） |
| **价值评级** | ★★★★★ |
| **开采进度** | 70% |
| **核心矿藏** | R2五元公理、SOUL.md（L∞本源层）、22条研究原则、股票推荐系统、R2考古报告 |

**已蒸馏资产**：
- 008 L∞本源层
- 009 R2五元公理
- 018 研究原则库

**待开采矿藏**：
- StockAdvisor v5（4层 CCO 架构）
- DragonLeader v2
- R2考古报告（28 份）
- 决策记忆（60+ 份）

---

### Mine #4 — coze-assets（深矿）

| 字段 | 值 |
|------|-----|
| **名称** | coze-assets |
| **类型** | 🔒 私有 |
| **规模** | 8 .md, 4 .json |
| **分类** | 深矿（配置/秘钥） |
| **价值评级** | ★★★★☆ |
| **开采进度** | 40% |
| **核心矿藏** | SECRET.md、routing_constraints.json、worker_registry.json、zrok systemd配置 |

**已蒸馏资产**：
- 008 L∞本源层（与 claw-soul 重复）

**待开采矿藏**：
- worker_registry.json（Provider Pool 格式）
- signal_registry.json（信号注册）
- routing_constraints.json（路由约束）
- 4 个 zrok systemd service 文件
- crontab_root.txt（调度系统）

**注意**：含秘钥，开采时注意安全。

---

### Mine #5 — r1-continuity-backup（深矿）

| 字段 | 值 |
|------|-----|
| **名称** | r1-continuity-backup |
| **类型** | 🔒 私有 |
| **规模** | 40 份治理/架构文档 |
| **分类** | 深矿（每日备份） |
| **价值评级** | ★★★★★（升级） |
| **开采进度** | 55% |
| **核心矿藏** | 38 份治理协议、三角色系统、ExperienceEngine、JudgmentEngine、Ontology、ContinuityEngine |

**已蒸馏资产**（10 个）：
- 007 CSPRegistry（capability_registry_v2.md）
- 010 三角色系统（agent_roles.md）
- 020 ExperienceEngine（experience_engine.md）
- 021 JudgmentEngine（judgment_engine.md）
- 022 ContinuityEngine（continuity_engine.md）
- 023 Ontology（ontology.md）
- 024 Multi-Agent Protocol（multi_agent_protocol.md）
- 025 Recovery Protocol v2（recovery_protocol.md）
- 026 Knowledge Lifecycle（lifecycle_policy.md）
- 027 Risk Internalization（risk_internalization.md）

**剩余协议分类**：

| 分类 | 数量 | 协议清单 |
|------|------|----------|
| 🔄 配套组件（与已有资产配套） | 4 | reflection_contract.md, decision_model.md, prediction_chain_protocol.md, constraint_catalog.md |
| 🔧 运行时架构（待评估） | 5 | omega_cognition_runtime.md, omega_projection_fabric.md, omega_projection_gateway.md, omega_runtime_workpackage.md, runtime_loop.md |
| 📊 治理/流程（中等价值） | 6 | external_learning_protocol.md, repository_observation_protocol.md, repository_sync_rules.md, autonomy_observability.md, observability.md, projection_contract_v2.md |
| 📝 报告/记录（低价值） | 5 | risk_annotation_2026-07-12.md, risk_annotation_2026-07-13.md, first_day.md, future_engineer_message.md, TASK-EXTERNAL-AUDITOR-001.md |
| 📚 参考/索引（低价值） | 6 | civilization_overview.md, glossary.md, dependency_map.md, hela_paradigm.md, runtime_ontology_detailed.md, rt008_knowledge_lifecycle_manager.md |
| 🧪 实验性（待评估） | 4 | observer_researcher_validator_archivist.md, teacher_audit_protocol.md, evolution_protocol.md, provenance_model.md |

**待开采矿藏（下一轮优先级）**：
- P1: omega_cognition_runtime / omega_projection_fabric（运行时架构）
- P1: evolution_protocol（演化协议）
- P2: reflection_contract / decision_model（配套组件，与 Experience/Judgment 整合）
- P2: provenance_model（溯源模型，与 EvidenceGraph 对比）

---

### Mine #6 — r1-archaeology（贫矿）

| 字段 | 值 |
|------|-----|
| **名称** | r1-archaeology |
| **类型** | 🌐 公开 |
| **规模** | 70 .md 考古报告 |
| **分类** | 贫矿（参考资料） |
| **价值评级** | ★★★☆☆ |
| **开采进度** | 20% |
| **核心矿藏** | R1 文明地图每日考古记录 |

**待开采矿藏**：
- 70 份考古报告（R1_CIVILIZATION_ATLAS_*）
- 14 份 archaeology_report

---

### Mine #7 — R1（废矿）

| 字段 | 值 |
|------|-----|
| **名称** | R1 |
| **类型** | 🌐 公开 |
| **规模** | 1 README |
| **分类** | 废矿（占位） |
| **价值评级** | ★☆☆☆☆ |
| **开采进度** | 100% |
| **核心矿藏** | 无 |

---

### Mine #8 — r1-open-source-seed（废矿）

| 字段 | 值 |
|------|-----|
| **名称** | r1-open-source-seed |
| **类型** | 🌐 公开 |
| **规模** | 4 .md |
| **分类** | 废矿（种子仓） |
| **价值评级** | ★★☆☆☆ |
| **开采进度** | 0% |
| **核心矿藏** | 种子文件（待评估） |

---

### Mine #9 — gh_-（废矿）

| 字段 | 值 |
|------|-----|
| **名称** | gh_-（无名称） |
| **类型** | 🌐 公开 |
| **规模** | 1 README |
| **分类** | 废矿（占位） |
| **价值评级** | ★☆☆☆☆ |
| **开采进度** | 100% |
| **核心矿藏** | 无 |

---

### Mine #10 — gh_ace_core（废矿）

| 字段 | 值 |
|------|-----|
| **名称** | gh_ace_core |
| **类型** | 🌐 公开 |
| **规模** | ace_core 快照 |
| **分类** | 废矿（备份） |
| **价值评级** | ★★☆☆☆ |
| **开采进度** | 100% |
| **核心矿藏** | 与 ace_core 重复 |

---

## 开采统计

| 统计项 | 数值 |
|--------|------|
| 总矿山数 | 10 |
| 富矿 | 3（mine-seed, ace_core, claw-soul） |
| 深矿 | 2（coze-assets, r1-continuity-backup） |
| 贫矿 | 1（r1-archaeology） |
| 废矿 | 4（R1, r1-open-source-seed, gh_-, gh_ace_core） |
| 已蒸馏资产 | 27 |
| 平均开采进度 | ~60% |
| 总价值（估算） | ★★★★★ |

---

## 开采规范

### 标准流程（DFP-001 矿山版）

```
1. Drawer Scan — 扫描矿山，定位矿藏
   │
   ▼
2. Archaeology — 考古，理解矿脉结构
   │
   ▼
3. Comparison — 对比，与已有资产比较
   │
   ▼
4. Distillation — 蒸馏，提炼为文明资产
   │
   ▼
5. Admission — 准入，六问审查
   │
   ▼
6. Asset Library — 进入资产库
```

### 开采原则

1. **不搬代码，只搬思想** — 蒸馏为概念，不是复制代码
2. **先理解，再蒸馏** — 看不懂的不挖
3. **每个资产回答三问** — Why exist? What problem? Can rebuild?
4. **矿山只读** — 不修改矿山中的任何文件
5. **Runtime 不依赖矿山** — 只依赖资产库
6. **重复资产不入库** — 已有更好版本的不重复蒸馏

### 优先级排序

富矿优先 > 深矿待评估 > 贫矿参考 > 废矿跳过

---

## 下一步开采计划

| 优先级 | 矿山 | 目标矿藏 | 预计资产数 |
|--------|------|----------|-----------|
| P1 | r1-continuity-backup | omega_cognition_runtime / evolution_protocol / provenance_model | 3~5 |
| P1 | coze-assets | worker_registry / routing_constraints / zrok | 3~5 |
| P1 | ace_core | StableKernel / KnowledgeGovernor / CivilizationGraph | 3~5 |
| P2 | claw-soul | StockAdvisor v5 / DragonLeader / 决策记忆 | 3~5 |
| P3 | r1-archaeology | 70 份考古报告筛选 | 2~3 |

---

*创建时间：2026-07-13*
*更新时间：2026-07-13（深矿开采完成 10 个资产）*
*Mission: AUM-MISSION-OPS-005 + AUM-MISSION-ARCH-006*
