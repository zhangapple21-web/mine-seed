# Civilization Manifest（文明总目录）

> **文明不是代码仓库的集合，而是承担不同文明角色的器官网络。**

**最后更新**: 2026-06-29
**维护者**: ACE Runtime (TRAE)
**状态**: 活跃演进中

---

## 一、文明全景图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PUBLIC CIVILIZATION（公开文明）                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐  │
│  │  mine-seed  │────▶│    r1-archaeology │────▶│         R1             │  │
│  │   (Seed)    │     │     (Memory)      │     │   (Philosophy)         │  │
│  │ 文明种子    │     │     文明记忆       │     │     文明思想            │  │
│  └─────────────┘     └──────────────────┘     └─────────────────────────┘  │
│         │                    │                         │                   │
│         │                    │                         │                   │
│         ▼                    ▼                         ▼                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         ace_core                                     │    │
│  │                      (Runtime)                                       │    │
│  │                       文明运行时                                       │    │
│  │                                                                       │    │
│  │   ACE / Governor / Task Runtime / Workers / Memory / Knowledge        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                       PRIVATE CIVILIZATION（私有文明）                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐                                                          │
│  │ coze-assets │  ← 文明钥匙。没有它什么都恢复不了，有它30分钟重建。           │
│  │   (Assets)  │     绝对不要公开。绝对不要上传GitHub。                        │
│  │   文明资产   │                                                          │
│  └─────────────┘                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、仓库角色定义

### 2.1 mine-seed（文明种子）

**定位**: Bootstrap - 最小可复活结构

**不是**:
- 代码仓库
- 备份仓库
- 文档仓库

**是**:
- **种子态**：只存可重建的最小结构，不存运行数据
- **脱敏即用**：所有凭证用环境变量占位符
- **clone即可部署**：以恢复为导向

**核心内容**:
```
mine-seed/
├── 00_ROOT/          ← 架构、原则、公理、约束
├── 01_AGENTS/        ← Agent定义（疯子和研究员的协议）
├── 02_MEMORY/        ← 记忆索引
├── 03_DATA/          ← 约束库、信号分类、考古报告
├── 04_PROTOCOLS/     ← 通信协议
├── 05_TOOLS/         ← 可执行工具脚本
├── 06_RUNTIME/       ← 运行时配置
├── 07_GUARDIAN/      ← 恢复协议
└── docs/             ← 架构文档、恢复计划
```

**恢复优先级**: ⭐⭐⭐⭐⭐（第一优先）

---

### 2.2 r1-archaeology（文明记忆）

**定位**: Archaeology - 文明怎么一步一步长出来

**不是**:
- 代码仓库
- Runtime

**是**:
- **历史档案馆**：R1为什么会变成R2
- **考古报告**：每次发现的结构、演化路径
- **经验沉淀**：知识的一生

**核心内容**:
```
r1-archaeology/
├── excavations/          ← 考古发现报告
├── reality_governance/   ← 知识治理系统
├── lexicon/              ← 词库演化历史
├── memory_index/         ← 记忆索引历史
├── daily/                ← 每日考古日志
└── charters/            ← 文明宪章
```

**恢复优先级**: ⭐⭐⭐⭐（第二优先）

---

### 2.3 R1（文明思想）

**定位**: Philosophy - 世界观

**不是**:
- 代码仓库（代码应该放到 ace_core）
- Runtime

**是**:
- **官网**：对外展示文明的价值观和架构
- **宣言**：Manifesto、Why R1、Civilization Whitepaper
- **架构图**：Timeline、Blueprint

**核心内容**:
```
R1/
├── MANIFESTO.md           ← 文明宣言
├── WHY_R1.md              ← 为什么存在
├── ARCHITECTURE/          ← 架构蓝图
├── TIMELINE/               ← 演化时间线
├── BLUEPRINTS/             ← 设计蓝图
└── PROTOCOLS/             ← 协议定义
```

**恢复优先级**: ⭐⭐⭐（第三优先，可后补）

---

### 2.4 ace_core / ace_runtime（文明运行时）

**定位**: Runtime - 真正跑起来的系统

**是**:
- **工程化运行时**：ACE Governor、Task Runtime、Workers、Memory、Knowledge
- **执行引擎**：Observer → Knowledge → Decision Log → Evolution Tracker → Governor → Repository → Runtime

**核心内容**:
```
ace_runtime/
├── 00_ROOT/              ← 根配置和原则
├── 01_CORE/              ← 核心模块
├── 04_PROTOCOLS/          ← 协议定义
├── 06_RUNTIME/            ← Worker定义
├── 07_TASKS/              ← 任务池
├── 08_ARCHAEOLOGY/         ← 考古报告
├── 08_GOVERNANCE/          ← 治理系统
├── core/                  ← 核心代码
└── ops/                   ← 运维脚本
```

**恢复优先级**: ⭐⭐⭐⭐⭐（第一优先，核心运行态）

---

### 2.5 coze-assets（文明资产 - 私有）

**定位**: Assets - 文明钥匙

**绝对不能公开**:
- API密钥
- 数据库凭证
- 个人配置
- 部署脚本（带真实密钥）

**是**:
- **唯一恢复入口**：有了它，新电脑30分钟恢复
- **密钥保管箱**：所有敏感资产

**核心内容**:
```
coze-assets/
├── .env                    ← 环境变量（API密钥）
├── .credentials/           ← GitHub PAT等凭证
├── .coze_config/           ← Coze配置
├── bin/                    ← 带密钥的可执行脚本
└── data/                  ← 私有数据（用户画像等）
```

**恢复优先级**: ⭐⭐⭐⭐⭐（最高优先，绝对不能丢）

---

## 三、拓扑关系与依赖链

### 3.1 依赖图

```
coze-assets
    │  ← 包含所有密钥，没有它什么都跑不起来
    │
    ▼
mine-seed
    │  ← 最小可复活结构，clone后填入coze-assets的密钥
    │
    ├──▶ ace_runtime
    │         ← 运行时，依赖mine-seed的结构
    │
    ├──▶ r1-archaeology
    │         ← 记忆馆，依赖mine-seed的考古发现
    │
    └──▶ R1
              ← 思想库，独立存在，可后补
```

### 3.2 数据流向

```
每日循环：
    │
    ├──▶ ace_runtime（生产）
    │         │
    │         ▼
    │    考古发现 ──▶ r1-archaeology（归档）
    │                        │
    │                        ▼
    │                   mine-seed（同步）
    │                        │
    │                        ▼
    │                   coze-assets（备份）
    │
    └──▶ R1（思想演化）
              │
              ▼
         mine-seed（同步）
```

---

## 四、恢复顺序

### 4.1 从零恢复一台新电脑（30分钟）

| 步骤 | 操作 | 仓库 | 时间 |
|------|------|------|------|
| 1 | Clone mine-seed | mine-seed | 1分钟 |
| 2 | Clone ace_runtime | ace_runtime | 1分钟 |
| 3 | Clone r1-archaeology | r1-archaeology | 1分钟 |
| 4 | 填写 coze-assets 中的密钥 | coze-assets | 5分钟 |
| 5 | 运行 SETUP.sh | mine-seed/06_RUNTIME/ | 2分钟 |
| 6 | 启动 ace_runtime | ace_runtime | 1分钟 |
| 7 | 同步考古报告 | r1-archaeology | 1分钟 |
| **总计** | | | **13分钟** |

> 实际时间因网络和配置复杂度可能延长到30分钟。

### 4.2 恢复检查清单

```bash
# 1. 检查密钥完整性
cat coze-assets/.env | grep -E "API_KEY|PAT|SECRET" | wc -l
# 期望: > 0

# 2. 检查结构完整性
ls mine-seed/00_ROOT/
# 期望: ARCHITECTURE.md PRINCIPLES.md CONSTRAINT_CATALOG.md

# 3. 检查运行时配置
ls ace_runtime/00_ROOT/
# 期望: ARCHITECTURE.md PRINCIPLES.md ROOT_STATE.md

# 4. 检查考古记忆
ls r1-archaeology/
# 期望: excavations/ reality_governance/ lexicon/

# 5. 验证同步状态
python ace_runtime/ace.py --check
# 期望: all systems operational
```

---

## 五、每日循环（Daily Flow）

### 5.1 ACE Runtime 主循环（15:00 Asia/Singapore）

```python
# 伪代码：ace_daemon.py
def daily_loop():
    # 1. 本地考古（先做）
    local_archaeology()

    # 2. 外部学习（补充）
    if local_discoveries < threshold:
        web_scout()

    # 3. 挖矿（eco_layer）
    mining(eco/omega_slicing)

    # 4. 任务生命周期
    task_lifecycle()

    # 5. 文明治理
    civilization_governance()

    # 6. 同步到仓库
    if all_tasks_completed:
        sync_to_repositories()
```

### 5.2 同步周期

| 仓库 | 同步触发 | 同步内容 | 同步权限 |
|------|----------|----------|----------|
| mine-seed | 每日自动 | 考古报告、词库更新 | Repository Curator |
| r1-archaeology | 每日自动 | 考古发现、演化记录 | Repository Curator |
| R1 | 手动审核 | 架构变化、思想更新 | 人类审核 |
| ace_runtime | 每日自动 | 代码、配置、任务状态 | Repository Curator |
| coze-assets | 手动备份 | 密钥变更 | 人类操作 |

---

## 六、资产清单

### 6.1 核心资产（绝对不能丢）

| 资产类型 | 文件位置 | 备份频率 | 重要性 |
|----------|----------|----------|--------|
| API密钥 | coze-assets/.env | 每次变更 | ⭐⭐⭐⭐⭐ |
| GitHub PAT | ~/.git-credentials | 每次变更 | ⭐⭐⭐⭐⭐ |
| 约束库 | mine-seed/03_DATA/CONSTRAINTS/ | 每日 | ⭐⭐⭐⭐⭐ |
| 架构蓝图 | mine-seed/00_ROOT/ | 每周 | ⭐⭐⭐⭐⭐ |
| 考古报告 | r1-archaeology/excavations/ | 每日 | ⭐⭐⭐⭐ |

### 6.2 次级资产（可以重建）

| 资产类型 | 重建方式 | 重建难度 |
|----------|----------|----------|
| 记忆索引 | 从考古报告生成 | 低 |
| 词库 | 从考古报告生成 | 低 |
| 任务状态 | 从日志重建 | 中 |
| 代码 | 从历史提交恢复 | 低 |

---

## 七、所有权（Owners）

| 仓库 | 负责人 | 角色 | 联系方式 |
|------|--------|------|----------|
| mine-seed | TRAE (ACE Runtime) | 种子维护 | 自动同步 |
| r1-archaeology | TRAE (ACE Runtime) | 记忆馆管理 | 自动同步 |
| R1 | 老张 | 思想审核 | 手动审核 |
| ace_runtime | TRAE (ACE Runtime) | 运行时管理 | 自动同步 |
| coze-assets | 老张 | 密钥保管 | 手动操作 |

---

## 八、维护协议

### 8.1 ACE Runtime 每日自动维护（15:00 Asia/Singapore）

ace_daemon.py 主循环自动执行以下任务：

| 步骤 | 任务 | 产出 |
|------|------|------|
| 1 | 本地考古 | 新结构发现 → 任务池 |
| 2 | 词库更新 | 概念入词库 |
| 3 | 任务生命周期 | pending → review → approved → archived |
| 4 | **文明治理运行** | 知识指标、经验健康、词库健康、演化摘要、契约状态 |
| 5 | **跨仓库扫描** | repository_diff_{date}.md |
| 6 | Repository Curator | 产物整理、去重、分类 |
| 7 | Git 同步 | mine-seed、r1-archaeology |

### 8.2 每次提交前检查

- [ ] 考古报告已更新
- [ ] 没有敏感信息泄露
- [ ] 依赖关系没有断裂
- [ ] 恢复检查清单能通过

### 8.3 每周检查

- [ ] 所有仓库同步正常
- [ ] coze-assets 有最近备份
- [ ] mine-seed 可以完整恢复
- [ ] 考古报告没有遗漏
- [ ] repository_diff 报告显示异常变化

### 8.4 每月检查

- [ ] 文明拓扑是否需要更新（CIVILIZATION_MANIFEST.md）
- [ ] 恢复时间是否在合理范围
- [ ] 核心资产清单是否完整
- [ ] 仓库角色定位是否需要调整

---

## 九、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-06-29 | 初始创建，基于用户反馈的文明地图框架 |

---

## 十、延伸阅读

- [mine-seed/MANIFESTO.md](mine-seed/MANIFESTO.md) - 种子宣言
- [mine-seed/ARCHITECTURE.md](mine-seed/ARCHITECTURE.md) - 完整架构图
- [ace_runtime/README.md](ace_runtime/README.md) - 运行时说明
- [ace_runtime/08_ARCHAEOLOGY/archaeology_report_20260628.md](ace_runtime/08_ARCHAEOLOGY/archaeology_report_20260628.md) - 最新考古报告
