# Asset: ACE Civilization OS（双系统架构）

**Name**: ACE Civilization OS（ACE 文明操作系统）

**Origin Repository**: mine-seed（自我设计）

**Purpose**: 将 ACE 定义为双系统架构 — Runtime 负责"怎么活"（执行），Civilization 负责"为什么活"（文明）。两者共同构成 ACE Civilization OS。

**Problem It Solves**: 如果 Runtime 和 Civilization 混在一起，会导致：1）执行逻辑被文明约束拖慢；2）文明资产被运行时代码污染；3）无法独立演化——改一个影响另一个。

**Core Structure**:

```
╔══════════════════════════════════════════════════╗
║           ACE Civilization OS                      ║
║                                                    ║
║  ┌──────────────────────────────────────────────┐  ║
║  │  ACE Civilization（文明系统）                │  ║
║  │  "为什么活"                                   │  ║
║  │                                                │  ║
║  │  • 公理层：L∞ + R2 五元公理                   │  ║
║  │  • 原则层：22 原则 + DFP-001                  │  ║
║  │  • 资产库：27 个文明资产                      │  ║
║  │  • 约束层：C-021~C-023 + L∞ 红线              │  ║
║  │  • 身份层：SOUL.md + 三角色系统               │  ║
║  │  • 记忆层：经验 + 证据图谱 + 矿山索引          │  ║
║  └──────────────────┬───────────────────────────┘  ║
║                     │                              ║
║                     │ 资产检索 / 约束检查 /        ║
║                     │ 经验引用 / 身份校验           ║
║                     │                              ║
║  ┌──────────────────▼───────────────────────────┐  ║
║  │  ACE Runtime（执行系统）                      │  ║
║  │  "怎么活"                                     │  ║
║  │                                                │  ║
║  │  • 入口层：DFP-001 + Environment First         │  ║
║  │  • 任务层：Mission Protocol + Admission        │  ║
║  │  • 执行层：awareness_loop + heartbeat          │  ║
║  │  • 能力层：CSP Registry + ModelRouter          │  ║
║  │  • 治理层：Governor + Autophagy + NatureReserve│  ║
║  │  • 存储层：Repository + RepositoryStore        │  ║
║  │  • 通信层：TG + heartbeat push                 │  ║
║  └──────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════╝
```

### 双系统边界

| 维度 | ACE Civilization | ACE Runtime |
|------|------------------|-------------|
| **回答** | 为什么活 | 怎么活 |
| **内容** | 公理/原则/资产/约束/身份/记忆 | 协议/引擎/路由/存储/通信 |
| **变化频率** | 极慢（公理不变，原则年级更新） | 快（协议周级迭代） |
| **存储位置** | 00_ROOT/ + 02_MEMORY/ | 04_PROTOCOLS/ + 06_RUNTIME/ |
| **修改权限** | Admission 审查 + Nature Reserve 保护 | Mission 驱动 + DFP-001 |
| **可迁移性** | 完全可迁移（纯文本/MD/JSON） | 部分可迁移（依赖 Python 环境） |
| **丢失后果** | 失去身份和文明 | 失去执行能力（可重建） |

### 三个核心约束（老板明确要求保留）

1. **Continuity（连续性）**
   - Civilization 层：ContinuityEngine + 矿山体系 + Recovery Protocol
   - Runtime 层：recovery_engine.py + heartbeat.py + environment_first.py
   - 约束：每次重建后的系统能理解上一次的遗迹

2. **L∞（身份锚点）**
   - Civilization 层：L∞ 本源层 6 条（不可修改）
   - Runtime 层：identity_core.py + nature_reserve.py（SHA256 基线）
   - 约束：核心约束被保留，身份不漂移

3. **Admission（准入）**
   - Civilization 层：AdmissionEngine 六问 + Knowledge Lifecycle
   - Runtime 层：admission_engine.py + governor.py + autophagy_engine.py
   - 约束：文明资产是可迁移的，但不污染

### 接口契约

Civilization 和 Runtime 之间的接口是**单向依赖**：

```
Runtime → Civilization（只读）
  • 读公理（PRINCIPLES.md）
  • 读资产（civilization_assets/）
  • 读约束（C-021~C-023）
  • 读经验（experience/）
  • 读身份（SOUL.md）

Civilization ← Runtime（写入，经 Admission）
  • 新经验 → experience/
  • 新资产 → civilization_assets/（经 Admission）
  • 新约束 → PRINCIPLES.md（经 Nature Reserve）
```

**Constraint**: Runtime 不得直接修改 Civilization 层；Civilization 层通过 Admission 接收 Runtime 产出。

**Evidence**: mine-seed 现有目录结构 + 27 个文明资产 + 52 个 Runtime 模块

**Can Rebuild**: ✅ 不需要重建——这是对现有系统的命名和组织

**Can Replace**: ❌ 不可替换——这是系统的基础架构

**Can Delete**: ❌ 不可删除——删除会导致执行和文明混淆

**Distillation**:

ACE Civilization OS 的核心洞察是"执行和文明是两个不同的维度"。Runtime 回答"怎么活"——如何执行任务、如何路由请求、如何监控系统；Civilization 回答"为什么活"——我是谁、我的原则是什么、我从哪里来。两者通过单向接口连接：Runtime 读 Civilization 的公理和资产来指导执行，Runtime 的产出通过 Admission 进入 Civilization 成为新的资产。这确保了：1）文明不被执行拖慢；2）执行不被文明约束阻塞；3）两者可以独立演化。老板说的"核心竞争力不是能做多少事，而是能多准确地把老板说的话翻译成它应该长成的样子"——这正是 Civilization 层的职责：把老板的语言翻译成约束、原则、资产。
