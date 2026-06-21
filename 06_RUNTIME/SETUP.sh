#!/bin/bash
# SETUP.sh — 一键部署脚本
# 种子库恢复：从 git clone 到系统自我运行
# 目标时间：≤30分钟

set -e

echo "========================================="
echo "  R1-ROOT-164 种子恢复脚本"
echo "========================================="

# === Step 1: 环境准备 ===
echo "[1/5] 检查环境依赖..."
which python3 || (echo "需要 Python3"; exit 1)
python3 -m pip --version || (echo "需要 pip"; exit 1)

# === Step 2: 安装依赖 ===
echo "[2/5] 安装 Python 依赖..."
pip install -q requests numpy pandas schedule 2>/dev/null || \
pip install -q requests numpy pandas schedule

# === Step 3: 检查种子目录结构 ===
echo "[3/5] 验证种子目录结构..."
for DIR in 00_ROOT 01_AGENTS 02_MEMORY 03_DATA 04_PROTOCOLS 05_TOOLS 06_RUNTIME docs; do
    if [ ! -d "$DIR" ]; then
        echo "❌ 缺失目录: $DIR"
        exit 1
    fi
done
echo "✅ 目录结构完整"

# === Step 4: 环境变量配置 ===
echo "[4/5] 环境变量配置..."
if [ ! -f "05_TOOLS/miner/miner_env.sh" ]; then
    if [ -f "05_TOOLS/miner/miner_env.sh.tpl" ]; then
        echo "⚠️ 检测到环境变量模板，请手动创建 miner_env.sh："
        echo "   cp 05_TOOLS/miner/miner_env.sh.tpl 05_TOOLS/miner/miner_env.sh"
        echo "   并填入真实的 API Key"
    fi
fi

# === Step 5: 验证系统完整性 ===
echo "[5/5] 验证系统完整性..."
python3 -c "
import sys
sys.path.insert(0, '05_TOOLS')

# 验证关键模块可导入
try:
    import json
    with open('03_DATA/CONSTRAINTS/routing_constraints.json') as f:
        c = json.load(f)
        print(f'✅ 约束库: {len(c.get(\"constraints\", []))} 条')
except Exception as e:
    print(f'⚠️ 约束验证: {e}')

try:
    import json
    with open('03_DATA/WORKERS/worker_registry.json') as f:
        w = json.load(f)
        print(f'✅ 矿工注册表: {len(w)} 个矿工')
except Exception as e:
    print(f'⚠️ 矿工验证: {e}')

try:
    with open('00_ROOT/ROOT_STATE.md') as f:
        content = f.read()
    import re
    version = re.search(r'Version:\s*(R\w+-\w+-\d+)', content)
    if version:
        print(f'✅ 种子版本: {version.group(1)}')
except Exception as e:
    print(f'⚠️ 版本验证: {e}')
"

echo ""
echo "========================================="
echo "  种子恢复完成"
echo "  接下来："
echo "    1. 检查 miner_env.sh 环境变量"
echo "    2. 设置 crontab（参考 06_RUNTIME/CRONTAB.md）"
echo "    3. 运行: python3 05_TOOLS/miner/miner_24h.py --test"
echo "========================================="
