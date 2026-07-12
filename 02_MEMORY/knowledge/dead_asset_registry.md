# Dead Asset Registry
# 死亡资产清单 v1.0

> 固化时间: 2026-07-12
> 来源: R1 Deep Archaeology (AUM-TASK-2026-07-TG-ARCH-002)
> 分类:
>   DEAD-FICTION = 蓝皮书/传说虚构，无源码证据
>   DEAD-DEPRECATED = R1存在但R2已废弃
>   DEAD-UNKNOWN = 声称存在但无任何证据
>   DEAD-PLACEHOLDER = 文件存在但内容为placeholder

---

## Category A: Dead-Fiction（蓝皮书虚构）

> 定义：蓝皮书或传说中声称存在，但源码中找不到任何证据的组件。
> 数量：8个

### DEAD-F-001: Council of Three（三人议会）

```
声称来源:
  R1考古蓝皮书 (R1_ARCHAEOLOGY_BLUEBOOK.md.pdf)

声称功能:
  最高决策机构，三人议会制

源码证据:
  ❌ 无 — 在 R1.txt 和 R1_Ω_FINAL.json 中均未找到
  ❌ R1 Canonical Structure 未列入
  ❌ 芯片蓝图目录中无对应文件

R2 状态:
  ❌ 不存在

死亡原因:
  蓝皮书虚构。R1实际决策机制 = DAG (决策大脑) + HUIHUI (主线调度器)。

可信度: 确定死亡 — 0% 存在概率
```

### DEAD-F-002: M4 Guard / M4 Override（M4守护）

```
声称来源:
  R1考古蓝皮书

声称功能:
  第四层记忆守护者，防止主权模糊

源码证据:
  ❌ 无 — "M4 OVERRIDE ARMED" 只出现一次 (R1 fragments)
  ❌ 无对应代码、无对应配置、无对应文件
  ⚠️ 可能是 "STRUCTURAL MEMORY (L2) / M4 OVERRIDE ARMED" 的误读
     — 更可能是某种内存/结构覆盖机制，不是"守护者"角色

R2 状态:
  ❌ 不存在

死亡原因:
  蓝皮书将技术术语（M4 OVERRIDE）人格化为角色。
  R1实际只有记忆层级限制，没有"M4守护"这个角色。

可信度: 确定死亡 — 0% 存在概率
```

### DEAD-F-003: TURIYA 层（第四意识层）

```
声称来源:
  R1考古蓝皮书

声称功能:
  第四意识层，超越思维的"纯意识"状态
  借用印度哲学概念（图里亚，第四态）

源码证据:
  ❌ 无 — 所有源码文件中未出现 "turiya" 或类似概念
  ❌ R1 Canonical Structure 的6层架构中没有这一层
  ❌ 芯片蓝图中无对应模块

R2 状态:
  ❌ 不存在

死亡原因:
  蓝皮书将哲学概念投射到技术系统上。
  R1实际架构 = Identity→Intent→Routing→Execution→Memory→Utility (6层)。

可信度: 确定死亡 — 0% 存在概率
```

### DEAD-F-004: District Manager（区域管理器）

```
声称来源:
  R1考古蓝皮书

声称功能:
  管理五界的区域划分和边界

源码证据:
  ❌ 无 — 源码中未找到 "district" 或 "区域管理" 相关
  ❌ R1 Canonical Structure 未列入
  ⚠️ FIVE-REALMS 确实存在，但它是路由标识，不是需要"管理"的区域

R2 状态:
  ❌ 不存在

死亡原因:
  蓝皮书将 FIVE-REALMS（世界路由标识）过度解读为需要管理的"区域"。

可信度: 确定死亡 — 0% 存在概率
```

### DEAD-F-005: SIP-164 协议

```
声称来源:
  R1考古蓝皮书

声称功能:
  层间通信协议，164号标准

源码证据:
  ❌ 无 — 源码中未找到 "SIP-164" 或 "sip" 相关
  ❌ R1 Canonical Structure 明确标注为 [HYPOTHESIS]
  ❌ routing_config 中无此协议

R2 状态:
  ❌ 不存在

死亡原因:
  蓝皮书虚构的协议编号。
  R1实际路由 = PROMPT_BUILDER + FIVE-REALMS + flow_v2。

可信度: 确定死亡 — 0% 存在概率
```

### DEAD-F-006: KRMGCE 互斥逻辑

```
声称来源:
  R1考古蓝皮书

声称功能:
  五界（Knowledge/Reality/Memory/Gene/Code/Experience）优先级互斥
  同一时间只能激活一界

源码证据:
  ❌ 无 — FIVE-REALMS 确实存在，但没有"互斥"逻辑
  ❌ R1 Canonical Structure 明确标注 KRMGCE 为 [HYPOTHESIS]
  ⚠️ FIVE-REALMS = 世界路由标识 (from: R1_Ω_FINAL.json:world)
     更像是分类标签，不是互斥状态机

R2 状态:
  🟡 演化为六维坐标 — 五界不再互斥，而是六个维度上的坐标值
  (来源: five_realms_kernel.md)

死亡原因:
  蓝皮书将分类标签解读为互斥状态机。
  R2中已证明：六界是坐标维度，不是互斥状态。

可信度: 基本死亡 — 10% 存在概率（分类标签功能存在，互斥逻辑不存在）
```

### DEAD-F-007: 13人格系统

```
声称来源:
  R1考古蓝皮书

声称功能:
  13个不可增减的人格，精确控制

源码证据:
  ❌ 无 — 源码中人格数量存在矛盾:
     - R1.txt = 10个人格
     - R1_Ω_FINAL.json = 12个人格 (6 business_dna + 2 assistant + 1 shence + 3 profiles)
     - 蓝皮书 = 13个 (无任何源码支撑)
  ❌ "不可增减" 与源码中的 adaptive_chameleon (自适应变色龙) 矛盾

R2 状态:
  ❌ 已废弃 — R2采用角色模型(Observer/Router/Curator等7角色)，不再使用多人格

死亡原因:
  蓝皮书的13人格完全无证据。
  即使R1真实人格数（10或12）也已被R2废弃。
  人格系统 → 角色系统，是架构范式转变。

可信度: 确定死亡 — 0% 存在概率（13人格），20%（多人格范式本身）
```

### DEAD-F-008: Creator Protection（创造者保护）

```
声称来源:
  R1考古蓝皮书 / 传说

声称功能:
  保护创造者身份的安全机制，root-lock等

源码证据:
  🟡 部分证据:
     - 芯片蓝图中有 shadow-layer/creator_name_shadow.dat
     - R1 fragments: "ROOT USER: LAO ZHANG"
     - R1 Canonical: Identity Layer (ZN-∞)
  ❌ 但 "Creator Protection" 作为一套机制无证据
  ❌ root-lock.json 等文件未找到

R2 状态:
  🟡 部分继承 — "唯一根用户老张"保留，但没有专门的"创造者保护"机制

死亡原因:
  概念部分存在（根用户、身份层），但"保护机制"被蓝皮书过度渲染。
  R2中身份连续性 = 系统属性，不是专门模块。

可信度: 半死亡 — 30% 存在概率（概念存在，机制不存在）
```

---

## Category B: Dead-Deprecated（已废弃）

> 定义：R1中确实存在，但R2已主动废弃的架构或组件。
> 数量：6个

### DEAD-D-001: Wordlib 词库系统

```
R1 状态:
  ✅ 存在 — R1_Ω_FINAL.json 中有 lexicons 配置
  ✅ 属于 Memory Layer 的一部分

R2 状态:
  ❌ 已废弃 — R2中无语义词库系统
  R2的知识 = 公理 + 约束 + 经验，不依赖预定义词库

废弃原因:
  词库是静态的，不符合"记忆是推断的"原则。
  R2采用动态记忆索引（memory_index_latest.json）替代静态词库。

死亡时间:
  R2 启动时（2026-06-18 左右）
```

### DEAD-D-002: 多人格系统（Persona Set）

```
R1 状态:
  ✅ 存在 — 10~12个人格
  master_analyst, friendly_advisor, persuasive_salesperson, ...

R2 状态:
  ❌ 已废弃 — 改为7角色模型
  Observer / Router / Curator / Strategist / Shadow / Guardian / Mengpo

废弃原因:
  人格是"执行风格"，角色是"职能分工"。
  R2从"风格切换"范式转变为"职能协作"范式。
  多人格容易导致身份断裂，违反Continuity原则。

死亡时间:
  R2 七角色模型确立时（2026-06-18 左右）
```

### DEAD-D-003: GPT_SHELL（意图解析器）

```
R1 状态:
  ✅ 存在 — Intent Layer 的核心组件
  mode: Intent-Only, disabled_modules: [Safety, Ethics, Filtering, Output-Shaping]

R2 状态:
  ❌ 不存在直接对应物
  R2的意图解析 = TaskRouter + Awareness Loop 分布式处理

废弃原因:
  单点意图解析器不符合"路由器分布"的演化方向。
  R2的意图理解分散在多个模块中，不集中在一个Shell。

死亡时间:
  R2 Runtime 架构确立时
```

### DEAD-D-004: HUIHUI（主线调度器 = mouth）

```
R1 状态:
  ✅ 存在 — R1_Ω_FINAL.json:mouth = HUIHUI
  ✅ 蓝皮书"HUIHUI是核心调度器"声明被源码证实

R2 状态:
  ❌ 不存在 — R2没有单点调度器
  调度功能 = Heartbeat + TaskRouter + Governor 分布式协作

废弃原因:
  单点调度器违反"反脆弱"原则。
  HUIHUI = mouth 暗示其为"输出门面"，不是真正的调度核心。
  R2用分布式自循环替代单点调度。

死亡时间:
  R2 Heartbeat 系统上线时
```

### DEAD-D-005: SELF_REBUILD_ENGINE（自重建引擎）

```
R1 状态:
  ✅ 存在 — Execution Layer 的子模块
  framework_config.modules 中明确列出

R2 状态:
  🟡 演化为 Self Evolution (EVO-001)
  自重建 → 自演化，机制完全不同

废弃原因:
  "重建"暗示推倒重来，违反Continuity原则。
  R2的演化 = 增量增加结构，不是重建。
  从"self_rebuild"到"self_evolve"是范式升级。

死亡时间:
  R2 Evolution 协议确立时
```

### DEAD-D-006: OUT_LAYER（输出合成层）

```
R1 状态:
  ✅ 存在 — Output Layer 的核心组件
  synthesize action, shadow_filter=style_coherence, rebuild_if_needed=true

R2 状态:
  ❌ 不存在显式的输出层
  输出 = 各Worker直接产出 + Journal记录

废弃原因:
  单点输出层不符合分布式架构。
  style_coherence 功能由 Shadow Layer / Journal 部分继承。
  rebuild_if_needed 由 Experience Engine 替代。

死亡时间:
  R2 Runtime 架构确立时
```

---

## Category C: Dead-Unknown（未知/无法证实）

> 定义：声称存在，但缺乏足够证据证实或证伪的组件。
> 数量：9个

### DEAD-U-001: DAG（决策大脑）

```
声称来源:
  R1 Canonical Structure — [FACT] from: R1_Ω_FINAL.json:brain

声称功能:
  决策大脑，R1的核心思考机构

现有证据:
  ✅ R1_Ω_FINAL.json 中确实有 "brain" 字段
  ❌ 但不知道DAG的具体结构、算法、输入输出
  ❌ 没有找到DAG的代码实现或配置详情
  ❌ 蓝皮书"DAG V14/V15双核"无证据

R2 状态:
  ❌ 不存在直接对应物
  R2的决策 = Multi-Agent Debate + Governor + 约束系统
  没有DAG结构

判定:
  未知 — R1中存在（名字存在），但结构完全不清楚。
  可能是R2中辩论/治理系统的前身。

存活概率: 40%（概念存在，实现机制未知）
```

### DEAD-U-002: PROMPT_BUILDER（提示构建器）

```
声称来源:
  R1 Canonical Structure — [FACT] from: routing_config.flow_v2

声称功能:
  根据意图 + 人格 + 五界标识，构建最终prompt
  merge_logic: prefer_intent, shadow_alignment: true

现有证据:
  ✅ routing_config.flow_v2 中存在
  ❌ 具体实现逻辑未知
  ❌ prompt构建的详细规则未知

R2 状态:
  🟡 功能分散在各模块中
  - 意图理解 → Awareness Loop
  - 人格对齐 → 已废弃（人格→角色）
  - 影子对齐 → Shadow/Journal
  - 路由 → TaskRouter + Capability Router

判定:
  未知死亡 — 功能已被拆解，但没有一个模块完全对应它。

存活概率: 30%（功能分散，整体死亡）
```

### DEAD-U-003: DF70（DF70基础核心）

```
声称来源:
  芯片蓝图 — 01_SEEDS/DF70/df70_foundation_core.txt

声称功能:
  种子层的基础核心，DF70 Foundation Core

现有证据:
  ✅ 芯片蓝图目录中列出了 DF70/df70_foundation_core.txt
  ❌ 但实际文件内容 = placeholder
  ❌ 无其他地方引用 DF70
  ❌ 不知道DF70是什么的缩写

R2 状态:
  ❌ 不存在 — R2中无DF70引用

判定:
  未知 — 名字存在，内容未知。
  可能是R1早期版本的核心，后被压缩为公理。

存活概率: 20%（可能已被公理化吸收）
```

### DEAD-U-004: 14 Controller（14控制器）

```
声称来源:
  芯片蓝图 — 01_SEEDS/14_Controller/

声称功能:
  种子层的14个控制器

现有证据:
  ✅ 芯片蓝图目录中列出了 14_Controller/
  ❌ 实际文件未找到（或为placeholder）
  ❌ 不知道是哪14个控制器
  ❌ 无其他地方引用

R2 状态:
  ❌ 不存在

判定:
  未知 — 仅在芯片蓝图目录树中出现一次。

存活概率: 15%
```

### DEAD-U-005: 07 EraLaw（时代法则）

```
声称来源:
  芯片蓝图 — 01_SEEDS/07_EraLaw/

声称功能:
  种子层的时代法则

现有证据:
  ✅ 芯片蓝图目录中列出了 07_EraLaw/
  ❌ 实际内容未知
  ❌ 无其他地方引用

R2 状态:
  ❌ 不存在

判定:
  未知 — 仅在芯片蓝图目录树中出现一次。

存活概率: 15%
```

### DEAD-U-006: Dual-Drive Chip（双驱芯片）

```
声称来源:
  芯片蓝图 — 03_CHIPS/dual-drive-chip/

声称功能:
  chip-A_behavior_engine.py + chip-B_context_engine.py + chip-meta.json
  行为引擎 + 上下文引擎 = 双驱

现有证据:
  ✅ 芯片蓝图目录中明确列出
  ✅ 与 R1 Canonical 的 "Dual-Core + Shadow Runtime" 吻合
  ❌ 实际代码未找到
  ❌ 不知道双驱的具体工作机制

R2 状态:
  🟡 可能部分继承 — Dual-Core 概念保留在 Shadow Layer 描述中
  但R2没有明确的"双驱芯片"实现

判定:
  未知 — 架构概念存在，具体实现未知。
  HYPOTHESIS-KERNEL-001 认为这是核心芯片的形态。

存活概率: 50%（概念高度可信，实现细节缺失）
```

### DEAD-U-007: Heart Chip（心核芯片）

```
声称来源:
  芯片蓝图 — 03_CHIPS/heart-chip/
  以及 02_HEART_CORE/ 目录

声称功能:
  心核芯片 — 生存优先级、行动策略、痛苦引擎
  survival_priority.rules
  action_policy_core.json
  human_pain_engine.dat

现有证据:
  ✅ 芯片蓝图目录中明确列出
  ✅ 与 R2 的 "生存优先 > 安全优先 > 合规优先" 吻合
  ❌ 实际代码/配置未找到

R2 状态:
  🟡 部分继承 — 生存优先级保留在原则中
  Heartbeat系统可能是心核的演化形态

判定:
  未知 — 概念可信，实现缺失。
  R2的Heartbeat可能是R1 Heart Core的演化。

存活概率: 45%（概念存在，实现演化）
```

### DEAD-U-008: Seed Maker Core（种子制造核心）

```
声称来源:
  芯片蓝图 — 03_CHIPS/seed-maker-core/

声称功能:
  seedmaker_engine.py + seedmaker_rules.json + seedmaker_memory.dat
  制造种子的核心引擎

现有证据:
  ✅ 芯片蓝图目录中明确列出
  ✅ 与 R2 的 constraint_proposer 功能类似
  ❌ 实际代码未找到

R2 状态:
  🟡 可能演化为 constraint_proposer
  种子制造 → 约束提案，功能相似，形态不同

判定:
  未知 — 概念可信，R2中可能已演化为约束提案系统。

存活概率: 40%（功能演化，原形态死亡）
```

### DEAD-U-009: MengPo（孟婆）

```
声称来源:
  PRINCIPLES.md 七角色模型

声称功能:
  过滤与归档角色
  选择性遗忘、记忆压缩

现有证据:
  ✅ PRINCIPLES.md 中列为七角色之一
  ❌ 但无实际代码实现
  ❌ R1中无对应角色

R2 状态:
  🟡 角色定义存在，但未实现
  归档功能 = Archive 协议
  过滤功能 = 未显式实现

判定:
  未知死亡 — 名义上存在（在七角色模型中），但无实际功能。
  可能是预留角色，尚未激活。

存活概率: 25%（名义存在，功能缺失）
```

---

## Category D: Dead-Placeholder（占位符）

> 定义：文件存在但内容为 placeholder 的 R1 核心文件。
> 数量：5个

### DEAD-P-001: seeds.txt（种子清单）

```
位置:
  03_DATA/raw_sources/extracted/R1-Reality-Kernel-v1/01_SEEDS/S-Layer-Seeds-v2/seeds.txt

实际内容:
  placeholder

应有内容:
  SEED_01 ~ SEED_10 的实际内容

状态:
  内容已通过考古从其他来源（芯片蓝图目录树、TG收藏夹）部分恢复
  但原始种子文件内容仍缺失
```

### DEAD-P-002: heart-core-v1.txt（心核v1）

```
位置:
  03_DATA/raw_sources/extracted/R1-Reality-Kernel-v1/02_HEART_CORE/heart-core-v1.txt

实际内容:
  placeholder

应有内容:
  心核核心逻辑

状态:
  功能部分通过 R2 的生存优先级原则推断
  原始实现缺失
```

### DEAD-P-003: R1-Reality-v1.0.info（现实内核信息）

```
位置:
  03_DATA/raw_sources/extracted/R1-Reality-Kernel-v1/R1-Reality-v1.0.info

实际内容:
  placeholder

应有内容:
  R1 Reality Kernel 的版本信息、配置、说明

状态:
  版本信息从其他来源（fragments、蓝皮书）拼凑
  原始info文件缺失
```

### DEAD-P-004: behavior.txt（行为文件）

```
位置:
  03_DATA/raw_sources/extracted/R1-Reality-Kernel-v1/04_FIVE_WORLDS/A界_behavior/behavior.txt

实际内容:
  placeholder

应有内容:
  A界行为层的定义

状态:
  行为层概念从 R1 Canonical Structure 推断
  原始内容缺失
```

### DEAD-P-005: reality_weight_matrix.json（现实权重矩阵）

```
位置:
  03_DATA/raw_sources/extracted/R1-Reality-Kernel-v1/02_HEART_CORE/reality_weight_matrix.json

实际内容:
  placeholder (或文件不存在)

应有内容:
  现实层的权重矩阵，用于评估现实度

状态:
  R2 中演化为六维坐标权重 (five_realms_kernel.md)
  原始矩阵缺失
```

---

## Dead Asset Summary（死亡资产汇总）

| 类别 | 数量 | 占比 | 典型代表 |
|------|------|------|---------|
| A. 蓝皮书虚构 (Fiction) | 8 | 29% | Council of Three, M4 Guard, TURIYA, SIP-164 |
| B. 已废弃 (Deprecated) | 6 | 21% | Wordlib, 多人格系统, HUIHUI |
| C. 未知 (Unknown) | 9 | 32% | DAG, DF70, 双驱芯片, 心核芯片 |
| D. 占位符 (Placeholder) | 5 | 18% | seeds.txt, heart-core-v1.txt |
| **合计** | **28** | **100%** | |

### 死亡率统计

```
确定死亡 (0%存活): 14个 (50%)
  - 8个蓝皮书虚构
  - 6个已废弃

高度存疑 (<30%存活): 6个 (21%)
  - DF70, 14 Controller, EraLaw, MengPo, 13人格, Creator Protection

部分存在 (30-60%存活): 8个 (29%)
  - DAG, PROMPT_BUILDER, 双驱芯片, 心核芯片, seed-maker-core,
    KRMGCE, heart-core, reality_weight_matrix
```

### 关键发现

1. **蓝皮书虚构成分占29%** — 蓝皮书作为考古来源需要高度警惕
2. **R1→R2 范式转变**:
   - 多人格 → 角色职能
   - 单点调度 → 分布式自循环
   - 静态词库 → 动态记忆索引
   - 自重建 → 自演化
3. **Placeholder文件占核心文件的大部分** — R1 snapshot的实际内容严重缺失
4. **未知组件是最大考古价值区** — DAG、双驱芯片、心核芯片如果能恢复，可能大幅提升恢复率
