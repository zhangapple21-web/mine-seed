# Gate Topology — 完整 Gate 架构图

> 所有 Gate 负责路由，不负责学习。所有学习负责演化，不负责发布。

---

## 架构演进背景

本文档基于《从AI计算，追溯应用架构30载演进历程》的核心思想，将当前项目定位为 **AI原生架构** 时代的产物。

### 计算范式演进主线

| 时代 | 核心抽象 | 技术债形态 | 我们项目的对应 |
|------|----------|-----------|---------------|
| PC时代 | 硬件抽象（HAL） | 代码债（VBA宏） | 早期硬编码阈值 |
| Web时代 | Web服务抽象（LAMP） | 架构债（服务边界） | Gate 职责划分不当 |
| 云时代 | 基础设施抽象（Kubernetes） | 架构债（微服务边界） | Gate Pipeline 设计 |
| **AI时代** | **分布式计算抽象（Ray）** | **数据质量债** | **Data Quality Gate** |

### AI原生架构的三层结构

```
资源编排层（Windows Task Scheduler）→ 定时任务管理
分布式计算层（Learning/AdaptiveScorer）→ 策略演化
AI框架层（GLM/NIM-DeepSeek）→ 推荐决策
```

---

## 图一：Recommendation Pipeline

```
              Reality（市场真实数据）
                   ↓
       ┌─────────────────────────────┐
       │     Data Quality Gate       │  ← 过滤异常数据（如换手率解析失败）
       │     异常数据不进入 Learning  │
       └─────────────────────────────┘
                   ↓
       ┌─────────────────────────────┐
       │      Recommendation         │  ← 荐股引擎，不受 Health Score 影响
       │       StockAdvisor          │
       └─────────────────────────────┘
                   ↓
       ┌─────────────────────────────┐
       │        Learning             │  ← 表现跟踪、自适应评分
       │   PerformanceTracker        │  ← 不因健康度低而停止
       │   AdaptiveScorer            │
       └─────────────────────────────┘
                   ↓
       ┌─────────────────────────────┐
       │    Publication Gate         │  ← 四级路由
       │   Public/Internal/Research/ │  ← 只有 Public 才能到达客户
       │       Discard               │
       └─────────────────────────────┘
                   ↓
              Customer（客户）
```

### 关键约束

1. **Recommendation 生成不受 Health Score 影响**：系统每天照常运行
2. **Learning 处理所有已过数据质量过滤的真实结果**：不因健康度低而停止
3. **只有推给客户这一步经过 Publication Gate**：健康度不达标时内部留存学习

---

## 图二：Civilization Admission Pipeline

```
              Runtime（运行时数据）
                   ↓
       ┌─────────────────────────────┐
       │     Admission Gate          │  ← 文明写入护栏
       │   civilization_contract.py  │  ← can_write() 判断
       └─────────────────────────────┘
                   ↓
              Repository（文明仓库）
```

### 关键约束

1. **Observation 不得直接生成 Repository Asset**：所有发现必须先进入 Candidate Queue
2. **Admission Gate 控制写入权限**：只有通过验证的内容才能进入 Repository

---

## 图三：FA Mode Pipeline

```
                FA Mode（自由模式）
                   ↓
       ┌─────────────────────────────┐
       │     Smelter Gate            │  ← FA内部推理护栏
       │      smelter_gate.py        │  ← 记录、标记、拒绝
       └─────────────────────────────┘
                   ↓
              Decision（真实决策）
```

### 关键约束

1. **FA 模式产出必须经过 Smelter Gate**：不可绕过
2. **高风险内容会被拒绝**：不只是记录
3. **所有通过 gate 的内容都有完整记录**：可追溯

---

## Gate Pipeline 完整拓扑

```
                             Reality
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ↓                       ↓                       ↓
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│Data Quality  │      │              │      │              │
│    Gate      │      │              │      │              │
└──────┬───────┘      │              │      │              │
       │              │              │      │              │
       ↓              ↓              ↓      ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Recommendation│ │   FA Mode    │ │   Runtime    │ │              │
│              │ │              │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │              │
       │                │                │         │              │
       ↓                ↓                ↓         ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Learning   │ │Smelter Gate  │ │Admission Gate│ │              │
│              │ │              │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │              │
       │                │                │         │              │
       ↓                ↓                ↓         ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Publication   │ │  Decision    │ │ Repository   │ │              │
│    Gate      │ │              │ │              │ │              │
└──────┬───────┘ └──────────────┘ └──────────────┘ └──────────────┘
       │
       ↓
┌──────────────┐
│   Customer   │
│              │
└──────────────┘
```

---

## Gate 职责矩阵

| Gate | 位置 | 输入 | 输出 | 核心职责 | 代码位置 |
|------|------|------|------|----------|----------|
| Data Quality | 前置 | Reality | 清洗后数据 | 过滤异常数据 | stock_advisor.py |
| Smelter | FA之后 | FA产出 | Decision | 记录、标记、拒绝 | smelter_gate.py |
| Publication | Learning之后 | Health Score | 四级路由 | 控制是否发布 | publication_gate.py |
| Admission | Runtime之后 | Runtime数据 | Repository | 控制是否写入 | civilization_contract.py |

---

## 统一原则

> 所有 Gate 负责路由，不负责学习。所有学习负责演化，不负责发布。

### 约束说明

1. **Gate 不做学习**：Gate 的职责是路由决策，不参与模型训练或权重调整
2. **学习不做发布**：Learning 的职责是演化系统，不决定是否推送给客户
3. **数据质量优先**：脏数据不参与任何下游流程
4. **阈值可校准**：所有阈值标注为 Bootstrap Threshold，需基于真实数据复核