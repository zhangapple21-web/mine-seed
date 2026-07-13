#!/bin/bash
# ACE Runtime — 0 依赖任务调度器
# crontab 触发 → source free_api.env → 执行任务 → push GitHub → ntfy 通知
# 不依赖 TRAE 额度，不依赖 Gateway

# 用法: bash run_free_task.sh <task_name>
# task_name: advisor | miner | signals | research_morning | research_noon | archivist | liveness

# set -e  # 不用 set -e，让任务失败不阻塞后续

TASK="${1:-help}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TODAY=$(date +%Y%m%d)
LOG_FILE="/tmp/mine_output/${TASK}_${TIMESTAMP}.log"

# 加载免费 API 环境
source "$SCRIPT_DIR/free_api.env"

echo "[TASK] ===== $TASK @ $(date) =====" | tee "$LOG_FILE"

# === Git push 函数（GitHub API 直推，不依赖 git CLI）===
git_push() {
    # 用 GitHub API 直推 cloud/ 目录下的新文件
    for f in "$CLOUD_DIR"/*/*.md; do
        [ -f "$f" ] || continue
        # 只推今天的新文件
        if [[ "$f" == *"$TODAY"* ]] || [[ "$f" == *"$(date +%Y%m%d)"* ]]; then
            repo_path="${f#$MINE_SEED/}"
            python3 "$SCRIPT_DIR/github_push.py" --file "$f" --path "$repo_path" \
                --message "cloud: $TASK $TODAY (free API)" 2>/dev/null || true
        fi
    done
}

# === ntfy 通知函数（走代理）===
ntfy_notify() {
    local title="$1"
    local message="$2"
    local priority="${3:-default}"
    # ntfy.sh 需要走代理
    export http_proxy="http://127.0.0.1:18080"
    export https_proxy="http://127.0.0.1:18080"
    # 用 python3 脚本文件避免 heredoc 编码问题
    python3 "$SCRIPT_DIR/ntfy_send.py" "$title" "$message" "$priority" 2>&1 || echo "[NTFY] Failed"
}

# ============================================================
# 任务定义
# ============================================================

case "$TASK" in
    advisor)
        echo "[ADVISOR] 每日荐股（免费 API）" | tee -a "$LOG_FILE"
        cd "$MINE_SEED/05_TOOLS/advisor"
        
        # 优先用 adata 增强版（全市场扫描 + K线 + 资金流向 + free_llm）
        echo "[ADVISOR] 运行 adata 增强版荐股引擎..." | tee -a "$LOG_FILE"
        python3 adata_advisor.py >> "$LOG_FILE" 2>&1
        
        # 检查是否成功生成
        if [ -f "$CLOUD_DIR/advisor/advisor_${TODAY}.md" ]; then
            echo "[ADVISOR] adata 增强版成功" | tee -a "$LOG_FILE"
        else
            # Fallback 到 stock_advisor.py（固定股票池 + 腾讯 API）
            echo "[ADVISOR] adata 版失败，fallback 到 stock_advisor.py..." | tee -a "$LOG_FILE"
            export ONE_API_URL=""
            export FREE_LLM_MODE=1
            python3 stock_advisor.py >> "$LOG_FILE" 2>&1 || {
                # 终极降级：free_llm 直接生成
                echo "[ADVISOR] 终极降级: free_llm 直接生成" | tee -a "$LOG_FILE"
                python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
from free_llm import call
import datetime
today = datetime.datetime.now().strftime('%Y-%m-%d')
result = call(
    f'你是A股市场分析师。生成今日({today})的简短荐股报告，推荐2只股票。格式：Markdown。',
    system='你是专业的A股投资顾问。',
    max_tokens=1000,
    prefer='glm'
)
report = f'# A股每日荐股 — {today}\n\n{result[\"content\"]}\n\n---\n渠道: {result[\"channel\"]}/{result[\"model\"]} | 耗时: {result[\"elapsed\"]:.1f}s\n'
outfile = f'$CLOUD_DIR/advisor/advisor_{today.replace(\"-\",\"\")}.md'
with open(outfile, 'w') as f: f.write(report)
print(f'Report: {outfile}')
" >> "$LOG_FILE" 2>&1
            }
            
            # 复制到 cloud/
            ADVISOR_OUT="$MINE_SEED/05_TOOLS/mine_output/advisor"
            LATEST=$(find "$ADVISOR_OUT" -name "advisor_*.md" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
            if [ -n "$LATEST" ]; then
                cp "$LATEST" "$CLOUD_DIR/advisor/advisor_${TODAY}.md" 2>/dev/null || true
            fi
        fi
        
        git_push
        ntfy_notify "每日荐股 $TODAY" "荐股报告已生成，见 GitHub cloud/advisor/" "high"
        ;;
    
    miner)
        echo "[MINER] 矿场班次（免费 API）" | tee -a "$LOG_FILE"
        cd "$SCRIPT_DIR"
        
        # 直接用 free_llm 跑矿场任务
        python3 -c "
import sys, os, json, datetime
sys.path.insert(0, '$SCRIPT_DIR')
from free_llm import call

tasks = [
    ('market_sentiment', '你是疯子矿场的市场分析师。简短分析当前A股市场情绪（100字以内）。格式：[情绪] [方向] [建议]', 'glm'),
    ('tech_analysis', '用100字分析当前A股技术面走势。关注沪指和创业板。', 'nim'),
    ('sector_rotation', '分析当前A股板块轮动趋势，列出3个强势板块和3个弱势板块。', 'glm'),
    ('risk_assessment', '评估当前A股市场风险等级（低/中/高），给出理由。', 'github'),
]

today = datetime.datetime.now().strftime('%Y-%m-%d')
output_dir = os.environ.get('OUTPUT_DIR', '/tmp/mine_output')
cloud_dir = os.environ.get('CLOUD_DIR', '/workspace/fengzi-repos/mine-seed/cloud/miner')

results = []
for task_name, prompt, prefer in tasks:
    print(f'[MINER] Running: {task_name}...')
    try:
        result = call(prompt, max_tokens=500, prefer=prefer)
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        outfile = f'{output_dir}/{task_name}_{ts}.md'
        with open(outfile, 'w') as f:
            f.write(f'# {task_name}\n\n渠道: {result[\"channel\"]} | 模型: {result[\"model\"]} | 耗时: {result[\"elapsed\"]:.1f}s\n\n{result[\"content\"]}')
        print(f'  OK: {result[\"channel\"]}/{result[\"model\"]} {result[\"elapsed\"]:.1f}s')
        results.append(task_name)
        
        # 复制到 cloud/
        import shutil
        os.makedirs(cloud_dir, exist_ok=True)
        shutil.copy(outfile, cloud_dir)
    except Exception as e:
        print(f'  FAIL: {e}')

print(f'\\n矿场完成: {len(results)}/{len(tasks)} 任务成功')
" >> "$LOG_FILE" 2>&1
        
        git_push
        ntfy_notify "矿场班次 $TODAY" "矿场完成，见 GitHub cloud/miner/" "default"
        ;;
    
    signals)
        echo "[SIGNALS] 信号发现（免费 API）" | tee -a "$LOG_FILE"
        cd "$MINE_SEED/05_TOOLS/signals"
        
        # 优先用 A股信号发现引擎 v2
        python3 signal_discovery_a.py >> "$LOG_FILE" 2>&1
        
        # 检查是否成功
        if [ -f "$CLOUD_DIR/signals/signals_${TODAY}.md" ]; then
            echo "[SIGNALS] A股信号引擎成功" | tee -a "$LOG_FILE"
        else
            # Fallback: inline free_llm
            echo "[SIGNALS] Fallback 到 inline free_llm..." | tee -a "$LOG_FILE"
            cd "$SCRIPT_DIR"
            python3 -c "
import sys, os, datetime
sys.path.insert(0, '$SCRIPT_DIR')
from free_llm import call

today = datetime.datetime.now().strftime('%Y-%m-%d')
result = call(
    f'今天是{today}。作为量化分析师，列出当前市场最值得关注的3个信号（动量/均值回归/波动率），每个信号包含：信号类型、方向、置信度（0-100）、理由。',
    system='你是专业的量化信号发现分析师。',
    max_tokens=800,
    prefer='glm'
)

output_dir = os.environ.get('OUTPUT_DIR', '/tmp/mine_output')
cloud_dir = os.environ.get('CLOUD_DIR', '/workspace/fengzi-repos/mine-seed/cloud/signals')
os.makedirs(cloud_dir, exist_ok=True)

ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
outfile = f'{output_dir}/signals_{ts}.md'
with open(outfile, 'w') as f:
    f.write(f'# 信号发现 — {today}\n\n渠道: {result[\"channel\"]} | 耗时: {result[\"elapsed\"]:.1f}s\n\n{result[\"content\"]}')

import shutil
shutil.copy(outfile, cloud_dir)
print(f'Signals: {outfile}')
" >> "$LOG_FILE" 2>&1
        fi
        
        git_push
        ntfy_notify "信号发现 $TODAY" "信号报告已生成" "default"
        ;;
    
    research_morning|research_noon)
        SHIFT=$(echo "$TASK" | sed 's/research_//')
        echo "[RESEARCH] 知识${SHIFT}班（免费 API）" | tee -a "$LOG_FILE"
        cd "$SCRIPT_DIR"
        
        python3 -c "
import sys, os, datetime
sys.path.insert(0, '$SCRIPT_DIR')
from free_llm import call

today = datetime.datetime.now().strftime('%Y-%m-%d')
shift = '$SHIFT'

prompts = {
    'morning': f'今天是{today}早上。作为研究科学家，总结昨日市场要点（3条），并列出今日需要关注的3个研究方向。',
    'noon': f'今天是{today}中午。作为研究科学家，总结上午市场表现（3条），并提出下午需要验证的2个假设。',
}

result = call(
    prompts.get(shift, '总结今日市场要点'),
    system='你是小疯子，ACE Runtime 研究域科学家。',
    max_tokens=600,
    prefer='glm'
)

cloud_dir = os.environ.get('CLOUD_DIR', '/workspace/fengzi-repos/mine-seed/cloud/research')
os.makedirs(cloud_dir, exist_ok=True)

outfile = f'{cloud_dir}/research_{shift}_{today}.md'
with open(outfile, 'w') as f:
    f.write(f'# 知识{shift}班 — {today}\n\n渠道: {result[\"channel\"]} | 耗时: {result[\"elapsed\"]:.1f}s\n\n{result[\"content\"]}')

print(f'Research: {outfile}')
" >> "$LOG_FILE" 2>&1
        
        git_push
        ntfy_notify "知识${SHIFT}班 $TODAY" "研究报告已生成" "default"
        ;;
    
    archivist)
        echo "[ARCHIVIST] 档案官归档" | tee -a "$LOG_FILE"
        cd "$MINE_SEED"
        
        # 归档今日产出
        TODAY_FILES=$(find cloud/ -name "*${TODAY}*" -type f 2>/dev/null | wc -l)
        MEMORY_FILE="02_MEMORY/recent_memory/daily/${TODAY}-archivist.md"
        
        mkdir -p "02_MEMORY/recent_memory/daily"
        cat > "$MEMORY_FILE" << EOF
# ${TODAY} — 档案官归档

## 今日产出统计
- cloud/ 文件数: ${TODAY_FILES}
- 归档时间: $(date)

## 文件列表
$(find cloud/ -name "*${TODAY}*" -type f 2>/dev/null | sed 's/^/- /')

## 系统状态
- Gateway: $(curl -s http://localhost:3000/api/status 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{d[\"data\"][\"channels\"]}ch/{d[\"data\"][\"models\"]}models')" 2>/dev/null || echo "DEAD")
- 免费 API: GLM(✅) + NIM(16key) + GitHub Models
EOF
        
        echo "[ARCHIVIST] 归档完成: $MEMORY_FILE" | tee -a "$LOG_FILE"
        git_push
        ntfy_notify "档案归档 $TODAY" "今日${TODAY_FILES}个文件已归档" "low"
        ;;
    
    liveness)
        echo "[LIVENESS] 世界存活自检" | tee -a "$LOG_FILE"
        
        # 检查免费 API
        GLM_OK=$(python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
from free_llm import call
try:
    r = call('ping', max_tokens=5, prefer='glm')
    print('ALIVE')
except:
    print('DEAD')
" 2>/dev/null)
        
        NIM_OK=$(python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
from free_llm import call
try:
    r = call('ping', max_tokens=5, prefer='nim')
    print('ALIVE')
except:
    print('DEAD')
" 2>/dev/null)
        
        GH_OK=$(python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
from free_llm import call
try:
    r = call('ping', max_tokens=5, prefer='github')
    print('ALIVE')
except:
    print('DEAD')
" 2>/dev/null)
        
        echo "  GLM: $GLM_OK" | tee -a "$LOG_FILE"
        echo "  NIM: $NIM_OK" | tee -a "$LOG_FILE"
        echo "  GitHub: $GH_OK" | tee -a "$LOG_FILE"
        echo "  Git: $(cd $MINE_SEED && git status --short | wc -l) uncommitted" | tee -a "$LOG_FILE"
        
        # 如果所有 API 都挂了，发紧急通知
        if [[ "$GLM_OK" == "DEAD" && "$NIM_OK" == "DEAD" && "$GH_OK" == "DEAD" ]]; then
            ntfy_notify "紧急: 所有API不可用" "GLM/NIM/GitHub 全部DEAD" "urgent"
        fi
        ;;
    
    *)
        echo "用法: bash run_free_task.sh <task_name>"
        echo ""
        echo "可用任务:"
        echo "  advisor          — 每日荐股（GLM）"
        echo "  miner            — 矿场班次（GLM+NIM+GitHub混用）"
        echo "  signals          — 信号发现（GLM）"
        echo "  research_morning — 知识早班（GLM）"
        echo "  research_noon    — 知识午班（GLM）"
        echo "  archivist        — 档案归档（无API）"
        echo "  liveness         — 存活自检（ping所有渠道）"
        echo ""
        echo "0 依赖 TRAE 额度，全部使用免费 API 直连"
        ;;
esac

echo "[TASK] Done at $(date)" | tee -a "$LOG_FILE"
