# 本地部署清单 — 交给 code 执行

> 云端部分已完成：7 个定时任务 + adata 增强荐股 + A股信号发现 + free_llm 基础设施
> 以下需在本地 Windows 环境完成

---

## 一、环境准备

### 1.1 安装 Python（如尚未安装）
- [ ] 安装 Python 3.10+（推荐 3.11）
- [ ] 安装时勾选 "Add Python to PATH"
- [ ] 验证：`python --version` 和 `pip --version`

### 1.2 安装 Python 依赖
```bash
pip install adata requests python-telegram-bot
```
- `adata`：A股多源数据（腾讯/新浪/百度/东财自动切换）
- `requests`：HTTP 请求
- `python-telegram-bot`：TG 推送（如用 TG）

### 1.3 安装 Git（如尚未安装）
- [ ] 下载安装 Git for Windows
- [ ] 验证：`git --version`

---

## 二、仓库同步

### 2.1 克隆 mine-seed 仓库
```bash
# 选择本地存放目录，如 D:\projects
cd D:\projects
git clone https://github.com/opelleda/mine-seed.git
cd mine-seed
```

### 2.2 后续更新
```bash
cd D:\projects\mine-seed
git pull origin main
```

---

## 三、配置环境变量

在 Windows 搜索栏输入 "环境变量" → "编辑系统环境变量" → "环境变量" → "用户变量" → "新建"

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `TG_BOT_TOKEN` | 你的 Telegram Bot Token | 从 @BotFather 获取 |
| `TG_CHAT_ID` | 你的 Telegram Chat ID | 从 @userinfobot 获取 |
| `GLM_API_KEY` | 你的 GLM API Key | 从智谱开放平台获取 |
| `GITHUB_TOKEN` | 你的 GitHub PAT | 用于 API 推送 |
| `MINE_SEED` | `D:\projects\mine-seed` | 本地仓库根目录 |

**验证方式**：打开 PowerShell，输入：
```powershell
$env:TG_BOT_TOKEN
```
应输出你的 Token。

---

## 四、测试验证

### 4.1 测试 free_llm 连通性
```bash
cd mine-seed\05_TOOLS\miner
python -c "from free_llm import call; r = call('ping', max_tokens=10, prefer='glm'); print('OK:', r['channel'])"
```
预期输出：`OK: glm`

### 4.2 测试 adata 数据获取
```bash
cd mine-seed\05_TOOLS\advisor
python -c "import adata; df = adata.stock.info.all_code(); print('股票总数:', len(df))"
```
预期输出：`股票总数: 5500+`

### 4.3 测试 Telegram 推送
```bash
cd mine-seed\05_TOOLS\runtime
python local_runtime.py --test-tg
```
预期：你的 TG 收到一条测试消息。

### 4.4 测试 adata_advisor（荐股引擎）
```bash
cd mine-seed\05_TOOLS\advisor
python adata_advisor.py
```
预期：生成 `cloud/advisor/advisor_YYYYMMDD.md` 文件。

---

## 五、设置 Windows 计划任务

### 5.1 打开任务计划程序
Win+R → 输入 `taskschd.msc` → 回车

### 5.2 创建基本任务
1. 右侧点击 "创建基本任务"
2. 名称：`ACE_Runtime_Advisor`
3. 触发器：每天，时间 08:15（开盘前）
4. 操作：启动程序
5. 程序：`python`
6. 参数：`D:\projects\mine-seed\05_TOOLS\advisor\adata_advisor.py`
7. 起始于：`D:\projects\mine-seed\05_TOOLS\advisor`

### 5.3 创建更多任务（按需）

| 任务名 | 时间 | 程序 | 参数 |
|--------|------|------|------|
| ACE_Miner | 每4小时 | python | `..\miner\miner_24h_free.py` |
| ACE_Signals | 每天 09:30 | python | `..\signals\signal_discovery_a.py` |
| ACE_Archivist | 每天 20:00 | python | `..\memory\archivist.py` |
| ACE_Liveness | 每小时 | python | `..\runtime\local_runtime.py --heartbeat` |

### 5.4 重要设置
- 勾选 "不管用户是否登录都要运行"
- 勾选 "使用最高权限运行"
- 配置中设置 "如果任务失败，每隔 10 分钟重启，最多 3 次"

---

## 六、可选增强（推荐后续做）

### 6.1 安装 Ollama（本地 LLM 兜底）
- [ ] 下载安装 Ollama for Windows：https://ollama.com/download
- [ ] 拉取轻量模型：`ollama pull qwen2.5:3b`
- [ ] 验证：`ollama run qwen2.5:3b` → 输入 "你好" 测试

### 6.2 安装 a-stock-data（本地增强数据源）
```bash
pip install mootdx
```
- 提供通达信本地数据解析
- 需要配合券商交易软件导出数据

### 6.3 配置本地 Gateway（如需完整矿场）
- 如需运行原版 `miner_24h.py`（含 Registry/Router/Judge）
- 需额外安装 Node.js 并启动 Gateway 服务
- **建议**：先用 `miner_24h_free.py`，功能已足够

---

## 七、文件映射（云端 → 本地）

| 云端文件 | 本地路径 | 说明 |
|----------|----------|------|
| `05_TOOLS/miner/free_llm.py` | `mine-seed/05_TOOLS/miner/free_llm.py` | 核心：0依赖LLM客户端 |
| `05_TOOLS/miner/run_free_task.sh` | `mine-seed/05_TOOLS/miner/run_free_task.sh` | 调度器（Linux crontab用） |
| `05_TOOLS/miner/miner_24h_free.py` | `mine-seed/05_TOOLS/miner/miner_24h_free.py` | 矿场v6（free_llm版） |
| `05_TOOLS/advisor/adata_advisor.py` | `mine-seed/05_TOOLS/advisor/adata_advisor.py` | 荐股引擎（adata+free_llm） |
| `05_TOOLS/advisor/stock_advisor.py` | `mine-seed/05_TOOLS/advisor/stock_advisor.py` | 荐股fallback |
| `05_TOOLS/signals/signal_discovery_a.py` | `mine-seed/05_TOOLS/signals/signal_discovery_a.py` | A股信号发现 |
| `05_TOOLS/runtime/local_runtime.py` | `mine-seed/05_TOOLS/runtime/local_runtime.py` | 本地运行时 |
| `05_TOOLS/miner/free_api.env` | `mine-seed/05_TOOLS/miner/free_api.env` | API密钥配置模板 |

---

## 八、快速启动命令（一次性复制给 code）

```powershell
# 1. 安装依赖
pip install adata requests python-telegram-bot

# 2. 克隆仓库
cd D:\projects
git clone https://github.com/opelleda/mine-seed.git

# 3. 设置环境变量（在系统设置中手动配置 TG_BOT_TOKEN, TG_CHAT_ID 等）

# 4. 测试
cd mine-seed\05_TOOLS\advisor
python adata_advisor.py

# 5. 查看输出
cat ..\..\cloud\advisor\advisor_*.md
```

---

## 九、故障排查

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError: No module named 'adata'` | `pip install adata` |
| `free_llm 所有渠道失败` | 检查 GLM_API_KEY 是否设置正确 |
| `TG 推送失败` | 检查 TG_BOT_TOKEN 和 TG_CHAT_ID，确保 Bot 已加入对应频道 |
| `adata 获取不到数据` | 检查网络，adata 会多源自动切换，重试即可 |
| `Windows 计划任务不执行` | 检查 "起始于" 路径是否正确，勾选 "使用最高权限" |

---

**状态**：云端部分 ✅ 已完成 | 本地部分 ⏳ 待 code 执行
