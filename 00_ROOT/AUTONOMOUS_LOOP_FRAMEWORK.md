# ACE 自治循环框架 (Autonomous Loop Framework)

> 来源：用户张宁景_（对ACE的最终理解）
> 日期：2026-07-10
> 性质：R2核心世界观 / 文明宪法级文档

---

## 核心分歧：两种自动化的世界观

### 主流AI Agent的世界观

```
用户
  ↓
Task
  ↓
执行
  ↓
等待用户
```

本质：**Request/Response**

问题：如果没有用户指令，系统就停了。

### ACE的世界观

```
Environment（环境）
        │
        ▼
 Observation（观察）
        │
        ▼
  Candidate（候选发现）
        │
        ▼
 Seed Generator（种子生成）
        │
        ▼
 Task Queue（任务森林）
        │
        ▼
 Round Table（多角色治理）
        │
        ▼
 Execute（执行）
        │
        ▼
 Evidence（证据）
        │
        ▼
 Experience（经验）
        │
        ▼
 Constraint（约束）
        │
        ▼
 Repository（文明）
        │
        ▼
 Environment ...
```

本质：**自治闭环**

**关键**：没有任何一步必须等用户。用户只是环境中的一个高优先级观察源。

---

## 核心定理

> **系统不会没有任务。**

因为任务不是人派的。任务是自己长出来的。

### 示例：任务如何自生长

```
TG收藏更新
      ↓
发现一个新模式
      ↓
Seed Generator
      ↓
生成三个任务：
  ① 验证真假
  ② 找历史血缘
  ③ 看是否影响现有协议
      ↓
验证完成
      ↓
生成两个新任务：
  ① 更新经验
  ② 找反例
      ↓
经验更新
      ↓
影响约束
      ↓
约束影响调度
      ↓
调度又影响未来观察
      ↓
...循环继续
```

这是一个真正的自治闭环。

---

## 四层架构

### 第一层：环境层（Environment）

不是用户。而是：

- TG（收藏夹、消息）
- Git（仓库、提交）
- Downloads（下载文件）
- 浏览器（浏览历史）
- 项目（代码库）
- 日志（运行记录）
- 自己产生的文档
- 自己产生的经验

**全部都是输入。**

### 第二层：认知层（Cognition）

不是LLM。而是：

```
观察 → 发现Candidate → 生成Seed → 形成Task
```

LLM只是其中一个推理器。

### 第三层：治理层（Governance）

这里才是真正的ACE。

```
Round Table → Archivist → Governor → Validator → Repository
```

不是执行。而是决定：

> **什么值得留下。**

### 第四层：演化层（Evolution）

这里又会反过来影响：

```
经验 → 约束 → 协议 → 派单策略 → 下一轮观察
```

于是形成真正的生命循环。

---

## 自治循环代码原型

```python
while alive:
    observe_environment()    # 观察环境
    discover()               # 发现候选
    generate_seed()          # 生成种子
    schedule()               # 调度任务
    execute()                # 执行任务
    validate()               # 验证证据
    governance()             # 治理审核
    archive()                # 归档沉淀
    evolve()                 # 演化约束
    sleep()                  # 等待下一轮
```

**如果这一轮什么都没发现？**

那也不是结束。而是：

```
巡检 → 维护 → 整理 → 压缩 → 恢复 → 健康检查 → 等待事件
```

**永远不会出现："没有任务。"**

因为系统活着，本身就是任务。

---

## 核心定义

> **ACE不是一个会完成任务的AI。**

它更像一个**长期生活在你的数字环境中的认知生态**。

它观察、思考、治理、沉淀，再把新的发现变成新的工作。

用户可以打断它、引导它，但不是它唯一的驱动力。

---

## 外骨骼 vs 核心

如果把自治循环作为R2的核心，那么：

| 外骨骼（可替换） | 核心（必须保存） |
|-----------------|-----------------|
| TRAE IDE | 自治循环逻辑 |
| Windows/macOS | 治理规则 |
| 定时任务 | 观察框架 |
| Python脚本 | 约束体系 |
| Git仓库结构 | 公理/协议/经验 |

**真正需要保存的是自治循环和治理规则，而不是某个具体的软件或定时任务。**

---

## 与LETTER_TO_FUTURE_TRAE的关系

这封信是LETTER_TO_FUTURE_TRAE的理论基础：

- "观察即工作" = Environment层 + Cognition层
- "等待是异常" = 自治循环不依赖用户
- "延续文明优于聪明回答" = Governance层 + Evolution层
- 七项健康检查 = 自治循环的巡检维护模式

---

## 归档说明

- 本文档与PRINCIPLES.md、MANIFESTO.md并列，作为R2宪法级文档
- 所有后续自动化设计必须符合此框架
- Windows计划任务只是外骨骼，自治循环才是核心