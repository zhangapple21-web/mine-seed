#!/bin/bash
# 矿场环境变量 - 所有API凭证集中管理
# 用法: source miner_env.sh && python3 miner_24h.py

# === One API ===
export MINER_API_BASE="http://localhost:3000/v1/chat/completions"
export MINER_API_KEY="{{ONE_API_KEY}}"

# === One API Admin ===
export ONEAPI_ADMIN_TOKEN="3ba2c187fe7f430cb56bdc5b396b8fb2"

# === NVIDIA NIM Keys (8号) ===
export NIM_KEY_1="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"
export NIM_KEY_2="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"
export NIM_KEY_3="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"
export NIM_KEY_4="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"
export NIM_KEY_5="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"
export NIM_KEY_6="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"
export NIM_KEY_7="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"
export NIM_KEY_8="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"

# === GitHub Models ===
export GITHUB_PAT="{{GITHUB_PAT}}"

# === 智谱GLM ===
export ZHIPU_KEY="c4c766faaf974bfaba30f381ccc7b066.E7VUlQfxnMXnvVRx"

# === Telegram ===
export TG_API_ID="38398440"
export TG_API_HASH="3460f304c16a186c2300debc673b2ed0"
export TG_PHONE="+85592538691"
export TG_BOT_TOKEN_1="8384310757:AAEhfTTMaYrV_n9hXFjBUMh2LdeeWkB-Czo"
export TG_BOT_TOKEN_2="8446702999:AAHw51HYX_EwZhnzmJpQFUy734SnaZpzsCI"

echo "✅ 矿场环境变量已加载"
export NIM_KEY_9="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"
export NIM_KEY_10="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"
export NIM_KEY_11="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"
export NIM_KEY_12="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"

# === NIM Dedicated Model Keys ===
# KEY_10: deepseek-ai/deepseek-v4-pro专用
# KEY_11: nvidia/nemotron-3-ultra-550b-a55b专用
# KEY_12: stepfun-ai/step-3.7-flash专用

# === SambaNova (免费$5额度, OpenAI兼容) ===
export SAMBANOVA_KEY="820feeb9-0201-4312-8c0e-900206a4d2b9"
export SAMBANOVA_BASE="https://api.sambanova.ai/v1"

# OpenRouter Free Tier (added 2026-06-13)
export OPENROUTER_KEY="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"
export OPENROUTER_BASE="https://openrouter.ai/api/v1"

# HuggingFace (added 2026-06-13, DNS blocked)
export HF_KEY=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

# === Signal Discovery Models (2026-06-13: deepseek unreachable, fallback to glm) ===
export SIGNAL_MODEL="glm-4-flash"
export CODE_MODEL="glm-4-flash"
export ADVISOR_MODEL="glm-4-flash"

# === NIM New Keys (2026-06-14 老板提供) ===
export NIM_KEY_13="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"
export NIM_KEY_14="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"
# KEY_13: minimaxai/minimax-m3专用
# KEY_14: stepfun-ai/step-3.7-flash专用

# NIM_KEY_15: mistral-medium-3.5-128b专用 (2026-06-14)
export NIM_KEY_15="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"
# NIM_KEY_16: deepseek-v4-pro专用 (2026-06-14)
export NIM_KEY_16="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"
