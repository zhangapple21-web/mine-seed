# NETWORK_BRIDGE.md — 公网桥接能力

> 2026-06-23 建立 | Phase A 验收通过

## 架构拓扑

```
用户请求
  ↓
Cloudflare DNS (api.zhangningjing.com)
  ↓
Cloudflare Worker (r1-bridge-proxy)
  │  验证 X-R1-Bridge-Key
  │  白名单路径: /v1/*
  │  无Key → 403
  ↓
zrok 隧道 (r1-oneapi.shares.zrok.io)
  │  Reserved Name 绑定
  │  systemd 自启 + 守护脚本
  ↓
OneAPI (127.0.0.1:3000)
  │  路由到 NIM/GitHub/GLM 等渠道
  │  无Authorization → 401
  ↓
下游模型服务
```

## 验收结果

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 本地OneAPI | 200 ✅ | `curl http://127.0.0.1:3000/v1/models` |
| zrok隧道 | 401 ✅ | 正常需带token |
| 公网桥带Key | 200 ✅ | 88个模型正常返回 |
| 公网桥无Key | 403 ✅ | Worker防护生效 |

## Cloudflare 配置

- **域名**: api.zhangningjing.com
- **Worker**: r1-bridge-proxy
- **DNS**: A记录指向 Worker
- **请求头验证**: `X-R1-Bridge-Key`

## Worker 职责

1. 验证 Bridge Key（无Key返回403）
2. 白名单路径检查（仅允许 /v1/ 下路径）
3. 转发请求到 zrok 隧道
4. 透流响应（不修改body）

## zrok 职责

1. 维持 r1-oneapi 保留名绑定
2. 隧道断线自动重连（systemd Restart=always）
3. 守护脚本每5分钟检查（crontab兜底）

## zrok 关键配置

- **二进制**: `/usr/local/bin/zrok2`
- **配置目录**: `/root/.zrok2/`
- **环境ID**: Ackujseo0j（本机 140.143.238.57）
- **systemd服务**: zrok-agent.service + zrok-share.service
- **ExecStart**: `/usr/local/bin/zrok2 share public --subordinate -b proxy -n public:r1-oneapi http://127.0.0.1:3000`
- **守护脚本**: `/usr/local/bin/tunnel_guardian.sh`（crontab每5分钟）
- **Reserved Name**: `https://r1-oneapi.shares.zrok.io`

## 已知问题

1. **zrok share稳定性**: 2026-06-23出现share进程丢失导致502，systemd 409冲突死循环。根因：旧share/name记录残留在zrok服务端。已通过delete share + delete name彻底清理
2. **东财IP限流**: 板块排行接口因IP限流降级失败，不影响核心链路
3. **zrok环境冗余**: 存在旧环境 IPLbbu-R7j（49.233.196.249），建议清理

## 下一阶段

- [ ] Phase B: 四模型对照测试
- [ ] 守护脚本v4：适配systemd模式
- [ ] zrok旧环境清理
- [ ] 监控告警：隧道断开自动ntfy通知

## 事件驱动发帖触发条件

- 隧道断开超30分钟恢复后复盘
- Phase B验收通过
- 守护脚本v4上线
