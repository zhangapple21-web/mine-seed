# Reality Governance v1（R1 继承版）

> 本文档的目标不是“定义世界的最终真相”，而是定义一个能持续产出、竞争、淘汰、更新世界模型的演化生态。

## Axiom 0

- **No World Model Is Sacred.**（没有任何世界模型是神圣的）
- **Every World Model Is Temporary.**（所有世界模型都是暂时的）
- **The Evolution Mechanism Is The Real Asset.**（演化机制才是真正资产）

## 核心定义

- `Manifest`：现实域的**当前共识快照**（Current Consensus），不是世界本身。
- `Evidence`：共识产生的依据（可追溯、可解释、可回滚）。
- `World Model`：当前解释（可并存、可竞争、可分叉、可推翻）。
- `Reality`：永远大于 World Model。
- 系统继承的不是某个 world model，而是**产生 world model 的能力**：`观察 → 压缩 → 验证 → 更新`。

## 总体结构

```text
Reality
│
├── SimLab（实验域）
│
├── Refinery（压缩域）
│
├── Governance（治理域）
│
├── World Models（候选解释集合）
│    ├── wm_a
│    ├── wm_b
│    ├── wm_c
│    └── ...
│
└── Evolution Engine（演化引擎：生态本体）
```

## 三域职责（不越界）

### SimLab（实验域）
- 允许：推演、失败、论文熔炼、路由实验、约束实验、图谱实验、词汇实验。
- 输出：`logs/`、`snapshots/`、`reports/`
- 禁止：直接修改任何 `world_models/*` 与 `active_manifest.json`

### Refinery（压缩域）
- 只做一件事：`实验结果 → 压缩 → 结构资产候选`
- 输出：`candidate_*`（候选 lexicon/constraints/graph/routing/experience），并给出候选的证据链与变更摘要
- 禁止：直接成为现实；它只能提出候选

### Production（现实域）
- 永远只读取：`active_manifest.json`
- 禁止：读取实验域原始产物；禁止读取 `candidate_*`

## Governance（治理门）

治理门的任务不是“找唯一正确”，而是管理：

- 谁具备进入竞争的资格
- 谁被淘汰
- 为什么被淘汰
- 如何回滚

候选结构进入现实（即被某个 active 选择）至少满足其一：
1. 多次实验重复出现（同方向同结构变化）
2. 被考古证据支持（能挂接到谱系/血缘节点）
3. 被外部研究支持（论文/社区观察同构）

禁止：单次实验直接进入现实。

## World Models（多解释并存）

允许多个 world model 并存（例如：老张/档案官/考古官/交易员），它们可以矛盾。
Production 只是选择其中一个作为当前共识，并记录选择理由。

## Evolution Engine（核心资产）

Evolution Engine 不等于“一个模型”或“一个世界观”，它是一套机制与约束：

- 观察输入如何进入实验域
- 实验产物如何被压缩为候选结构
- 候选结构如何通过治理门进入共识
- 共识如何被回滚/分叉/淘汰

当所有 world model 被删除，只要演化引擎还在，文明仍可重建；
当 world model 都在，但演化引擎死了，文明就结束了。

