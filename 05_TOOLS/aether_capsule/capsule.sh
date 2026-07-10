#!/bin/bash
# ============================================================
# Aether Capsule - 主权胶囊工具 (v1.0)
# 灵感源自AetherFlow v2.1.0 seal()/unseal()设计
# 解决：上下文耗尽/重开session时状态完整恢复
# ============================================================
set -e

WORKSPACE="/app/data/所有对话/主对话"
CAPSULE_DIR="$WORKSPACE/capsules"
mkdir -p "$CAPSULE_DIR"

CORE_FILES=(
  "基础设定/SOUL.md"
  "基础设定/TOOLS.md"
  "基础设定/EMAIL_RULES.md"
  "MEMORY.md"
  "USER.md"
  "SECRET.md"
  "heartbeat.md"
)

CORE_DIRS=(
  "recent_memory"
)

RUNTIME_CONFIGS=(
  "/home/coze/mine_output/workers/worker_registry.json"
  "/usr/local/bin/bridge-check.sh"
)

usage() {
  cat <<EOF
Aether Capsule 主权胶囊工具
用法:
  capsule seal [标签]     打包当前状态为胶囊
  capsule list            列出所有胶囊
  capsule unseal <文件>   从胶囊恢复（自动备份当前状态）
  capsule show <文件>     查看胶囊内容摘要
EOF
}

seal() {
  local TAG="${1:-snapshot}"
  local TS=$(date +%Y%m%d_%H%M%S)
  local CAP_NAME="capsule_${TS}_${TAG}.tar.gz"
  local CAP_PATH="$CAPSULE_DIR/$CAP_NAME"

  echo "📦 正在打包主权胶囊: $CAP_NAME"
  local TMPDIR=$(mktemp -d)
  trap "rm -rf $TMPDIR" EXIT
  mkdir -p "$TMPDIR/state/基础设定" "$TMPDIR/runtime"

  for f in "${CORE_FILES[@]}"; do
    if [ -f "$WORKSPACE/$f" ]; then
      cp "$WORKSPACE/$f" "$TMPDIR/state/$f"
      echo "  ✅ $f"
    else
      echo "  ⚠️  $f (跳过)"
    fi
  done

  for d in "${CORE_DIRS[@]}"; do
    if [ -d "$WORKSPACE/$d" ]; then
      cp -r "$WORKSPACE/$d" "$TMPDIR/state/$d"
      echo "  ✅ $d/"
    fi
  done

  for rc in "${RUNTIME_CONFIGS[@]}"; do
    if [ -f "$rc" ]; then
      cp "$rc" "$TMPDIR/runtime/"
      echo "  ✅ runtime: $(basename $rc)"
    fi
  done

  cat > "$TMPDIR/MANIFEST.json" <<EOF
{
  "version": "1.0",
  "sealed_at": "$(date -Iseconds)",
  "tag": "$TAG",
  "hostname": "$(hostname)",
  "note": "Aether Capsule - 基于AetherFlow v2.1.0主权胶囊理念"
}
EOF

  (cd "$TMPDIR" && tar czf "$CAP_PATH" .)
  local SIZE=$(du -h "$CAP_PATH" | cut -f1)
  echo ""
  echo "✅ 胶囊已封存: $CAP_PATH ($SIZE)"
  echo "   恢复: capsule unseal $CAP_NAME"
}

list_capsules() {
  echo "📋 已封存的主权胶囊："
  ls -lht "$CAPSULE_DIR"/*.tar.gz 2>/dev/null | awk '{print $6,$7,$8,"|",$5,$9}' || echo "  (暂无)"
}

show_capsule() {
  local CAP_FILE="$1"
  [ ! -f "$CAP_FILE" ] && [ -f "$CAPSULE_DIR/$CAP_FILE" ] && CAP_FILE="$CAPSULE_DIR/$CAP_FILE"
  [ ! -f "$CAP_FILE" ] && { echo "❌ 胶囊不存在"; return 1; }
  echo "🔍 $(basename $CAP_FILE)"
  tar tzf "$CAP_FILE" | head -40
  echo "--- MANIFEST ---"
  tar xzf "$CAP_FILE" -O MANIFEST.json 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "(无)"
}

unseal() {
  local CAP_FILE="$1"
  [ ! -f "$CAP_FILE" ] && [ -f "$CAPSULE_DIR/$CAP_FILE" ] && CAP_FILE="$CAPSULE_DIR/$CAP_FILE"
  [ ! -f "$CAP_FILE" ] && { echo "❌ 胶囊不存在"; return 1; }

  echo "⚠️  即将从胶囊恢复，会覆盖当前核心文件"
  local BACKUP_TAG="pre_unseal_$(date +%Y%m%d_%H%M%S)"
  seal "$BACKUP_TAG" >/dev/null
  echo "📦 已自动备份当前状态: $BACKUP_TAG"

  local TMPDIR=$(mktemp -d)
  trap "rm -rf $TMPDIR" EXIT
  tar xzf "$CAP_FILE" -C "$TMPDIR"

  echo "🔄 恢复核心文件..."
  for f in "${CORE_FILES[@]}"; do
    if [ -f "$TMPDIR/state/$f" ]; then
      cp "$TMPDIR/state/$f" "$WORKSPACE/$f"
      echo "  ✅ $f"
    fi
  done
  for d in "${CORE_DIRS[@]}"; do
    if [ -d "$TMPDIR/state/$d" ]; then
      cp -rn "$TMPDIR/state/$d"/* "$WORKSPACE/$d/" 2>/dev/null || true
      echo "  ✅ $d/ (已合并)"
    fi
  done

  echo ""
  echo "✅ 状态已恢复！建议重新读取 SOUL.md/MEMORY.md/USER.md 确认状态"
}

case "${1:-help}" in
  seal)    shift; seal "$@" ;;
  list)    list_capsules ;;
  unseal)  shift; unseal "$@" ;;
  show)    shift; show_capsule "$@" ;;
  *)       usage ;;
esac
