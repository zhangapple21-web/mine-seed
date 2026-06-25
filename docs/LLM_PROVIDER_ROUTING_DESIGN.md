# LLM Provider 路由与密钥隔离方案（设计稿）

目标：把你给的三组 LLM 供应商（主力 API易 → 备用 OpenRouter → 备用 Gemini）做成“可替换节点”，并确保**密钥永不进入开源仓库**，同时允许脚本/自动任务按优先级自动切换。

## 设计原则

- 结构 → 协议 → 记忆 → 路由 → 模型：供应商与模型是执行层，可替换
- 密钥不进 Git：任何 token/key 只允许存在于本地 `.secrets/` 或环境变量
- 可审计：仓库里保留“配置模板 + 路由规则 + 日志格式”，不保留密钥

## 文件与目录

### 1) 仓库内（可开源）

- `docs/llm_providers.example.json`
  - 不含密钥，只包含字段结构与优先级示例
- `05_TOOLS/llm_provider/`
  - `provider_router.py`：读取本地密钥配置并按优先级选择可用 provider
  - `README.md`：如何使用/如何验证/如何排障

### 2) 本地（不进 Git）

由于 `.gitignore` 已忽略 `.secrets/`，密钥文件放这里：

- `.secrets/llm_providers.json`
  - 只在本机存在，包含真实 key 与 endpoint
  - 由 `provider_router.py` 读取

## 路由规则（确定性）

优先级：主力 → 备用1 → 备用2

每次调用前先做“轻量健康检查”（例如对 provider 的 `/models` 或等价 endpoint 做一次短超时探测）：

1. 主力可用则使用主力
2. 主力不可用则切备用1
3. 备用1不可用则切备用2
4. 三者都不可用：返回明确错误 + 记录日志（不包含密钥）

## 日志与可观测性

写到（仓库内可追溯，不含密钥）：

- `mine-seed/02_MEMORY/recent_memory/daily/YYYY-MM-DD-trae-auto.md`

每次记录：

- 选择了哪个 provider（仅名字）
- 是否发生 fallback
- 健康检查失败原因（HTTP code / timeout / DNS 等）

## 用户需要做的一步（不可替代）

由于安全原因，我不能把你在聊天里贴的明文 key 写入任何文件或命令行（会在日志中二次泄露）。

但我会把 **模板、脚本、路由逻辑、PR** 全部准备好；你只需要把三组 key 粘贴进本地文件：

- `mine-seed/.secrets/llm_providers.json`

粘贴一次即可，后续自动任务会一直使用，并且不会被提交到 GitHub。

## 验收标准

1. 仓库内无任何明文 key
2. 本地放入 `.secrets/llm_providers.json` 后：
   - 路由脚本能按优先级选中 provider
   - 主力不可用时能自动 fallback
3. 自动任务日志能记录 provider 选择与 fallback（不泄露密钥）

