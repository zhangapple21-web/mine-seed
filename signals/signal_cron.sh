#!/bin/bash
source /home/coze/miner_env.sh
cd /home/coze

echo "=== Signal Discovery Cron $(date) ==="

# deepseek API不可达，改用glm-4-flash (2026-06-13)
export SIGNAL_MODEL="glm-4-flash"
export CODE_MODEL="glm-4-flash"

# 轮流跑不同类型信号
SIGNAL_TYPES=("momentum signals" "volatility signals" "mean reversion signals" "volume price divergence signals")
HOUR=$(date +%H)
IDX=$(( (HOUR / 4) % 4 ))
REQUEST="${SIGNAL_TYPES[$IDX]}"

echo "Running: $REQUEST (model=$SIGNAL_MODEL)"
timeout 300 python3 /home/coze/signal_discovery.py "$REQUEST" 2>&1

echo "=== Signal Cron Done $(date) ==="
