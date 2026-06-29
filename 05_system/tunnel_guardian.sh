#!/bin/bash
# ============================================================
# Tunnel Guardian v3 - Reserved Share 模式
# 职责：保证share活着，而不是生成新的share
# ============================================================
ZROK_TOKEN="bfaHO4DlN87Z"
RESERVED_NAME="r1-oneapi"
BRIDGE_KEY="e8a43023a7873cb5a67db8d6e92b483c"
API_DOMAIN="https://api.zhangningjing.com"
LOG_FILE="/tmp/tunnel_guardian.log"
FAIL_CACHE="/tmp/tunnel_guardian_fail"
MAX_RETRIES=2
ZROK_BIN="/usr/local/bin/zrok2"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

health_check() {
    # 检查1: 本地OneAPI是否活着
    local oneapi_ok
    oneapi_ok=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:3000/v1/models -H "Authorization: Bearer test" 2>/dev/null)
    if [ "$oneapi_ok" = "000" ]; then
        log "❌ 检查1失败: OneAPI本地不可达"
        return 1
    fi

    # 检查2: zrok agent进程
    if ! pgrep -f "zrok2 agent" > /dev/null; then
        log "❌ 检查2失败: zrok agent进程不存在"
        return 1
    fi

    # 检查3: zrok share进程
    if ! pgrep -f "zrok2 share" > /dev/null; then
        log "❌ 检查3失败: zrok share进程不存在"
        return 1
    fi

    # 检查4: 直接验证reserved share endpoint（不依赖Worker）
    local direct_ok
    direct_ok=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 15 \
        "https://${RESERVED_NAME}.shares.zrok.io/v1/models" 2>/dev/null)

    case "$direct_ok" in
        401)
            # 401 = zrok通了 + OneAPI要求token（最佳状态）
            log "✅ Reserved Share 健康 (HTTP 401)"
            return 0
            ;;
        502)
            log "⚠️ Reserved Share 502: zrok隧道延迟高，等待下次检查"
            return 0
            ;;
        *)
            log "❌ Reserved Share 不可达 (HTTP $direct_ok)"
            return 1
            ;;
    esac
}

do_recovery() {
    log "🔄 === 开始自动恢复（Reserved模式）==="

    # 1. 杀所有share进程（保留agent）
    log "  → 停止旧share进程..."
    pkill -f "zrok2 share" 2>/dev/null
    sleep 2
    pkill -9 -f "zrok2 share" 2>/dev/null
    sleep 1

    # 2. 检查agent是否活着，死了就重来全套
    if ! pgrep -f "zrok2 agent" > /dev/null; then
        log "  → agent也挂了，完整重来..."
        rm -rf /root/.zrok2/ 2>/dev/null
        $ZROK_BIN enable "$ZROK_TOKEN" --headless 2>/dev/null
        if [ $? -ne 0 ]; then
            sleep 5
            $ZROK_BIN enable "$ZROK_TOKEN" --headless 2>/dev/null
        fi
        sleep 3

        # 重建reserved name（服务端保留，本地可能丢了）
        $ZROK_BIN create name "${RESERVED_NAME}" -n public 2>/dev/null
    fi

    # 3. 用reserved name重新share（URL不变！）
    log "  → 启动Reserved Share: ${RESERVED_NAME}.shares.zrok.io..."
    nohup $ZROK_BIN share public --subordinate -b proxy -n public:${RESERVED_NAME} \
        http://127.0.0.1:3000 > /tmp/zrok_share.log 2>&1 &
    
    # 等几秒让连接建立
    sleep 8

    # 4. 验证恢复
    if health_check; then
        log "✅ 恢复成功！URL不变: ${RESERVED_NAME}.shares.zrok.io"
        return 0
    else
        log "❌ 恢复后验证失败，10秒后重试..."
        sleep 10
        if health_check; then
            log "✅ 延迟验证通过"
            return 0
        fi
        log "❌ 恢复彻底失败"
        return 1
    fi
}

# ===== 主逻辑 =====
if [ -f "$FAIL_CACHE" ]; then
    FAIL_COUNT=$(cat "$FAIL_CACHE")
else
    FAIL_COUNT=0
fi

if health_check; then
    echo 0 > "$FAIL_CACHE"
    exit 0
else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo "$FAIL_COUNT" > "$FAIL_CACHE"
    
    if [ "$FAIL_COUNT" -ge "$MAX_RETRIES" ]; then
        log "⚠️ 连续${FAIL_COUNT}次检查失败，触发自动恢复"
        do_recovery
        echo 0 > "$FAIL_CACHE"
    else
        log "⚠️ 第${FAIL_COUNT}次检查失败，等待下次确认"
    fi
fi
