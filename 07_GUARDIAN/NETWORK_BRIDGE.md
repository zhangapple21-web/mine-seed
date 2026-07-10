# NETWORK_BRIDGE.md — 公网桥接能力

> 2026-06-25 更新 | 双通道架构 | Restart=always

## 架构拓扑

```
用户请求
  ↓
zrok 公网隧道
  │
  ├── oneapi-v1.shares.zrok.io → 127.0.0.1:3000 (OneAPI)
  │    验证: 带Key → 200, 无Key → 401
  │
  └── data-r1-v5.shares.zrok.io → 127.0.0.1:3001 (Dashboard/数据服务)
       验证: /dashboard/ → 200

OneAPI (127.0.0.1:3000) → 路由到 NIM/GitHub/GLM 等渠道
```

## 当前隧道状态（2026-06-25）

| 隧道 | 公网地址 | 本地端口 | Share Token | 状态 |
|------|---------|---------|------------|------|
| oneapi-v1 | https://oneapi-v1.shares.zrok.io | 3000 | 3oi2i3lkrha4 | ✅ Active |
| data-r1-v5 | https://data-r1-v5.shares.zrok.io | 3001 | fnwyl68f5x4u | ✅ Active |
| 废弃 | r1-oneapi (RESERVED=true) | - | - | ❌ 已停用 |

## zrok 关键配置

- **二进制**: `/usr/local/bin/zrok2`
- **配置目录**: `/root/.zrok2/`
- **Agent PID**: 41359 (zrok2 agent start)
- **环境ID**: Ackujseo0j（本机 140.143.238.57）

### systemd服务

**zrok-share-oneapi.service** (Restart=always)
```
ExecStart=/bin/bash -c '/usr/local/bin/zrok2 share public --subordinate -b proxy -n public:oneapi-v1 http://127.0.0.1:3000'
```

**zrok-share-3001.service** (Restart=always)
```
ExecStart=/bin/bash -c '/usr/local/bin/zrok2 share public --subordinate -b proxy -n public:data-r1-v5 http://127.0.0.1:3001'
```

- **守护脚本**: `/usr/local/bin/tunnel_guardian.sh`（crontab每5分钟）

## 故障恢复流程

### 502 Bad Gateway 修复步骤
```bash
# 1. 定位故障隧道
systemctl status zrok-share-oneapi.service

# 2. 释放zrok服务端锁死的share和name
zrok2 delete share <share_token>
zrok2 delete name <name>

# 3. 重建name
zrok2 create name <name> -r

# 4. 重启service
systemctl restart zrok-share-<name>.service
```

### 关键约束
- script包装导致zrok share退出码为0，Restart=on-failure不会触发重启 → 必须用Restart=always
- name锁死机制：进程崩溃后name未释放，直接restart会shareConflict → 必须完整释放链
- StartLimitBurst=5作为重启安全阀

## 废弃架构

- Cloudflare Worker (r1-bridge-proxy) — 已停用
- 旧域名 api.zhangningjing.com — DNS已移除
- 旧隧道 r1-oneapi — RESERVED=true 已废弃

## 下一阶段

- [ ] 移除script包装，改用纯binary ExecStart
- [ ] 健壮性：alert当share进程丢失超3分钟
- [ ] 监控告警：隧道断开自动ntfy通知
