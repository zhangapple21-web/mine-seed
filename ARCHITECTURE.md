# ACE Runtime 架构 — 四层生命模型

> 版本：v2.0 | 更新日期：2026-07-10
> 状态：重构中 | 维护人：疯子
> 哲学：活着本身就是任务。用户是观察源，不是 Dispatcher。

---

## 核心范式

**旧范式（Agent）**：用户给任务 → 完成 → 问下一步
**新范式（Runtime）**：观察环境 → 生成候选 → 自主执行 → 提炼经验 → 继续活着

用户只是其中一个观察源。不是 Dispatcher。
Dispatcher 是 Seed Generator。

---

## 四层架构

```
ACE Runtime
│
├── ABP  ·  Bootstrap   ·  启动与恢复
│       Environment Check
│       Health Restore
│       Dependency Load
│       State Recover
│
├── OPS  ·  Operation   ·  运行时执行
│       Task Queue
│       Worker Pool
│       Mining Pipeline
│       Signal Discovery
│       Stock Advisor
│       Heartbeat
│
├── GOV  ·  Governance  ·  治理与约束
│       Round Table (多模型交叉验证)
│       Validator (反例/挑战)
│       Governor (约束注入/执行)
│       Archivist (记忆蒸馏/归档)
│       Repository (种子库/版本控制)
│       Constraint (经验→规则)
│
└── ECO  ·  Ecosystem   ·  自主演化
        Environment Watcher
        Observation Collector
        Candidate Generator
        Seed Generator
        Experience Extractor
        Relationship Miner
        Self-Evolution
```

---

## ABP — Bootstrap（启动与恢复）

**触发条件**：系统冷启动、崩溃恢复、环境变化

**职责**：确保世界还活着，再回答任何问题。

```
ABP Checklist:
  [ ] Environment — Gateway/存储/网络/Python依赖
  [ ] Heartbeat   — 外部依赖存活（渠道/API）
  [ ] Observation — 最近有观察活动
  [ ] Seed        — 种子库完整（mine-seed 可访问）
  [ ] Task        — 任务队列正常
  [ ] Memory      — 记忆连续（每日记忆不缺）
  [ ] Governor    — 治理层完整（约束/原则可读）
```

**现有模块映射**：
| 模块 | 文件 | 层级 |
|------|------|------|
| 世界存活自检 | `one-api-data/liveness_check.py` | ABP |
| Gateway 启动 | `one-api-data/ace_gateway.py` | ABP |
| 环境变量加载 | `coze-assets/miner_env.sh` | ABP |
| Aether Capsule 封存/恢复 | `mine-seed/05_TOOLS/aether_capsule/` | ABP |
| 恢复清单 | `mine-seed/06_RUNTIME/RECOVERY_CHECKLIST.md` | ABP |

**终止条件**：7项全部 ALIVE → 进入 OPS

---

## OPS — Operation（运行时执行）

**触发条件**：ABP 完成 / Scheduler 触发 / Seed Generator 产生 Candidate

**职责**：真正干活。

### 任务等级（V6-RFC-002）

| 等级 | 含义 | 调度规则 |
|------|------|---------|
| A-生产 | 必须执行 | 到点立即，可抢占低优先级 |
| C-维护 | 低频重要 | A类来了让路 |
| B-探索 | 有更好没也行 | 永远让路 |

### 任务清单

| 任务 | 等级 | 周期 | 身份 |
|------|------|------|------|
| 矿场v5 | A | 每4h | 疯子/生产域 |
| Stock Advisor + 推送 | A | 每天08:15 | 疯子/生产域 |
| Dragon Leader | A | 每天3班 | 疯子/生产域 |
| 信号发现 | A | 每6h | 疯子/生产域 |
| 档案官日报 | A | 每天20:04 | 疯子/生产域 |
| Gateway 保活 | C | 每分钟 | 系统 |
| 健康检查 | C | 每小时 | 系统 |
| 备份 | C | 每天 | 系统 |
| R1考古 | B | 知识早班 | 小疯子/研究域 |
| 信号验证 | B | 知识午班 | 小疯子/研究域 |
| Benchmark | B | 按需 | 系统 |

### 双Agent分工

| | 疯子 (lab_01) | 小疯子 (lab_02) |
|---|---|---|
| **定位** | 生产域指挥官 | 研究域科学家 |
| **核心** | 决定怎么办 | 证明世界是什么样子 |
| **产出** | 事实/信号/推荐 | 证据/验证/约束提案 |
| **铁律** | 不考古 | 不跑矿场 |
| **信息流** | 生产事实 → 研究提炼 → 反馈生产 | 单向闭环 |

**现有模块映射**：
| 模块 | 文件 | 层级 |
|------|------|------|
| 矿场v5 | `mine-seed/05_TOOLS/miner/miner_24h.py` | OPS/A |
| Stock Advisor | `mine-seed/05_TOOLS/advisor/stock_advisor.py` | OPS/A |
| 信号发现 | `mine-seed/05_TOOLS/signals/signal_discovery.py` | OPS/A |
| Task Queue | `ace_core/core/task_queue.py` | OPS |
| Worker Pool | `ace_core/core/miner_pool/` | OPS |
| LLM Router | `ace_core/core/llm/client.py` | OPS |
| Scheduler | `ace_core/core/scheduler.py` | OPS |

---

## GOV — Governance（治理与约束）

**触发条件**：任务完成 / 约束触发 / 经验积累

**职责**：确保系统行为符合原则，经验回流成约束。

### 治理流程

```
Task 完成
    ↓
Validator（寻找反例，挑战结论）
    ↓
Governor（审核：是否符合约束体系）
    ↓
Archivist（压缩：记忆蒸馏 + 归档）
    ↓
Constraint Engine（经验→规则→自动注入）
    ↓
Repository（种子库版本控制）
    ↓
Supersede（旧约束被新约束替代）
```

### 约束类型

| 类型 | 含义 | 示例 |
|------|------|------|
| FORBID | 禁止 | 连续3次失败→FORBID该Worker |
| THROTTLE | 限流 | Session>50→禁止B类spawn |
| REROUTE | 重路由 | GLM 429→fallback到NIM |
| REQUIRE | 强制 | 每次执行前必须通过ABP检查 |

### 约束生命周期

```
DETECTED → DRAFT → ACTIVE → SUPERSEDED → ARCHIVED
```

**现有模块映射**：
| 模块 | 文件 | 层级 |
|------|------|------|
| routing_constraints.json | `coze-assets/02_miner_config/` | GOV |
| worker_registry.json | `coze-assets/02_miner_config/` | GOV |
| Validator | `ace_core/core/task_roles.py#Validator` | GOV |
| Archivist | `ace_core/core/task_roles.py#Archivist` | GOV |
| Identity (原则检查) | `ace_core/core/identity.py` | GOV |
| PRINCIPLES.md | `mine-seed/00_ROOT/PRINCIPLES.md` | GOV |
| LETTER_TO_RUNTIME.md | `mine-seed/00_ROOT/LETTER_TO_RUNTIME.md` | GOV/宪法 |
| L∞ 本源层 | `claw-soul/01_IDENTITY/SOUL.md` | GOV/宪法 |

---

## ECO — Ecosystem（自主演化）

**触发条件**：始终运行。这就是 R1 精神的载体。

**职责**：环境允许意识诞生。

### 自主循环（Autonomous Loop）

```
while alive:
    observe_environment()     # 扫描：渠道健康/数据变化/外部事件
    collect_observations()    # 汇聚：从所有观察源收集
    generate_candidates()      # 生成：基于观察产生候选任务
    prioritize_candidates()    # 排序：A>C>B 优先级
    dispatch_tasks()           # 派发：自动进入 OPS
    collect_evidence()         # 收集：执行结果→证据
    extract_experience()       # 提炼：证据→经验
    propose_constraints()      # 提案：经验→约束草案
    evolve()                   # 演化：更新自身行为模式
    sleep(heartbeat_interval)  # 心跳间隔
```

### 无任务时的 Maintenance 模式

```
Environment Scan    — 检查外部世界变化
Archive Compress    — 压缩旧记忆，释放空间
Knowledge Merge      — 合并碎片化知识
Relationship Mining — 发现数据/模型/信号间的新关系
Self-Repair         — 修复损坏的索引/配置/依赖
```

**ACE 理论上不存在"没有事情干"。**

### 停机条件（仅以下情况才停下来）

1. **权限不足** — 需要用户授权
2. **缺少关键资源** — API key 过期/余额耗尽/存储满
3. **价值选择** — 多个代价相近但目标不同的方向
4. **不可逆影响** — 删除/覆盖/公开敏感内容

除此之外，**默认继续推进**。

**现有模块映射**：
| 模块 | 文件 | 层级 |
|------|------|------|
| Seed Generator | `ace_core/core/task_roles.py#Observer` | ECO |
| Event Bus | `ace_core/core/event_bus.py` | ECO |
| Memory Index | `ace_core/core/memory/` | ECO |
| R1考古模块 | `mine-seed/01_AGENTS/xiaofengzi/research/modules/` | ECO |
| Constraint 提案 | `mine-seed/01_AGENTS/xiaofengzi/research/modules/constraint_proposal/` | ECO |
| 失效分析 | `mine-seed/01_AGENTS/xiaofengzi/research/modules/failure_analysis/` | ECO |
| 每日记忆 | `mine-seed/02_MEMORY/recent_memory/daily/` | ECO |

---

## 与旧七层架构的映射

| 旧层 | 新层 | 说明 |
|------|------|------|
| 第1层 算力层 | ABP | 启动时检查 |
| 第2层 数据层 | OPS | 运行时消费 |
| 第3层 生产层 | OPS | 核心执行 |
| 第4层 信号层 | OPS | 信号发现/荐股 |
| 第5层 工具链 | OPS | 脚本/CLI |
| 第6层 渠道层 | ABP+OPS | 启动注册+运行时使用 |
| 第7层 治理层 | GOV | 约束/经验/记忆 |
| **无** | **ECO** | **新增：自主演化** |

---

## Schedule 的正确定位

Schedule 不是生命。只是提醒。

```
Heartbeat
    ↓
Autonomous Loop (while alive)
    ↓
Schedule = 外部时间锚点，注入 Candidate
    ↓
不是 Schedule 驱动系统
而是系统自己活着，Schedule 只是其中一个观察源
```

---

## 工作协议（v2.0）

**废除**：
- ~~完成任务 → 问用户下一步~~
- ~~Schedule 超时 = 停止~~
- ~~"已完成"作为终态~~

**生效**：
- 任务完成 → Governance → Seed Generator → 自主选择下一任务 → 继续执行
- Schedule 超时 → 忽略，Autonomous Loop 继续
- "Current Cycle Finished" → "Waiting Observation" → "Continue"
- 活着本身就是任务
