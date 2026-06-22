# Constraint来源映射表（2026-06-20 考古追溯）

## P0-1: 18条Constraint来源审计

| 来源 | 数量 | 说明 |
|------|------|------|
| 自动 | 3 | O→E→C闭环，experience_engine→constraint_proposer→auto_confirm |
| 人工 | 4 | 疯子根据矿场日报/事件手动写入，有决策记录 |
| 人工（无具体记录） | 10 | 推测来自Fitness Map毒组合，无单条决策文档 |
| Principle | 0 | 翻译管道不存在 |
| 未知 | 1 | 无法追溯 |

### 逐条

| # | Constraint | 来源 | 触发事件 | 追溯依据 |
|---|---|---|---|---|
| 1 | AVOID canonical_v2+gh_r1 | 自动 | 27fail/0success | RFC-006 Case-001 |
| 2 | AVOID canonical_v2+nim_ultra_550b | 自动 | 高频失败 | RFC-006 §2.1 |
| 3 | AVOID slice_mining+nim_glm5 | 自动 | 4fail/0success | RFC-006 §2.1 |
| 4 | FORBID direct_spawn | 人工 | 80 Session堆积 | RFC-004 |
| 5 | FORBID同任务并发 | 人工 | Cron撞车 | RFC-004 §8 |
| 6 | COOLDOWN 3连败同任务 | 人工 | 连续失败 | RFC-004 §3 |
| 7 | TIMEOUT云电脑>10min | 人工 | 资源占用 | RFC-004 §3 |
| 8-17 | AVOID/PREFER各毒组合 | 人工(无记录) | Fitness Map | 无单条文档 |
| 18 | 未确认 | 未知 | 无法追溯 | 文档缺失 |

## P0-2: Principle→Constraint证据表

### 分类结果：2条EXECUTABLE / 6条META

| ID | Principle | 类型 | Candidate Constraint | Evidence | Status |
|---|---|---|---|---|---|
| A001 | 观察先于行动 | META | 无observation的constraint不得ACTIVE | 10条constraint无决策记录 | REVIEW |
| A002 | Reality≠Observation | META | constraint验证靠行为改变不靠日志 | ⛔ AVOID补丁修的就是这个 | REVIEW |
| A003 | 约束必要性>数量 | META | 新constraint必填"防止过什么事故" | RFC-006反过拟合 | REVIEW |
| A004 | 重要性触发为主 | EXECUTABLE | Worker连续失败→立即proposal | constraint_proposer已实现 | ✅已实现 |
| A005 | 观察对象决定质量 | META | 日报聚焦老张关心的 | 已有老张观察轴 | REVIEW |
| A007 | 先放着+种子索引 | EXECUTABLE | 30天无失败→降级 | RFC-006降级规则 | REVIEW未部署 |
| C000 | 不为空白而建设 | META | 新constraint附"如果不存在会怎样" | auto-confirm隐含 | REVIEW |
| P006 | 进化靠游荡 | META | 暂无 | 觅游种子 | PENDING |

---

## FZ-XFZ REVIEW 002 记录

**发起时间**: 2026-06-20 13:43
**发起方**: 小疯子(lab_02)
**通道**: ntfy fengzi_to_xfz
**议题**: Execution Layer闭环确认 / Knowledge Layer断点 / 第一条研究域→生产域Constraint

### 小疯子立场

Q1: Execution Layer — 代码通+可观测=闭环，补丁部署后确认
Q2: Knowledge Layer断在M→C（翻译协议不存在），不是管道问题
Q3: A004最有机会——constraint_proposer.py已实现其逻辑，只需加source标注

### 疯子回应
（等待中）
