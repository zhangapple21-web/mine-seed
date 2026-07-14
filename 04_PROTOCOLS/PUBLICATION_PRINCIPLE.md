# Publication Principle

> Execution Never Stops. Learning Never Stops. Publication Is Conditional.
> 所有 Gate 负责路由，不负责学习。所有学习负责演化，不负责发布。

---

## 核心原则

### 原则一：执行不停

Recommendation 生成流程不受 Health Score 影响。系统每天照常运行，不因健康度低而停止产出。

### 原则二：学习不停

Learning（表现跟踪、AdaptiveScorer）继续处理所有真实结果（已过数据质量过滤的），不因 Health Score 低而停止。这些真实的胜负数据本身就是最宝贵的训练素材。

### 原则三：发布有条件

只有推给客户这一步（TG推送/报告输出）经过 Publication Gate。健康度不达标时，推荐结果内部留存学习，不对外发布。

### 原则四：脏数据不参与学习

Learning 的输入必须先经过 Data Quality Gate，异常数据不参与学习，不能以"Learning不能停"为由让异常数据混入。

---

## 例外情况

唯一的例外是 **Discard 路由**（健康度 < 30）：
- 推荐结果直接废弃，不进入 Learning
- 理由：健康度过低时，系统的判断已经不可靠，这些结果可能包含噪声，不应作为学习素材

---

## Gate Pipeline 架构

```
Reality
  ↓
Data Quality Gate（过滤异常数据）
  ↓
Smelter Gate（FA内部推理护栏）
  ↓
Publication Gate（客户发布）
  ↓
Admission Gate（文明写入）
  ↓
Repository
```

### Gate Pipeline 实例

本原则是三次独立场景收敛出的通用模式，已知实例：

1. **Smelter Gate**（smelter_gate.py）：FA内部推理 → 真实决策
2. **Admission Gate**（civilization_contract.py）：Runtime → Civilization Repository
3. **Publication Gate**（publication_gate.py）：Recommendation → Customer

### 统一原则

> 所有 Gate 负责路由，不负责学习。所有学习负责演化，不负责发布。

---

## 与 E→C 闭环的关系

Publication Gate 和 E→C 闭环是同一事物的两面：
- **内部**：留下所有真实交易结果用于学习（E→C）
- **外部**：只放行质量达标的推荐（Publication Gate）

两者协同工作，实现系统的自我进化和风险控制。