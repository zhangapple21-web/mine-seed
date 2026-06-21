# ASSET_INVENTORY.md — 资产清单
> 种子库 Phase 1 资产盘点 | 2026-06-21

---

## A. 必须保存

种子库核心资产，缺任何一个都无法重建系统。

### A1. 约束系统
| 文件 | 路径 | 说明 |
|------|------|------|
| `routing_constraints.json` | `/home/coze/routing_constraints.json` | 核心约束库，18条（17AVOID+1PREFER） |
| `constraint_proposer.py` | `/home/coze/constraint_proposer.py` | 约束提案引擎 |
| `sync_constraints.py` | `/home/coze/sync_constraints.py` | 约束同步工具 |

### A2. 矿场核心
| 文件 | 路径 | 说明 |
|------|------|------|
| `miner_24h.py` | `/home/coze/miner_24h.py` | v5矿场主程序（含Monkey Patch） |
| `miner_cron.sh` | `/home/coze/miner_cron.sh` | cron调度脚本（含锁机制） |
| `miner_env.sh` | `/home/coze/miner_env.sh` | 环境变量模板（API凭证用占位符替换） |
| `worker_registry.json` | `/home/coze/worker_registry.json` | 矿工注册表 |
| `mine_output/summary.json` | `/home/coze/mine_output/summary.json` | 班次汇总最新快照 |

### A3. 路由与调度
| 文件 | 路径 | 说明 |
|------|------|------|
| `task_router.py` | `/home/coze/task_router.py` | 任务路由引擎（v5） |
| `task_router_v2.py` | `/home/coze/task_router_v2.py` | 路由v2变体 |
| `model_router.py` | `/home/coze/model_router.py` | 模型路由 |

### A4. 信号系统
| 文件 | 路径 | 说明 |
|------|------|------|
| `signal_discovery.py` | `/home/coze/signal_discovery.py` | 信号发现引擎 |
| `signal_cron.sh` | `/home/coze/signal_cron.sh` | 信号cron脚本 |
| `signal_taxonomy.json` | `/home/coze/signal_taxonomy.json` | 信号分类法 |
| `fitness_tracker.py` | `/home/coze/fitness_tracker.py` | 适应度追踪器 |
| `fitness_tracker_log.jsonl` | `/home/coze/fitness_tracker_log.jsonl` | 适应度日志 |

### A5. 部署脚本
| 文件 | 路径 | 说明 |
|------|------|------|
| `archivist.py` | `/home/coze/archivist.py` | 档案官主程序 |
| `archivist_cron.sh` | `/home/coze/archivist_cron.sh` | 档案官cron |
| `experience_engine.py` | `/home/coze/experience_engine.py` | 经验压缩引擎 |
| `knowledge_cron_early.sh` | `/home/coze/knowledge_cron_early.sh` | 知识早班cron |
| `knowledge_cron_noon.sh` | `/home/coze/knowledge_cron_noon.sh` | 知识午班cron |

### A6. 协议文件
| 文件 | 路径 | 说明 |
|------|------|------|
| `shared/api.py` | `/home/coze/shared_api.py` | 共享API服务 |
| `lab_bus.py` | `/home/coze/lab_bus.py` | 双实验室消息总线（GitHub Gist） |
| `lab_comm.py` | `/home/coze/lab_comm.py` | lab_02通信客户端 |
| `lab_ntfy.py` | `/home/coze/lab_ntfy.py` | ntfy.sh通信客户端 |
| `shared/r1_principles.md` | `/home/coze/shared/r1_principles.md` | R1公理库 |
| `shared/README.md` | `/home/coze/shared/README.md` | 共享目录说明 |

### A7. 配置模板
| 文件 | 路径 | 说明 |
|------|------|------|
| `routing_constraints.json.bak.*` | `/home/coze/` | 约束历史备份（保留最新2份） |
| `task_router.py.bak.*` | `/home/coze/` | 路由历史备份（保留最新2份） |

### A8. 运行架构文档
| 文件 | 路径 | 说明 |
|------|------|------|
| `MEMORY.md` | `./MEMORY.md` | 当前会话记忆——核心运行状态 |
| `USER.md` | `./USER.md` | 用户画像 |
| `SOUL.md` | `./基础设定/SOUL.md` | 身份定义 |
| `TOOLS.md` | `./基础设定/TOOLS.md` | 工具操作经验 |
| `O→E→M→C→R架构` | 存档在MEMORY.md | 完整架构链路 |

### A9. 股票系统
| 文件 | 路径 | 说明 |
|------|------|------|
| `stock_advisor/stock_advisor.py` | `/home/coze/stock_advisor/stock_advisor.py` | Stock Advisor主程序 |
| `stock_advisor/stock_query.py` | `/home/coze/stock_advisor/stock_query.py` | 股票查询模块 |
| `stock_advisor/advisor_cron.sh` | `/home/coze/stock_advisor/advisor_cron.sh` | 开盘日定时任务 |
| `stock_advisor/lineage_review.py` | `/home/coze/stock_advisor/lineage_review.py` | 谱系审查 |
| `stock_advisor/host_profile.json` | `/home/coze/stock_advisor/host_profile.json` | 主持人画像 |

---

## B. 重要但可重建

种子库不保存原始文件，但应在恢复文档中注明如何重建。

| 资产 | 路径/来源 | 重建方式 |
|------|-----------|---------|
| 班次产出（canonical_v2_*.md） | `mine_output/` | 重新运行miner_24h.py生成 |
| 信号日志 | `mine_output/signals/` | 重新运行signal_discovery.py |
| 班次报告（班次报告_*.md） | `mine_output/` | 重新运行miner_cron.sh |
| 切片产出（slice_mining_*.md） | `mine_output/` | 重新运行miner_24h.py |
| 升级分析（upgrade_analysis_*.md） | `mine_output/` | 重新运行miner_24h.py |
| 档案官日志 | `mine_output/knowledge/` | 重新运行archivist.py |
| cron日志 | `mine_output/cron.log` | 重新运行后自动生成 |
| 共享API日志 | `shared_api.log` | 重新启动后自动生成 |
| stock_pool.pkl | `/home/coze/stock_pool.pkl` | 从akshare/futu重拉 |
| hs300_stocks.pkl | `/home/coze/hs300_stocks.pkl` | 从akshare重拉 |
| zz500_stocks.pkl | `/home/coze/zz500_stocks.pkl` | 从akshare重拉 |
| stock_industry_map.pkl | `/home/coze/stock_industry_map.pkl` | 从akshare重拉 |
| computer_use/ | `/home/coze/computer_use/` | 临时会话缓存，不保存 |
| TG收集产出 | `/home/coze/tg_collector/output/` | 重新运行tg_saved_collector.py |
| 对话转录音档 | `/app/data/所有对话/` | 平台自动保存 |

---

## C. 不上传

以下内容**严禁**进入GitHub仓库：

### API凭证（miner_env.sh 需脱敏后上传）
- One API Key 和 Admin Token
- 所有8个NVIDIA NIM Key
- GitHub PAT
- 智谱GLM API Key
- Telegram Bot Token × 2
- TG Bot Token

### 隐私数据
- SECRET.md（密码/密钥）
- 用户个人信息（USER.md 需脱敏）
- TG Bot Session文件
- TG收集的对话/用户数据

### 运行缓存
- `__pycache__/` 目录
- `.coze/` 目录
- `.cache/` 目录
- `.config/` 目录
- `*.pkl` 文件（可重建，不上传）
- `*.log` 文件（可重建，不上传）

---

## D. 当前cron结构（系统骨架）

```
0 */4 * * *    miner_cron.sh               → miner_24h.py + experience_engine.py
30 2,6,10,14,18,22  * * *  signal_cron.sh  → signal_discovery.py
4 20 * * *     archivist_cron.sh            → archivist.py
@reboot        shared_api.py（进程保活）
* * * * *      shared_api.py 保活监控
0 * * * *      lab_ntfy.py ping             → 跨机心跳
```

**日程系统**（Coze Calendar，非cron）：
| 任务 | 时间 | 说明 |
|------|------|------|
| Stock Advisor | 开盘日08:15 | 早盘建议 |
| Dragon Leader | 开盘日09:30/13:30/14:50 | 龙头识别×3 |
| 矿场v5 | 每4h | 自动执行 |
| 信号发现 | 每6h | 信号轮询 |