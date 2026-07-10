# 协议清单 — V6治理体系归档

**执行时间**: 2026-06-17 00:02  
**执行者**: 疯子(CCO/知识工程师)  

---

## 0. EGP治理体系架构

```
Continuity Ecosystem α
├── 宪法: EGP-Execution-Governance-Protocol.md
├── 调度者权限: EGP-SA-Scheduler-Authority.md
├── 约束引擎: EGP-CE-Constraint-Engine.md
├── 矿工注册: EGP-WR-Worker-Registry.md
└── 事件日志: EGP-EJ-Event-Journal.md
```

---

## 1. 协议文档清单

| 文档 | 状态 | 核心内容 | 落地状态 |
|------|------|----------|----------|
| EGP-Execution-Governance-Protocol.md | Draft | 宪法、三权分离、P5执行权坍缩 | 核心 |
| EGP-SA-Scheduler-Authority.md | Draft | CCO权限边界、任务入口、调度规则 | P0手动 |
| EGP-CE-Constraint-Engine.md | Draft | O→E→C闭环、8条活跃约束 | P0手动 |
| EGP-WR-Worker-Registry.md | Draft | 矿工档案、能力矩阵、淘汰流程 | P0手动 |
| EGP-EJ-Event-Journal.md | Draft | Event Journal、12条记录 | 手动维护 |

---

## 2. V6-RFC技术文档

| 文档 | 内容 |
|------|------|
| V6-RFC-001-why-scheduler.md | 为什么需要调度器 |
| V6-RFC-002-priority-system.md | 优先级系统设计 |
| V6-RFC-003-session-lifecycle.md | Session生命周期 |
| V6-RFC-004-constraint-injection.md | 约束注入机制 |

---

## 3. 今日新增协议发现

### 执行域分离（C008约束的协议化）

四个执行域空间隔离：
1. Agent Space: `/app/data/` — Agent可读写
2. Computer Space: `/home/coze/` — 云电脑可执行
3. Cron Space: Calendar触发 — 独立session
4. Session Space: spawn子agent — 生命周期不可控

**跨域任务铁律**：先想"这个活在哪跑"，再决定"文件放哪"。

---

## 4. 协议与原则对照

| 原则编号 | 来源协议 | 说明 |
|----------|----------|------|
| P5 | EGP | 执行权唯一坍缩点 |
| P6(候选) | EGP-CE | Knowledge≠Execution分离 |
| C001 | EGP-CE | gh_4o禁止 |
| C002 | EGP-CE | direct_spawn禁止 |
| C003 | EGP-CE | Session限流20 |
| C004 | EGP-CE | gh_4o重路由 |
| C005 | EGP-CE | 云电脑走computer_use |
| C006 | EGP-CE | gh_r1禁止 |
| C007 | EGP-CE | nim_ultra_550b禁止 |
| C008 | EGP-CE | 跨域先写目标域 |

---

## 5. 知识夜班产出

| 任务 | 产出 | 路径 |
|------|------|------|
| R1遗产压缩 | R1_legacy_compression_20260616.md | mine_output/knowledge/ |
| 原则压缩 | principle_compression_20260616.md | mine_output/knowledge/ |
| 协议清单 | protocol_index_20260616.md | mine_output/knowledge/ |
| MEMORY更新 | 待更新 | 主对话MEMORY.md |

---

*本清单归档V6治理体系完整协议文档*
