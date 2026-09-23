#!/bin/bash
# 种子归档脚本 — 同步运行时数据到 mine-seed 仓库
# GitHub 认证只通过运行时环境变量提供。

set -euo pipefail

REPO="${REPO_PATH:-/home/coze/shared/mine-seed}"
GITHUB_USER="${GITHUB_USER:-zhangapple21-web}"
GITHUB_REPO="${GITHUB_REPO:-mine-seed}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
DATE_TAG=$(date +%Y-%m-%d)

if [ -z "$GITHUB_TOKEN" ]; then
  echo "ERROR: GITHUB_TOKEN is required; do not hardcode PATs." >&2
  exit 2
fi

cd "$REPO"
git remote set-url origin "https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"

# Inject authentication only for the individual Git operation. The token is
# never written to the remote URL, repository config, a file, or log output.
git_auth() {
  git -c "http.extraheader=AUTHORIZATION: bearer ${GITHUB_TOKEN}" "$@"
}

git_auth fetch origin main --prune
# Refuse to overwrite local work; archive should run from a clean checkout.
if ! git diff --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  echo "ERROR: working tree is not clean before sync" >&2
  exit 3
fi
git checkout main
git_auth pull --ff-only origin main

copy_if_present() {
  local source="$1" target="$2"
  if [ -f "$source" ]; then
    mkdir -p "$(dirname "$target")"
    cp "$source" "$target"
  fi
}

copy_if_present /home/coze/experience.json "$REPO/03_DATA/experience.json"
copy_if_present /home/coze/mine_output/observation_log.json "$REPO/03_DATA/observation_log.json"
copy_if_present /home/coze/worker_registry.json "$REPO/03_DATA/WORKERS/worker_registry.json"
copy_if_present /home/coze/routing_constraints.json "$REPO/03_DATA/CONSTRAINTS/routing_constraints.json"
copy_if_present /home/coze/signal_taxonomy.json "$REPO/03_DATA/CONSTRAINTS/signal_taxonomy.json"
copy_if_present /home/coze/mine_output/signals/signal_registry.json "$REPO/03_DATA/CONSTRAINTS/signal_registry.json"

mkdir -p "$REPO/03_DATA/seeds"
for pattern in \
  /home/coze/mine_output/seeds/*.json \
  /home/coze/mine_output/signals/seed_*.json \
  /home/coze/mine_output/signals/thought_seed_*.json \
  /home/coze/mine_output/signals/seed_*.md; do
  for file in $pattern; do
    [ -f "$file" ] && cp "$file" "$REPO/03_DATA/seeds/"
  done
done

copy_if_present /home/coze/miner_24h.py "$REPO/05_TOOLS/miner/miner_24h.py"
copy_if_present /home/coze/experience_engine.py "$REPO/05_TOOLS/memory/experience_engine.py"
copy_if_present /home/coze/signal_discovery.py "$REPO/05_TOOLS/signals/signal_discovery.py"
copy_if_present /home/coze/mine_output/signals/dragon_leader_v2.py "$REPO/05_TOOLS/signals/dragon_leader_v2.py"
copy_if_present /home/coze/miner_cron.sh "$REPO/05_TOOLS/miner/miner_cron.sh"
copy_if_present /home/coze/signal_cron.sh "$REPO/05_TOOLS/signals/signal_cron.sh"
copy_if_present /home/coze/archivist_cron.sh "$REPO/05_TOOLS/memory/archivist_cron.sh"

if git diff --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "→ 数据无变化，跳过空提交"
  exit 0
fi

git add -A
git -c user.name="$GITHUB_USER" -c user.email="${GITHUB_USER}@users.noreply.github.com" \
  commit -m "seed: sync live runtime data $DATE_TAG"

git_auth push origin main

echo "→ 种子归档完成: $DATE_TAG"
