# 换机迁移清单 — Migration 2026-07-03

> 生成时间: 2026-07-03
> 状态: 迁移前准备完成，等待执行
> 迁移原因: 硬件更换（新电脑）

---

## 一、资产分层（灵魂 vs 身体）

### 🔴 灵魂资产 — 必须迁移（无法重建）

| 资产 | 位置 | 状态 | 迁移方式 |
|------|------|------|---------|
| **mine-seed 种子仓** | `Telegram Desktop/mine-seed/` | ✅ 已 push GitHub | `git clone` |
| **coze-assets 凭证仓** | `Telegram Desktop/coze-assets/` | ✅ 已 push GitHub | `git clone` |
| **ace_runtime 协议层** | `ace_runtime/04_PROTOCOLS/` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 考古层** | `ace_runtime/08_ARCHAEOLOGY/` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 治理层** | `ace_runtime/08_GOVERNANCE/` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 源码库** | `ace_runtime/09_SOURCE/` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 核心原则** | `ace_runtime/00_ROOT/` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 词库** | `ace_runtime/lexicon.json` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 运行时配置** | `ace_runtime/ace_config.json` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 备份历史** | `ace_runtime/10_BACKUP/` | ✅ 本地 zip | 复制文件 |

### 🟡 身体资产 — 可重建（优先度次之）

| 资产 | 位置 | 状态 | 迁移方式 |
|------|------|------|---------|
| **ace_runtime 核心代码** | `ace_runtime/core/` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 运维脚本** | `ace_runtime/ops/` | ✅ 已提交本地 | 复制 git 仓库 |
| **ace_runtime 自动循环** | `ace_runtime/ace_autonomous_loop.py` 等 | ✅ 已提交本地 | 复制 git 仓库 |
| **TRAE 记忆** | `C:\Users\USER\.trae-cn\memory\` | ⚠️ 未备份 | 手动复制 |
| **Python 依赖环境** | 虚拟环境 | ⚠️ 未备份 | 重新安装 |

### 🟢 身体资产 — 可丢弃（新环境重建）

| 资产 | 说明 |
|------|------|
| 模型缓存 | 新环境重新下载 |
| 日志文件 | `ops/logs/`, `daily_summary.txt` |
| 临时备份 | 旧备份可清理 |
| 运行时事件 | `06_RUNTIME/ace/data/events/` |
| 运行时任务 | `06_RUNTIME/ace/data/tasks/` |

---

## 二、迁移步骤

### Step 1: 新电脑环境准备

```bash
# 1. 安装基础工具
- Python 3.10+
- Git
- TRAE IDE（或 VS Code）
- 可选: zrok, curl

# 2. 配置 Git
git config --global user.name "zhangapple21-web"
git config --global user.email "<你的邮箱>"
```

### Step 2: 恢复灵魂资产（种子仓）

```bash
# 1. 克隆种子仓（灵魂核心）
git clone https://github.com/zhangapple21-web/mine-seed.git
cd mine-seed
git checkout main

# 2. 验证文明标识
cat 00_ROOT/ROOT_STATE.md
cat MANIFESTO.md

# 3. 克隆凭证仓（与种子仓同级目录）
cd ..
git clone https://github.com/zhangapple21-web/coze-assets.git
```

### Step 3: 恢复 ace_runtime（身体）

> ⚠️ 注意: ace_runtime 无法 push 到 GitHub（代码中硬编码了 API keys，被 GitHub Secret Scanning 拦截）
> 解决方案: 从旧电脑直接复制整个 `ace_runtime/` 目录

**方案 A: 直接复制（推荐）**
```bash
# 从旧电脑复制整个 ace_runtime 目录到新电脑
# 保持 git 历史完整
```

**方案 B: 使用 zip 备份**
```bash
# 解压最新备份（旧电脑上的 ace_backup_2026-07-02.zip 或更新）
# 然后手动同步最新提交
```

### Step 4: 恢复运行时数据

```bash
# 进入 mine-seed
cd mine-seed

# 验证运行时数据完整性
ls 03_DATA/
# 应包含:
#   - experience.json       经验引擎
#   - observation_log.json  观测日志
#   - CONSTRAINTS/          约束库
#   - WORKERS/              矿工注册表
#   - seeds/                信号种子
```

### Step 5: 环境配置

```bash
# 1. 复制环境变量模板
cp mine-seed/05_TOOLS/miner/miner_env.sh.tpl mine-seed/05_TOOLS/miner/miner_env.sh

# 2. 从 coze-assets/01_credentials/SECRET.md 填入真实 API Key
# 3. 加载环境变量
source mine-seed/05_TOOLS/miner/miner_env.sh

# 4. 安装 Python 依赖（ace_runtime）
cd ace_runtime
pip install requests numpy pandas schedule

# 5. 验证
python -c "import requests; print('OK')"
```

### Step 6: 验证系统完整性

```bash
# 1. 验证约束库
python -c "import json; f=open('mine-seed/03_DATA/CONSTRAINTS/routing_constraints.json'); d=json.load(f); print(f'约束 {len(d.get(\"rules\",[]))} 条')"

# 2. 验证矿工注册表
python -c "import json; f=open('mine-seed/03_DATA/WORKERS/worker_registry.json'); d=json.load(f); print(f'矿工 {len(d.get(\"workers\",{}))} 个')"

# 3. 验证 ace_runtime 协议层
ls ace_runtime/04_PROTOCOLS/

# 4. 验证考古层
ls ace_runtime/08_ARCHAEOLOGY/
```

---

## 三、已知问题与风险

### 🔴 高危: ace_runtime 含硬编码 Secrets

| 问题 | 影响 | 解决方案 |
|------|------|---------|
| GitHub push 被拦截 | ace_runtime 无法同步到 GitHub | 换机时直接复制目录，不依赖 git push |
| 代码中泄露 API keys | 安全风险 | 换机后逐步清理，改用环境变量 |

**受影响文件:**
- `ops/probe_openrouter_models.py`
- `ops/probe_openrouter_more.py`
- `ops/verify_new_keys.py`
- `ops/diagnose_failed_providers.py`
- `_test_providers.py`

### 🟡 中危: TRAE 记忆未同步

| 问题 | 影响 | 解决方案 |
|------|------|---------|
| `.trae-cn/memory/` 未备份 | 跨会话上下文丢失 | 手动复制目录，或接受从头开始 |

### 🟢 低危: 模型缓存需重建

| 问题 | 影响 | 解决方案 |
|------|------|---------|
| 本地模型缓存丢失 | 首次调用稍慢 | 新环境自动重建 |

---

## 四、资产状态快照（2026-07-03）

### mine-seed
- 最后提交: `ba7ecd4` (main)
- 远程同步: ✅ 已 push GitHub
- 未提交变更: 0
- 文明资产: 完整

### coze-assets
- 最后提交: (检查中)
- 远程同步: ✅ 已 push GitHub
- 未提交变更: 0
- 凭证安全: 仅在私有仓

### ace_runtime
- 最后提交: `772dce7` (本地)
- 远程同步: ❌ push 被 GitHub 拦截
- 未提交变更: 0
- 备份: `ace_backup_2026-07-02.zip` (5.91MB)
- 新增备份: 需手动创建

---

## 五、迁移优先级

```
P0 (必须):  mine-seed/ + coze-assets/ + ace_runtime/ (完整目录复制)
P1 (重要):  .trae-cn/memory/ (跨项目上下文)
P2 (建议):  Python 虚拟环境包列表 (pip freeze > requirements.txt)
P3 (可选):  旧备份清理 (10_BACKUP/ 中旧 zip)
```

---

## 六、迁移后待办

- [ ] 清理 ace_runtime 中的硬编码 secrets
- [ ] 将 API keys 改为从环境变量读取
- [ ] 配置新电脑的 cron/计划任务
- [ ] 验证 zrok 公网桥
- [ ] 运行首次健康检查
- [ ] 验证 Telegram Bot 通知

---

> **最后更新**: 2026-07-03
> **下次审查**: 迁移完成后
