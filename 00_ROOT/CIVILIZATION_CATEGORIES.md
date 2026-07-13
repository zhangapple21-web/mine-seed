# Civilization Categories — 文明资产分类标准

> 级别：协议（Protocol）— 所有蒸馏工作必须遵守
> 维护者：Governor
> 版本：v1.0

---

## 核心原则

### 1. 六类资产

| 类别 | 定义 | 稳定性 | 生命周期 |
|------|------|--------|----------|
| **Kernel** | 系统运行的核心能力模块 | 高 | 长期 |
| **Blueprint** | 可复用的架构模板/模式 | 中 | 演化 |
| **Protocol** | 行为约定/接口规范 | 高 | 长期 |
| **Constraint** | 禁止/必须遵守的规则 | 高 | 长期 |
| **Experience** | 从失败/成功中沉淀的规律 | 中 | 迭代 |
| **Identity** | 文明的人格/价值观/记忆 | 极高 | 永续 |

### 2. 明确不属于文明的

以下**不进入 Repository**，停留在各自区域：

- **Mission** — 待完成事项 → 停留在 Mission Center
- **Code** — 具体实现 → 停留在 Runtime
- **Bug** — 工程问题 → 停留在 Ops Log
- **Log** — 运行记录 → 停留在 History

**准入规则**：

```
Mission
  ↓ 完成
  ↓ Distillation
  ↓ Admission Review (Governor)
  ↓
Repository (6 类资产之一)
```

---

## 分类详解

### Kernel — 核心能力

**定义**：系统无法脱离它运行。更换 Kernel 等于重建系统。

**判断标准**：
- 是否被 3 个以上上层模块依赖？
- 移除它是否导致系统瘫痪？

**示例**：
- `free_llm.py` — 统一 LLM 访问层
- `stock_query.py` — 统一数据访问层
- Gateway（如果还在用）

**命名规范**：功能名 + "Kernel" 或动词名词

---

### Blueprint — 蓝图模板

**定义**：可复用的架构模式，与具体实现解耦。

**判断标准**：
- 去掉具体实现细节后，模式是否仍然成立？
- 能否套用到其他领域？

**示例**：
- Signal Discovery Pipeline（多源数据 → 信号 → 排序 → 输出）
- Triple Fallback 模式
- CCO Selection Trace（四层筛选）

**命名规范**：描述模式，不加领域限定词
- ❌ "A股信号发现"
- ✅ "Signal Discovery Pipeline"

---

### Protocol — 协议约定

**定义**：模块间如何通信、如何协作的约定。

**判断标准**：
- 是否定义了输入/输出格式？
- 是否定义了执行顺序？
- 违反它是否导致系统故障？

**示例**：
- Deployment Protocol（无 Docker/Redis/MQ/DB 依赖）
- Recovery Protocol（L1-L4 恢复等级）
- Mission 传递格式（待定义）

**命名规范**：名词 + "Protocol"

---

### Constraint — 约束规则

**定义**：禁止做什么、必须做什么。

**判断标准**：
- 是否以 "禁止" / "必须" / "不得" 开头？
- 违反它是否有明确后果？

**示例**：
- "不得把 API Key 提交到 Git"
- "Runtime 不得依赖 Docker"
- "Mission 不得直接进入 Repository"

**命名规范**：RC-XXX（Rule Constraint）或描述性短语

---

### Experience — 经验沉淀

**定义**：从具体事件/失败/成功中提炼的规律。

**判断标准**：
- 是否经历了至少一次验证？
- 是否可以指导未来决策？
- 是否已经去除了具体情境的噪音？

**示例**：
- "sandbox 重置会杀死 cron" → 在 recovery 中加入 L1 自动修复
- "GLM 国内直连更快，NIM 需走代理"
- "adata 的 EastMoney 源在云端被墙，但腾讯源可用"

**命名规范**：现象 → 规律，不加编号

---

### Identity — 文明人格

**定义**：文明是谁、相信什么、追求什么。

**判断标准**：
- 删除它，文明是否还是同一个文明？
- 它是否回答了 "我们是谁"？

**示例**：
- `PRINCIPLES.md`
- `SOUL.md`
- 核心公理（如 Security Exclusion First）

**命名规范**：价值观/人格描述

---

## 准入审查流程

### Step 1: 蒸馏（Distillation）

产出者（云端 Architecture）将工作压缩为：
- 名称
- 类型（6 选一）
- 定义（一句话）
- 来源（哪些代码/文件）
- 约束（如果有）

### Step 2: 提交 Admission Review

以文件形式提交到 `02_MEMORY/recent_memory/admission/`：

```
admission_YYYYMMDD_XXX.md
```

内容格式：

```markdown
# Admission Review

## 提议资产

- 名称：
- 类型：
- 来源：
- 理由：

## Governor 决策

- [ ] PASS
- [ ] REJECT
- [ ] MERGE（与已有资产合并）
- [ ] SUPERSEDE（替代旧资产）
- [ ] ARCHIVE（归档，不进入活跃层）

## 决策理由

（Governor 填写）
```

### Step 3: Governor 决策

Governor 审查后决定：
- PASS → 进入 Repository 对应目录
- REJECT → 丢弃，记录原因
- MERGE → 与已有资产合并
- SUPERSEDE → 替代旧资产，旧资产进入 Archive
- ARCHIVE → 不活跃，但保留历史

### Step 4: 登记索引

通过后的资产登记到：

```
00_ROOT/CIVILIZATION_INDEX.json
```

---

## 日报格式

### Civilization Daily

每日凌晨自动生成：

```
# Civilization Daily — YYYY-MM-DD

## 今日变化

| 类别 | 新增 | 删除 | 合并 | 总分变化 |
|------|------|------|------|----------|
| Kernel | +1 | 0 | 0 | +5 |
| Blueprint | +2 | 0 | 0 | +4 |
| Protocol | +0 | 0 | 0 | 0 |
| Constraint | +1 | 0 | 0 | +2 |
| Experience | +4 | 0 | 0 | +4 |
| Identity | +0 | 0 | 0 | 0 |

## Repository 总览

| 类别 | 总数 | 较昨日 |
|------|------|--------|
| Kernel | 17 | +1 |
| Blueprint | 28 | +2 |
| Protocol | 35 | +0 |
| Constraint | 42 | +1 |
| Experience | 89 | +4 |
| Identity | 12 | +0 |

## 文明评分

昨日：212
今日：219
变化：+7

## 下一步建议

（Governor 或 Architecture 填写）
```

---

## 附录：Mission Center

Mission 不进入 Repository，停留在 Mission Center：

```
missions/
  active/       — 待执行
  in_progress/  — 执行中
  completed/    — 已完成（等待蒸馏）
  archived/     — 已蒸馏完成，不再追踪
```

Mission 完成后进入蒸馏流程，不直接入库。

---

*本文件由 Governor 定义，所有蒸馏工作必须遵守。*
