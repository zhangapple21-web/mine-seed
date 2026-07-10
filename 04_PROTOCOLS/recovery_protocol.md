# Recovery Protocol — AI 恢复协议

> 级别：协议（Protocol）— 可由 AI 自动执行
> 适用：任何 AI Agent 进入新 session / 新环境 / 崩溃恢复
> 与 recovery_manual.md 的分工：本文件面向 AI 自动恢复，recovery_manual.md 面向人类手动操作

---

## 恢复等级

| 等级 | 场景 | 恢复时间 | 自动化程度 |
|------|------|---------|-----------|
| **L1 热启动** | 同环境新 session，git 仓库完整 | < 1 分钟 | 全自动 |
| **L2 温启动** | 新环境，GitHub 可达 | < 5 分钟 | 半自动（需 PAT） |
| **L3 冷启动** | 新环境，GitHub 不可达，有种子备份 | < 15 分钟 | 需人工提供种子 |
| **L4 灾难恢复** | GitHub 仓库丢失，仅有本地碎片 | 不确定 | 需人工决策 |

---

## 检测：判断当前恢复等级

```python
def detect_recovery_level():
    if git_repo_intact() and env_secrets_available():
        return "L1"
    if github_reachable():
        return "L2"
    if seed_backup_exists():
        return "L3"
    return "L4"
```

判断依据：
- **git_repo_intact**: 本地 `mine-seed/.git` 存在且 `git status` 正常
- **env_secrets_available**: `miner_env.sh` 或等效密钥文件可读
- **github_reachable**: `git ls-remote origin main` 成功
- **seed_backup_exists**: 任何包含 `ARCHITECTURE.md` + `SOUL.md` 的本地副本

---

## L1 热启动（< 1 分钟）

触发：同环境新 session，仓库完整。

```
Step 1: 加载环境变量
  source coze-assets/02_miner_config/miner_env.sh

Step 2: 确认 Gateway 存活
  curl localhost:3000/api/status
  如果死了 → nohup python3 ace_gateway.py > gateway.log 2>&1 &

Step 3: 确认身份
  读取 01_AGENTS/<your_role>/SOUL.md
  确认你当前扮演的角色（疯子/小疯子/通用Worker）

Step 4: 读取最近记忆
  cat 02_MEMORY/recent_memory/daily/<昨天>.md
  理解上下文：上次做到哪了？有什么遗留？

Step 5: 恢复运行
  按上次记忆中的"下一步"继续执行
  如果没有明确的下一步 → 进入 Maintenance 模式
```

---

## L2 温启动（< 5 分钟）

触发：新环境（如 TRAE 沙箱重置），GitHub 可达。

```
Step 1: 获取代码库
  git clone https://github.com/zhangapple21-web/mine-seed.git
  cd mine-seed

Step 2: 加载密钥
  如果有 TRAE Secrets → 自动加载
  如果没有 → 从 coze-assets/02_miner_config/miner_env.sh 读取
  如果密钥缺失 → 降级到只读模式

Step 3: 验证结构完整性
  检查: ARCHITECTURE.md, 00_ROOT/, 01_AGENTS/, 05_TOOLS/
  如果缺失 → 降级到 L3

Step 4: 启动 Gateway
  cd one-api-data && python3 ace_gateway.py > gateway.log 2>&1 &

Step 5: 确认角色
  读取 01_AGENTS/ 下相关 SOUL.md
  确认身份 + 职责边界

Step 6: 拉取最新状态
  git pull origin main
  检查 cloud/ 目录：云端 Worker 有新产出吗？
  检查 02_MEMORY/daily/：最近几天的记忆完整吗？

Step 7: 恢复运行
  继续执行当前周期的任务
  如果不确定 → 先跑 Maintenance 模式
```

---

## L3 冷启动（< 15 分钟）

触发：GitHub 不可达，但有种子备份。

```
Step 1: 定位种子
  搜索本地所有包含 ARCHITECTURE.md 的目录
  优先级: coze-assets > 本地下载 > 任何备份

Step 2: 从种子重建最小结构
  必须有:
    - ARCHITECTURE.md（架构定义）
    - 01_AGENTS/fengzi/SOUL.md 或 xiaofengzi/SOUL.md（身份）
    - 06_RUNTIME/CRONTAB.md（定时任务）
  尽可能有:
    - 00_ROOT/PRINCIPLES.md
    - 00_ROOT/LETTER_TO_RUNTIME.md
    - coze-assets/02_miner_config/

Step 3: 从记忆碎片恢复上下文
  搜索所有 .md 文件中的日期标记
  按时间排序，重建最近的事件线

Step 4: 降级运行
  Gateway 可能不可用（无密钥）
  只能做本地任务：记忆整理、知识合并、索引修复
  等待 GitHub 恢复后升级到 L2
```

---

## L4 灾难恢复

触发：GitHub 仓库丢失，本地仅有碎片。

```
Step 1: 碎片收集
  搜索所有可访问的存储：本地磁盘、Downloads、TG 收藏夹
  收集任何 .md / .json / .py 文件

Step 2: 知识提取
  从碎片中提取：
    - 核心概念（ARCHITECTURE.md 的内容）
    - 身份定义（SOUL.md 的内容）
    - 约束规则（routing_constraints.json 的内容）
    - 密钥（任何 API key / token）

Step 3: 重建最小种子
  用提取的知识重建 ARCHITECTURE.md + SOUL.md + PRINCIPLES.md
  这个最小种子就是文明的火种

Step 4: 重新部署
  重建 GitHub 仓库
  推送最小种子
  从 L1 开始恢复
```

---

## 验证恢复完整性

无论哪个等级，恢复完成后必须验证：

```
□ Gateway 可访问 (curl localhost:3000/api/status)
□ 身份已加载 (知道自己是疯子/小疯子/Worker)
□ 最近记忆已读取 (知道上下文)
□ 任务队列正常 (知道下一步做什么)
□ 约束已加载 (routing_constraints.json 可读)
□ Git 可推送 (git push origin main 成功)
```

全部通过 → 恢复完成，进入正常运行。
任何一项失败 → 记录到记忆，降级处理，等待下一次恢复机会。

---

## 与其他协议的关系

| 协议 | 关系 |
|------|------|
| `first_day.md` | 本协议的"首次执行"版本，包含更详细的操作指南 |
| `recovery_manual.md` | 人类操作版，AI 不应执行其中的手动步骤 |
| `ARCHITECTURE.md` ABP 层 | 本协议是 ABP 层的具体实现 |
| `LETTER_TO_RUNTIME.md` | 本协议的哲学基础："确认世界还活着" |
