#!/bin/bash
# 公网桥验证脚本（当前针对 data-r1-v5 / 3001 dashboard）
# 用法: bridge-check.sh [quick]

MODE=${1:-quick}
ZROK_URL="https://data-r1-v5.shares.zrok.io"
LOCAL_URL="http://127.0.0.1:3001"
DASHBOARD_PATH="/dashboard/"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "=== 公网桥全链路验证 ==="
echo ""

# Layer 1: zrok direct
echo -n "[1] zrok直连 ... "
ZK=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" \
  "$ZROK_URL$DASHBOARD_PATH" 2>/dev/null)
if [ "$ZK" = "200" ]; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL (HTTP $ZK)${NC}"; fi

# Layer 2: local dashboard
echo -n "[2] 本地3001 ... "
LC=$(curl -s --max-time 5 -o /dev/null -w "%{http_code}" \
  "$LOCAL_URL$DASHBOARD_PATH" 2>/dev/null)
if [ "$LC" = "200" ]; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL (HTTP $LC)${NC}"; fi

# Layer 3: systemd services
echo -n "[3] zrok服务状态 ... "
if systemctl is-active zrok-share-3001.service &>/dev/null; then
  echo -e "${GREEN}zrok-share-3001: active${NC}"
else
  echo -e "${RED}zrok-share-3001: inactive${NC}"
fi
echo -n "    "
if systemctl is-active zrok-agent.service &>/dev/null; then
  echo -e "${GREEN}zrok-agent: active${NC}"
else
  echo -e "${RED}zrok-agent: inactive${NC}"
fi

if [ "$MODE" = "full" ]; then
  echo ""
  echo "[Full] 响应头检查:"
  curl -I --max-time 8 "$ZROK_URL$DASHBOARD_PATH" 2>/dev/null | head -n 5
fi

echo ""
echo "=== 验证完成 ==="
