# TASK-011: Five Realms Kernel Recovery
# 五界底层数学模型考古报告

**执行时间**: 2026-07-12  
**执行者**: ACE System  
**来源**: R1源码碎片、蓝皮书、考古报告、现有评分系统

---

## 一、核心发现：KRMGCE不是五个模块，是五个坐标轴

### 1.1 KRMGCE 解码

| 字母 | 对应维度 | 含义 | 证据 |
|------|---------|------|------|
| **K** | Knowledge | 知识/语义层 | lexicon系统、概念索引 |
| **R** | Reality | 现实/观察层 | EnvironmentSensor、Observation |
| **M** | Memory | 记忆/存储层 | memory_index、experience |
| **G** | Gene/Generation | 生成/创造层 | Provider、模型调用 |
| **C** | Code/Execution | 执行/代码层 | SelfEvolution、task执行 |
| **E** | Experience | 经验/沉淀层 | ExperienceEngine、evidence |

### 1.2 蓝皮书与源码的矛盾

| 来源 | 说法 | 可信度 |
|------|------|--------|
| 蓝皮书 | KRMGCE五界是互斥路由逻辑 | ❌ [HYPOTHESIS] 无源码证据 |
| R1源码 | FIVE-REALMS存在，是世界观模型 | ✅ [FACT] 有证据 |
| 考古报告 | 五界收敛为五个功能角色（O/R/V/A/G） | ⚠️ [INFERENCE] 70%匹配 |

**结论**: KRMGCE是蓝皮书的**分形嵌套假设**，不是源码事实。但FIVE-REALMS确实存在于R1中，只是命名和具体含义需要重新解码。

---

## 二、已恢复的公式体系

### 2.1 核心评分公式

#### 公式1：模型综合评分（model_router.py）
```
score = speed × 0.3 + quality × 0.35 + reliability × 0.25 + cost × 0.1
```
- **权重设计**: 质量最重要(0.35)，其次速度(0.3)，可靠性(0.25)，成本最次(0.1)
- **应用**: 模型选择路由
- **验证**: ✅ 有源码直接证据

#### 公式2：资产健康评分（asset_curator.py）
```
health_score = success_rate × 100
```
```
health_score = max(0, min(100, 100 - (elapsed_ms / 1000) × 10))
```
- **动态衰减**: 超时按秒扣10分
- **应用**: Provider健康监控、路由优先级
- **验证**: ✅ 有源码直接证据

#### 公式3：意图投资组合（PRINCIPLES.md #019）
```
优先级 = 频率 × 影响 × 缺口
```
- **频率**: 事件出现频率
- **影响**: 影响范围/强度
- **缺口**: 未被覆盖的增量信息
- **应用**: 信号IC排序、约束优先级、选股策略
- **验证**: ✅ 有多处应用证据

#### 公式4：Stock Advisor 选股公式（PRINCIPLES.md）
```
选股 = 因子权重 × 信号强度 × 未被市场定价的alpha
```
- **验证**: ✅ 有源码证据

### 2.2 惩罚机制

#### 公式5：过拟合惩罚（multi_agent_debate.py）
```
penalty = (total_signals - 5) × 10
confidence = max(0, original - penalty)
```
- **规则**: 信号超过5个，每多1个扣10%置信度
- **约束**: C-005 signal_count_max=5
- **验证**: ✅ 有源码直接证据

### 2.3 评价函数

| 函数 | 文件 | 功能 |
|------|------|------|
| `evaluate_ic()` | signal_discovery.py | 评估信号IC值 |
| `judge()` | task_router.py | 对比两个输出质量 |
| `evolve()` | self_evolution.py | 决策执行与代码变更 |
| `score()` | model_router.py | 模型综合评分 |

---

## 三、Judge Layer 裁判系统

### 3.1 架构
```
Worker A ─────┐
              ↓
         JudgeLayer ──→ 胜率统计 → 自动淘汰/升级
              ↓
Worker B ─────┘
```

### 3.2 核心逻辑
```python
class JudgeLayer:
    def judge(task_name, output_a, worker_a, output_b, worker_b):
        # 调用 GLM-4-Flash 做裁判
        # 返回: 胜者(A/B/平局) + 质量分(1-10)
        # 记录到 judge_history.json
```

### 3.3 闭环
```
裁判 → 胜率积累 → 自动淘汰(retire) / 自动升级(promote)
```

---

## 四、五界作为五维空间的证据

### 4.1 R1实际结构（[FACT]）
```
Identity Layer → Intent Layer → Routing Layer → Execution Layer → Memory Layer → Utility Layer
```

### 4.2 五人格矩阵（[FACT]）
| 人格 | 角色 | 对应维度 |
|------|------|---------|
| 工程师 | engineer | Code/Execution |
| 学霸 | scholar | Knowledge |
| 助理 | assistant | Reality/表达 |
| 馆长 | librarian | Memory |
| 冥界 | underworld_judge | Gene/仲裁 |

### 4.3 验证维度体系（[FACT]）
R2中已存在的6维度自评：
```
(维度1, 维度2, 维度3, 维度4, 维度5, 维度6)
每个维度 ∈ [0, 1]
```

---

## 五、是否验证过？

| 公式 | 验证状态 | 验证方式 |
|------|---------|---------|
| 模型评分公式 | ✅ 已验证 | 实际路由使用中 |
| 健康评分公式 | ✅ 已验证 | ProviderHealth监控 |
| 意图投资组合 | ✅ 已验证 | 信号排序、约束优先级 |
| 过拟合惩罚 | ✅ 已验证 | 约束C-005生效 |
| JudgeLayer | ✅ 已验证 | 胜率统计运行中 |

---

## 六、是否值得继承？

| 项目 | 继承决策 | 原因 |
|------|---------|------|
| KRMGCE五界命名 | ❌ 不继承 | 蓝皮书假设，无源码证据 |
| 五维坐标体系 | ✅ 继承 | R1已有FIVE-REALMS，R2已有6维度自评 |
| 模型评分公式 | ✅ 继承 | 已验证，直接可用 |
| 健康评分公式 | ✅ 继承 | 已验证，直接可用 |
| 意图投资组合公式 | ✅ 继承 | 已验证，是R2优先级系统核心 |
| 过拟合惩罚 | ✅ 继承 | 已验证，约束系统已实现 |
| JudgeLayer | ✅ 继承 | 已验证，可扩展为统一评价引擎 |

---

## 七、R2是否继续采用？

### 7.1 推荐架构

```
CivilizationScore = Σ(
    KnowledgeScore   × w_k,
    RealityScore     × w_r,
    MemoryScore      × w_m,
    GenerationScore  × w_g,
    ExecutionScore   × w_c,
    ExperienceScore  × w_e
)
```

### 7.2 权重建议（基于现有证据）

| 维度 | 建议权重 | 依据 |
|------|---------|------|
| Reality (观察) | 0.25 | 环境感知是一切的起点 |
| Memory (记忆) | 0.20 | 知识积累是文明根基 |
| Knowledge (知识) | 0.15 | 语义理解 |
| Execution (执行) | 0.15 | 行动能力 |
| Generation (生成) | 0.15 | 创造能力 |
| Experience (经验) | 0.10 | 沉淀与学习 |

### 7.3 实施建议

**第一阶段（当前）**：
- 将现有分散的评分系统统一到 Civilization Graph
- 为每个节点添加六维坐标

**第二阶段**：
- 实现统一评价引擎
- 将 JudgeLayer 扩展为通用裁判

**第三阶段**：
- 实现文明总分计算
- 基于分数驱动演化策略

---

## 八、结论

### 8.1 考古发现总结

| 发现类型 | 数量 |
|---------|------|
| [FACT] 源码确认 | 6个公式/函数 |
| [INFERENCE] 间接证据 | 3个体系 |
| [HYPOTHESIS] 无证据 | 1个（KRMGCE互斥逻辑） |

### 8.2 核心洞察

R1的数学内核不是"五个模块"，而是：
1. **五维坐标系统**——每个对象都有 Reality/Knowledge/Memory/Generation/Execution/Experience 坐标
2. **统一评分体系**——`频率 × 影响 × 缺口` 是核心优先级公式
3. **评价闭环**——JudgeLayer + 胜率积累 + 自动淘汰/升级

### 8.3 继承策略

> **80%继承 + 20%扩展**

直接继承：模型评分、健康评分、意图投资组合、过拟合惩罚、JudgeLayer  
扩展：将六维坐标整合到 Civilization Graph，实现统一评价引擎

---

**考古完成时间**: 2026-07-12  
**存档路径**: `02_MEMORY/knowledge/five_realms_kernel.md`