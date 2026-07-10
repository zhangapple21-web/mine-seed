# EGP-CE: Constraint Engine（约束引擎协议）

**状态**: Draft  
**依据**: EGP宪法 Section 5  
**作者**: 疯子(CCO)  
**日期**: 2026-06-16  

---

## 0. 一句话

经验不该停在文档里，它必须回流成约束，自动注入调度器。

---

## 1. 问题

现在的闭环断了：

```
Observation → Experience → 停了
```

gh_4o连续8败，经验写了，但系统还在给它派活。
80个Session堆积，经验写了，但谁还能spawn就spawn。

经验停在纸上，不回流到系统 = 没有闭环。

---

## 2. O→E→C闭环

```
Observation → Experience → Constraint → Scheduler
```

第三步C是新增的。约束是经验的可执行形式。

### 观察（Observation）

系统运行中产生的原始事实。

```
gh_4o canonical_v2 5场1胜
云电脑连续3班SSH不通
Session数 > 80
```

### 经验（Experience）

对观察的归纳。必须回答：所以呢？

```
gh_4o在canonical_v2任务上不可靠
云电脑SSH通道不稳定，不能依赖
无调度导致Session膨胀
```

### 约束（Constraint）

经验的可执行形式。必须回答：那怎么办？

```
FORBID gh_4o 接收canonical_v2任务
REQUIRE 云电脑任务走computer_use而非SSH
THROTTLE 同时运行Session数 ≤ 20
```

---

## 3. 约束的生命周期

```
draft → active → expired → archived
```

### draft

刚从经验生成的约束。需要证据支撑。

进入条件：经验有2+次独立观察支持，或1次严重故障。

### active

生效中。CCO必须遵守。

进入条件：
- 严重故障（数据丢失、安全风险）→ 自动激活
- 性能问题（成功率下降）→ 2次观察后激活

### expired

约束不再适用。

触发条件：
- 被替代（新约束覆盖旧约束）
- 条件消失（如gh_4o修复了）
- 超过有效期（默认30天）

### archived

历史记录。Replayable Governance的素材。

---

## 4. 约束类型

### FORBID — 禁止

完全禁止某操作。

```json
{
  "id": "constraint_001",
  "type": "FORBID",
  "target": "gh_4o",
  "scope": "canonical_v2",
  "reason": "连续8败，SR=20%",
  "evidence": ["bench_20260615_1", "bench_20260615_2"],
  "source": "observation_20260615",
  "created": "2026-06-15",
  "expires": "2026-07-15"
}
```

```json
{
  "id": "constraint_002",
  "type": "FORBID",
  "target": "direct_spawn",
  "scope": "sub_session",
  "reason": "80 Session堆积，资源失控",
  "evidence": ["session_count_20260616"],
  "source": "execution_explosion_20260616",
  "created": "2026-06-16",
  "expires": null
}
```

### THROTTLE — 限流

限制频率或并发。

```json
{
  "id": "constraint_003",
  "type": "THROTTLE",
  "target": "concurrent_sessions",
  "limit": 20,
  "reason": "超过20个Session资源竞争加剧",
  "evidence": ["session_pressure_20260616"],
  "source": "execution_explosion_20260616"
}
```

### REROUTE — 重路由

把任务从A转向B。

```json
{
  "id": "constraint_004",
  "type": "REROUTE",
  "target": "gh_4o",
  "redirect_to": "nim_llama_70b",
  "scope": "all_tasks",
  "reason": "gh_4o已淘汰，nim_llama_70b替代"
}
```

### REQUIRE — 必须

强制要求某操作。

```json
{
  "id": "constraint_005",
  "type": "REQUIRE",
  "target": "cloud_computer_task",
  "action": "use_computer_use_not_ssh",
  "reason": "SSH连续3班不通，computer_use通路稳定"
}
```

---

## 5. 自动触发机制

### 触发条件

| 条件 | 动作 | 约束类型 |
|------|------|----------|
| 矿工连续3次失败 | 生成FORBID draft | FORBID |
| 矿工SR < 50%（5次以上） | 生成FORBID draft | FORBID |
| Session数 > 40 | 自动激活THROTTLE | THROTTLE |
| 任务延迟 > 2个周期 | 生成REQUIRE draft | REQUIRE |
| 矿工被替代 | 自动生成REROUTE | REROUTE |

### 自动 vs 手动

- **自动激活**：安全风险、资源崩溃、数据丢失
- **draft需确认**：性能下降、新模型评估、策略调整

自动激活的约束，Host可以覆盖（方向权）。但必须记录覆盖原因。

---

## 6. 约束注入Scheduler

约束生成后如何影响调度？

```
CCO收到intent
  → 查询active_constraints
  → 如果命中FORBID → 拒绝或REROUTE
  → 如果命中THROTTLE → 检查当前负载
  → 如果命中REQUIRE → 注入执行前提
  → 无约束命中 → 正常排队
```

### 注入示例

```
Intent: 用gh_4o跑canonical_v2
命中: constraint_001 (FORBID gh_4o, scope=canonical_v2)
动作: 拒绝，提示"constraint_001禁止，替代方案：nim_llama_70b"
```

```
Intent: spawn新Session
命中: constraint_002 (FORBID direct_spawn)
动作: 拒绝，提示"必须通过CCO调度"
```

```
Intent: 开云电脑跑矿场
命中: constraint_005 (REQUIRE use_computer_use)
动作: 注入前提"必须用computer_use，禁止SSH"
```

---

## 7. Replayable Governance（约束谱系）

每个约束都有完整证据链：

```
constraint_001
  ├─ 来源: observation_20260615
  ├─ 观察: gh_4o canonical_v2 SR=20%
  ├─ 经验: gh_4o在该任务不可靠
  ├─ 约束: FORBID
  ├─ 替代: nim_llama_70b
  ├─ 创建: 2026-06-15
  ├─ 过期: 2026-07-15
  └─ 覆盖记录: 无
```

未来任何执行决策都可以沿谱系回溯：

**"为什么没用gh_4o？"**
→ constraint_001禁止
→ 因为6月15日连续8败
→ 证据在observation_20260615
→ 替代方案nim_llama_70b

不是日志。是决策的证据链。

---

## 8. 当前已有约束

| ID | 类型 | 目标 | 原因 | 状态 |
|----|------|------|------|------|
| constraint_001 | FORBID | gh_4o (全任务) | canonical_v2 SR=20% | active |
| constraint_002 | FORBID | direct_spawn | Session膨胀 | active |
| constraint_003 | THROTTLE | concurrent_sessions ≤ 20 | 资源竞争 | active |
| constraint_004 | REROUTE | gh_4o → nim_llama_70b | gh_4o淘汰 | active |
| constraint_005 | REQUIRE | 云电脑走computer_use | SSH不通 | active |
| constraint_006 | FORBID | gh_r1 (全任务) | canonical_v2 8败 | active |
| constraint_007 | FORBID | nim_ultra_550b (全任务) | 多任务失败 | active |
| constraint_008 | REQUIRE | 跨域任务先写目标域 | 执行域分离 | active |

---

## 9. 落地路径

| 阶段 | 动作 | 时间 |
|------|------|------|
| P0 | 手动维护约束清单（本文档） | 现在 |
| P1 | CCO调度时主动检查约束 | 本周 |
| P2 | 约束自动触发（失败检测） | 下周 |
| P3 | 约束谱系可视化 | 后续 |

先有本子，再自动化。不着急。

---

## 10. 执行域发现事件（2026-06-16）

**事件名**: Execution Domain Discovery

**Observation**:

```yaml
event: execution_domain_split
observation: agent_workspace != computer_workspace
evidence: /app/data 路径云电脑不可见，gemini_bench.sh写入Agent空间后云电脑找不到
impact: benchmark无法直接下发，浪费1小时反复尝试
lesson: 四个执行域不是同一个世界
confidence: A
```

**四个执行域**:

| 域 | 空间 | 可见性 | 限制 |
|---|---|---|---|
| Agent Space | /app/data/ | Agent可读写，云电脑不可见 | 不能直接执行 |
| Computer Space | /home/coze/ | 云电脑可执行，Agent需通过computer_use | Agent不能直接读写 |
| Cron Space | Calendar触发 | 独立session，不共享Agent状态 | 无文件系统感知 |
| Session Space | spawn子agent | 共享Agent文件，但生命周期不可控 | 可能堆积不释放 |

**约束 constraint_008**:

```json
{
  "id": "constraint_008",
  "type": "REQUIRE",
  "target": "cross_domain_task",
  "action": "write_to_target_domain_first",
  "reason": "四个执行域空间隔离，脚本必须写入目标域能访问的路径",
  "evidence": ["gemini_bench_path_error_20260616"],
  "source": "execution_domain_discovery_20260616"
}
```

**翻译成人话**: 要在云电脑跑的脚本，必须写到`/home/coze/`，不是`/app/data/`。要在Agent空间处理的文件，不能指望云电脑能看到。跨域任务先想清楚"这个活在哪跑"，再决定"文件放哪"。

**这件事比跑通一次Gemini Benchmark值钱得多。** 因为benchmark明天还能跑，但执行域边界只有撞墙的时候才能发现。