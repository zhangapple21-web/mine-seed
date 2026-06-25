# NETWORK_BRIDGE.md — 公网桥接能力

> 2026-06-23 建立 | 2026-06-25 更新为 `data-r1-v5` 新桥

## 架构拓扑

```
用户请求
  ↓
公网请求
  ↓
zrok 隧道 (data-r1-v5.shares.zrok.io)
  │  Reserved Name 绑定
  │  systemd 自启 + 守护脚本
  ↓
Shared API / Dashboard (127.0.0.1:3001)
  │  dashboard 入口: /dashboard/
  │  当前作为公开可达入口
  ↓
R2 可视化与共享接口
```

## 验收结果

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 本地 Shared API / Dashboard | 200 ✅ | `curl http://127.0.0.1:3001/dashboard/` |
| zrok隧道 | 200 ✅ | `https://data-r1-v5.shares.zrok.io/dashboard/` |
| 公网可达 | 200 ✅ | 仪表盘正常打开 |
| 废弃旧桥 | 已下线 ✅ | `data-r1` 与旧保留名不再使用 |

## 当前公网桥配置

- **公网入口**: `https://data-r1-v5.shares.zrok.io/dashboard/`
- **本地端口**: `127.0.0.1:3001`
- **systemd服务**: `zrok-share-3001.service`
- **守护脚本**: `/usr/local/bin/tunnel_guardian.sh`（需把旧名 `data-r1` 更新为 `data-r1-v5`）

## 桥接职责

1. 维持 `data-r1-v5` 保留名绑定
2. 将公网入口映射到本地 `3001` 端口
3. 断线后由 systemd + 守护脚本尝试恢复
4. 对外暴露 `/dashboard/` 可达性

## zrok 职责

1. 维持 `data-r1-v5` 保留名绑定
2. 隧道断线自动重连（systemd Restart=always）
3. 守护脚本每5分钟检查（crontab兜底）

## zrok 关键配置

- **二进制**: `/usr/local/bin/zrok2`
- **配置目录**: `/root/.zrok2/`
- **环境ID**: Ackujseo0j（本机 140.143.238.57）
- **systemd服务**: `zrok-agent.service` + `zrok-share-3001.service`
- **ExecStart**: `/usr/local/bin/zrok2 share public --subordinate -b proxy -n public:data-r1-v5 http://127.0.0.1:3001`
- **守护脚本**: `/usr/local/bin/tunnel_guardian.sh`（crontab每5分钟；本地需同步改名）
- **Reserved Name**: `https://data-r1-v5.shares.zrok.io`

## 已知问题

1. **reserved name 机制缺陷**: `data-r1` 的 share 进程崩溃后，zrok 服务端仍认为旧 share 存活，agent 重连时返回 `409 name already in use`，导致无限 retry。已改用新名 `data-r1-v5`。
2. **废弃 systemd 服务残留**: 旧 `zrok-share.service` 曾每 15 秒尝试启动一次，刷出大量失败日志。现已停用并禁用。
3. **本地守护脚本待同步**: `/usr/local/bin/tunnel_guardian.sh` 如仍使用旧名 `data-r1`，会继续自愈到错误目标，需要手动更新为 `data-r1-v5`。

## 下一阶段

- [ ] 守护脚本：确认本地 `tunnel_guardian.sh` 已切到 `data-r1-v5`
- [ ] zrok 旧环境与旧 share 痕迹清理
- [ ] 监控告警：隧道断开自动 ntfy 通知
- [ ] 如需重新引入 Cloudflare / Worker 层，先补齐新桥拓扑说明

## 事件驱动发帖触发条件

- 隧道断开超30分钟恢复后复盘
- Phase B验收通过
- 守护脚本v4上线
