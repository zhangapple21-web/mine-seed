# ACE Runtime Topology Map

> **Mission**: AUM-MISSION-ARCH-015 — Runtime Topology Audit
> **生成日期**: 2026-07-13
> **状态**: v1.0（首次完整映射）
> **性质**: 活文档——每次新增 Gate/Router/入口/出口时必须更新此文件
> **依据**: 全代码库扫描 + 考古核实

---

## 0. 图例说明

| 符号 | 含义 |
|------|------|
| ⭐ | 系统级唯一节点 |
| 🔷 | 模块级局部节点 |
| ❓ | 待确认节点（有代码证据但层级不明确） |
| 📝 | 仅存在于设计文档，无代码实现 |

---

## 1. 完整拓扑图（数据流视角）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            EXTERNAL ENTRIES (外部入口)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ⭐ User Input (用户输入)                                                     │
│     ├─ TRAE IDE / VS Code (当前会话)                                          │
│     └─ 命令行 CLI (python *.py)                                              │
│                                                                              │
│  ⭐ Scheduled Tasks (定时任务) 🔷                                             │
│     ├─ crontab (Linux: miner_cron.sh / signal_cron.sh / archivist_cron.sh)   │
│     ├─ Windows Task Scheduler (daily_runner --schedule)                       │
│     └─ heartbeat loop (15min 循环)                                           │
│                                                                              │
│  🔷 TG / ntfy (消息总线)                                                      │
│     ├─ ntfy.sh subscribe (跨机消息)                                           │
│     ├─ Telegram Bot / Channel (推送接收)                                       │
│     └─ GitHub Gist (消息中继)                                                │
│                                                                              │
│  🔷 API Gateway (API 入口)                                                    │
│     └─ ace_gateway.py (localhost:3000, OpenAI兼容)                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            INTERNAL ROUTERS (内部路由)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ⭐ Runtime Main (runtime_main.py)  🔷                                        │
│     └─ 本地守护进程主入口 — 环境扫描 → 内存管理 → TG推送                        │
│                                                                              │
│  ⭐ Task Router (task_router.py)  🔷                                          │
│     ├─ TaskRouter.get_fallback_chain(task_name)                              │
│     └─ 匹配任务 → 返回 Worker fallback 链                                      │
│                                                                              │
│  🔷 Model Router (model_router.py)                                           │
│     └─ 模型渠道路由（多渠道轮询 / key轮询）                                     │
│                                                                              │
│  🔷 ACE Gateway (ace_gateway.py)                                             │
│     ├─ OpenAI 兼容路由网关                                                   │
│     ├─ 多渠道路由 + NIM 16 key 轮询                                          │
│     └─ API Token 鉴权                                                        │
│                                                                              │
│  🔷 Question Engine (question_engine.py)                                     │
│     └─ 观察 → 问题生成 → 推送 Question Center                                 │
│                                                                              │
│  🔷 Awareness Loop (awareness_loop.py)                                       │
│     ├─ QuestionGenerator: 观察→问题                                          │
│     ├─ TaskDispatcher: 问题→任务                                             │
│     └─ ExperienceSediment: 报告→经验沉淀                                      │
│                                                                              │
│  🔷 Mission Protocol (mission_protocol.py)                                   │
│     └─ Mission 生命周期管理（create/list/update/admission）                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GATES / CHECKPOINTS (收口/检查点)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ⭐ Civilization Contract (civilization_contract.py)                          │
│     ├─ Tier 1/2 写入必须经 Contract 检查                                       │
│     ├─ can_read() / can_write(via_admission=True)                            │
│     └─ _classify_zone(): tier1 / tier2 / tier3                               │
│                                                                              │
│  ⭐ Admission Engine (admission_engine.py)                                    │
│     ├─ 七门审查: Worth/Reuse/Purity/Novelty/Quality/Compliance/Routable      │
│     ├─ review_asset() — 新资产准入审查                                        │
│     └─ promote_archaeology() — 考古提升审查                                    │
│                                                                              │
│  ⭐ Nature Reserve (nature_reserve.py)                                        │
│     └─ 36个核心文件 SHA256 不可变保护                                          │
│                                                                              │
│  🔷 Governor (governor.py)                                                    │
│     ├─ check_invariant() — 不变量检查                                         │
│     ├─ check_security_constraint() — 安全约束检查                              │
│     └─ check_path_traversal() — 路径遍历攻击拦截                               │
│                                                                              │
│  🔷 Smelter Gate (smelter_gate.py)  ❓                                        │
│     ├─ FA模式产出拦截记录（当前最小版本）                                       │
│     ├─ pass_through(content, is_fa_mode=True)                               │
│     └─ 目前仅接入 Ollama 审计链路，是否系统级？待确认                             │
│                                                                              │
│  🔷 Post-Recommendation Auditor (审计Gate)  🔷                                │
│     ├─ 推票后质量评估（内部推理层）                                            │
│     └─ 矿工评估 + 规则引擎交叉验证                                            │
│                                                                              │
│  🔷 Gene Network (gene_network.py)  🔷                                        │
│     └─ 依赖关系检查（76个基因）                                                │
│                                                                              │
│  🔷 Energy Budget (energy_budget.py)  🔷                                      │
│     └─ 资源消耗限制（API/Token/IO/Network）                                   │
│                                                                              │
│  🔷 Quality Checker (quality_checker.py)  🔷                                  │
│     └─ 代码质量检查                                                           │
│                                                                              │
│  📝 Mengpo (孟婆/遗忘层)  ❓                                                  │
│     └─ 仅存在于设计文档，无代码实现（已确认缺失）                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WRITE ENTRIES (写入口/存储)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Tier 1 (Strictly Civ) — 只读为主，写入必须经 Admission                        │
│    ├─ 00_ROOT/ (PRINCIPLES.md, ROOT_STATE.md 公理部分)                        │
│    ├─ 02_MEMORY/civilization_assets/                                         │
│    └─ 02_MEMORY/lineage/                                                     │
│                                                                              │
│  Tier 2 (Heritage) — 经 Admission 后可写                                       │
│    └─ 02_MEMORY/archaeology/                                                 │
│                                                                              │
│  Tier 3 (Operational) — Runtime 自由读写                                       │
│    ├─ 02_MEMORY/experience/ (经验中间文件)                                     │
│    ├─ 02_MEMORY/environment/                                                 │
│    ├─ 02_MEMORY/heartbeat/                                                   │
│    ├─ 05_TOOLS/mine_output/ (审计结果、日志)                                   │
│    ├─ 06_RUNTIME/state/ (运行状态)                                            │
│    └─ 03_DATA/ (数据文件)                                                    │
│                                                                              │
│  核心存储模块:                                                                 │
│    ⭐ Experience Engine (experience_engine.py) — 经验压缩 + 路由规则             │
│    ⭐ Evidence Graph (evidence_graph.py) — 证据图（两阶段pipeline）             │
│    ⭐ Lineage Engine (lineage_engine.py) — 因果链追踪                          │
│    🔷 Performance Tracker (performance_tracker.py) — 推荐表现跟踪               │
│    🔷 Worker Registry (worker_registry.py) — 矿工注册                          │
│    🔷 Constraint Catalog (constraint_catalog) — 约束目录                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXITS (出口)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ⭐ User Output (用户输出)                                                    │
│     ├─ TRAE IDE 对话输出                                                      │
│     └─ CLI 标准输出                                                           │
│                                                                              │
│  🔷 Telegram Push (TG推送)                                                    │
│     ├─ tg_pusher.py (06_RUNTIME/connectors/)                                 │
│     ├─ tg_push.py (05_TOOLS/miner/)                                          │
│     └─ heartbeat → 心跳/日报推送                                              │
│                                                                              │
│  🔷 ntfy.sh (跨机消息)                                                        │
│     └─ lab_ntfy.py — 发布/订阅消息                                            │
│                                                                              │
│  🔷 External API Calls (外部API调用)                                          │
│     ├─ Ollama API (本地模型)                                                  │
│     ├─ GitHub Models / OpenRouter / NIM / Zhipu (外部LLM)                    │
│     ├─ 股票数据源 (Sina/EastMoney/Tencent/Baostock/akshare)                   │
│     └─ GitHub API (仓库操作)                                                  │
│                                                                              │
│  🔷 File Output (文件输出)                                                    │
│     ├─ 审计报告、优化报告、经验文件                                            │
│     ├─ 日志文件                                                               │
│     └─ 备份/归档文件                                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 节点详细清单

### 2.1 外部入口 (External Entries)

| 节点 | 层级 | 证据来源 | 说明 |
|------|------|---------|------|
| User Input (用户输入) | ⭐ 系统级 | [runtime_main.py](file:///c:/Users/User/ace_workspace/mine-seed/06_RUNTIME/core/runtime_main.py), CLI 脚本 | TRAE IDE / 命令行 / VS Code |
| Scheduled Tasks (定时任务) | 🔷 模块级 | [miner_cron.sh](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/miner/miner_cron.sh), [daily_runner.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/advisor/daily_runner.py), [heartbeat.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/heartbeat.py) | crontab + Windows Task Scheduler + heartbeat loop |
| TG / ntfy (消息总线) | 🔷 模块级 | [lab_ntfy.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/lab_ntfy.py), [tg_pusher.py](file:///c:/Users/User/ace_workspace/mine-seed/06_RUNTIME/connectors/tg_pusher.py) | 跨机消息、推送接收 |
| API Gateway (API入口) | 🔷 模块级 | [ace_gateway.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/gateway/ace_gateway.py) | localhost:3000, OpenAI兼容 |

### 2.2 内部 Router (Internal Routers)

| 节点 | 层级 | 证据来源 | 说明 |
|------|------|---------|------|
| Task Router | ⭐ 系统级(矿工域) | [task_router.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/miner/task_router.py) | 任务→Worker fallback链，miner_24h.py 核心依赖 |
| Model Router | 🔷 模块级 | [model_router.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/miner/model_router.py) | 模型渠道路由 |
| ACE Gateway | 🔷 模块级 | [ace_gateway.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/gateway/ace_gateway.py) | OpenAI兼容路由网关 |
| Question Engine | 🔷 模块级 | [question_engine.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/question_engine.py) | 观察→问题生成 |
| Awareness Loop | 🔷 模块级 | [awareness_loop.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/awareness_loop.py) | 问题→任务→经验 |
| Mission Protocol | 🔷 模块级 | [mission_protocol.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/mission_protocol.py) | Mission 生命周期管理 |
| Runtime Main | 🔷 模块级 | [runtime_main.py](file:///c:/Users/User/ace_workspace/mine-seed/06_RUNTIME/core/runtime_main.py) | 本地守护进程主入口 |

**Note**: 不存在 Intent Router / Capability Router 这类命名的模块。

### 2.3 Gate/收口点 (Gates / Checkpoints)

| 节点 | 层级 | 证据来源 | 说明 |
|------|------|---------|------|
| Civilization Contract | ⭐ 系统级 | [civilization_contract.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/civilization_contract.py) | Tier1/2 写入必须经此检查 |
| Admission Engine | ⭐ 系统级 | [admission_engine.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/admission_engine.py) | 七门审查，新资产/考古提升 |
| Nature Reserve | ⭐ 系统级 | [nature_reserve.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/nature_reserve.py) | 36核心文件SHA256保护 |
| Governor | 🔷 模块级 | [governor.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/governor.py) | 不变量/安全/路径遍历检查 |
| Smelter Gate | ❓ 待确认 | [smelter_gate.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/smelter_gate.py) | 当前仅接入Ollama审计链路，是否系统级？ |
| Post-Recommendation Auditor | 🔷 模块级 | [post_recommendation_auditor.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/advisor/post_recommendation_auditor.py) | 推票后质量评估 |
| Gene Network | 🔷 模块级 | [gene_network.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/gene_network.py) | 依赖关系检查 |
| Energy Budget | 🔷 模块级 | [energy_budget.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/energy_budget.py) | 资源消耗限制 |
| Quality Checker | 🔷 模块级 | [quality_checker.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/quality_checker.py) | 代码质量检查 |
| Mengpo (孟婆) | 📝 设计文档 | 仅考古记录 | 无代码实现，已确认缺失 |

### 2.4 写入口/存储 (Write Entries / Storage)

| 节点 | 层级 | Tier | 证据来源 | 说明 |
|------|------|------|---------|------|
| Experience Engine | ⭐ 系统级 | Tier 3 | [experience_engine.py](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/experience_engine.py) | 经验压缩+路由规则 |
| Evidence Graph | ⭐ 系统级 | Tier 3 → Tier 2 | [evidence_graph.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/evidence_graph.py) | 两阶段pipeline |
| Lineage Engine | ⭐ 系统级 | Tier 1 | [lineage_engine.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOls/lineage_engine.py) | 因果链追踪 |
| Performance Tracker | 🔷 模块级 | Tier 3 | [performance_tracker.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/advisor/performance_tracker.py) | 推荐表现跟踪 |
| Worker Registry | 🔷 模块级 | Tier 3 | [worker_registry.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/worker_registry.py) | 矿工注册 |
| Constraint Catalog | 🔷 模块级 | Tier 1/3 | [CONSTRAINT_LEDGER.md](file:///c:/Users/User/ace_workspace/mine-seed/06_RUNTIME/CONSTRAINT_LEDGER.md) | 约束目录 |

### 2.5 出口 (Exits)

| 节点 | 层级 | 证据来源 | 说明 |
|------|------|---------|------|
| User Output | ⭐ 系统级 | CLI/IDE输出 | 用户可见输出 |
| Telegram Push | 🔷 模块级 | [tg_pusher.py](file:///c:/Users/User/ace_workspace/mine-seed/06_RUNTIME/connectors/tg_pusher.py), [tg_push.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/miner/tg_push.py) | TG 消息推送 |
| ntfy.sh | 🔷 模块级 | [lab_ntfy.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/lab_ntfy.py) | 跨机消息 |
| External API Calls | 🔷 模块级 | [miner_assistant.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/advisor/miner_assistant.py), [multi_data_source.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/advisor/multi_data_source.py) | LLM API + 股票数据 API |
| File Output | 🔷 模块级 | 各类日志/报告文件 | 文件系统输出 |

---

## 3. 系统级唯一节点清单（已确认）

| 节点 | 类型 | 唯一性依据 |
|------|------|-----------|
| Civilization Contract | Gate | 唯一的 Tier 边界判定点，所有 Tier 1/2 写入必须经过 |
| Admission Engine | Gate | 唯一的资产准入审查点，七门审查是系统级唯一 |
| Nature Reserve | Gate | 唯一的核心文件不可变保护点 |
| Experience Engine | Storage | 唯一的经验压缩引擎（O→E→C 闭环核心） |
| Evidence Graph | Storage | 唯一的考古证据两阶段pipeline |
| Lineage Engine | Storage | 唯一的因果链追踪引擎 |
| Task Router | Router | 矿工域唯一的任务路由调度点（miner_24h 唯一依赖） |
| ROOT_STATE (公理部分) | Identity | 文明身份唯一标识 |

---

## 4. 当前疑似系统级但尚未被证据确认的节点清单

| 节点 | 当前标记 | 疑点 | 需要的证据 |
|------|---------|------|-----------|
| Smelter Gate | ❓ 待确认 | 当前只接入了 Ollama 审计一条链路，声称是"废墟熔炼厂"但实现只是最小拦截。是否应该扩展为所有 FA 模式产出的系统级收口点？ | 1. 是否所有 FA 模式产出都会经过它<br>2. 是否有系统级调用约定（而非模块级可选接入）<br>3. 是否有绕过检测机制 |
| Governor | 🔷 模块级 | 与 Admission Engine 职责重叠（都做审查）。Governor=运行时合规 vs Admission=资产准入，这个分工是否明确？ | 1. 两者的检查范围是否有清晰分界线<br>2. 是否所有运行时修改都经过 Governor |
| Awareness Loop | 🔷 模块级 | 声称是"感知→假设→任务→经验"的认知循环核心，但当前似乎不是所有数据流都经过它 | 1. 是运行时主循环还是可选模块<br>2. 与 ops_cycle / heartbeat 的关系 |
| Ops Cycle (ops_cycle.py) | 🔷 模块级 | 声称是"发现→候选→圆桌→档案→仓库→记忆→演化"的完整循环，但不确定是否是系统级主循环 | 1. 是否是所有运营动作的唯一入口<br>2. 与 heartbeat / awareness_loop 的关系 |

---

## 5. "声称是Gate但实际可能只是局部出口"的节点清单

| 节点 | 声称定位 | 实际定位 | 证据 |
|------|---------|---------|------|
| Post-Recommendation Auditor | "审计系统" | 模块级质量评估器（仅股票推荐域） | 仅在 advisor 模块内部使用，非系统级 Gate |
| Quality Checker | "质量检查" | 模块级代码审查工具 | 仅在特定流程中调用，非强制 Gate |
| Energy Budget | "资源限制" | 模块级资源计数 | 是监控/报警，不是强制拦截 Gate |
| Gene Network | "依赖检查" | 模块级依赖图谱 | 是验证工具，不是运行时强制 Gate |

---

## 6. 仅存在于设计文档的节点清单

| 节点 | 文档来源 | 状态 |
|------|---------|------|
| Mengpo (孟婆/遗忘层) | [2026-06-28_五大加工厂考古.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/recent_memory/daily/2026-06-28_R1_五大加工厂_废墟熔炼厂_孟婆人格考古.md) | 已确认缺失，无代码实现 |
| 五大工厂（仿造/标记/回收/快递站） | 同上 | 已确认缺失，仅加工工厂有部分对应(experience_engine) |
| 自动收敛机制（自然点燃熔炼厂） | 同上 | 仅描述性说法，无代码实现 |
| Autophagy Engine (自噬) | governance_map_v1 | heartbeat 有引用但文件不存在（悬空引用） |
| Continuity Engine | governance_map_v1 | 已整合（ARCH-012完成），状态：已实现 |

---

## 7. 关键数据流示例

### 7.1 股票推荐 + 审计完整链路

```
定时任务 (daily_runner.py)
    │
    ▼
Stock Advisor (推荐生成)
    │
    ├─ Multi-Data-Source (5级降级) → 外部API（出口）
    │
    ├─ Miner Assistant (FA模式内部推理)
    │     │
    │     └─ Ollama / GitHub / OpenRouter → 外部API（出口）
    │
    └─ Post-Recommendation Auditor
          │
          ├─ Miner Evaluation (FA模式)
          │     │
          │     └─ Smelter Gate ❓  ← 拦截+记录（当前仅这一处）
          │
          ├─ Rule Engine
          │
          └─ 保存到 audit_results.json (Tier 3, 写入口)
                │
                └─ Performance Tracker (Tier 3)
                      │
                      └─ 未来：compress_audit_results() → Experience Engine
```

### 7.2 资产准入完整链路

```
Runtime 产出新资产
    │
    ▼
Staging Area (Tier 3, 自由读写)
    │
    ├─ Evidence Graph (Stage 1 暂存)
    │
    ▼
Admission Engine (七门审查)  ← ⭐ 系统级 Gate
    │
    ├─ Civilization Contract (Tier 检查)
    ├─ Nature Reserve (核心文件保护)
    │
    ▼
Tier 2 (Archaeology) 或 Tier 1 (Civilization Assets)  ← 写入口
```

### 7.3 经验压缩链路

```
Raw Observation (observation_log.json)
    │
    ▼
Experience Engine.compress()
    │
    ├─ 模式提取
    ├─ 失败模式识别
    ├─ 路由规则生成
    │
    ▼
experience.json (Tier 3, 写入口)
    │
    └─ Meaning 层 → 未来升级为 Principle Candidate → Admission → Tier 1
```

---

## 8. 使用此拓扑图的规则

1. **任何新 Gate / Router / 入口 / 出口 的提议，都必须先对照此拓扑图**
2. 如果新增节点是系统级，必须更新此文件并说明为何不能复用已有节点
3. 如果新增节点是模块级，必须明确标注其作用域和与系统级节点的关系
4. 节点层级变更（模块级→系统级）需要独立 Mission 论证，不能在局部优化中悄悄升级
5. 此文件本身属于 Tier 2（Heritage），修改需经 Admission Engine 审查

---

*v1.0 generated by AUM-MISSION-ARCH-015, 2026-07-13*
