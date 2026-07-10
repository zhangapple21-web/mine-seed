#!/bin/bash
# A股自动荐股引擎调度脚本
# advisor_cron.sh

# 设置环境
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# source miner_env.sh 如果存在
if [ -f "$PROJECT_DIR/miner_env.sh" ]; then
    source "$PROJECT_DIR/miner_env.sh"
fi

# 日志
LOG_DIR="$PROJECT_DIR/mine_output/advisor"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/advisor_cron.log"

# 时间戳
echo "========================================" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 荐股引擎调度开始" >> "$LOG_FILE"

# 运行荐股引擎
cd "$PROJECT_DIR"
python3 "$SCRIPT_DIR/stock_advisor.py" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "$(date '+%Y-%m-%d %H:%M:%S') - 荐股引擎调度结束 (exit=$EXIT_CODE)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

exit $EXIT_CODE
