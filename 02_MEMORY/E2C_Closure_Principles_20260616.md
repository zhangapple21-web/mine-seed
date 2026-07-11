# E→C闭环原则压缩

> 压缩时间: 20260616 05:30
> 来源: experience_to_constraint_closure.md (近中记录)
> 优先级: P2 - 矿场V6 L1核心特性


# E→C闭环 核心原则 (V6-L1)

## P1: 经验必须可执行
- 档案官AVOID标记 ≠ 调度器硬约束
- 经验记录只是数据，约束才是行动
- O→E是记录，E→C是执行

## P2: 约束自动生成，失败组合自动规避
- 触发：连续失败N次 或 状态切换
- 动作：写active_constraints.json + 更新路由表
- 验证：回放时约束可追溯

## P3: 冷却优于硬删，阶梯优于二值
- 不要立即删掉失败的模型
- 用冷却时长替代alive/dead
- 冷却到期自动回到候选队列

---

# E→C闭环协议 v1.0

WHEN node.status changes to degraded/dead:
  1. READ recent_failures FROM observation_log
  2. GENERATE constraint_entry:
     - type: FORBID | AVOID | PREFER
     - target: node_id
     - scope: scheduler | routing | fallback
     - reason: obs_xxx
  3. WRITE active_constraints.json
  4. UPDATE task_mapping
  5. LOG constraint_trace (for replay)

ENFORCE constraint BEFORE task_dispatch:
  - CHECK skip_set first
  - REJECT if FORBID
  - DOWNGRADE if AVOID
  - BOOST if PREFER


## 一句话总结
**经验是数据，约束才是行动；O→E是记录，E→C是执行。**
