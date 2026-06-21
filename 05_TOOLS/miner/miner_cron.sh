#!/bin/bash
# 矿场cron运行器 v3 - v5任务路由+裁判+经验层
LOCKFILE="/tmp/miner_shift.lock"

if [ -f "$LOCKFILE" ]; then
    PID=$(cat "$LOCKFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[$(date)] 上一班次还在跑(PID=$PID)，跳过"
        exit 0
    fi
    rm -f "$LOCKFILE"
fi

echo $$ > "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

# 加载环境变量
source /home/coze/miner_env.sh

# 运行v5矿场
cd /home/coze
python3 miner_24h.py $(date +%H)

# 班次结束后压缩经验
python3 experience_engine.py >> /home/coze/mine_output/experience.log 2>&1
