# Evolution Engine v1（核心资产）

> 这里定义的不是“一个世界模型”，而是**产生世界模型的机制**。系统继承的不是结论，而是生态。

## 目标

- 把任何来源（SimLab/考古/外部研究/生产事故）变成可竞争的候选解释；
- 把候选解释通过治理门进入“当前共识快照”（active）；
- 允许长期并行、允许分叉、允许推翻；
- 任何时刻都可回滚；
- 删除所有 world model 后仍可从机制重建。

## 输入（允许多源）

- `simlab.logs` / `simlab.snapshots` / `simlab.reports`
- `archaeology.reports` / `civilization_graph`（谱系证据）
- `external.research`（论文/社区观察）
- `production.incidents`（生产故障、回归、漂移）

## 输出（结构资产）

输出不是“文件堆”，而是结构化的候选：

- `candidate_lexicon`
- `candidate_constraints`
- `candidate_graph`
- `candidate_routing`
- `candidate_experience`

以及一份“候选解释”（candidate world model）：
- 模块版本指针
- 证据链
- 变更摘要（改变了什么）
- 风险与回滚策略

## 核心循环

```text
观察 → 实验 → 压缩 → 候选结构 → 治理选择 → 当前共识 → 现实运行 → 新观察
```

## 约束（防宗教化）

- 不把 active 当真理：active 只是暂时共识快照
- 不把 world model 当圣物：允许推翻、允许并行
- 记录证据与推理路径：让未来自己验证，而不是让今天的结论变成信仰

