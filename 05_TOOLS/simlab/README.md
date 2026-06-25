# SimLab：推演实验室（隔离域）

SimLab 是一个不影响生产域的“推演/回放/对照”实验室：  
只读输入（抽象后的事件/日志/研究产物），只写输出快照（snapshot），不触碰任何真实身份、真实密钥与真实用户数据。

它对应 R1 中的 `sandbox/r1_simulator_v1`：**BEHAVIORAL_SIMULATION_ONLY**。

## 设计边界（硬约束）

1. 仅模拟“行为结构”，不模拟身份/记忆/口头禅原文
2. 不读取/不写入任何 token、key、授权名单
3. 不访问外部网络（除非输入本身是公开数据源，且走统一代理层；默认关闭）
4. 输出快照只能包含：
   - 指标（pattern counts、step counts、latency 等）
   - 结构（decision path、fallback path）
   - 脱敏后的摘要（不含原始对话/PII）

## 目录结构

```text
05_TOOLS/simlab/
├── README.md
├── simlab_manifest_v1.json          # 实验室宣言：目的/限制/安全/输入输出
└── simlab_runner.py                 # 最小闭环 runner：读输入流→产出 snapshot
```

## 最小闭环怎么跑

在 `mine-seed` 根目录运行：

```bash
python 05_TOOLS/simlab/simlab_runner.py
```

它会：

1. 从 `02_MEMORY/recent_memory/daily/` 读取最近 N 天的日报（文本）
2. 抽象出“行为事件”（例如：发现/整理/建立关系/输出）
3. 输出一份脱敏快照到 `output/simlab/`（该目录已被 `.gitignore` 忽略）

## 为什么要做这个

考古不是复刻一个人，而是复刻“可继承的结构能力”。  
SimLab 的存在，让我们可以把“结构链条”用可复现的方式跑一遍，并留下快照证据。

