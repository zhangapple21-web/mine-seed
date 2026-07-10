# 三层架构文档 v3.0
> ACE Runtime / Cloud Workers / Repository

---

## 核心架构拆分

```
┌─────────────────────────────────────────────────────────────┐
│                     ACE Runtime (本地)                       │
│  负责"活着"：中枢、环境观察、治理、记忆、心跳、TG推送          │
│  运行在 Windows / Linux 本地，持续运行                        │
└─────────────────────────────────────────────────────────────┘
                              ↕
                              │ GitHub (文明总线)
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   Cloud Workers (云端)                       │
│  负责"打工"：挖矿、信号、荐股、生成报告、Push Git、结束        │
│  运行在云端容器/Serverless，单次任务，完成即退出               │
└─────────────────────────────────────────────────────────────┘
```

### 职责边界

| 职责 | ACE Runtime (本地) | Cloud Workers (云端) |
|------|-------------------|---------------------|
| 环境观察 | ✅ 持续扫描 | ❌ |
| 治理决策 | ✅ RoundTable/Governor | ❌ |
| 记忆管理 | ✅ 本地记忆索引 | ❌ |
| 心跳循环 | ✅ 15分钟一次 | ❌ |
| TG 推送 | ✅ 用户通讯渠道 | ❌ |
| 挖矿 | ❌ | ✅ 单次任务 |
| 信号发现 | ❌ | ✅ 单次任务 |
| 荐股报告 | ❌ | ✅ 生成+Push Git |
| 档案整理 | ❌ | ✅ 生成+Push Git |
| Git Push | ✅ (持续更新) | ✅ (任务产出) |

---

## 层级结构

### 第一层：ACE Runtime（本地 Living OS）

```
06_RUNTIME/
├── core/
│   ├── runtime_main.py       → 主循环入口
│   ├── heartbeat.py          → 15分钟心跳
│   ├── environment_scan.py   → 环境扫描(EFP)
│   └── memory_manager.py     → 记忆管理
├── governance/
│   ├── roundtable.py         → 圆桌会议
│   └── governor.py           → 治理者
├── connectors/
│   ├── tg_pusher.py          → TG推送
│   ├── ntfy_listener.py      → ntfy.sh监听
│   └── git_sync.py           → Git同步
└── windows/
    ├── win_run.py            → 路径适配
    └── run_heartbeat.ps1     → 计划任务脚本
```

**运行模式**：
- 持续运行（daemon）
- 每 15 分钟心跳：EFP → 扫描 → 治理 → Git Sync → TG 更新
- 监听 GitHub 变更 → 发现新报告 → 推送到 TG

### 第二层：Cloud Workers（云端劳工）

```
05_TOOLS/
├── worker_stock_advisor.py   → 荐股Worker
├── worker_signal_discovery.py → 信号Worker
├── worker_miner.py           → 挖矿Worker
├── worker_archivist.py       → 档案Worker
└── worker_runner.py          → Worker调度器
```

**运行模式**：
- 单次任务（task-based）
- 启动 → 执行 → 产出到 cloud/ 目录 → Push Git → 结束
- 不持有状态，不持续运行
- 通过 ntfy.sh 向 Runtime 发送完成通知

### 第三层：Repository（文明总线）

```
mine-seed/
├── cloud/                    → Cloud Workers 产出区
│   ├── advisor/              → 荐股报告
│   ├── signals/              → 信号发现结果
│   ├── miner/                → 挖矿数据
│   └── archivist/            → 档案整理结果
├── 02_MEMORY/                → Runtime 记忆区
├── 04_PROTOCOLS/             → 协议层
├── 00_ROOT/                  → 根公理
└── r1_archaeology/           → R1 考古层
```

**作用**：
- 两边的桥梁
- 版本控制 + 历史追溯
- 资产索引 + 约束存储
- 跨环境同步

---

## 数据流

### 云端到本地

```
Cloud Worker
    ↓
生成报告
    ↓
写入 cloud/advisor/YYYYMMDD.md
    ↓
Push GitHub
    ↓
本地 Runtime git pull
    ↓
检测新文件
    ↓
推送到 TG
    ↓
归档到 02_MEMORY/
```

### 本地到云端

```
本地 Runtime
    ↓
环境扫描发现新资产
    ↓
RoundTable 审议
    ↓
Governor 批准
    ↓
Push GitHub
    ↓
Cloud Workers 读取
    ↓
执行下一轮任务
```

---

## 关键协议

### 协议层（04_PROTOCOLS/）

| 协议 | 归属 | 作用 |
|------|------|------|
| environment_first.py | Runtime | 环境优先扫描 |
| recovery_protocol.py | Runtime | 自动恢复 |
| ops_005_self_loop.py | Runtime | 14步自循环 |
| roundtable.py | Runtime | 圆桌会议 |
| governor.py | Runtime | 治理者 |
| worker_runner.py | Cloud | Worker调度 |

---

## 部署规范

### Cloud Workers

```bash
# 启动方式（单次任务）
python worker_stock_advisor.py --date 20260714
# 产出：cloud/advisor/advisor_20260714.md
# 完成：git push + ntfy.sh 通知
```

### ACE Runtime

```bash
# Windows 启动方式（持续运行）
python 06_RUNTIME/core/runtime_main.py
# 或通过计划任务每15分钟运行
schtasks /run /tn ACE_Heartbeat
```

---

## 与旧架构的关系

| 旧组件 | 新归属 | 说明 |
|--------|--------|------|
| miner_24h.py | Cloud Worker | 拆成单次任务 |
| signal_discovery.py | Cloud Worker | 拆成单次任务 |
| stock_advisor.py | Cloud Worker | 拆成单次任务 |
| heartbeat.py | Runtime | 保留，加 Git Sync |
| archivist.py | Cloud Worker | 拆成单次任务 |
| tg_push.py | Runtime | 移到 Runtime |
| ntfy_push.py | Cloud Worker | 保留，通知完成 |