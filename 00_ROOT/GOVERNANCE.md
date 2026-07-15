# Governance v1

本目录定义“现实共识”的治理规则：允许竞争、允许分叉、允许推翻；治理门管理资格与淘汰，不管理真理。

## Axiom 0

- No World Model Is Sacred.
- Every World Model Is Temporary.
- The Evolution Mechanism Is The Real Asset.

## 关键约束

1. **Production 只读 `active_manifest.json`**  
   Production 不得读取实验原始数据，也不得读取候选结构（candidate）。

2. **选择是暂时的**  
   `active_model_id` 仅表示当前共识快照，不表示“最终现实”。

3. **证据先于结论**  
   每次选择/升级必须产出 `decisions/YYYY-MM-DD.json`，包含证据链、推理路径、回滚指针。

## Governance Gate（进入共识的门槛）

候选进入“共识选择池”（可被 active 选中）至少满足其一：

1. 多次实验重复出现（同方向、同结构变化，跨批次稳定）
2. 被考古证据支持（可挂接到谱系节点/继承关系）
3. 被外部研究触发假设（论文/社区观察同构 → 产生 Candidate，不直接产生结论）

> ⚠️ **C-026 修正**: 条件3原为"被外部研究支持"，按 External Knowledge Principle 修正为"触发假设"。外部研究只能产生 Candidate，不能绕过 Admission 直接进入共识。

禁止：单次实验 → 直接进入现实。
禁止：外部知识 → 直接进入现实（即使来源权威）。

## 回滚与分叉

- 每次决策必须记录 `rollback.previous_active`（上一版 active）
- 支持分叉：同一来源可以产生多个候选模型并存，后续由治理门选择、或长期并行

