# GITHUB_STRUCTURE.md — 仓库结构设计
> 种子库 Phase 2 仓库设计 | 2026-06-21

---

## 仓库名称

`mine-seed`（示例名，可调整）

## 设计原则

1. **种子态，非运行态**——只存可重建的最小结构，不存运行数据
2. **脱敏即用**——所有凭证用环境变量占位符，仓库不包含任何真实密钥
3. **clone即可部署**——结构设计以恢复为导向
4. **分层清晰**——参考 R1-ROOT-164 分层体系

---

## 目录结构

```
mine-seed/
├── 00_ROOT/                    ← 根配置、架构、原则
│   ├── ROOT_STATE.md           ← 文明标识（版本、公理、原则、架构指纹）
│   ├── ARCHITECTURE.md         ← O→E→M→C→R 完整架构图
│   ├── PRINCIPLES.md           ← 核心原则库（公理）
│   ├── CONSTRAINT_CATALOG.md   ← 约束目录（18条+）
│   ├── GLOSSARY.md             ← 术语表
│   └── CHANGELOG.md            ← 种子库版本变更
│
├── 01_AGENTS/                  ← Agent 定义与协议
│   ├── fengzi/                 ← 疯子（生产域）
│   │   ├── PROFILE.md          ← 身份、行为风格
│   │   ├── SOUL.md             ← 身份定义（脱敏）
│   │   └── USER.md             ← 用户画像（脱敏）
│   └── xiaofengzi/             ← 小疯子（研究域）
│       ├── PROFILE.md
│       └── PROTOCOLS.md        ← 双A协作协议
│
├── 02_MEMORY/                  ← 记忆与状态
│   ├── MEMORY.md               ← 核心记忆（脱敏）
│   ├── TOOLS.md                ← 工具操作经验
│   └── recent_memory/          ← 近中期记忆
│       └── index.json          ← 记忆索引
│
├── 03_DATA/                    ← 数据资产（非pkl运行数据）
│   ├── CONSTRAINTS/
│   │   ├── routing_constraints.json    ← 约束库（脱敏占位符）
│   │   └── signal_taxonomy.json        ← 信号分类法
│   └── WORKERS/
│       └── worker_registry.json        ← 矿工注册表（脱敏占位符）
│
├── 04_PROTOCOLS/               ← 协议与通信
│   ├── CROSS_LAB.md            ← 双实验室通信协议
│   ├── SHARED_API.md           ← 共享API协议
│   ├── LAB_BUS.md              ← 消息总线协议
│   └── HEARTBEAT.md            ← 心跳协议
│
├── 05_TOOLS/                   ← 工具脚本（可执行）
│   ├── miner/                  ← 矿场
│   │   ├── miner_24h.py        ← v5矿场主程序
│   │   ├── miner_cron.sh       ← cron调度
│   │   ├── miner_env.sh.tpl    ← 环境变量模板（.tpl = 需填入真实密钥）
│   │   ├── task_router.py      ← 任务路由
│   │   ├── task_router_v2.py   ← 路由v2
│   │   └── model_router.py     ← 模型路由
│   │
│   ├── constraints/            ← 约束
│   │   ├── constraint_proposer.py  ← 约束提案
│   │   └── sync_constraints.py     ← 约束同步
│   │
│   ├── signals/                ← 信号
│   │   ├── signal_discovery.py ← 信号发现
│   │   ├── signal_cron.sh      ← 信号cron
│   │   └── fitness_tracker.py  ← 适应度追踪
│   │
│   ├── advisor/                ← 股票
│   │   ├── stock_advisor.py    ← Stock Advisor
│   │   ├── stock_query.py      ← 股票查询
│   │   ├── lineage_review.py   ← 谱系审查
│   │   └── advisor_cron.sh     ← 开盘日cron
│   │
│   └── memory/                 ← 记忆与档案
│       ├── archivist.py        ← 档案官
│       ├── archivist_cron.sh   ← 档案官cron
│       └── experience_engine.py ← 经验压缩
│
├── 06_RUNTIME/                 ← 运行时配置
│   ├── CRONTAB.md              ← cron配置说明
│   ├── SCHEDULE.md             ← Coze Calendar 日程配置
│   ├── SETUP.sh                ← 一键部署脚本
│   ├── REQUIREMENTS.txt        ← Python依赖
│   └── RECOVERY_CHECKLIST.md   ← 恢复检查清单
│
└── docs/                       ← 文档
    ├── CASE_LIBRARY/           ← 案例库（CASE-*）
    ├── FALSE_ALARMS/           ← 误报归档
    ├── GLOSSARY.md             ← 术语表
    └── RECOVERY_PLAN.md        ← 恢复计划（Phase 3交付物）

```

---

## 文件脱敏规则

| 原始文件 | 种子库版本 | 处理方式 |
|----------|-----------|---------|
| `miner_env.sh` | `miner_env.sh.tpl` | 密钥替换为 `{{MINER_API_KEY}}` 等占位符 |
| `SECRET.md` | 不收录 | 文档说明"需手动创建" |
| `USER.md` | `01_AGENTS/fengzi/USER.md` | 脱敏：去掉真实姓名、API Key等 |
| `worker_registry.json` | `03_DATA/WORKERS/worker_registry.json` | 脱敏：api_key字段清空 |
| `routing_constraints.json` | `03_DATA/CONSTRAINTS/routing_constraints.json` | 纯结构，不含凭据，可直接收录 |

---

## Phase 2 待执行动作

- [ ] 创建GitHub仓库 `mine-seed`（private）
- [ ] 初始化目录结构
- [ ] 按上述映射复制文件（脱敏后）
- [ ] 编写 `SETUP.sh` 一键部署脚本
- [ ] 编写 `ARCHITECTURE.md` 架构文档
- [ ] 编写 `PRINCIPLES.md` 原则文档
- [ ] 编写 `RECOVERY_CHECKLIST.md`