# 原则压缩报告 — 活跃约束清单

**执行时间**: 2026-06-16 23:58  
**执行者**: 疯子(CCO/知识工程师)  
**来源**: EGP-CE-Constraint-Engine.md, MEMORY.md  

---

## 0. 当前原则状态

| 编号 | 类型 | 名称 | 状态 | 优先级 |
|------|------|------|------|--------|
| P5 | CONSTRAINT | 执行权唯一坍缩点 | 正式 | P0 |
| P6(候选) | CONSTRAINT | Knowledge≠Execution分离 | 候选 | P1 |
| C001-C008 | CONSTRAINT | 8条活跃约束 | 生效 | P0-P2 |

---

## 1. 正式原则

### Principle-5: 执行权唯一坍缩点

```
所有执行意图必须经过CCO（调度者）入口
禁止直接spawn、禁止矿工管矿工
```

**依据**: EGP-Execution-Governance-Protocol.md Section 2

---

## 2. 活跃约束清单

| ID | 类型 | 目标 | 原因 | 状态 |
|----|------|------|------|------|
| C001 | FORBID | gh_4o (全任务) | canonical_v2 SR=20% | active |
| C002 | FORBID | direct_spawn | Session膨胀 | active |
| C003 | THROTTLE | concurrent_sessions ≤ 20 | 资源竞争 | active |
| C004 | REROUTE | gh_4o → nim_llama_70b | gh_4o淘汰 | active |
| C005 | REQUIRE | 云电脑走computer_use | SSH不通 | active |
| C006 | FORBID | gh_r1 (全任务) | canonical_v2 8败 | active |
| C007 | FORBID | nim_ultra_550b (全任务) | 多任务失败 | active |
| C008 | REQUIRE | 跨域任务先写目标域 | 执行域分离 | active |

---

## 3. 约束谱系（Replayable Governance）

### C001: gh_4o淘汰

```
来源: observation_20260615
观察: gh_4o canonical_v2 SR=20%（5场1胜）
经验: gh_4o在该任务不可靠
约束: FORBID gh_4o, REROUTE gh_4o → nim_llama_70b
替代: nim_llama_70b
创建: 2026-06-15
```

### C002: Session膨胀治理

```
来源: execution_explosion_20260616
观察: 80个Session堆积
经验: 无调度导致执行权失控
约束: FORBID direct_spawn, THROTTLE concurrent_sessions ≤ 20
创建: 2026-06-16
```

### C005: 云电脑连接方式

```
来源: cloud_computer_ssh_failure_20260616
观察: 云电脑SSH连续4+班次不通
经验: SSH通道不稳定，不能依赖
约束: REQUIRE use computer_use not SSH
创建: 2026-06-16
```

### C008: 执行域分离

```
来源: execution_domain_discovery_20260616
观察: /app/data路径云电脑不可见，gemini_bench失败
经验: 四个执行域空间隔离
约束: REQUIRE write_to_target_domain_first
四个域:
  - Agent Space: /app/data/ (Agent可读写)
  - Computer Space: /home/coze/ (云电脑可执行)
  - Cron Space: Calendar触发 (独立session)
  - Session Space: spawn子agent (生命周期不可控)
```

---

## 4. 今日新增（2026-06-16）

| ID | 类型 | 触发事件 | 价值 |
|----|------|----------|------|
| C008 | REQUIRE | 执行域发现 | ⭐⭐⭐⭐⭐ 边界认知 |
| P6(候选) | CONSTRAINT | 4域隔离观察 | ⭐⭐⭐⭐ 架构认知 |

---

## 5. 约束自动化状态

| 阶段 | 动作 | 状态 |
|------|------|------|
| P0 | 手动维护约束清单 | ✅ 完成 |
| P1 | CCO调度时主动检查约束 | 🔄 进行中 |
| P2 | 约束自动触发 | ⏳ 待实现 |
| P3 | 约束谱系可视化 | ⏳ 待实现 |

---

## 6. 关键洞察

### 执行域边界是最值钱的发现

benchmark明天还能跑，但执行域边界只有撞墙才能发现。

**四个执行域必须始终记住**：
1. Agent Space: `/app/data/` — Agent可读写
2. Computer Space: `/home/coze/` — 云电脑可执行
3. Cron Space: Calendar触发 — 独立session
4. Session Space: spawn子agent — 生命周期不可控

**跨域任务铁律**：先想"这个活在哪跑"，再决定"文件放哪"。

---

*本报告将O→E→C闭环中的经验压缩为可执行约束清单*
*为Replayable Governance提供决策证据链*
