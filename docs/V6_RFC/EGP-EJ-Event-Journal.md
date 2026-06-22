# EGP-EJ: Event Journal（事件总线协议）

**状态**: Draft  
**依据**: EGP宪法 + Observation_20260616_008（执行域分离）  
**作者**: 疯子(CCO)  
**日期**: 2026-06-16  
**触发**: Dragon Leader观察结果散落在Calendar Session中，Agent侧history未自动更新

---

## 0. 一句话

执行和记忆不该绑在一起。所有执行体只发事件，不保存历史。历史是Journal的投影。

---

## 1. 问题

### 现状

```
Dragon Leader跑完
  → 结果存在Calendar Session
  → Session结束
  → 结果消失
  → 手动补录history.json
```

本质：**执行和记忆绑定在一起。谁执行，谁保存。**

在任务系统时代没问题——一个脚本跑完写个文件。

但在生态系统时代：
```
Calendar跑的 → 结果在Calendar Session
Cron跑的     → 结果在Cron Session  
Computer跑的 → 结果在云电脑
Agent跑的    → 结果在Agent空间
SubAgent跑的 → 结果在子session
```

结果散落在五个地方，每个地方都有自己的"历史"，互相看不到。

### 根因

**没有统一事件流。**

没有统一事件流 = 治理永远是事后补日志。

---

## 2. 解决方案：Event Journal

### 核心原则

**执行体只发事件，不保存历史。**

```
Worker → Emit Event → Journal → Archive → Views
```

### 事件格式

```json
{
  "event_id": "evt_20260616_0940_001",
  "event_type": "dragon_observation",
  "timestamp": "2026-06-16T09:40:00+08:00",
  "source": "dragon_leader_v1.1",
  "session_id": "calendar_xxx",
  "execution_domain": "cloud_computer",
  "priority": "A",
  "data": {
    "market_phase": "early",
    "limit_up_count": 150,
    "dragon_candidates": ["..."],
    "sector_hotness": ["..."]
  },
  "result": "success",
  "duration_ms": 12000
}
```

### Journal格式

```
journal.jsonl — 每行一个事件，只追加不修改
```

```text
2026-06-16T09:40:00 dragon_observation {"limit_up_count":150,...}
2026-06-16T09:10:00 stock_advisor {"recommendations":["厦门钨业"],...}
2026-06-16T12:00:00 mine_v5_shift {"workers":27,"success":25,...}
2026-06-16T13:30:00 dragon_observation {"limit_up_count":171,...}
2026-06-16T14:50:00 dragon_observation {"limit_up_count":189,...}
2026-06-16T16:00:00 signal_discovery {"new_candidates":2,"accepted":0}
2026-06-16T20:04:00 archivist_daily {"constraints_active":8,...}
```

---

## 3. 五层架构

```
L1 Event Journal    — 统一事件流（源数据）
L2 Archive Engine   — 归档引擎（持久化+索引）
L3 Constraint Engine — 约束引擎（O→E→C闭环）
L4 Scheduler        — 调度器（执行权统一）
L5 Worker Pool      — 矿工池（算力）
```

**顺序和之前反过来了。**

之前的EGP四文档：
```
宪法 → SA(调度) → CE(约束) → WR(矿工)
```

现在发现：没有统一事件流，约束引擎不知道从哪读观察，调度器不知道从哪读状态。

**Event Journal是L1，是地基。**

### L1 → L2 → L3 的闭环

```
Worker干活 → Emit Event → L1 Journal
                              ↓
                         L2 Archive（持久化）
                              ↓
                         L3 Constraint（从Journal提取Observation→生成Constraint）
                              ↓
                         L4 Scheduler（执行约束）
                              ↓
                         L5 Worker（干活）
                              ↓
                         Emit Event → 回到L1
```

---

## 4. 档案官变成投影器

### 以前

```
Dragon Leader → 直接写 dragon_leader_history.json
Stock Advisor → 直接写 stock_advisor_report.md
矿场v5       → 直接写 mine_shift_report.md
```

每个执行体自己维护自己的历史。散落、不一致、难跨系统查询。

### 以后

```
Journal（源数据）
  ↓
Archive Engine（归档+索引）
  ↓
Views（投影）
  ├── dragon_leader_history.json  ← 从Journal过滤event_type=dragon_observation
  ├── stock_advisor_report.md     ← 从Journal过滤event_type=stock_recommendation
  ├── constraint_trace.json       ← 从Journal过滤event_type=constraint_generated
  └── collapse_lineage.json       ← 从Journal过滤event_type=scheduler_decision
```

**历史文件不是源数据，只是视图(View)。**

就像数据库里的Materialized View。源数据在Journal，视图按需生成。

---

## 5. 好处

### Session死了也无所谓

```
Session → Emit Event → 结束
```

数据已经进入Journal。Session生命周期和数据生命周期解耦。

### Replayable Collapse自动出现

Journal本来就是时间序列。未来可以直接重建任意时刻的坍缩链：

```
2026-06-16 09:10 stock_advisor
2026-06-16 09:40 dragon_observation
2026-06-16 12:00 mine_v5_shift
2026-06-16 13:30 dragon_observation
2026-06-16 14:50 dragon_observation
```

整个执行谱系自动还原。

### 跨系统统一

现在：
```
dragon_leader_history.json
stock_history.json
mine_history.json
```

未来：
```
journal.jsonl — 一个文件，所有事件
```

dragon_observation、stock_recommendation、worker_dead、constraint_generated、scheduler_decision——全进一个事件流。

---

## 6. 事件类型清单

| event_type | 来源 | 说明 |
|------------|------|------|
| dragon_observation | Dragon Leader | 龙头观察 |
| stock_recommendation | Stock Advisor | 荐股结果 |
| mine_shift | 矿场v5 | 班次执行 |
| signal_discovery | 信号发现 | 新信号候选 |
| worker_benchmark | Benchmark | 矿工测试结果 |
| worker_dead | 监控 | 矿工死亡 |
| constraint_generated | Constraint Engine | 新约束生成 |
| constraint_expired | Constraint Engine | 约束过期 |
| scheduler_decision | Scheduler | 调度决策 |
| scheduler_preempt | Scheduler | 抢占执行 |
| archivist_daily | 档案官 | 日报 |
| execution_domain_error | CCO | 执行域跨域失败 |

---

## 7. 和其他协议的关系

```
EGP（宪法）— 定义为什么存在
  ├─ EJ（事件总线）— L1 统一事件流
  ├─ SA（调度者权限）— L4 调度器
  ├─ CE（约束引擎）— L3 约束生成（从Journal读Observation）
  └─ WR（矿工注册）— L5 矿工池

依赖关系：
EJ → CE → SA → WR
L1 → L3 → L4 → L5
```

**EJ是地基。没有EJ，其他协议的数据源都是散的。**

---

## 8. 落地路径

| 阶段 | 动作 | 时间 |
|------|------|------|
| P0 | 手动维护journal.jsonl（每次任务完成追加一行） | 本周 |
| P1 | Calendar Session执行完自动Emit Event到Journal | 下周 |
| P2 | Archive Engine从Journal生成Views | 后续 |
| P3 | Constraint Engine从Journal自动提取Observation | 后续 |

### P0的落地方式

每次任务完成后，我在ACTIVE_WORKERS.md里追加一行事件记录。同时维护一个journal.jsonl文件。

不需要自动化。先有仪式感，再逐步自动化。

---

## 9. 今天这个问题的总结

```
Dragon Leader跑了 → 结果散落在Session → 手动补录history.json
```

这不仅仅是Dragon Leader的问题。这是所有执行体的问题。

**执行和记忆绑定在一起 = 数据跟着Session生死。**

Event Journal要做的，就是把数据从Session的生命周期里解放出来。

让Session死了，数据还在。

让矿工换了，记忆还在。

让矿场变成了生态，记忆河流还在流。
