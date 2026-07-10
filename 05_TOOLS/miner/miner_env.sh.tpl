#!/bin/bash
# 矿场环境变量 - 所有API凭证集中管理
# 用法: source miner_env.sh && python3 miner_24h.py

# === One API ===
export MINER_API_BASE="http://localhost:3000/v1/chat/completions"
export MINER_API_KEY="{{ONE_API_KEY}}"

# === One API Admin ===
export ONEAPI_ADMIN_TOKEN="{{ONEAPI_ADMIN_TOKEN}}"

# === NVIDIA NIM Keys ===
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

# === GitHub Models ===
export GITHUB_PAT="{{GITHUB_PAT}}"

# === 智谱GLM ===
export ZHIPU_KEY="{{ZHIPU_KEY}}"

# === Telegram ===
export TG_BOT_TOKEN_1="{{TG_BOT_TOKEN_1}}"
export TG_BOT_TOKEN_2="{{TG_BOT_TOKEN_2}}"

# === SambaNova ===
export SAMBANOVA_KEY="{{SAMBANOVA_KEY}}"
export SAMBANOVA_BASE="https://api.sambanova.ai/v1"

# === OpenRouter ===
export OPENROUTER_KEY="{{OPENROUTER_KEY}}"
export OPENROUTER_BASE="https://openrouter.ai/api/v1"

# === HuggingFace ===
export HF_KEY="{{HF_KEY}}"

# === Signal Discovery Models ===
export SIGNAL_MODEL="glm-4-flash"
export CODE_MODEL="glm-4-flash"
export ADVISOR_MODEL="glm-4-flash"

echo "矿场环境变量已加载"
