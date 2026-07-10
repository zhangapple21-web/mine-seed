#!/bin/bash
# 公网桥全链路验证脚本 - 故障排查第一步必须跑这个
# 用法: bridge-check.sh [quick|full]

MODE=${1:-quick}
BRIDGE_KEY="e8a43023a7873cb5a67db8d6e92b483c"
DEFAULT_TOKEN="yV17PtngX3rkWRsv44Cf4cB288054cDc8442737a05AbEc0d"
PUB_URL="https://api.zhangningjing.com"
ZROK_URL="https://r1-oneapi.shares.zrok.io"
LOCAL_URL="http://127.0.0.1:3000"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "=== 公网桥全链路验证 ==="
echo ""

# Layer 1: Cloudflare Worker + bridge key
echo -n "[1] Cloudflare Worker (bridge key) ... "
CF=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" \
  -H "X-R1-Bridge-Key: $BRIDGE_KEY" \
  -H "Authorization: Bearer $DEFAULT_TOKEN" \
  "$PUB_URL/v1/models" 2>/dev/null)
if [ "$CF" = "200" ]; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL (HTTP $CF)${NC}"; fi

# Layer 2: zrok direct
echo -n "[2] zrok直连 ... "
ZK=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $DEFAULT_TOKEN" \
  "$ZROK_URL/v1/models" 2>/dev/null)
if [ "$ZK" = "200" ]; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL (HTTP $ZK)${NC}"; fi

# Layer 3: OneAPI local
echo -n "[3] OneAPI本地 ... "
LC=$(curl -s --max-time 5 -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $DEFAULT_TOKEN" \
  "$LOCAL_URL/v1/models" 2>/dev/null)
if [ "$LC" = "200" ]; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL (HTTP $LC)${NC}"; fi

# Layer 4: systemd services
echo -n "[4] zrok服务状态 ... "
if systemctl is-active zrok-share.service &>/dev/null; then
  echo -e "${GREEN}zrok-share: active${NC}"
else
  echo -e "${RED}zrok-share: inactive${NC}"
fi
echo -n "    "
if systemctl is-active zrok-agent.service &>/dev/null; then
  echo -e "${GREEN}zrok-agent: active${NC}"
else
  echo -e "${RED}zrok-agent: inactive${NC}"
fi

if [ "$MODE" = "full" ]; then
  echo ""
  echo "[Full] 模型数量统计:"
  MODELS=$(curl -s --max-time 8 \
    -H "X-R1-Bridge-Key: $BRIDGE_KEY" \
    -H "Authorization: Bearer $DEFAULT_TOKEN" \
    "$PUB_URL/v1/models" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',[])))" 2>/dev/null)
  echo "    可用模型: ${MODELS:-N/A}"
fi

echo ""
echo "=== 验证完成 ==="
