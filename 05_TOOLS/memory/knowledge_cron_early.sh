#!/bin/bash
# 知识早班脚本 - 每日05:00
# P2任务，遇P0/P1资源紧张立即暂停
# 优先级：R1遗产压缩 > 原则压缩 > 协议生成

source /home/coze/miner_env.sh

LOG="/home/coze/mine_output/knowledge/knowledge_early.log"
echo "=== Knowledge Early Shift $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

# 运行档案官（如果尚未运行）
cd /home/coze
python3 /home/coze/archivist.py >> "$LOG" 2>&1

echo "=== Knowledge Early Shift Done $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
