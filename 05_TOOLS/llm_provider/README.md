# LLM Provider 路由器（主力 → 备用）

目的：把 LLM 供应商当作可替换执行节点，按优先级自动 fallback，同时保证密钥不进入开源仓库。

## 你需要准备什么

1. 仓库里已经有模板：`docs/llm_providers.example.json`
2. 你只需要把它复制到本地密钥目录并填写 `api_key`：

路径：`mine-seed/.secrets/llm_providers.json`

> `.secrets/` 已被 `.gitignore` 忽略，不会被提交到 GitHub。

## 配置格式

`llm_providers.json` 结构：

- `providers[]`：
  - `name`: string
  - `priority`: number（越小优先级越高）
  - `enabled`: bool
  - `base_url`: OpenAI-compatible provider 的 base url
  - `endpoint`: Gemini 的完整 endpoint（generateContent）
  - `api_key`: 密钥（只放本地）

## 用法

### 1) 自检（不打印密钥）

在 `mine-seed` 根目录运行：

```bash
python 05_TOOLS/llm_provider/provider_router.py
```

你应看到输出类似：

```text
providers_loaded= 3
- apiyi kind=openai priority=1 enabled=True
- openrouter kind=openai priority=2 enabled=True
- gemini kind=gemini priority=3 enabled=True
```

### 2) 在脚本里调用（OpenAI-compatible）

```python
from 05_TOOLS.llm_provider.provider_router import openai_chat_completions_with_fallback

resp = openai_chat_completions_with_fallback(
    messages=[{"role": "user", "content": "ping"}],
    model="gpt-4.1-mini",
)
print(resp["choices"][0]["message"]["content"])
```

## 安全规则

- 禁止把任何 `api_key` 写入仓库
- 禁止把 `.secrets/` 下的文件加入 git
- PR/日志里只允许记录 provider 名称与错误类型，不允许出现 key

