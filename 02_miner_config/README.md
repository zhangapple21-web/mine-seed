# 矿场环境变量

## 运行前要求

请不要将真实 API Key、GitHub PAT、Telegram token 或其他机密写入仓库文件。
所有秘密必须通过环境变量、宿主机 secret store 或 `.env.local` 注入，不要提交到 Git。

## 推荐配置方式

```bash
export GITHUB_USER="zhangapple21-web"
export GITHUB_TOKEN="<your-token>"
export NIM_KEY_1="<key>"
export NIM_KEY_2="<key>"
export GH_MODELS_KEY="<key>"
export ZHIPU_KEY="<key>"
export TG_BOT_TOKEN_1="<token>"
```

可参考模板：`02_miner_config/.env.example`

## 关键变量

| 变量 | 用途 | 备注 |
|------|------|------|
| `GITHUB_USER` | GitHub 用户名 | 例如 `zhangapple21-web` |
| `GITHUB_TOKEN` | GitHub PAT / API 认证 | 仅在运行时注入，不写入仓库 |
| `NIM_KEY_1..N` | NVIDIA NIM Keys | 通过环境变量提供 |
| `GH_MODELS_KEY` | GitHub Models Key | 避免写死在脚本中 |
| `ZHIPU_KEY` | 智谱 GLM Key | 避免写死在脚本中 |
| `TG_BOT_TOKEN_1..N` | Telegram Bot Token | 仅本地或 secret store |

## 约束系统

- 约束文件: `routing_constraints.json`
- 版本: v5，21条 ACTIVE
- 核心保护: `nim_mistral_675b`（基准）、拦截低效 worker

## 常用命令

```bash
source 02_miner_config/.env.local
python3 /home/coze/miner_24h.py
bash /home/coze/signal_cron.sh
bash /home/coze/seed_archive.sh
tail -n 50 /home/coze/mine_output/cron.log
```

## 安全要求

- 绝不在仓库内保留真实 PAT / token
- 绝不在脚本里硬编码 `https://user:token@github.com/...`
- 绝不将 `SECRET.md`、`miner_env.sh`、`.env` 提交到 Git
- 仅在运行时读取环境变量、secrets manager 或本地 `.env.local`
