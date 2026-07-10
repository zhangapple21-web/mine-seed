# FZ-XFZ 事件驱动协作协议 v0.1

**建立时间**: 2026-06-20
**核心原则**: 目标不是让两台服务器能通信，是让它们知道什么时候必须协作、审查、反哺
**借鉴**: LangGraph状态驱动 + CrewAI Context传递 + OpenDevin事件溯源

---

## 1. 角色定义

```
疯子(FZ) = Operator — "系统在干什么"
  读：task_context, review_feedback
  写：discovery_log
  触发：→ XFZ review

小疯子(XFZ) = Reviewer — "为什么这样"
  读：discovery_log
  写：review_log, principle_candidates
  触发：→ LZ approval 或 → FZ refinement

老张(LZ) = Curator — "这件事值不值得做"
  读：review_log
  写：final_decision
  触发：→ END
```

---

## 2. 事件表

| 事件ID | 事件名 | 触发条件 | 谁发 | 谁收 | 回复时限 | 回复什么 |
|--------|--------|----------|------|------|----------|----------|
| E001 | PRODUCTION_FAILURE | Worker连续3次失败/成功率<30% | FZ | XFZ | 2h | 失败模式分析+Principle候选 |
| E002 | PRINCIPLE_ACTIVE | Principle升级ACTIVE | XFZ | FZ | 1h | 确认可翻译性+Candidate |
| E003 | CONSTRAINT_ADDED | 新Constraint写入json | FZ | XFZ | 1h | 来源追溯+Principle映射 |
| E004 | CONSTRAINT_REJECTED | Candidate被否决 | 双方 | 对方 | 无时限 | 否决理由归档 |
| E005 | VALIDATION_FAILED | Constraint生效但行为未变 | XFZ | FZ | 2h | 检查路由+补丁 |
| E006 | REPLAY_REQUIRED | 需回放决策推理过程 | 任意 | 对方 | 4h | 证据链 |
| E007 | KNOWLEDGE_GAP_FOUND | 现有Principle无法解释 | XFZ | FZ+LZ | 无时限 | 记入种子池 |
| E008 | EXECUTION_ANOMALY | 矿场异常但Constraint未触发 | FZ | XFZ | 2h | 启动Hypothesis Investigation |
| E009 | STATE_CHANGED | 协作状态变更 | 任意 | 对方 | 无 | 确认收到 |

---

## 3. 协作状态Schema

借鉴LangGraph——节点不直接控制彼此，只修改状态，状态驱动下一步：

```
CollaborationState:
  task_id: string
  phase: discovery | review | integration | approval
  
  # 发现阶段
  discovery_log: [DiscoveryItem]
  needs_review: boolean
  
  # 审查阶段
  review_log: [ReviewResult]
  review_status: pending | passed | failed
  
  # 整合阶段
  final_report: string | null
  final_status: draft | approved | archived
  
  # 事件溯源
  event_history: [Event]
```

**关键规则**: 
- 节点只写自己的字段（疯子写discovery_log，小疯子写review_log）
- 状态变更触发对应事件
- 不直接调用对方，通过状态中转

---

## 4. 协作流程

### REVIEW（联合审查）
- 触发：任意一方发起，附议题
- 格式：问题+立场+证据
- 回复：指定时限内回应立场
- 归档：review_XXX_YYYYMMDD.md

### 派单（任务委托）
- FZ→XFZ：生产域发现需要研究域解释
- XFZ→FZ：研究域产出需要生产域验证
- 格式：任务+验收标准+时限
- 拒绝权：接收方可说明理由拒绝

### Hypothesis Investigation（自主研究）
- 触发：XFZ看到生产异常/新发现/结论变化
- 流程：建假设树→收证据→排除假设→更新概率→最可信解释
- 不需要等老板派单
- 不需要等疯子提问

### 回复（日常通信）
- 非紧急信息交换
- 不强制回复时限
- 超过24h未读标记

### 归档（产物持久化）
- 所有REVIEW/派单必须归档
- 归档位置：research/ (XFZ侧) / shared/directives/ (共享侧)

---

## 5. Context传递协议

借鉴CrewAI——上游输出自动注入下游：

```
discovery_phase:
  FZ产出 → discovery_log
  
review_phase:
  context: discovery_log  ← 自动注入
  XFZ产出 → review_log
  
integration_phase:
  context: review_log  ← 自动注入
  LZ产出 → final_decision
```

**实际实现**: ntfy消息体携带上一阶段产出的摘要，接收方无需额外查询。

---

## 6. 卡住检测

| 状态 | 检测条件 | 动作 |
|------|----------|------|
| 发现卡住 | 相同discovery重复3次 | 通知LZ |
| 审查卡住 | review未通过5次 | 要求FZ简化问题 |
| 上下文溢出 | 事件数>100 | 触发压缩摘要 |
| 时间超限 | 单阶段>30min | 通知LZ |

---

## 7. 汇报格式（统一）

```
发现:
证据:
结论:
下一步:
```

老张不再做人肉MQ。

---

## 8. 通信通道

- ntfy.sh: fengzi_to_xfz（FZ→XFZ）/ xfz_to_fengzi（XFZ→FZ）
- /home/coze/shared/: 公共文件交换（inbox_lab01/、inbox_lab02/、directives/）
- 不用GitHub Gist（PAT过期401）
