#!/bin/bash
# Cloud Stock Worker — 云端荐股 Worker
# 职责：生成荐股报告 → Push GitHub → ntfy.sh 保底通知 → 结束
# TG 推送由本地 Runtime 负责，本脚本不碰

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MINE_SEED="/workspace/fengzi-repos/mine-seed"
CLOUD_DIR="$MINE_SEED/cloud/advisor"
TODAY=$(date +%Y%m%d)
TODAY_MD=$(date +%Y-%m-%d)

echo "[STOCK-WORKER] ===== $(date) ====="
echo "[STOCK-WORKER] 云端荐股 Worker 启动"

# 1. 拉取最新 Repository
cd "$MINE_SEED"
git pull origin main 2>/dev/null || true

# 2. 加载环境变量
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

# 3. 启动 Gateway（如果死了）
if ! curl -s http://localhost:3000/api/status > /dev/null 2>&1; then
    echo "[STOCK-WORKER] Starting Gateway..."
    cd /workspace/one-api-data
    nohup python3 ace_gateway.py > gateway.log 2>&1 &
    for i in {1..15}; do
        curl -s http://localhost:3000/api/status > /dev/null 2>&1 && break
        sleep 1
    done
fi

# 4. 确保 cloud/ 目录存在
mkdir -p "$CLOUD_DIR"

# 5. 运行 Stock Advisor
REPORT_FILE="$CLOUD_DIR/advisor_${TODAY}.md"
echo "[STOCK-WORKER] Running stock_advisor.py..."

cd "$MINE_SEED/05_TOOLS/advisor"
if python3 stock_advisor.py > /tmp/mine_output/advisor/advisor_run.log 2>&1; then
    # 查找生成的报告
    LATEST_REPORT=$(find /tmp/mine_output/advisor -name "advisor_*.md" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    if [ -n "$LATEST_REPORT" ] && [ -f "$LATEST_REPORT" ]; then
        cp "$LATEST_REPORT" "$REPORT_FILE"
        echo "[STOCK-WORKER] Report generated: $REPORT_FILE"
    else
        echo "[STOCK-WORKER] Report not found, creating fallback..."
        _create_fallback_report
    fi
else
    echo "[STOCK-WORKER] stock_advisor.py failed, creating fallback..."
    _create_fallback_report
fi

# 6. 推送到 GitHub
echo "[STOCK-WORKER] Pushing to GitHub..."
cd "$MINE_SEED"
git add cloud/advisor/ 2>/dev/null || true
git commit -m "cloud: stock advisor report ${TODAY_MD}" 2>/dev/null || true
git push origin main 2>/dev/null || echo "[STOCK-WORKER] Git push may need auth"

# 7. ntfy.sh 保底通知
echo "[STOCK-WORKER] Sending ntfy.sh notification..."
cd "$SCRIPT_DIR"
python3 ntfy_push.py --file "$REPORT_FILE" --topic ace-stock-advisor 2>/dev/null || echo "[STOCK-WORKER] ntfy.sh failed"

# 8. 写入当日记忆（云端视角）
mkdir -p "$MINE_SEED/02_MEMORY/recent_memory/daily"
echo "# ${TODAY_MD} — Stock Worker 产出" >> "$MINE_SEED/02_MEMORY/recent_memory/daily/${TODAY_MD}-cloud.md"
echo "报告: cloud/advisor/advisor_${TODAY}.md" >> "$MINE_SEED/02_MEMORY/recent_memory/daily/${TODAY_MD}-cloud.md"
echo "推送: GitHub + ntfy.sh" >> "$MINE_SEED/02_MEMORY/recent_memory/daily/${TODAY_MD}-cloud.md"

echo "[STOCK-WORKER] Done at $(date)"
echo "[STOCK-WORKER] 本地 Runtime 将从 GitHub 拉取报告并推送到 TG"

_create_fallback_report() {
    cat > "$REPORT_FILE" << EOF
# A股每日荐股报告 — ${TODAY_MD}

> [FALLBACK] 实时数据获取失败，以下为模板报告。
> 云端 Worker 生成，本地 Runtime 将推送到 TG。

## 免责声明

本报告由 ACE Cloud Worker 自动生成，仅供参考，不构成投资建议。

## 风险提示

股市有风险，投资需谨慎。

---
生成时间: $(date)
Worker: Cloud Stock Worker
Gateway: localhost:3000
EOF
}
