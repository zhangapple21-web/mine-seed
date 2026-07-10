#!/bin/bash
# 矿场环境变量 - 所有API凭证集中管理
# 用法: source miner_env.sh && python3 miner_24h.py
# v2.0 - 新增 Cerebras / SiliconFlow / Ollama 免费渠道

# === One API ===
export MINER_API_BASE="http://localhost:3000/v1/chat/completions"
export MINER_API_KEY="{{ONE_API_KEY}}"

# === One API Admin ===
export ONEAPI_ADMIN_TOKEN="{{ONEAPI_ADMIN_TOKEN}}"

# === NVIDIA NIM Keys (16 key 轮询) ===
export NIM_KEY_1="{{NIM_KEY_1}}"
export NIM_KEY_2="{{NIM_KEY_2}}"
export NIM_KEY_3="{{NIM_KEY_3}}"
export NIM_KEY_4="{{NIM_KEY_4}}"
export NIM_KEY_5="{{NIM_KEY_5}}"
export NIM_KEY_6="{{NIM_KEY_6}}"
export NIM_KEY_7="{{NIM_KEY_7}}"
export NIM_KEY_8="{{NIM_KEY_8}}"
export NIM_KEY_9="{{NIM_KEY_9}}"
export NIM_KEY_10="{{NIM_KEY_10}}"
export NIM_KEY_11="{{NIM_KEY_11}}"
export NIM_KEY_12="{{NIM_KEY_12}}"
export NIM_KEY_13="{{NIM_KEY_13}}"
export NIM_KEY_14="{{NIM_KEY_14}}"
export NIM_KEY_15="{{NIM_KEY_15}}"
export NIM_KEY_16="{{NIM_KEY_16}}"

# === GitHub Models (免费, 限流) ===
export GITHUB_PAT="{{GITHUB_PAT}}"

# === 智谱GLM (免费无限) ===
export ZHIPU_KEY="{{ZHIPU_KEY}}"

# === Telegram ===
export TG_BOT_TOKEN_1="{{TG_BOT_TOKEN_1}}"
export TG_BOT_TOKEN_2="{{TG_BOT_TOKEN_2}}"

# === SambaNova (免费额度) ===
export SAMBANOVA_KEY="{{SAMBANOVA_KEY}}"
export SAMBANOVA_BASE="https://api.sambanova.ai/v1"

# === OpenRouter (29+ 免费模型, 免信用卡) ===
export OPENROUTER_KEY="{{OPENROUTER_KEY}}"
export OPENROUTER_BASE="https://openrouter.ai/api/v1"

# === HuggingFace ===
export HF_KEY="{{HF_KEY}}"

# === Cerebras (每天100万Token免费, 无需信用卡) ===
# 注册: https://cloud.cerebras.ai
# 特点: Llama 3.3 70B @ 2600+ tokens/s, 每天100万Token, UTC 00:00 重置
export CEREBRAS_KEY="{{CEREBRAS_KEY}}"

# === SiliconFlow 硅基流动 (免费额度) ===
# 注册: https://siliconflow.cn
# 特点: DeepSeek-R1, Qwen2.5-72B 等国产模型免费额度
export SILICONFLOW_KEY="{{SILICONFLOW_KEY}}"

# === Ollama 本地模型 (Windows 本地, 零成本) ===
# 需要在 Windows 本地安装 Ollama 并启动: ollama serve
# TRAE 沙箱通过 host.docker.internal 访问宿主 Windows
export OLLAMA_BASE="http://host.docker.internal:11434/v1"

# === Signal Discovery Models ===
export SIGNAL_MODEL="glm-4-flash"
export CODE_MODEL="glm-4-flash"
export ADVISOR_MODEL="glm-4-flash"

# === 模型优先级配置 (Gateway 权重) ===
# Tier 1 (weight=5): Ollama 本地 (免费, 私有, 无审查)
# Tier 2 (weight=3): GLM-4-flash (免费无限, 中文强)
# Tier 3 (weight=2): GitHub Models / NIM / OpenRouter / Cerebras
# Tier 4 (weight=1): SambaNova / SiliconFlow

echo "矿场环境变量 v2.0 已加载"
echo "渠道: GLM(免费) + NIM(16key) + GitHub + OpenRouter + Cerebras + SiliconFlow + Ollama(本地)"
