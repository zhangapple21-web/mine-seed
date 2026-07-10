# mine-seed — ACE 文明种子库

> 私有仓库 | 仅灵魂核心 + 工具链
> 备份协议：鲸落分片协议（PROTO-007）+ 双脑备份协议（PROTO-008）
> 最后更新：2026-07-10

---

## 仓库定位

这是 ACE（Autonomous Civilization Engine）的**种子态仓库**，存放松散结构、可重建的最小文明资产。

**不是运行态**——运行时数据（mine_output/、logs/）不纳入版本控制。

---

## 目录结构

```
mine-seed/
├── 00_ROOT/                    # 宪法、架构、根状态
├── 01_AGENTS/                  # Agent 定义（fengzi / xiaofengzi）
├── 02_MEMORY/                  # 记忆与状态
├── 03_DATA/                    # 数据资产（约束、矿工注册表、种子）
├── 04_PROTOCOLS/               # 协议与通信
├── 05_TOOLS/                   # 可执行工具链
│   ├── miner/                  # 矿场 v5
│   ├── signals/                # 信号发现
│   ├── memory/                 # 档案官 + 经验引擎
│   ├── advisor/                # 股票顾问
│   └── constraints/            # 约束同步
├── 06_RUNTIME/                 # 运行时配置（CRONTAB、SETUP）
├── 07_GUARDIAN/                # 网络桥、守护、修复
└── docs/                       # 文档、RFC、案例库
```

---

## 快速启动

```bash
# 1. 安装依赖
pip install requests numpy pandas schedule

# 2. 配置环境变量
cp 05_TOOLS/miner/miner_env.sh.tpl 05_TOOLS/miner/miner_env.sh
# 编辑 miner_env.sh 填入真实 API Key

# 3. 一键验证
bash 06_RUNTIME/SETUP.sh
```

---

## ACE 每日自主循环

| 任务 | 频率 | 脚本 |
|------|------|------|
| 矿场 v5 | 每4小时 | `05_TOOLS/miner/miner_cron.sh` |
| 信号发现 | 每6小时 | `05_TOOLS/signals/signal_cron.sh` |
| 档案官 | 每天 20:04 | `05_TOOLS/memory/archivist_cron.sh` |
| 共享API保活 | 每分钟 | `04_PROTOCOLS/shared_api.py` |
| 跨机心跳 | 每小时 | `04_PROTOCOLS/lab_ntfy.py` |

Windows 环境见 `06_RUNTIME/CRONTAB.md` 的适配说明。

---

## 密钥管理

本仓库为**私有仓库**，API 密钥集中存放在：
- `05_TOOLS/miner/miner_env.sh`（真实密钥，勿泄露）
- `05_TOOLS/miner/miner_env.sh.tpl`（脱敏模板，用于重建）

---

## 备份签名

`ACE_CIVILIZATION_BACKUP_v1.0_2026-07-03`
