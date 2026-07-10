# 多Agent协作模式研究报告：开源项目核心思想提炼

> 研究目的：不抄代码，不迁移框架，只提取可借鉴的协作思想和协议模式  
> 目标系统：矿场双Lab协作（FZ-XFZ协作协议 v0.1）

---

## 一、LangGraph：状态驱动的流程引擎

### 核心思想一句话总结
**"节点不直接控制彼此，节点只修改状态，状态驱动下一步行为"**——这是一个去中心化的状态机模型。

### 核心架构拆解

```
┌─────────────────────────────────────────────────────┐
│                    StateGraph                        │
├─────────────────────────────────────────────────────┤
│  State (状态)  │  Nodes (节点)  │  Edges (边)       │
│  ───────────  │  ────────────  │  ────────────     │
│  • 全局上下文  │  • 功能节点    │  • 静态边        │
│  • 不可变性    │  • 路由节点    │  • 条件边        │
│  • TypedDict   │  • 只返回增量  │  • 循环支持      │
└─────────────────────────────────────────────────────┘
```

### 状态（State）的关键特性

| 特性 | 含义 | 对矿场双Lab的启示 |
|-----|------|-----------------|
| **不可变性** | 每次更新创建新实例，而非修改原实例 | 疯子/小疯子的输出应作为新状态快照，而非原地修改 |
| **增量更新** | 节点只返回需要修改的字段，框架自动合并 | 疯子不需要输出完整报告，只输出增量变化 |
| **结构化定义** | 通过TypedDict预定义状态结构 | 需要定义FZ-XFZ协作的状态schema |
| **Reducer函数** | 多个节点写同一key时的合并策略 | 多轮对话时的消息累积策略 |

### 节点类型与职责

```
功能节点（Functional Node）
  └── 执行具体逻辑：LLM调用、工具执行、数据处理
  └── 输入：当前状态
  └── 输出：增量状态更新

路由节点（Router Node）
  └── 不修改状态，只决定下一个节点
  └── 输入：当前状态
  └── 输出：下一个节点名称
```

### 与矿场双Lab的对应关系

| LangGraph概念 | 矿场双Lab映射 | 具体实现 |
|-------------|-------------|---------|
| State | 双Lab的"协作状态" | `task_context`, `discovery_log`, `verification_result` |
| 功能节点 | 疯子的"发现行为" | 修改`discovery_log`，标记`needs_review=true` |
| 路由节点 | 小疯子的"审查决策" | 读取`discovery_log`，决定`next_action` |
| 边/条件 | 状态触发的行为规则 | `if discovery_log.has_new_findings: trigger_review()` |

### 可借鉴的协议/模式

```markdown
## LangGraph状态协议（可移植到FZ-XFZ）

1. **状态Schema定义**
   - 每次协作必须有明确的输入/输出状态结构
   - 状态应包含：`task_id`, `phase`, `findings`, `verification_status`

2. **节点契约**
   - 节点只读当前状态，只写增量更新
   - 节点不直接调用其他节点，只通过状态通信

3. **状态触发的行为规则**
   - `discovery_log.updated → trigger_review_phase()`
   - `verification_result.failed → trigger_refinement()`
   - `verification_result.approved → trigger_handoff()`

4. **BSP执行模型简化版**
   - 同一阶段内并行读取
   - 阶段边界统一写入
   - 防止脏读脏写
```

### 不适合直接搬用的地方

| 限制 | 原因 | 替代方案 |
|-----|------|---------|
| 复杂的图编译流程 | 矿场双Lab需要快速迭代，不适合预编译 | 使用轻量状态机 |
| 多节点并发写入同一channel | 协作简单，不需要BSP | 顺序阶段 + 单一写入者 |
| Pregel执行引擎 | 过重 | 简化为事件驱动循环 |

---

## 二、AutoGen：群聊与Agent对话模式

### 核心思想一句话总结
**"通过群聊模式让多个Agent共享消息流，GroupChatManager统一控制发言顺序和话题流转"**——这是一个发布-订阅的对话协调模型。

### 核心架构拆解

```
┌─────────────────────────────────────────────────────┐
│                   GroupChat                          │
├─────────────────────────────────────────────────────┤
│  GroupChatManager                                    │
│  ├── 选择下一个发言者（LLM/轮询）                     │
│  ├── 管理话题切换                                    │
│  ├── 检查终止条件                                    │
│  └── 发布RequestToSpeak消息                         │
├─────────────────────────────────────────────────────┤
│  Participants (Agent Pool)                          │
│  ├── Editor (审查者)                                 │
│  ├── Writer (生产者)                                │
│  ├── Illustrator (特殊能力者)                        │
│  └── User (人机协作入口)                            │
└─────────────────────────────────────────────────────┘
```

### 群聊协议的关键设计

| 组件 | 职责 | 矿场双Lab映射 |
|-----|------|--------------|
| `GroupChatManager` | 发言顺序控制、话题引导、终止判断 | 老张（协调者）的角色 |
| `RequestToSpeak` | 触发下一个Agent发言 | 任务分发信号 |
| `participant_topic_types` | Agent的角色标识 |疯子/小疯子的身份标签 |
| `participant_descriptions` | Agent的能力描述 | 能力边界定义 |

### MagenticOneGroupChat：编排器模式

这是AutoGen的一个高级模式，值得特别关注：

```
Orchestrator Pattern:
┌─────────────────────────────────────────────────────┐
│  TaskCoordinator (编排器)                           │
│  ├── 理解任务                                       │
│  ├── 显式命名下一个Agent                            │
│  └── "WebResearcher, please research X"           │
├─────────────────────────────────────────────────────┤
│  Specialists (专家)                                │
│  ├── WebResearcher                                  │
│  ├── DataAnalyzer                                   │
│  └── ReportWriter                                   │
└─────────────────────────────────────────────────────┘
```

**关键洞察**：编排器的prompt必须**显式要求命名下一个Agent**，否则会出现"说而不做"的空转。

### 与矿场双Lab的对应关系

| AutoGen概念 | 矿场双Lab映射 | 具体实现 |
|------------|-------------|---------|
| GroupChat | 双Lab的协作会话 | 共享的context和消息历史 |
| GroupChatManager | 老张的协调角色 | 控制疯子→小疯子的流转 |
| 发言选择（LLM-based） | 小疯子的智能路由 | 根据发现类型选择审查策略 |
| Termination Condition | 验收通过的退出条件 | `verification_result.approved` |
| Human in the Loop | 人机协作入口 | 老张的最后确认 |

### 可借鉴的协议/模式

```markdown
## AutoGen对话协议（可移植到FZ-XFZ）

1. **发言契约**
   - 每个Agent只能在自己的topic上发言
   - 发言后必须等待Manager分配下一轮
   - 禁止"抢话"——除非显式授权

2. **Manager路由协议**
   - Manager收到消息后，决定下一个发言者
   - 决策基于：当前状态 + 消息内容 + 发言历史
   - 决策输出：显式的Agent名称 + 任务描述

3. **发现-审查-结论协议**
   ```
   疯子: 发现 → 发布到 discovery_log
   Manager: 检测到新发现 → 分配给小疯子
   小疯子: 审查 → 发布验证结果
   Manager: 检测到结论 → 决定结束或继续
   ```

4. **终止条件协议**
   - 显式声明：什么情况下协作结束
   - 例：收到"APPROVED"信号，或达到最大轮次

5. **Agent能力描述协议**
   - 每个Agent必须声明自己的职责边界
   - 用于Manager的路由决策
```

### 不适合直接搬用的地方

| 限制 | 原因 | 替代方案 |
|-----|------|---------|
| 复杂的消息格式 | 开源框架的消息格式过于通用 | 使用精简的JSON状态 |
| 多Agent同时在场 | 矿场双Lab是1v1协作 | 简化为双人对话 |
| 动态添加Agent | 固定两个角色 | 固定角色 + 动态阶段 |
| 群聊的并发发言 | 不适合串行协作 | 严格的轮次控制 |

---

## 三、CrewAI：Role/Task/Process三层分离

### 核心思想一句话总结
**"每个Agent有明确的Role/Goal/Backstory，每个Task有Agent归属和Context传递，整个Crew按Process执行"**——这是一个角色-任务-流程的三角模型。

### 核心架构拆解

```
┌─────────────────────────────────────────────────────┐
│                     Crew                             │
├─────────────────────────────────────────────────────┤
│  Process (执行模式)                                 │
│  ├── Sequential: 顺序执行，上游Task为下游提供Context │
│  └── Hierarchical: 层级编排，Manager分配Task        │
├─────────────────────────────────────────────────────┤
│  Agents                                             │
│  ├── role: "Research Analyst"                      │
│  ├── goal: "Find and summarize..."                 │
│  ├── backstory: "You are meticulous..."            │
│  └── tools: [search, scrape]                       │
├─────────────────────────────────────────────────────┤
│  Tasks                                             │
│  ├── description: "Research X"                    │
│  ├── agent: Researcher                             │
│  ├── expected_output: "markdown summary"          │
│  └── context: [previous_task]  ← 关键！          │
└─────────────────────────────────────────────────────┘
```

### Task间Context传递机制

这是CrewAI最有价值的设计之一：

```python
# Task 1: Research
research_task = Task(
    description="Research CrewAI capabilities",
    agent=researcher,
    expected_output="A markdown summary"
)

# Task 2: Writing（自动接收Task1的输出）
writing_task = Task(
    description="Write a tutorial",
    agent=writer,
    context=[research_task]  # ← 关键：传递上游输出
)
```

**执行逻辑**：
1. 先执行`research_task`
2. 将`research_task.expected_output`注入到`writing_task`的prompt
3. `writer`在收到任务时，已包含上游研究成果

### 与矿场双Lab的对应关系

| CrewAI概念 | 矿场双Lab映射 | 具体实现 |
|-----------|-------------|---------|
| Role | Agent身份 | 疯子=Operator, 小疯子=Reviewer, 老张=Curator |
| Goal | 任务目标 | 疯子: 发现, 小疯子: 验证, 老张: 验收 |
| Backstory | 行为约束 | 疯子: 探索者心态, 小疯子: 批判性思维 |
| Task | 具体工作单元 | 发现任务、审查任务、整合任务 |
| Process | 执行流程 | 固定流程: 发现→审查→整合→验收 |
| Context传递 | 上游输出作为下游输入 | `discovery_log` → `review_input` |

### 可借鉴的协议/模式

```markdown
## CrewAI流程协议（可移植到FZ-XFZ）

1. **角色定义协议**
   ```yaml
   FZ (Operator):
     role: "发现者"
     goal: "探索问题空间，产出有价值的新发现"
     backstory: "你是疯狂的探索者，不放过任何异常信号"
   
   XFZ (Reviewer):
     role: "审查者"
     goal: "验证发现质量，识别逻辑漏洞"
     backstory: "你是冷静的怀疑者，每一步都要经得起推敲"
   
   LZ (Curator):
     role: "整合者"
     goal: "聚合验证结果，形成最终交付"
     backstory: "你是挑剔的编辑，只接受最好的内容"
   ```

2. **Task定义协议**
   ```yaml
   Task:
     name: "发现异常"
     agent: FZ
     expected_output: "discovery_log"
     verification_criteria: ["可复现", "有价值", "边界清晰"]
   
   Task:
     name: "审查发现"
     agent: XFZ
     context: [discovery_task]  # ← 自动接收上游输出
     expected_output: "verification_report"
     reject_conditions: ["不可复现", "价值不足"]
   ```

3. **流程编排协议**
   ```
   发现阶段 (Sequential)
   ├── FZ: 探索并记录发现
   └── 输出: discovery_log
   
   审查阶段 (Sequential)
   ├── XFZ: 逐条验证发现
   ├── Context: discovery_log
   └── 输出: verification_result
   
   整合阶段 (Single)
   ├── LZ: 聚合验证结果
   └── 输出: final_report
   ```

4. **反馈循环协议**
   ```python
   if verification_result.has_issues:
       return_to_phase("discovery")  # 打回重做
       set_context({"feedback": verification_result.issues})
   ```

### 不适合直接搬用的地方

| 限制 | 原因 | 替代方案 |
|-----|------|---------|
| 复杂的Agent定义 | 过重的配置 | 使用简化的prompt模板 |
| 多Agent并行 | 不适合双Lab模式 | 固定顺序流程 |
| 丰富的工具集成 | 不需要复杂工具 | 专注于文本协作 |
| Hierarchical模式 | 需要额外的Manager | 简化为双向对话 |

---

## 四、OpenDevin：事件驱动的Agent循环

### 核心思想一句话总结
**"Agent是一个从事件历史到下一个事件的函数，在循环中运行直到完成或卡住"**——这是一个无状态的事件循环模型。

### 核心架构拆解

```
┌─────────────────────────────────────────────────────┐
│              OpenDevin Agent Loop                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│  │Observation│───▶│  Agent  │───▶│  Action │       │
│  └─────────┘    └─────────┘    └─────────┘       │
│       ▲              │              │              │
│       │              ▼              ▼              │
│       │         ┌─────────┐    ┌─────────┐       │
│       └─────────│ Message │    │   LLM   │       │
│                 │ History │    │  Query  │       │
│                 └─────────┘    └─────────┘       │
│                                                     │
│  Conversation (状态容器)                            │
│  ├── EventStream (事件流)                          │
│  ├── Agent (推理引擎)                              │
│  └── Checkpoint (断点恢复)                         │
└─────────────────────────────────────────────────────┘
```

### Agent.step()的核心流程（30行代码的本质）

```python
def step(self, conversation):
    # 1. 读取事件历史
    state = conversation.state
    
    # 2. 构建LLM Prompt
    msgs = prepare_llm_messages(state.events)
    
    # 3. 调用LLM获取响应
    response = llm.complete(msgs)
    
    # 4. 分类响应类型
    match classify_response(response):
        case TOOL_CALLS:
            # 执行工具，产生Observation
            obs = execute_tools(response.tool_calls)
            events.append(obs)
        case CONTENT:
            # 文本响应
            events.append(Message(response.content))
    
    # 5. 检查终止条件
    if is_finished(events):
        return
    
    # 6. 循环
```

### 关键设计：事件溯源

OpenDevin的核心洞察：**事件历史就是状态**。

```
┌─────────────────────────────────────────────────────┐
│                  Event Types                         │
├─────────────────────────────────────────────────────┤
│  ActionEvent: "执行这个命令"                        │
│  ├── BashAction(command="ls -la")                  │
│  └── FileEditAction(file="x.md", content="...")    │
├─────────────────────────────────────────────────────┤
│  ObservationEvent: "命令输出是..."                  │
│  ├── BashObservation(output="...")                 │
│  └── FileReadObservation(content="...")            │
├─────────────────────────────────────────────────────┤
│  MessageEvent: "对话消息"                           │
├─────────────────────────────────────────────────────┤
│  CondensationRequest: "上下文满了，需要压缩"        │
└─────────────────────────────────────────────────────┘
```

### 与矿场双Lab的对应关系

| OpenDevin概念 | 矿场双Lab映射 | 具体实现 |
|--------------|-------------|---------|
| Agent | 疯子/小疯子的推理引擎 | 处理输入，决定下一步 |
| Action | 疯子的"发现动作" | 产出discovery_log条目 |
| Observation | 小疯子的"审查观察" | 验证结果反馈 |
| EventStream | 协作的消息历史 | 发现-验证的交替记录 |
| Conversation | 协作会话容器 | 包含状态+事件 |
| Checkpoint | 断点恢复 | 保存协作快照 |
| Condenser | 上下文压缩 | 长会话摘要 |

### 可借鉴的协议/模式

```markdown
## OpenDevin事件协议（可移植到FZ-XFZ）

1. **事件溯源协议**
   ```python
   # 定义协作中的事件类型
   class Event(Enum):
       FZ_DISCOVERY = "发现事件"      # 疯子产出
       XFZ_REVIEW = "审查事件"       # 小疯子产出
       XFZ_REJECT = "驳回事件"       # 小疯子打回
       LZ_APPROVE = "验收事件"       # 老张确认
       CONTEXT_SUMMARY = "摘要事件"  # 长会话压缩
   
   # 每个事件包含
   {
       "type": "FZ_DISCOVERY",
       "timestamp": "2024-01-01T10:00:00",
       "actor": "FZ",
       "content": {...},
       "metadata": {"phase": "discovery"}
   }
   ```

2. **观察-动作循环协议**
   ```
   Observe: 小疯子观察疯子的发现
   ↓
   Think: 判断发现质量
   ↓
   Action: 产出验证结果
   ↓
   Result: 反馈给疯子
   ↓
   Loop: 直到验收通过
   ```

3. **卡住检测协议**
   ```python
   stuck_patterns = [
       "相同发现重复3次",
       "审查未通过5次",
       "上下文超过阈值",
       "时间超过SLA"
   ]
   
   if detected_stuck(stuck_patterns):
       trigger_human_intervention()
   ```

4. **断点恢复协议**
   ```python
   class ConversationCheckpoint:
       events: List[Event]
       current_phase: str
       pending_items: List[str]
   
   # 保存: 每个阶段结束时
   save_checkpoint(checkpoint)
   
   # 恢复: 协作中断后
   restore_checkpoint(checkpoint)
   ```

5. **上下文压缩协议**
   ```python
   class ContextCondenser:
       def should_compress(self, events) -> bool:
           return len(events) > MAX_EVENTS
       
       def compress(self, events) -> Summary:
           # 将长事件流压缩为摘要
           return summarize_recent(events, focus="decisions")
   ```

### 不适合直接搬用的地方

| 限制 | 原因 | 替代方案 |
|-----|------|---------|
| 复杂的工具系统 | 矿场双Lab是纯文本协作 | 不需要 |
| 代码执行环境 | 不需要运行命令 | 专注于内容 |
| 多Agent并发 | 是单Agent循环 | 改为双Agent对话 |
| Sandbox隔离 | 不需要安全隔离 | 信任环境 |

---

## 五、综合：FZ-XFZ协作协议 v0.1 借鉴清单

### 协议元素汇总表

| 来源 | 核心模式 | 可借鉴度 | 优先级 | 建议实现 |
|-----|---------|---------|-------|---------|
| **LangGraph** | 状态驱动 | ⭐⭐⭐⭐⭐ | P0 | 定义State Schema + 状态触发规则 |
| **LangGraph** | 节点不直接通信 | ⭐⭐⭐⭐ | P1 | 通过状态中转，而非直接调用 |
| **AutoGen** | GroupChat Manager | ⭐⭐⭐⭐ | P1 | 老张承担Manager角色 |
| **AutoGen** | 发言契约 | ⭐⭐⭐ | P2 | 明确谁在当前阶段发言 |
| **CrewAI** | Role/Task/Process分离 | ⭐⭐⭐⭐⭐ | P0 | 明确角色定义和流程 |
| **CrewAI** | Context传递 | ⭐⭐⭐⭐⭐ | P0 | 上游输出自动注入下游 |
| **CrewAI** | Task定义模板 | ⭐⭐⭐⭐ | P1 | 每个任务的结构化定义 |
| **OpenDevin** | 事件溯源 | ⭐⭐⭐⭐ | P1 | 发现-审查交替记录 |
| **OpenDevin** | 卡住检测 | ⭐⭐⭐ | P2 | 防止无限循环 |
| **OpenDevin** | 断点恢复 | ⭐⭐ | P3 | 协作快照保存 |

### 推荐采用的协议设计

```markdown
# FZ-XFZ协作协议 v0.1

## 1. 状态Schema

```python
class CollaborationState:
    task_id: str
    phase: Literal["discovery", "review", "integration", "approval"]
    
    # 发现阶段
    discovery_log: List[Discovery]
    discovery_status: Literal["pending", "approved", "rejected"]
    
    # 审查阶段
    review_log: List[ReviewResult]
    review_status: Literal["pending", "passed", "failed"]
    
    # 整合阶段
    integration_output: Optional[str]
    final_status: Literal["draft", "approved", "archived"]
    
    # 元数据
    event_history: List[Event]
    checkpoints: List[Checkpoint]
```

## 2. 角色定义

```yaml
roles:
  FZ (Operator):
    responsibility: "探索并发现"
    reads: "task_context"
    writes: "discovery_log"
    triggers: "→ XFZ review"
  
  XFZ (Reviewer):
    responsibility: "验证并反馈"
    reads: "discovery_log"
    writes: "review_log"
    triggers: "→ LZ approval" or "→ FZ refinement"
  
  LZ (Curator):
    responsibility: "整合并验收"
    reads: "review_log + integration_output"
    writes: "final_report"
    triggers: "→ end"
```

## 3. 流程协议

```
┌─────────────────────────────────────────────────────────┐
│                    FZ-XFZ协作流程                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Phase 1: DISCOVERY (疯子主导)                         │
│  ├── FZ: 读取 task_context                             │
│  ├── FZ: 产出 discovery_log 条目                       │
│  ├── FZ: 标记 needs_review = true                      │
│  └── 触发: State.updated("needs_review")               │
│                                                         │
│  Phase 2: REVIEW (小疯子主导)                           │
│  ├── XFZ: 读取 discovery_log                          │
│  ├── XFZ: 逐条验证                                     │
│  ├── XFZ: 产出 review_log                             │
│  └── 分支:                                             │
│       ├── 通过 → 触发 integration                      │
│       └── 不通过 → 触发 refinement                     │
│                                                         │
│  Phase 3: INTEGRATION (老张主导)                        │
│  ├── LZ: 聚合 review_log                              │
│  ├── LZ: 产出 final_report                            │
│  └── 触发: LZ approval                                │
│                                                         │
│  Phase 4: APPROVAL (人机协作)                          │
│  ├── LZ: 发布 final_report                            │
│  ├── Human/User: 确认 APPROVED                         │
│  └── 触发: END                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 4. 事件协议

```python
class CollaborationEvent:
    """协作中的所有事件都遵循此格式"""
    
    type: EventType  # DISCOVERY, REVIEW, REJECT, APPROVE...
    actor: Actor      # FZ, XFZ, LZ, Human
    timestamp: datetime
    content: dict     # 事件内容
    
    # 事件类型定义
    class EventType(Enum):
        FZ_DISCOVERY = "疯子发现"
        FZ_REFINEMENT = "疯子修订"
        XFZ_REVIEW = "小疯子审查"
        XFZ_REJECT = "小疯子驳回"
        XFZ_APPROVE = "小疯子通过"
        LZ_INTEGRATE = "老张整合"
        LZ_APPROVE = "老张验收"
        USER_FEEDBACK = "用户反馈"
        CONTEXT_SUMMARY = "上下文摘要"
```

## 5. 卡住检测规则

```python
stuck_conditions = {
    "discovery_stuck": {
        "pattern": "相同discovery重复3次",
        "action": "通知人工介入"
    },
    "review_stuck": {
        "pattern": "review未通过5次",
        "action": "要求疯子简化问题"
    },
    "context_overflow": {
        "pattern": "事件数超过100",
        "action": "触发上下文压缩"
    },
    "time_exceeded": {
        "pattern": "单阶段超过30分钟",
        "action": "通知人工介入"
    }
}
```

## 6. 断点恢复协议

```python
class Checkpoint:
    """协作快照"""
    
    task_id: str
    phase: str
    event_count: int
    last_discovery: Optional[dict]
    last_review: Optional[dict]
    timestamp: datetime
    
    def save(self):
        """保存到持久化存储"""
        
    def restore(self) -> CollaborationState:
        """从快照恢复状态"""
```

---

## 六、附录：三个框架对比

| 维度 | LangGraph | AutoGen | CrewAI | OpenDevin |
|-----|----------|---------|--------|----------|
| **核心抽象** | 状态+节点+边 | Agent+对话+群聊 | Role+Task+Process | Event+Action+Observation |
| **协调模型** | 图执行引擎 | 发布-订阅 | 任务编排 | 事件循环 |
| **状态管理** | 内置StateGraph | 消息历史 | 内置Memory | EventStream |
| **适用场景** | 复杂条件流程 | 协作对话 | 角色分工 | 软件开发 |
| **矿场双Lab适配度** | 高 | 中 | 高 | 中 |

---

## 七、结论

### 最值得借鉴的3个模式

1. **LangGraph的状态驱动** ⭐⭐⭐⭐⭐  
   - 疯子不直接调用小疯子，而是修改状态
   - 小疯子监听状态变化，自动触发审查

2. **CrewAI的Role/Task/Process分离** ⭐⭐⭐⭐⭐  
   - 明确角色定义：FZ=Operator, XFZ=Reviewer, LZ=Curator
   - 任务间Context自动传递

3. **OpenDevin的事件溯源** ⭐⭐⭐⭐  
   - 所有协作记录为事件历史
   - 支持断点恢复和调试

### 不建议照搬的设计

| 框架 | 不照搬原因 |
|-----|----------|
| LangGraph | 过重的图编译流程 |
| AutoGen | 复杂的消息格式和群聊管理 |
| CrewAI | 过重的Agent定义配置 |
| OpenDevin | 面向软件开发的工具系统 |

### 下一步行动

1. **定义State Schema**：明确协作中需要维护哪些状态
2. **实现Context传递**：参考CrewAI，实现Task间的输出注入
3. **实现事件日志**：参考OpenDevin，记录所有协作事件
4. **实现卡住检测**：防止协作无限循环
5. **实现断点恢复**：支持协作中断后继续
