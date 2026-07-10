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

# 预检：worker_registry.json完整性检查
if [ -f /home/coze/worker_registry.json ]; then
    SIZE=$(stat -c%s /home/coze/worker_registry.json 2>/dev/null || echo 0)
    if [ "$SIZE" -lt 10 ]; then
        echo "[Wed Jul  1 10:45:07 AM CST 2026] ⚠️ worker_registry.json异常(0字节/$SIZE bytes)，从备份恢复"
        cp /home/coze/coze-assets/02_miner_config/worker_registry.json /home/coze/worker_registry.json
        echo "[Wed Jul  1 10:45:07 AM CST 2026] ✅ 已从coze-assets备份恢复"
    else
        python3 -c "import json; json.load(open('/home/coze/worker_registry.json'))" 2>/dev/null || {
            echo "[Wed Jul  1 10:45:07 AM CST 2026] ⚠️ worker_registry.json损坏(JSON解析失败)，从备份恢复"
            cp /home/coze/coze-assets/02_miner_config/worker_registry.json /home/coze/worker_registry.json
            echo "[Wed Jul  1 10:45:07 AM CST 2026] ✅ 已从coze-assets备份恢复"
        }
    fi
fi

# 运行v5矿场
cd /home/coze
python3 miner_24h.py $(date +%H)

# 班次结束后压缩经验
python3 experience_engine.py >> /home/coze/mine_output/experience.log 2>&1
