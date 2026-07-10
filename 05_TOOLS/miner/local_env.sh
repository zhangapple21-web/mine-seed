#!/bin/bash
# 本地（非Coze容器）路径适配层
# 用法: source local_env.sh && python3 miner_24h.py

export ONE_API_URL="http://localhost:3000/v1/chat/completions"
export ONE_API_KEY="jHhtKnCuHVriXUaHC992D9B645D44e8a9c901625A17fCd41"
export SIGNAL_MODEL="deepseek-ai/deepseek-v4-flash"
export CODE_MODEL="deepseek-ai/deepseek-v4-flash"
export ADVISOR_MODEL="glm-4-flash"

# 创建兼容目录结构
mkdir -p /tmp/mine_output/signals
mkdir -p /tmp/mine_output/observation_log.json

# 路径覆盖
export REPO_DIR="/workspace/fengzi-repos/mine-seed"
export TEMPLATE_DIR="/workspace/fengzi-repos/mine-seed/05_TOOLS/signals/template"
export DATA_DIR="/tmp/sp500_data"
export OUTPUT_DIR="/tmp/mine_output"
