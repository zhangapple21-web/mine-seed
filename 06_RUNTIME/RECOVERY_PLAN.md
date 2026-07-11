# RECOVERY_PLAN.md — 恢复验证计划
> 种子库 Phase 3 恢复验证 | 2026-06-21

---

## 核心目标

> 不是"上传成功"。
> 是验证：**如果服务器消失，是否能 `git clone` 然后重新部署？**

---

## 恢复场景

**场景描述：** lab_01 和 lab_02 两台云电脑同时丢失，所有文件、cron配置、Agent配置全部消失。仅有 GitHub 私有仓库 `mine-seed` 可用。

**恢复成功标准：** 从 `git clone` 开始到系统恢复自我运行，能在 **30分钟内** 完成。

---

## 恢复步骤

### Step 0: 前置条件
```
输入：GitHub仓库访问权限 + 一台新的Linux云电脑
时间：~5分钟
```

- [ ] 创建/登录云电脑（Ubuntu 22.04+）
- [ ] 安装 Python 3.10+、pip、git
- [ ] `git clone https://github.com/<org>/mine-seed.git`
- [ ] `cd mine-seed`

### Step 1: 环境准备
```
时间：~5分钟
```

- [ ] 运行 `06_RUNTIME/SETUP.sh` 一键部署
  - 创建目录结构
  - 安装 Python 依赖 (`pip install -r 06_RUNTIME/REQUIREMENTS.txt`)
  - 检查基础环境（python3、bash、curl）
- [ ] 手动填写 `05_TOOLS/miner/miner_env.sh`（从安全渠道获取API密钥）
- [ ] 加载环境变量：`source 05_TOOLS/miner/miner_env.sh`

### Step 2: 配置恢复
```
时间：~5分钟
```

- [ ] 参考 `06_RUNTIME/CRONTAB.md` 配置 crontab
- [ ] 参考 `06_RUNTIME/SCHEDULE.md` 在 Coze 平台配置 Calendar 日程（如适用）
- [ ] 创建 `/home/coze/mine_output/` 等运行时目录

### Step 3: 单模块验证
```
时间：~10分钟
```

- [ ] **约束系统**：运行 `python3 05_TOOLS/constraints/constraint_proposer.py` → 验证约束加载正常
- [ ] **矿工路由**：运行 `python3 05_TOOLS/miner/task_router.py --test` → 验证路由正常
- [ ] **信号系统**：运行 `python3 05_TOOLS/signals/signal_discovery.py --test` → 验证信号引擎启动
- [ ] **Stock Advisor**：运行 `python3 05_TOOLS/advisor/stock_advisor.py --test` → 验证顾问模块启动（行情数据缺失可跳过）

### Step 4: 全链路验证
```
时间：~5分钟
```

- [ ] 手动触发矿场班次：`bash 05_TOOLS/miner/miner_cron.sh`
- [ ] 检查产出：`ls /home/coze/mine_output/` → 应有新生成的班次文件
- [ ] 检查日志：无异常报错
- [ ] 触发信号发现：`bash 05_TOOLS/signals/signal_cron.sh`

### Step 5: 通信恢复
```
时间：~5分钟
```

- [ ] 启动共享API：`nohup python3 /home/coze/shared_api.py &`
- [ ] 验证心跳：`python3 05_TOOLS/miner/lab_ntfy.py ping`
- [ ] 如果是双实验室场景，在 lab_02 上部署通信客户端

---

## 恢复验证矩阵

| 模块 | 依赖 | 无网络可恢复？ | 验证方式 |
|------|------|---------------|---------|
| 约束系统 | 无外部依赖 | ✅ | python3 import |
| 矿场v5 | One API + 模型API | ⚠️ 需网络 | 触发班次 |
| 信号发现 | 模型API | ⚠️ 需网络 | 触发扫描 |
| Stock Advisor | 行情数据源 | ⚠️ 需行情 | 启动检查 |
| 档案官 | 模型API | ⚠️ 需网络 | 运行脚本 |
| 消息总线 | GitHub Gist | ⚠️ 需网络 | ping测试 |
| crontab | 系统服务 | ✅ | 查看定时器 |

---

## 风险点

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| API密钥丢失 | 系统无法与模型通信 | miner_env.sh.tpl 注释清晰，记录每个密钥的获取来源 |
| Coze Agent配置丢失 | 无法自动执行 | SCHEDULE.md 记录所有日程UID和配置参数 |
| 依赖包版本不一致 | 脚本运行异常 | REQUIREMENTS.txt 锁定版本号 |
| 云电脑IP/域名变化 | 通信断连 | 所有地址用环境变量，SETUP.sh 支持配置 |

---

## 一句话

> 种子库不是备份。是把系统从"运行态"压缩成"种子态"。未来真正值钱的不是服务器。是已经长出来的结构。
---

## 补充要求：DISASTER_TEST（灾难恢复演练）

恢复计划不能只写不练。必须真实落地验证。

### 演练脚本

```bash
# 在隔离环境中执行
mkdir -p /tmp/recovery_test
cd /tmp/recovery_test
git clone <repo_url> mine-seed
cd mine-seed

# 按SETUP.sh部署
bash 06_RUNTIME/SETUP.sh

# 单模块验证
python3 05_TOOLS/constraints/constraint_proposer.py --test
python3 05_TOOLS/miner/task_router.py --test
python3 05_TOOLS/signals/signal_discovery.py --test
```

### 验收标准

- [ ] `git clone` → 部署完成 ≤ 5分钟
- [ ] 约束加载正常 ≤ 1分钟
- [ ] 路由引擎启动正常 ≤ 1分钟
- [ ] 信号引擎启动正常 ≤ 1分钟
- [ ] 手动触发矿场班次成功 ≤ 3分钟
- [ ] 日志无报错

### 交付物

第一次演练后生成 `DISASTER_RECOVERY_REPORT.md`，记录：
- 实际耗时 vs 预期耗时
- 失败环节及根因
- 文档缺失项
- 下次演练改进点

> 未验证的恢复 = 未恢复