#!/bin/bash
# 知识午班脚本 - 每日12:00
# P2任务，遇P0/P1资源紧张立即暂停
# 优先级：原则压缩 > 协议生成 > 溯源探索

source /home/coze/miner_env.sh

LOG="/home/coze/mine_output/knowledge/knowledge_noon.log"
echo "=== Knowledge Noon Shift $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

# 运行档案官
cd /home/coze
python3 /home/coze/archivist.py >> "$LOG" 2>&1

echo "=== Knowledge Noon Shift Done $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
