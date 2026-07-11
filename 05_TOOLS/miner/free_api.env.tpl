#!/bin/bash
# ACE Runtime — 免费 API 环境变量模板
# 用法: 复制为 free_api.env 并填入真实密钥
# source free_api.env

# === 智谱 GLM（免费无限量，主力）===
export GLM_KEY="YOUR_GLM_KEY"
export GLM_BASE="https://open.bigmodel.cn/api/paas/v4/chat/completions"
export GLM_MODEL="glm-4-flash"

# === NVIDIA NIM（16 key 轮询，次主力）===
export NIM_BASE="https://integrate.api.nvidia.com/v1/chat/completions"
export NIM_KEY_1="nvapi-YOUR_KEY_1"
export NIM_KEY_2="nvapi-YOUR_KEY_2"
# ... NIM_KEY_3 到 NIM_KEY_16 同理
export NIM_MODEL="meta/llama-3.1-8b-instruct"

# === GitHub Models（免费限流，备用）===
export GH_MODELS_BASE="https://models.inference.ai.azure.com/chat/completions"
export GH_MODELS_KEY="YOUR_GITHUB_PAT"
export GH_MODELS_MODEL="gpt-4o-mini"

# === Ollama（本地，完全免费）===
export OLLAMA_BASE="http://localhost:11434/api/chat"
export OLLAMA_MODEL="qwen2.5:7b"

# === ntfy.sh 推送 ===
export NTFY_SERVER="https://ntfy.sh"
export NTFY_TOPIC="ace-stock-advisor"

# === 路径 ===
export MINE_SEED="/workspace/fengzi-repos/mine-seed"
export OUTPUT_DIR="/tmp/mine_output"
export CLOUD_DIR="$MINE_SEED/cloud"

mkdir -p "$OUTPUT_DIR" "$CLOUD_DIR/advisor" "$CLOUD_DIR/miner" "$CLOUD_DIR/signals" "$CLOUD_DIR/research"
