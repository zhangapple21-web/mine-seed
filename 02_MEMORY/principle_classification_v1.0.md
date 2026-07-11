# Principle 正式分类表 v1.0

**建立时间**: 2026-06-20
**分类标准**: EXECUTABLE = 能直接翻译成可执行Constraint（AVOID/PREFER/FORBID规则）；META = 只能做审核标准或哲学指导

---

## EXECUTABLE Principles（可执行 — 能进入路由器）

| ID | Principle | 翻译方向 | 已有Constraint映射 | 翻译难度 | 状态 |
|----|-----------|----------|-------------------|----------|------|
| A004 | 重要性触发为主+时间保底 | Worker连续失败→立即proposal | constraint_proposer.py已实现 | 低 | ✅已实现，缺source标注 |
| A007 | 先放着+种子索引 | 30天无失败→降级PENDING | RFC-006降级规则 | 中 | ⚠️已设计未部署 |

**翻译协议（EXECUTABLE专用）**:
```
Principle(A004) → Candidate("Worker连续3次失败立即触发反思") → Review → Constraint({action:"TRIGGER", task:"*", worker:"*", condition:"3_consecutive_fail"})
```

---

## META Principles（元规则 — 做审核标准）

| ID | Principle | 审核用途 | 对Constraint的约束 | 状态 |
|----|-----------|----------|-------------------|------|
| A001 | 观察先于行动 | 新Constraint必须有observation支撑 | 无observation的Constraint不得ACTIVE | REVIEW |
| A002 | Reality≠Observation | Constraint验证靠行为改变不靠日志 | 日志说生效≠真实生效 | ⚠️当前正在验证 |
| A003 | 约束必要性>数量 | 新Constraint必填"防止过什么事故" | 反过拟合审核标准 | REVIEW |
| A005 | 观察对象决定质量 | Constraint关注老张关心的 | 聚焦审核标准 | REVIEW |
| C000 | 不为空白而建设 | 新Constraint附"如果不存在会怎样" | 必要性审核标准 | 铁律 |
| P006 | 进化靠游荡 | 游荡产出不做Constraint | 自由探索保护 | PENDING |

**META Principles不直接进路由器，但审核任何新Constraint时必须对照。**

---

## 翻译协议 v0.1

```
Observation → Principle（研究域：小疯子负责）
Principle → 分类（EXECUTABLE / META）
    EXECUTABLE → Candidate Constraint → Review → ACTIVE Constraint → routing_constraints.json
    META → 审核标准 → 审核任何新Constraint时必须对照
```

**关键规则**:
1. 不自动化翻译——每次产出时自然对照
2. EXECUTABLE的Candidate必须附Evidence
3. Review由疯子做（生产域负责人）
4. 每条Constraint加source字段标注来源

## Evidence Table

| Principle | Evidence | Candidate Constraint | Review Status | Decision |
|-----------|----------|---------------------|---------------|----------|
| A004 | constraint_proposer.py已实现 | Worker连续失败→立即proposal | ✅已实现 | 需加source=principle:A004 |
| A007 | RFC-006降级规则 | 30天无失败→降级PENDING | ⚠️已设计未部署 | 等疯子部署 |
| A001 | 10条constraint无决策记录 | 无observation的Constraint不得ACTIVE | REVIEW | 待人工审核 |
| A002 | ⛔ AVOID补丁修的就是这个 | Constraint验证靠行为改变 | REVIEW | 等16:00验证 |
| A003 | RFC-006反过拟合 | 新Constraint必填"防止过什么事故" | REVIEW | 待人工审核 |
| A005 | 已有老张观察轴 | 日报聚焦老张关心的 | REVIEW | 待人工审核 |
| C000 | auto-confirm隐含 | 新Constraint附"如果不存在会怎样" | REVIEW | 铁律级 |
| P006 | 觅游种子 | 暂无 | PENDING | 长期验证 |
