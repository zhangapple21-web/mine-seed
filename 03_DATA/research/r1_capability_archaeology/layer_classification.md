# AUM-MISSION-ARCH-021 — Layer Confusion Resolution

**任务**: Layer Confusion Resolution — 概念分层归位  
**日期**: 2026-07-14  
**考古人**: ACE Capability Archaeology Engine (Layer Pruning Mode)  
**状态**: ✅ Layer Classification Complete  

---

## 一、核心问题

> 为什么 R2 越研究越乱？

**因为概念在层与层之间漂移。**

例如 `Boundary`：
- 在公理体系里叫 "不变量"
- 在约束体系里叫 "规则"
- 在代码实现里叫 "gate/check"
- 在能力描述里叫 "verify"

同一件事，四个名字，四层的语言混着用。这就是 Layer Confusion。

---

## 二、四层定义

### 2.1 Goal（目标层）

**定义**: 系统存在的根本目的。如果 Goal 没了，系统就没有存在的理由。

**特征**:
- 只有一个或极少数几个
- 不涉及"怎么做"，只涉及"为什么存在"
- 任何技术更替都不会改变 Goal

### 2.2 Invariant（不变量层）

**定义**: 系统必须永远遵守的底层约束。如果 Invariant 被违反，系统就不是"它"了。

**特征**:
- 不依赖具体实现
- 不依赖具体能力
- 是 Goal 的保障条件

### 2.3 Capability（能力层）

**定义**: 系统能做什么。如果 Capability 没了，系统还在，只是"不能做这个了"。

**特征**:
- 可以增减
- 不依赖具体实现
- 是 Invariant 的实现手段

### 2.4 Implementation（实现层）

**定义**: 具体怎么做。可以随时替换，不影响 Capability。

**特征**:
- 技术会过时
- 可以任意更换
- 是 Capability 的具体载体

---

## 三、15个概念的分层归位

### 3.1 概念清单

| 序号 | 概念 | 原归属（混乱状态） | 错误原因 | 正确归属 |
|------|------|-------------------|---------|---------|
| 1 | **Continuity** | Goal / Invariant | 被混用 | **Goal** |
| 2 | **Boundary** | Invariant / Constraint | Constraint 是 Implementation | **Invariant** |
| 3 | **Identity** | Invariant / Memory | Memory 是 Implementation | **Invariant** |
| 4 | **Repository** | Capability / Memory | Memory 是 Implementation | **Implementation** |
| 5 | **Reason** | Capability / Transform | Transform 是 Capability | **Transform** (子类) |
| 6 | **Compression** | Capability / Refinery | Refinery 是 Implementation | **Transform** (子类) |
| 7 | **Evolution** | Capability / Property | Property 不是任何一层 | **System Property** (不属于四层) |
| 8 | **Policy** | Capability / Governance | Governance 是 Constraint | **Implementation** |
| 9 | **Constraint** | Invariant / Capability | 混淆了约束和能力 | **Implementation** |
| 10 | **Admission** | Capability / Governance | Governance 是组织制度 | **Implementation** |
| 11 | **Memory** | Capability / Remember | Remember 是 Capability | **Implementation** |
| 12 | **Capability** | Capability / Invariant | Capability 就是这一层的名字 | **层名，不是概念** |
| 13 | **Reality** | Invariant / Environment | 环境不是系统属性 | **外部输入，不属于系统四层** |
| 14 | **Invariant** | Invariant / 层名 | Invariant 就是这一层的名字 | **层名，不是概念** |
| 15 | **Goal** | Goal / 层名 | Goal 就是这一层的名字 | **层名，不是概念** |

### 3.2 为什么每个概念只能属于一层

**案例 1：Boundary 为什么不是 Constraint？**

- Boundary（不变量）= "系统必须有不可逾越的边界"
- Constraint（实现）= "具体的一条规则，如 '禁止修改核心协议文件'"

**区别**:
- Boundary 是原则：系统不能没有边界
- Constraint 是规则：边界在这里，具体怎么守

**案例 2：Identity 为什么不是 Memory？**

- Identity（不变量）= "我是谁"
- Memory（实现）= "存储历史记录的文件系统/SQLite"

**区别**:
- Identity 是属性：系统知道自己是谁
- Memory 是工具：用来保持 Identity 的工具

**案例 3：Evolution 为什么不属于四层？**

- Evolution 不是系统"能做什么"（不是 Capability）
- Evolution 不是系统"必须遵守什么"（不是 Invariant）
- Evolution 不是系统"为什么存在"（不是 Goal）
- Evolution 不是"具体怎么做"（不是 Implementation）

**Evolution 是系统整体行为产生的 emergent property（涌现属性）。**

```
Observe → Transform → Act → Observe
                ↓
         Experience 沉淀
                ↓
         Constraint 积累
                ↓
         System Update
                ↓
           Evolution
```

**案例 4：Governance 为什么不属于 Capability？**

- Governance（治理）不是"能做什么"
- Governance 是"什么能做，什么不能做"
- Governance 是组织的制度，不是个体的能力
- 没有 Governance，系统照样能 Observe/Transform/Act，只是风险更大

### 3.3 最终分层

#### Goal 层（1个）

| 概念 | 定义 | 证据 |
|------|------|------|
| **Continuity** | 保持自身可延续性 | `a12_r2_core_axioms_latest.md` 第34行: "系统存在的唯一目标：保持自身可延续性" |

#### Invariant 层（3个）

| 概念 | 定义 | 证据 |
|------|------|------|
| **Boundary** | 系统必须有不可逾越的边界 | `a12_r2_core_axioms_latest.md` 第61行: "边界公理" |
| **Identity** | 系统的身份由连续记忆定义 | `a12_r2_core_axioms_latest.md` 第78行: "连续公理" |
| **Observation** | 系统必须能观察自己和世界 | `a12_r2_core_axioms_latest.md` 第91行: "感知公理" |

**注意**：Invariant 只有 3 个，不是 5 个。Evolution 和 Risk Conversion 不是 Invariant。

#### Capability 层（3个）

| 概念 | 定义 | 子类 | 证据 |
|------|------|------|------|
| **Observe** | 感知现实世界 | Read, Watch, Capture, Search | `R1_CIVILIZATION_GRAPH.json` 第978行: "Experience Compression Layer" |
| **Transform** | 将信息从一种形态变为另一种 | Compress, Reason, Reflect, Distill, Plan, Verify | `WORLD_MODEL_ARCHITECTURE.md` 第46行: "实验结果 → 压缩 → 结构资产候选" |
| **Act** | 对现实世界执行操作 | Write, Send, Execute, Modify, Publish | `telegram_bot.py`: 消息发送 |

**注意**：原来的 7 个 Capability（Observe/Verify/Remember/Reason/Decide/Act）被压缩为 3 个。

- Verify → 归入 Transform（验证是信息变换）
- Remember → 归入 Transform（记忆是信息持久化）
- Reason → 归入 Transform（推理是信息处理）
- Decide → 归入 Transform（决策是信息评估）

#### Implementation 层（不限）

| 概念 | 所属 Capability | 具体技术 |
|------|---------------|---------|
| **Browser** | Observe / Act | Selenium, Playwright, Puppeteer |
| **API** | Observe / Act | HTTP, WebSocket, GraphQL |
| **Telegram** | Observe / Act | Bot API, Saved Messages |
| **Filesystem** | Observe / Act / Transform | Local files, SQLite |
| **Repository** | Transform | Git, Civilization Repository |
| **Memory** | Transform | Holo-Memory, SQLite, JSON |
| **Policy** | Transform | rules, contracts, allowlists |
| **Constraint** | Transform | boundary checks, gates |
| **Admission** | Transform | workflow, review process |
| **MCP** | Act / Observe | stdio, sse, http, ws |
| **SSH** | Act | remote command |
| **Desktop** | Act | AutoHotkey, PyAutoGUI |

---

## 四、被移除的概念

### 4.1 不属于四层的概念

| 概念 | 原因 | 新定位 |
|------|------|--------|
| **Evolution** | 是系统整体行为的涌现属性，不是系统的一层 | System Property（系统性质） |
| **Reality** | 是外部世界，不是系统的一部分 | External Input（外部输入） |
| **Capability** | 是层名，不是具体概念 | Layer Name |
| **Invariant** | 是层名，不是具体概念 | Layer Name |
| **Goal** | 是层名，不是具体概念 | Layer Name |

### 4.2 为什么 Evolution 不属于 Capability

**反例**:
- Browser 有 Evolution 吗？没有。
- Repository 有 Evolution 吗？没有。
- LLM 有 Evolution 吗？没有。

**正解**:
- Evolution 是 Observe → Transform → Act → Observe 整个闭环产生的
- Evolution 不是"系统能做什么"，而是"系统做了什么之后发生了什么"
- Evolution 是 emergent property（涌现属性），不是 designed property（设计属性）

### 4.3 为什么 Governance 不属于 Capability

**反例**:
- 没有 Governance，系统能 Observe 吗？能。
- 没有 Governance，系统能 Transform 吗？能。
- 没有 Governance，系统能 Act 吗？能。

**正解**:
- Governance 是"约束系统行为"的制度
- Governance 不是"系统能做什么"，而是"系统被允许做什么"
- Governance 是组织的制度层，不是个体的能力层

---

## 五、Capability 压缩验证

### 5.1 从 7 个压缩到 3 个

**原来的 Capability DAG（7个）**:
```
Observe → Verify → Remember → Reason → Decide → Act → Observe
```

**问题**:
- Verify = Observe 的质量检查 → 属于 Transform
- Remember = 信息持久化 → 属于 Transform
- Reason = 信息处理 → 属于 Transform
- Decide = 信息评估 → 属于 Transform

**压缩后的 Capability DAG（3个）**:
```
Observe → Transform → Act → Observe
```

**验证**:

| 原 Capability | 新归属 | 验证理由 |
|--------------|--------|---------|
| Observe | Observe | ✅ 核心能力，不可压缩 |
| Verify | Transform | 验证是信息变换（从不确定到确定） |
| Remember | Transform | 记忆是信息变换（从瞬态到持久态） |
| Reason | Transform | 推理是信息变换（从原始数据到结构化结论） |
| Decide | Transform | 决策是信息变换（从多个选项到单一选择） |
| Act | Act | ✅ 核心能力，不可压缩 |

### 5.2 从 3 个压缩到 2 个？

**尝试**:
```
Observe → Transform → Observe
```

**问题**:
- Act 是系统对现实世界的物理影响（写文件、发消息、执行命令）
- Transform 是系统内部的信息处理
- 两者有本质区别：Act 有副作用，Transform 没有副作用

**结论**: 不能压缩到 2 个。Act 必须独立。

### 5.3 从 3 个压缩到 1 个？

**尝试**:
```
Transform
```

**问题**:
- 没有 Observe，Transform 没有输入
- 没有 Act，Transform 没有输出
- 系统变成封闭回路，不与现实交互

**结论**: 不能压缩到 1 个。系统必须与现实交互。

### 5.4 最终结论

**Capability 的最小核心 = 3 个**:

```
Observe（感知现实）
Transform（变换信息）
Act（影响现实）
```

**原因**:
- Observe = 输入端：系统必须能感知现实
- Transform = 处理端：系统必须能处理信息
- Act = 输出端：系统必须能影响现实

缺少任何一个，系统就不完整。

---

## 六、四层关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Goal（目标层）                           │
│                                                                 │
│    Continuity —— 保持自身可延续性                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                      Invariant（不变量层）                       │
│                                                                 │
│    Boundary —— 系统必须有不可逾越的边界                          │
│    Identity —— 系统的身份由连续记忆定义                          │
│    Observation —— 系统必须能观察自己和世界                       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                      Capability（能力层）                        │
│                                                                 │
│    Observe —— 感知现实世界                                      │
│       ├─ Read / Watch / Capture / Search                        │
│                                                                 │
│    Transform —— 变换信息形态                                    │
│       ├─ Compress / Verify / Remember / Reason / Decide         │
│                                                                 │
│    Act —— 影响现实世界                                          │
│       ├─ Write / Send / Execute / Modify / Publish              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Implementation（实现层）                      │
│                                                                 │
│    Browser / API / Telegram / Filesystem / MCP / SSH / Desktop │
│    Repository / Memory / Policy / Constraint / Admission        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 七、为什么这解决了 Layer Confusion

### 7.1 原来的混乱

```
Continuity = Goal + Invariant（混了两层）
Boundary = Invariant + Constraint（混了两层）
Identity = Invariant + Memory（混了两层）
Repository = Capability + Memory（混了两层）
Reason = Capability + Transform（混了两层）
Compression = Capability + Refinery（混了两层）
Evolution = Capability + Property（不属于任何层）
Policy = Capability + Governance（混了两层）
Constraint = Invariant + Capability（混了两层）
Admission = Capability + Governance（混了两层）
Memory = Capability + Implementation（混了两层）
```

### 7.2 现在的清晰

```
Continuity = Goal（唯一）
Boundary = Invariant（唯一）
Identity = Invariant（唯一）
Repository = Implementation（唯一）
Reason = Transform（子类，唯一）
Compression = Transform（子类，唯一）
Evolution = System Property（不属于四层，明确）
Policy = Implementation（唯一）
Constraint = Implementation（唯一）
Admission = Implementation（唯一）
Memory = Implementation（唯一）
```

### 7.3 层与层之间的关系

```
Goal（为什么存在）
    ↓ 保障
Invariant（必须遵守什么）
    ↓ 实现
Capability（能做什么）
    ↓ 载体
Implementation（具体怎么做）
```

**关键规则**:
- 上层不依赖下层：Goal 不依赖 Invariant，Invariant 不依赖 Capability
- 下层服务于上层：Implementation 服务于 Capability，Capability 服务于 Invariant
- 同层不依赖同层：Browser 不依赖 API，API 不依赖 Telegram

---

## 八、与 R1 公理的对照

| R1 公理 | 正确分层 | 之前错误分层 |
|---------|---------|------------|
| 统一公理（保持可延续性） | Goal | ✅ 正确 |
| 边界公理 | Invariant | ❌ 之前混为 Invariant + Constraint |
| 连续公理 | Invariant | ❌ 之前混为 Invariant + Memory |
| 感知公理 | Invariant | ❌ 之前混为 Invariant + Capability |
| 笨者生存定律 | System Property | ❌ 之前未识别 |
| 流动优先定律 | System Property | ❌ 之前未识别 |
| 复杂性负担定律 | System Property | ❌ 之前未识别 |
| 形态可变定律 | System Property | ❌ 之前未识别 |
| 风险内化定律 | System Property | ❌ 之前未识别 |

**发现**: R1 的 5 条生存定律全部是 System Property，不是 Invariant。

**原因**: 生存定律是"观察到的规律"，不是"必须遵守的约束"。系统可以不遵守笨者生存定律（可以建造复杂的结构），只是后果可能是死亡。

---

## 九、最终答案

### 9.1 15个概念的分层结果

| 概念 | 归属 | 理由 |
|------|------|------|
| Continuity | **Goal** | 系统存在的根本目的 |
| Boundary | **Invariant** | 系统必须永远遵守的约束 |
| Identity | **Invariant** | 系统必须永远遵守的约束 |
| Observation | **Invariant** | 系统必须永远遵守的约束 |
| Observe | **Capability** | 系统能感知现实 |
| Transform | **Capability** | 系统能变换信息 |
| Act | **Capability** | 系统能影响现实 |
| Repository | **Implementation** | 具体存储方式 |
| Memory | **Implementation** | 具体持久化方式 |
| Policy | **Implementation** | 具体规则文件 |
| Constraint | **Implementation** | 具体检查逻辑 |
| Admission | **Implementation** | 具体工作流程 |
| Browser | **Implementation** | 具体技术工具 |
| API | **Implementation** | 具体技术工具 |
| Telegram | **Implementation** | 具体技术工具 |
| MCP | **Implementation** | 具体技术工具 |
| Evolution | **System Property** | 涌现属性，不属于四层 |
| Reality | **External Input** | 外部世界，不属于系统 |

### 9.2 层的数量

| 层 | 数量 | 例子 |
|---|------|------|
| Goal | 1 | Continuity |
| Invariant | 3 | Boundary, Identity, Observation |
| Capability | 3 | Observe, Transform, Act |
| Implementation | 不限 | Browser, API, Telegram, Filesystem, MCP |
| System Property | 不限 | Evolution, 笨者生存定律, 流动优先定律 |
| External Input | 1 | Reality |

### 9.3 文明的最小核

如果必须砍掉所有非核心，文明的最小核是什么？

```
Goal: Continuity
Invariant: Boundary, Identity, Observation
Capability: Observe, Transform, Act
Implementation: Filesystem（最笨的实现）
```

**理由**:
- Filesystem 是最"笨"的实现：零配置、零依赖、零维护成本
- 笨者生存定律验证：越笨的结构活得越久
- 即使所有高级技术（Browser/API/MCP）消失，Filesystem 还在

---

## 十、后续验证

### 10.1 验证规则

**规则 1**: 如果一个概念能出现在两层，说明分层失败。
**规则 2**: 如果 Implementation 被删除后 Capability 消失，说明 Capability 抽象失败。
**规则 3**: 如果 Capability 被删除后 Invariant 消失，说明 Invariant 抽象失败。

### 10.2 验证结果

| 验证 | 结果 |
|------|------|
| 规则 1（无跨层概念） | ✅ 通过 |
| 规则 2（删除 Browser → Observe 仍在） | ✅ 通过 |
| 规则 2（删除 API → Observe 仍在） | ✅ 通过 |
| 规则 2（删除 MCP → Act 仍在） | ✅ 通过 |
| 规则 3（删除 Observe → Boundary 仍在） | ✅ 通过 |
| 规则 3（删除 Act → Identity 仍在） | ✅ 通过 |

---

**报告完成时间**: 2026-07-14  
**状态**: ✅ Layer Classification Complete  
**结论**: Layer Confusion 已解决，概念已分层归位。

---

*下一步：等待决策是否将四层体系写入 Civilization Repository。*
