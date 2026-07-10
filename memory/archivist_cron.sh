#!/bin/bash
# 档案官定时任务脚本
# 每日20:04运行，矿场20:00班次结束后

# 加载环境变量
source /home/coze/miner_env.sh

# 运行档案官
cd /home/coze
python3 /home/coze/archivist.py >> /home/coze/mine_output/knowledge/archivist.log 2>&1

# 日志输出运行状态
echo "$(date '+%Y-%m-%d %H:%M:%S') - Archivist cron completed" >> /home/coze/mine_output/knowledge/archivist.log
