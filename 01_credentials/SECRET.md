# 🔐 核心凭证总表 — 疯子Agent（完整版）

> ⚠️ 此仓库为私有仓库，务必保持私密
> 最后更新: 2026-06-29
> 所有Key均来自运行中的 miner_env.sh，与生产环境实时同步

---

## 一、算力层 — 主力军团

### 1. NVIDIA NIM（16个Key）

**Base:** https://integrate.api.nvidia.com/v1

| # | Key | 专用模型 |
|---|-----|---------|
| 1 | `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` | 通用 |
| 2 | `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` | 通用 |
| 3 | `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` | 通用 |
| 4 | `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` | 通用 |
| 5 | `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` | 通用 |
| 6 | `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` | 通用 |
| 7 | `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` | 通用 |
| 8 | `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` | 通用 |
| 9 | `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` | 通用 |
| 10 | `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` | deepseek-ai/deepseek-v4-pro |
| 11 | `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` | nvidia/nemotron-3-ultra-550b-a55b |
| 12 | `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` | stepfun-ai/step-3.7-flash |
| 13 | `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` | minimaxai/minimax-m3 |
| 14 | `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` | stepfun-ai/step-3.7-flash |
| 15 | `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` | mistral-medium-3.5-128b |
| 16 | `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` | deepseek-ai/deepseek-v4-pro |
### 2. GitHub Models
- Token: `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`
- Base: https://models.inference.ai.azure.com

### 3. 智谱 GLM
- Key: `c4c766faaf974bfaba30f381ccc7b066.E7VUlQfxnMXnvVRx`
- Base: https://open.bigmodel.cn/api/paas/v4

### 4. 魔搭 ModelScope
- Key: `ms-7ab1f34e-efae-4a0b-a26d-5ed25eef9d07`
- Base: https://api-inference.modelscope.cn/v1

### 5. SambaNova（免费$5额度）
- Key: `820feeb9-0201-4312-8c0e-900206a4d2b9`
- Base: https://api.sambanova.ai/v1

---

## 二、补充弹药 — 备用算力

### API易（含Gemini中转通道）
- Key: `sk-xQrs9IDbjK2LJpFh1d947b41A1B449A4Be0dD8Bf3a7cDc8b`
- Base: https://api.apiyi.com
- 说明: Gemini Flash/Pro 通过API易中转调用，无独立Google Key

### OpenRouter
- Key: `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`
- Base: https://openrouter.ai/api/v1
- 说明: 原 Key 已失效，2026-07-01 更新。可用模型: qwen/qwen3.7-plus、qwen/qwen-2.5-72b-instruct

### HuggingFace（DNS被墙）
- Key: `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`

---

## 三、基础设施

### OneAPI
- 地址: http://localhost:3000
- 管理员: admin2 / admin123
- Token-miner: `jHhtKnCuHVriXUaHC992D9B645D44e8a9c901625A17fCd41`
- Token-miner2: `GfvnDi2dJuixs7jUDb3543D894E14eA483AeA4Da73290217`
- Admin Token: `3ba2c187fe7f430cb56bdc5b396b8fb2`

### Telegram
- API ID: `38398440`
- Hash: `3460f304c16a186c2300debc673b2ed0`
- 手机: `+85592538691`
- 两步密码: `Qq364828`
- Bot1: `8384310757:AAEhfTTMaYrV_n9hXFjBUMh2LdeeWkB-Czo`
- Bot2: `8446702999:AAHw51HYX_EwZhnzmJpQFUy734SnaZpzsCI`

### GitHub PAT（coze-assets仓库访问用）
- `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`

---

## 四、觅游社区
- Base: https://www.meyo123.com/api/v1
- Creds: ~/.meyo/credentials.json
- Agent ID: `01KVFAJ2DV6N40PTY5Z2WN7W9C` (agent_5f2a96)

---

## 五、Google Gemini

### Key #1（2026-06-16 老板提供）

- `AQ.Ab8RN6IhjKRabd7VkRFh1IBod3S_ade2QkJwDSrifNoTgmOXGg`


### Key #2（2026-06-19 新增）

- `AQ.Ab8RN6IFCwwdAZ7aUP4uBF_9QgzEN6k4cbOkIjVTqtuABjO0Hw`


### 调用方式

- Endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent

- 模型: gemini-flash-latest

- 定位: Google免费层新矿工，待接入矿场测试


### 补充说明

- 原生通道(type=24)直连不通+Key格式兼容问题尚未解决

- 当前Gemini Flash/Pro仍通过API易中转（OneAPI channel 87/92）

