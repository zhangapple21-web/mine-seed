# 系统架构文档
> R1-ROOT-164

---

## 总体架构：O -> E -> M -> C -> R

```
Observation -> Experience -> Meaning -> Constraint -> Route
```

## 物理拓扑

```
lab_01（生产域）
├── 矿场v5（miner_24h.py）
├── 信号发现（signal_discovery.py）
├── Stock Advisor（stock_advisor.py）
├── Dragon Leader（龙头识别）
├── 约束系统（routing_constraints.json）
├── 共享API（shared_api.py）
└── cron调度

lab_02（研究域）
├── R1研究栈
├── 社区互动
└── 认知分析

通信：lab_bus.py（GitHub Gist）+ lab_ntfy.py（ntfy.sh）
```

## 关键公理

| 编号 | 内容 |
|------|------|
| Axiom_000 | 系统核心价值在于结构，不在于运行实例 |
| Axiom_001 | 一个结构可多次实例化 = 架构可迁移 |
| Axiom_002 | 协议比实现更持久 |
| Axiom_003 | 结构可以分层，但分层不是隔离 |
| Axiom_004 | 系统在没有管理员的情况下继续演化 = 自治 |
| Axiom_005 | 记忆是手段，不是目的 |
| Axiom_006 | 看不见不等于不存在 |
| Axiom_007 | 约束不是限制，是生存策略 |
| Axiom_008 | 监控盲区不等于系统故障 |
| Axiom_009 | 种子态 < 运行态 |
| Axiom_010 | 未验证的恢复 = 未恢复 |
