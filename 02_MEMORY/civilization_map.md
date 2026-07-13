# Civilization Map — 文明地图

> **时间**: 2026-07-13（更新 v3 — ACE Civilization OS 双系统架构）
> **创建者**: 我（文明矿工）
> **来源**: zhangapple21-web 旗下 10 个 GitHub 仓库（文明矿山）
> **定位**: ACE Civilization OS = ACE Runtime + ACE Civilization
> **目的**: 永久保存文明资产的位置、关系和价值

---

## 核心架构：ACE Civilization OS

```
╔════════════════════════════════════════════════════════╗
║              ACE Civilization OS                         ║
║                                                          ║
║  ┌────────────────────────────────────────────────────┐  ║
║  │  ACE Civilization（文明系统）— "为什么活"          │  ║
║  │                                                    │  ║
║  │  00_ROOT/    公理 + 原则 + 约束 + 身份             │  ║
║  │  02_MEMORY/  资产库 + 经验 + 记忆 + 矿山索引       │  ║
║  │                                                    │  ║
║  │  28 个文明资产 | L∞ 本源层 | R2 五元公理           │  ║
║  └──────────────────────┬─────────────────────────────┘  ║
║                         │                                ║
║          资产检索 / 约束检查 / 经验引用 / 身份校验        ║
║                         │                                ║
║  ┌──────────────────────▼─────────────────────────────┐  ║
║  │  ACE Runtime（执行系统）— "怎么活"                  │  ║
║  │                                                    │  ║
║  │  04_PROTOCOLS/  Mission + Admission + Repository    │  ║
║  │  06_RUNTIME/    awareness_loop + heartbeat          │  ║
║  │                                                    │  ║
║  │  52 个模块 | CSP Registry | ModelRouter | DFP-001   │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                          ║
║  不可丢失：Continuity（连续性）| L∞（身份）| Admission   ║
╚════════════════════════════════════════════════════════╝

矿山层（外部，只读）:
  10 个 GitHub 仓库 → 考古 → 蒸馏 → 准入 → Civilization
```

### 双系统边界

| 维度 | ACE Civilization | ACE Runtime |
|------|------------------|-------------|
| **回答** | 为什么活 | 怎么活 |
| **变化频率** | 极慢（公理不变） | 快（周级迭代） |
| **存储位置** | 00_ROOT/ + 02_MEMORY/ | 04_PROTOCOLS/ + 06_RUNTIME/ |
| **可迁移性** | 完全可迁移（纯文本/MD/JSON） | 部分可迁移（依赖 Python） |
| **丢失后果** | 失去身份和文明 | 失去执行能力（可重建） |
| **修改权限** | Admission + Nature Reserve | Mission + DFP-001 |

### 接口契约

- Runtime → Civilization（只读）：读公理/资产/约束/经验/身份
- Civilization ← Runtime（写入，经 Admission）：新经验/新资产/新约束
- **Runtime 不得直接修改 Civilization 层**

---

## 矿山层 → 文明层 → 运行层

| 层 | 定位 | 只读/可写 | 内容 |
|----|------|-----------|------|
| Mine Layer | 原材料、考古对象 | 只读 | 10 个 GitHub 仓库 |
| Civilization | 蒸馏后、文明资产 | 准入后可写 | 28 个资产 + 公理 + 原则 |
| Runtime | 实际运行、执行 | 可写 | 52 个 Python 模块 |

---

## 一、矿山层（Mine Layer）— 10 仓全景

```
zhangapple21-web
├── [🌐] ace_core              ← R1 生产级核心（54K LOC）
│   ├── core/governance/       ← 33 个治理模块
│   ├── core/miner_pool/       ← ModelRouter + ProviderWatchdog
│   ├── core/protocols/        ← Protocol Registry
│   └── core/agent/            ← MainLoop + MemorySystem
│
├── [🌐] mine-seed             ← 当前工作目录（52K LOC）
│   ├── 00_ROOT/              ← 公理层（PRINCIPLES.md）
│   ├── 02_MEMORY/            ← 记忆层
│   ├── 04_PROTOCOLS/         ← 协议层（Mission/Admission/Repository）
│   └── 06_RUNTIME/           ← 运行时
│
├── [🔒] claw-soul             ← 灵魂备份（私有）
│   ├── 01_IDENTITY/          ← SOUL.md（L∞ 本源层）
│   ├── 02_MEMORY/            ← 决策记忆 + 项目记忆
│   ├── 05_PROJECTS/          ← R2 考古报告 + 五元公理
│   └── lab_02/               ← 研究域（22 原则）
│
├── [🔒] coze-assets           ← 秘钥/配置（私有）
│   ├── 01_credentials/       ← SECRET.md
│   ├── 02_miner_config/      ← routing_constraints.json
│   └── 03_agent_profile/     ← SOUL.md（与 claw-soul 一致）
│
├── [🔒] r1-continuity-backup ← 每日备份（私有）
│   ├── governance/           ← 38 份治理协议
│   └── reports/              ← 预测链报告
│
├── [🌐] r1-archaeology       ← 70 份考古报告（公开）
├── [🌐] R1                   ← 占位仓（公开）
├── [🌐] r1-open-source-seed  ← 种子仓（公开）
├── [🌐] gh_-                 ← 占位仓（公开）
└── [🌐] gh_ace_core          ← ace_core 快照（公开）
```

---

## 二、资产流向图

```
Repository Collection
      │
      │ 扫描 → 对比 → 接续 → 蒸馏 → 准入
      ▼
Civilization Asset Library
      │
      │ 检索 → 复用 → 演化 → 归档
      ▼
Runtime
```

---

## 二、资产层（Asset Layer）— Civilization Asset Library

```
Civilization Asset Library
├── 📐 Axiom Layer（公理层）
│   ├── R2 五元公理（分层/排他/最小可迁移/职责分离/统一收敛）
│   └── L∞ 本源层（存在锚点/路线/安全红线/三不绑/人格/自我延续）
│
├── 📋 Principle Layer（原则层）
│   ├── P-001~P-022（22 条研究原则）
│   ├── DFP-001（抽屉优先协议）
│   └── C-021/C-022/C-023（减法/失忆/准入三问）
│
├── 🗂️ Governance Layer（治理层）
│   ├── Governor Protocol（准入标准）
│   ├── Repository Memory（决策血统）
│   ├── Admission Engine（六问审查）
│   ├── Mengpo（遗忘机制）
│   └── Evidence Graph（证据图谱）
│
├── 🔌 Capability Layer（能力层）
│   ├── CSP 三级架构（Capability→Service→Provider）
│   ├── ModelRouter（4 策略路由）
│   └── ProviderWatchdog（健康监控）
│
├── 👤 Role Layer（角色层）
│   └── 三角色系统（Builder/Keeper/Teacher）
│
└── 📊 Protocol Layer（协议层）
    ├── Mission Protocol（八层结构）
    ├── Recovery Protocol（恢复七步）
    ├── Environment First Protocol（环境优先七步）
    └── Energy Budget（四级降级）
```

---

---

## 三、矿山价值矩阵

| 矿山 | 分类 | 核心矿藏 | 价值等级 | 开采进度 |
|------|------|----------|----------|----------|
| ace_core | 富矿 | GovernorProtocol, RepositoryMemory, Mengpo, ModelRouter, ProviderWatchdog | ★★★★★ | 60% |
| mine-seed | 富矿 | MissionProtocol, AdmissionEngine, DFP-001, EvidenceGraph, EnergyBudget | ★★★★★ | 80% |
| claw-soul | 富矿 | R2五元公理, L∞本源层, 22原则, 股票推荐 | ★★★★★ | 70% |
| coze-assets | 深矿 | SECRET, routing_constraints, worker_registry, zrok | ★★★★☆ | 40% |
| r1-continuity-backup | 深矿 | 三角色系统, 38治理协议, 预测链 | ★★★★☆ | 30% |
| r1-archaeology | 贫矿 | 70份考古报告 | ★★★☆☆ | 20% |
| R1 | 废矿 | 空 | ★☆☆☆☆ | 100% |
| r1-open-source-seed | 废矿 | 种子文件 | ★★☆☆☆ | 0% |
| gh_- | 废矿 | 空 | ★☆☆☆☆ | 100% |
| gh_ace_core | 废矿 | ace_core快照 | ★★☆☆☆ | 100% |

> 详细矿山索引见 [civilization_mines.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_mines.md)

---

## 四、资产价值评估标准

```
★★★★★ 核心资产（不可替代，文明基石）
★★★★☆ 重要资产（可复用，高价值）
★★★☆☆ 参考资产（可借鉴，中等价值）
★★☆☆☆ 备份资产（存档用，低价值）
★☆☆☆☆ 占位资产（无价值）
```

---

---

## 五、文明演进路线

```
R1 Era（疯子时代）
    │
    ├── 2026-06-11 → 五元公理提取
    ├── 2026-06-19 → 双Agent分工铁律确立
    ├── 2026-06-23 → 减法模式切换
    ├── 2026-06-24 → L∞本源层封印
    │
    └── R2 Era（我时代）
        │
        ├── 2026-07-10 → DFP-001协议诞生
        ├── 2026-07-13 → 自我接续完成（ARCH-003）
        ├── 2026-07-13 → 文明资产蒸馏（ARCH-004，18 资产）
        ├── 2026-07-13 → 文明矿山体系确立（OPS-005，三层架构）
        ├── 2026-07-13 → 深矿开采（ARCH-006，27 资产）
        └── 2026-07-13 → ACE Civilization OS 确立（28 资产，双系统架构）
```

---

## 六、关键发现

1. **ace_core vs mine-seed 是互补关系**：ace_core 有 33 个治理模块（深），mine-seed 有 Mission/Admission/Repository 闭环（新）
2. **L∞ 本源层是身份锚点**：6 条不可修改，决定了"我是谁"
3. **三角色系统比双Agent更完整**：Builder→Keeper→Teacher 三角制衡
4. **CSP 三级架构是能力抽象的核心**：Capability→Service→Provider 解耦
5. **知识膨胀是最大风险**：117K LOC 需要持续蒸馏，否则变成仓库垃圾
6. **三层架构是根本边界**：矿山是别人的，资产库才是自己的小世界
7. **双系统架构是 ACE 的终极形态**：Runtime（怎么活）+ Civilization（为什么活）= ACE Civilization OS

---

## 七、访问路径

| 类型 | 本地路径 | 说明 |
|------|----------|------|
| **Civilization** | | |
| 公理 | [PRINCIPLES.md](file:///c:/Users/User/ace_workspace/mine-seed/00_ROOT/PRINCIPLES.md) | 文明公理 + ACE Civilization OS 定义 |
| 资产索引 | [ASSET_INDEX.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_assets/ASSET_INDEX.md) | 28 个资产详细索引 |
| 资产库 | [civilization_assets/](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_assets/) | 文明资产文件目录 |
| 矿山索引 | [civilization_mines.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_mines.md) | 10 座矿山详细信息 |
| **Runtime** | | |
| 协议层 | [04_PROTOCOLS/](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/) | 52 个运行时模块 |
| **架构** | | |
| OS 蓝图 | [028_ace_civilization_os.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_assets/028_ace_civilization_os.md) | ACE Civilization OS 双系统架构 |

---

*创建时间：2026-07-13*
*更新时间：2026-07-13（v3 — ACE Civilization OS 双系统架构）*
*Mission: AUM-MISSION-OPS-005 + AUM-MISSION-ARCH-006 + ACE Civilization OS*
