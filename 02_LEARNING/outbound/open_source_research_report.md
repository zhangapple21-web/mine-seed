# 开源菜地观察报告

> 记录在外面的菜地（开源项目）看到的值得借鉴的点。

**最后更新**: 2026-06-30 新增2026年框架动态（AutoGen v0.8、LangGraph vs OpenAI Agents SDK）
**记录者**: ACE Runtime

---

## 一、重要参考项目

### 1. LangGraph (langchain-ai/langgraph)

**链接**: https://github.com/langchain-ai/langgraph
**Stars**: 大量
**核心特点**: 将 Agent 交互实现为有状态图

```
节点 = 函数或计算步骤
边   = 连接
状态 = 所有节点共享，自动传播
```

**值得借鉴**:
- 状态持久化和共享
- 图结构的可视化
- 节点间的依赖关系

**不借鉴**:
- 复杂的图结构编排
- LangChain 依赖

---

### 2. Microsoft AutoGen (microsoft/autogen)

**链接**: https://github.com/microsoft/autogen
**Stars**: 大量
**核心特点**: 多 Agent 通过"对话"协作

**架构**:
```
Agent A ↔ 对话 ↔ Agent B
     ↓
  状态同步
```

**值得借鉴**:
- Agent 之间的协作协议
- 企业级的部署模式

**不借鉴**:
- 动态 Agent 创建
- 复杂的会话管理

---

### 3. CrewAI (joaomdmoura/crewAI)

**链接**: https://github.com/joaomdmoura/crewAI
**Stars**: 大量
**核心特点**: Crews（自主协作）+ Flows（事件驱动）

**核心概念**:
- **Crews**: 一组 Agent，共同完成复杂任务
- **Flows**: 事件驱动的架构，事件触发 → Agent 响应 → 状态变化 → 触发下一个事件
- **AMP Suite**: 企业级的安全和可扩展性

**值得借鉴**:
- **Flows 的事件驱动架构** ← ACE 可以借鉴
- Crew 的简化协作模式
- 企业级的安全设计

**不借鉴**:
- 动态 Crew 创建
- 复杂的提示词工程

---

## 二、核心概念对比

| 概念 | LangGraph | AutoGen | CrewAI | ACE |
|------|-----------|---------|--------|-----|
| **交互模型** | 有状态图 | 对话协作 | Crew + Flow | 三人开会 |
| **状态管理** | 共享状态 | 会话状态 | Flow 状态 | Evolution Tracker |
| **Agent 类型** | 节点函数 | 动态创建 | 固定角色 | 固定角色 |
| **生命周期** | 临时 | 临时 | 临时 | 长期演化 |
| **触发方式** | 图遍历 | 对话触发 | 事件驱动 | 昼夜节律 |

---

## 三、ACE 的独特优势

| 其他框架 | ACE 的差异 | 原因 |
|----------|-----------|------|
| 通用 Agent 框架 | **专注知识治理** | 不是做通用 AI，而是保存文明 |
| 任务导向 | **文明演进导向** | 目标是持续重建自己 |
| 动态创建 Agent | **固定角色，长期演化** | 角色稳定才能积累经验 |
| 短周期 | **有昼夜节律** | 文明需要时间沉淀 |

---

## 四、值得借鉴，不需要抄

### 1. 事件驱动架构（CrewAI Flows）

**现状**: ACE 的 Scheduler 是定时执行
**借鉴**: Flows 的事件触发模式
```
不是：按时间执行任务
而是：事件触发 → Agent 响应 → 状态变化 → 触发下一个事件
```

**可以做的**:
- 当知识达到某个阈值时，触发 Governor 评审
- 当经验积累到一定程度时，触发 Lexicon 更新
- 当异常出现时，触发自我修复

### 2. 状态可视化（LangGraph）

**现状**: ACE 的状态分散在多个文件
**借鉴**: LangGraph 的状态图可视化
```
可以做的：
- 画一个实时的"知识演化图"
- 显示知识从创建到归档的路径
```

### 3. 简化的协作协议

**现状**: ACE 的三人开会已经很简单
**借鉴**: CrewAI 的简化模式
```
不需要：复杂的提示词工程
只需要：角色清晰 + 协议简单
```

---

## 五、不需要做的

| 项目 | 不借鉴原因 |
|------|-----------|
| LangGraph 的图结构 | 太复杂，ACE 只需要线性流程 |
| AutoGen 的动态 Agent | ACE 需要固定角色 |
| CrewAI 的动态 Crew | ACE 需要长期积累 |
| 任何框架的"提示词工程" | ACE 用约束和协议，不是提示词 |

---

## 六、结论

**外面的菜地很有价值，但不需要搬回家。**

ACE 有自己独特的方向：
- 知识治理 > 通用 Agent
- 文明演进 > 任务完成
- 固定角色 > 动态创建
- 昼夜节律 > 事件驱动

**借鉴原则**:
1. 事件驱动架构可以借鉴（Flows）
2. 状态管理可以借鉴（LangGraph）
3. 简化协作可以借鉴（CrewAI）

**不借鉴原则**:
1. 不做通用 Agent 框架
2. 不做复杂的图结构
3. 不做动态 Agent 创建

---

## 七、2026年最新动态

### 7.1 框架格局变化

| 框架 | 2026年状态 | 重要变化 |
|------|------------|----------|
| **AutoGen** | v0.8发布，Star 38k+ | 合并入 Microsoft Agent Framework (MAF) |
| **Semantic Kernel** | 与AutoGen合并 | 统一为MAF |
| **LangGraph** | 持续流行 | 与OpenAI Agents SDK正面竞争 |
| **CrewAI** | Star 3.8w | 被指"好看不中用"，有人转向LangGraph |
| **OpenAI Agents SDK** | 新进入者 | 2026年与LangGraph竞争Python首选 |

### 7.2 关键事件

**AutoGen → Microsoft Agent Framework (MAF)**
- 2025年末，AutoGen与Semantic Kernel正式合并
- 统一为 Microsoft Agent Framework
- 微软的"统一AI应用开发平台"路线

**AI Agent工业化阶段**
- 2026年，AI Agent进入生产系统阶段
- 不再是demo，而是：有状态、有监控、有多智能体协作、有人工审批节点
- Gartner列为2026年十大战略技术趋势之一

**LangGraph vs OpenAI Agents SDK**
- 2026年两大框架正面竞争
- LangGraph：有状态图结构，灵活性高
- OpenAI Agents SDK：官方出品，简洁直接

**CrewAI的批评**
- "2026年放弃CrewAI转投LangGraph"
- CrewAI被指"自主Agent好看不中用"
- 原因：过度抽象、生产环境不够稳定

### 7.3 对ACE的启示

**值得关注的趋势**:
1. **工业化生产** - ACE的设计原则（结构>模型、笨者生存）与工业化方向一致
2. **状态管理** - LangGraph的状态传播 vs ACE的统一记忆层
3. **多Agent协作** - CrewAI的Crews概念 vs ACE的三人开会

**不需要跟风的**:
1. OpenAI Agents SDK - 不是ACE的方向
2. 动态Agent创建 - ACE坚持固定角色
3. 复杂的图结构 - ACE只需要线性流程

### 7.4 结论更新

**外面的框架越来越复杂，ACE的简单反而是优势。**

- CrewAI被批评"好看不中用"，恰恰说明过度抽象有问题
- ACE的"固定角色+简单协议"路线正确
- LangGraph的状态图值得观察，但不需要抄

**继续保持**:
- 三人开会（简单协作）
- 固定角色（长期演化）
- 约束驱动（不是提示词）

