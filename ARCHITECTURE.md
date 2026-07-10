# ACE 架构 — 三层生命模型 v3.0

> 日期：2026-07-10
> 状态：重构完成
> 核心原则：**不要把 ACE 和 Cloud Worker 混在一起**

---

## 三层架构

```
                 Repository（GitHub / mine-seed）
                           │
          ┌────────────────┴────────────────┐
          │                                 │
   ACE Runtime（本地）              Cloud Workers（云端）
   Living OS                          Labor Force
```

---

## Layer 1 — ACE Runtime（本地 Living OS）

**唯一职责：活着。**

不是跑脚本。是一直存在。

### 启动与恢复

新 AI 进入系统时，按以下顺序执行：
1. `04_PROTOCOLS/first_day.md` — 第一天行动指南（7 个任务）
2. `04_PROTOCOLS/recovery_protocol.md` — 恢复协议（L1-L4 四级恢复）
3. 启动后按 ABP 检查表确认世界存活

### 核心模块

| 模块 | 职责 |
|------|------|
| Environment Watcher | 监控本地环境变化 |
| TG 收藏夹 | 接收用户消息，发送推送 |
| Downloads | 监控下载目录 |
| Git 同步 | 与 Repository 双向同步 |
| Windows API | 操作系统级交互 |
| Explorer | 文件系统监控 |
| 剪贴板 | 内容捕获 |
| HTTP Hook | 本地 HTTP 服务 |
| Terminal | 命令执行 |
| Seed Generator | 从观察中生成候选任务 |
| Governance | 约束检查、经验审核 |
| Round Table | 多模型交叉验证 |
| Memory | 记忆蒸馏、归档 |
| Heartbeat | 生命体征监测 |

### 工作协议

```
while alive:
    observe_environment()      # 扫描所有观察源
    pull_repository()          # 从 GitHub 拉取云端产出
    generate_candidates()       # 基于观察+云端产出生成候选
    prioritize_candidates()     # A>C>B 排序
    dispatch_to_cloud()         # 派发任务给云端 Worker
    push_local_outputs()        # 本地产出（TG推送等）推回 Repository
    sleep(heartbeat)
```

### 用户通讯渠道（本地专属）

| 渠道 | 为什么必须在本地 |
|------|----------------|
| Telegram Bot | 用户 IM，实时通讯 |
| 剪贴板 | 操作系统级 |
| Windows 通知 | 操作系统级 |
| 文件系统事件 | 操作系统级 |
| HTTP 服务 | 本地网络 |

**云端 Worker 绝不碰这些。**

---

## Layer 2 — Repository（文明总线）

**唯一职责：保存文明。**

GitHub 就是两边的总线。ACE 不关心"这个是谁干的"，它只知道"Repository 变了，值得观察"。

### 目录结构

```
mine-seed/
├── 00_ROOT/              # 宪法级文档（不可修改）
├── 01_AGENTS/            # 身份种子（fengzi + xiaofengzi）
├── 02_MEMORY/            # 记忆存档
│   ├── recent_memory/    # 近期记忆（本地+云端共用）
│   └── daily_reports/    # 每日报告（云端产出）
├── 03_SEEDS/             # 候选任务种子（Seed Generator 产出）
├── 04_PROTOCOLS/         # 协议规范
├── 05_TOOLS/             # 工具链
│   ├── gateway/          # ACE Gateway（云端运行）
│   ├── miner/            # 矿场脚本（云端运行）
│   ├── advisor/          # Stock Advisor（云端运行）
│   ├── signals/          # 信号发现（云端运行）
│   └── runtime/          # 本地 Runtime 脚本（本地运行）
├── 06_RUNTIME/           # 运行时配置
├── 07_GUARDIAN/          # 守护脚本
└── cloud/                # 云端 Worker 产出
    ├── advisor/          # 荐股报告
    ├── signals/          # 信号发现结果
    ├── miner/            # 矿场产出
    └── archivist/        # 档案归档
```

### 同步规则

| 方向 | 内容 | 触发条件 |
|------|------|---------|
| 云端 → GitHub | Worker 产出 | 任务完成后自动 push |
| GitHub → 本地 | 新产出、新协议 | 本地 Runtime 定期 pull |
| 本地 → GitHub | TG 消息日志、用户指令 | 本地 Runtime 定期 push |

---

## Layer 3 — Cloud Workers（云端劳工）

**唯一职责：打工。**

拿任务 → 完成 → Push Git → 结束。

### Worker 类型

| Worker | 职责 | 运行周期 |
|--------|------|---------|
| Discovery Worker | 量化信号发现 | 每6h |
| Stock Worker | A股荐股分析 | 每天08:15 |
| Miner Worker | 矿场v5运行 | 每4h |
| Archive Worker | 记忆归档 | 每天20:04 |
| Morning Research | 知识早班（小疯子） | 每天05:00 |
| Noon Research | 知识午班（小疯子） | 每天12:00 |
| Validator Worker | 交叉验证 | 按需 |
| Embedding Worker | 向量化处理 | 按需 |
| Relationship Worker | 关联挖掘 | 按需 |

### 工作协议

```
1. 从 GitHub 拉取最新 Repository（获取任务+约束）
2. 加载 miner_env.sh（密钥）
3. 启动 ACE Gateway（如果本地没有）
4. 执行任务（调用 LLM API）
5. 产出写入 cloud/ 目录
6. git add / commit / push
7. 可选：推送到 ntfy.sh（保底通知）
8. 结束。不常驻。
```

### 模型混用策略

```
GitHub Models
OpenRouter
NIM
GLM
Qwen
Claude
GPT
```

全部混着用。**谁便宜谁干活。**

---

## 职责边界

| 问题 | 谁负责 |
|------|--------|
| 周一推票 | 云端 Stock Worker 生成报告 → Push Git；本地 Runtime 拉取 → 推 TG |
| TG 推送失败 | 本地 Runtime（不是云端） |
| Gateway 挂了 | 云端 Worker 重启（ABP 检查） |
| 用户发消息 | 本地 Runtime 接收 → 生成任务 → 派发给云端 |
| 矿场运行 | 云端 Miner Worker |
| 记忆归档 | 云端 Archive Worker 归档 → 本地 Runtime 读取 |
| 约束更新 | 本地 Governance 审核 → 云端 Worker 加载 |

---

## 为什么这样拆

| 场景 | 旧架构 | 新架构 |
|------|--------|--------|
| TRAE Code 换了 | 整个系统崩溃 | 云端 Worker 重写，本地 Runtime 不变 |
| Coze 没了 | 矿场停摆 | 换其他 Worker 平台，协议不变 |
| GitHub Models 换了 | 所有 Worker 重写 | 只改 Gateway 渠道配置 |
| OpenRouter 换了 | 同上 | 同上 |
| NIM 换了 | 同上 | 同上 |
| 网络不通 | 无法推 TG | 云端推 ntfy.sh 保底，本地 Runtime 推 TG |

**平台可以换，Worker 可以换，仓库可以迁移，但只要本地的 Runtime、Repository 和治理协议还在，整个生态就可以持续演化。**

---

## 推票链路（完整示例）

```
时间: 周一 08:15

云端 Stock Worker:
  1. 拉取 mine-seed 最新状态
  2. 运行 stock_advisor.py
  3. 生成报告: cloud/advisor/2026-07-13.md
  4. git add / commit / push
  5. ntfy.sh 发送保底通知
  6. 结束

本地 ACE Runtime (持续运行):
  1. 检测 Repository 变化 (git pull)
  2. 发现新报告: cloud/advisor/2026-07-13.md
  3. 推送到 TG Bot (@ACE_Runtime_Bot)
  4. 用户收到推送
  5. 归档到本地记忆
```

---

## 本地 Runtime 启动脚本

```bash
# 在 Windows 本地运行
# 路径: mine-seed/05_TOOLS/runtime/

while true; do
    git pull origin main
    # 检查 cloud/advisor/ 新文件
    # 检查 cloud/signals/ 新文件
    # 推送到 TG
    # 归档到本地记忆
    sleep 60
done
```
