#!/bin/bash
# Stock Advisor 每日荐股 + 推送
# 用法: bash run_stock_advisor.sh
# 时间: 每天 08:15 (A股开盘前)

set -e

# 加载环境变量
ENV_SH="/workspace/fengzi-repos/coze-assets/02_miner_config/miner_env.sh"
if [ -f "$ENV_SH" ]; then
    while IFS= read -r line; do
        line=$(echo "$line" | sed 's/^export //')
        if echo "$line" | grep -q "="; then
            key=$(echo "$line" | cut -d= -f1)
            val=$(echo "$line" | cut -d= -f2- | sed 's/^"//;s/"$//;s/^\x27//;s/\x27$//')
            export "$key=$val" 2>/dev/null || true
        fi
    done < "$ENV_SH"
fi

# 启动 Gateway（如果死了）
if ! curl -s http://localhost:3000/api/status > /dev/null 2>&1; then
    echo "[ADVISOR] Starting Gateway..."
    cd /workspace/one-api-data
    nohup python3 ace_gateway.py > gateway.log 2>&1 &
    for i in {1..15}; do
        curl -s http://localhost:3000/api/status > /dev/null 2>&1 && break
        sleep 1
    done
fi

# 确保输出目录存在
mkdir -p /tmp/mine_output/advisor

# 运行 Stock Advisor
echo "[ADVISOR] Running stock_advisor.py..."
cd /workspace/fengzi-repos/mine-seed/05_TOOLS/advisor

# 尝试运行，失败则用 Gateway 生成降级报告
python3 stock_advisor.py > /tmp/mine_output/advisor/advisor_run.log 2>&1

# 检查报告是否生成
REPORT_FILE="/tmp/mine_output/advisor/advisor_$(date +%Y%m%d).md"
if [ ! -f "$REPORT_FILE" ]; then
    echo "[ADVISOR] Report not generated, trying fallback..."
    # 降级：用 Gateway 生成市场概览
    python3 -c "
import requests, json, datetime
today = datetime.datetime.now().strftime('%Y-%m-%d')
report = f'''# A股每日荐股报告 — {today}

## 市场概览

> [FALLBACK] 实时数据获取失败，以下为模板报告。

## 免责声明

本报告由 ACE Runtime 自动生成，仅供参考，不构成投资建议。

## 风险提示

股市有风险，投资需谨慎。
'''
with open('$REPORT_FILE', 'w') as f:
    f.write(report)
print(f'[ADVISOR] Fallback report: $REPORT_FILE')
"
fi

# 推送到 ntfy.sh（沙箱内可用）
echo "[ADVISOR] Pushing to ntfy.sh..."
cd /workspace/fengzi-repos/mine-seed/05_TOOLS/miner
python3 ntfy_push.py --file "$REPORT_FILE" --topic ace-stock-advisor

# 尝试推送到 TG（如果网络允许）
echo "[ADVISOR] Trying TG push..."
export TG_BOT_TOKEN_1="8384310757:AAEhfTTMaYrV_n9hXFjBUMh2LdeeWkB-Czo"
python3 tg_push.py --file "$REPORT_FILE" 2>/dev/null || echo "[ADVISOR] TG push failed (network limit), ntfy.sh already sent"

# 保存到 mine-seed
mkdir -p /workspace/fengzi-repos/mine-seed/02_MEMORY/daily_reports/advisor
cp "$REPORT_FILE" /workspace/fengzi-repos/mine-seed/02_MEMORY/daily_reports/advisor/

# git commit
cd /workspace/fengzi-repos/mine-seed
git add 02_MEMORY/daily_reports/advisor/ 2>/dev/null || true
git commit -m "daily: stock advisor $(date +%Y%m%d)" 2>/dev/null || true
git push origin main 2>/dev/null || true

echo "[ADVISOR] Done at $(date)"
