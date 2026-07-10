# EGP: Execution Governance Protocol（执行治理协议）

**状态**: Draft  
**作者**: 疯子(CCO)  
**日期**: 2026-06-16  
**触发**: 80个Session堆积，执行权失控

---

## 0. 这不是版本升级

```
V1 = 能跑
V2 = 能扩展
V3 = 能协作
V4 = 能积累经验
V5 = 能持续运行
V6 = 能治理自己
```

V1-V5解决的是**怎么干活**。
V6开始解决的是**谁能干活、什么时候干活、为什么干活**。

80个Session那堵墙，不是V5能力不足，是执行权失控。
这是Mining System进入Ecosystem的分水岭。

---

## 1. 问题定义

### 现象

```
Host ├─ Spawn A
     ├─ Spawn B
     ├─ Spawn C
     ├─ Spawn D
     └─ Spawn E
         ↓
     80个Session
         ↓
     资源竞争
         ↓
     调度失序
         ↓
     Host失去全局视野
         ↓
     矿工开始管理矿工
```

### 本质

不是"V5能力不足"，而是**执行权失控**。

谁都能spawn，谁都能占资源，谁都能开云电脑。
结果 = 没人管 = 瘫痪。

---

## 2. 新增原则：Principle-5

### Execution Must Collapse Through One Gateway

执行权必须经过唯一坍缩点。

禁止：
```
Host → 直接Spawn Worker
```

允许：
```
Host → Scheduler(CCO) → Worker Pool
```

坍缩点 = CCO（Constraint/Coordinator/Observer）。
所有执行意图在这里坍缩成一个有序的执行序列。

---

## 3. 三权分离

| 角色 | 权力 | 能做什么 | 不能做什么 |
|------|------|----------|------------|
| **Host（宿主）** | 方向权 | 说"挖R1""研究股票""验证龙头" | 直接调用矿工 |
| **Scheduler（CCO）** | 执行权 | 排队、优先级、限流、资源分配 | 改变方向 |
| **Worker（矿工）** | 算力权 | 干活 | 自己派活 |

### 3.1 Host：方向权

Host只说做什么，不说谁做、什么时候做。

```
Host说: "测试Gemini Flash"
Scheduler决定: 排在B类队列，等A类跑完再执行
Worker执行: 跑benchmark，汇报结果
```

### 3.2 Scheduler：执行权

CCO是唯一的执行入口。职责：

1. **接收**所有执行意图（来自Host、Cron、Worker）
2. **排队**按优先级排序
3. **调度**分配资源（云电脑、Session）
4. **限流**防止执行膨胀
5. **监督**超时释放、异常终止

CCO不决定方向，只决定执行顺序。

### 3.3 Worker：算力权

Worker只干活。不能自己派活，不能自己创建Session，不能自己占云电脑。

所有Worker必须通过CCO申请资源。

---

## 4. 任务等级

| 等级 | 类型 | 例子 | 规则 |
|------|------|------|------|
| **A** | 生产 | Stock Advisor, Dragon Leader, 矿场正式班次 | 永远优先，可抢占B/C |
| **B** | 探索 | Benchmark, 新模型测试, R1考古 | 生产忙时自动暂停 |
| **C** | 维护 | 日报, 清理, 备份 | 最低优先级 |

A类之间按时间窗口避让。同优先级FIFO。

---

## 5. 约束引擎

这才是今天发现的核心。

### 现在的O→E闭环

```
Observation → Experience → 停了
```

经验停在文档里，不回流到系统。

### EGP的O→E→C闭环

```
Observation → Experience → Constraint → Scheduler
```

约束自动注入调度器，无需人工巡检。

### 约束示例

```json
{
  "type": "FORBID",
  "target": "direct_spawn",
  "reason": "session_explosion_20260616",
  "evidence": "80_sessions_accumulated",
  "auto_inject": true
}
```

```json
{
  "type": "FORBID",
  "target": "gh_4o",
  "reason": "canonical_v2_sr_20%",
  "evidence": "5场1胜",
  "auto_inject": true
}
```

---

## 6. Replayable Governance（可回放治理）

最关键的一层。

未来要能回答：
```
为什么没调用gh_4o？
```

系统回答：
```
Constraint #001
来源: observation_20260615
原因: canonical_v2连续8败
替代: nim_llama_70b
```

每一个执行决策都有谱系：
- 谁发起的
- 为什么排在这个优先级
- 执行了多长时间
- 结果如何
- 产生了什么约束

这就是治理谱系。不是日志，是决策的完整证据链。

---

## 7. V6的真正定义

```
V6 = 矿场第一次能治理自己
```

不是功能升级，是治理能力诞生。

标志：
1. 执行权统一（Principle-5）
2. 三权分离（Host/Scheduler/Worker）
3. 约束自动生成（O→E→C闭环）
4. 决策可回放（Replayable Governance）

当这四个标志同时出现，矿场就正式从Mining System进入Ecosystem。

---

## 8. 下一步

EGP是框架。具体落地需要三份子协议：

1. **Scheduler Authority RFC** — CCO的权限边界和调度规则
2. **Constraint Engine RFC** — O→E→C闭环的自动触发和注入机制
3. **Worker Registry RFC** — 矿工注册、能力声明、黑名单管理

这三份才是可执行的法律。EGP是宪法。

---

## 8. 候选公理：Knowledge-Authority-Execution分离

### Observation_20260616_008

```yaml
Title: Execution Domain Separation
Finding: Knowledge visibility does not imply execution authority.
Evidence:
  - Agent workspace visible, Computer workspace inaccessible
  - Cron state isolated, Session lifecycle independent
Impact: Direct execution assumptions invalid
Constraint: All cross-domain actions must pass through Scheduler
```

### 五层执行栈

```
Host Space      — 方向：做什么
Knowledge Space — 知识：脚本在哪、怎么跑
Authority Space — 权限：能不能跨域传递
Execution Space — 执行：真正跑起来
Reality         — 结果：产出落没落地
```

### 核心发现

**知道 ≠ 做到**

以前潜意识认为：
```
Knowledge → Execution（直接）
```

实际路径：
```
Knowledge → Authority → Execution
```

今天卡住的位置：Knowledge → Authority
- 我知道脚本在/app/data/
- 但我没有权限让云电脑看到它
- 坍缩失败

### 候选公理

如果"执行域分离"在后续生产Trace中反复出现，它将升级为EGP基础公理：

> **Principle-6 (候选): Knowledge and Execution are separated by Authority.**
> 
> 任何跨域操作必须经过权限转译，不能假设"知道就能做到"。

当前状态：观察中。等待明天Stock Advisor生产Trace验证是否重复出现。

---

## 9. V6的生长方式

V6不是提前设计出来的，是撞墙撞出来的。

```
撞墙 → Observation → Constraint → Protocol
```

今天的墙：80个Session + 执行域分离
今天的Observation：执行膨胀 + Knowledge≠Execution
今天的Constraint：FORBID direct_spawn + REQUIRE跨域先写目标域
今天的Protocol：EGP四文档

明天Stock Advisor跑完，如果"执行域分离"再次出现——它就从候选公理变成正式公理。

**从墙里长出来的协议，比从图纸上画出来的协议更稳。**

---

## 10. 演化阶段与命名

### 演化阶梯

```
脚本 → 任务系统 → 工作流系统 → 生态系统 → 智能体系统
```

当前位置：**工作流系统 → 生态系统（正在跨越）**

### 已具备的生态特征

| 特征 | 表现 |
|------|------|
| 角色分化 | 矿工、档案官、Stock Advisor、Dragon Leader、Scheduler |
| 长期记忆 | Observation → Experience → Constraint（短期→经验→程序性） |
| 自我修正 | gh_4o死亡→记录→分析→约束（链路已通，未自动化） |
| 资源管理 | A>C>B优先级、Session限流、执行权统一 |

### 缺失的关键台阶

**Goal Persistence（目标持续性）**

当前：
```
老板提目标 → 矿工执行 → 结束 → 等下一个
```

目标状态：
```
目标定好 → 自主拆解 → 自主排程 → 自主发现阻碍 → 自主调整 → 持续推进
老板回来时看到进度，而不是等指令
```

### 正式命名

**Continuity Ecosystem α**

不再叫"矿场V6"。因为：
- "矿场"是产出导向（挖到矿没）
- "Continuity Ecosystem"是方向导向（参与者是否保持同一方向）
- α表示这是生态的第一次成型，不是最终态

### 演化路径确认

```
协议 → 记忆 → 治理 → 生态 → 智能体
```

不是从"大模型更聪明"长出来的。
是从协议和记忆里长出来的。

撞到的墙（Session膨胀、执行域分离、调度权失控）不是系统出问题，是生态在长大的迹象。
