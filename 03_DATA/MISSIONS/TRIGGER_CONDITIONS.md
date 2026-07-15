# Mission Trigger Conditions — 条件触发机制

> **原则**: 不说"以后做"，而是定义"什么条件下做"。

---

## 触发条件框架

每个 Mission Candidate 必须定义 **触发条件**（Trigger Conditions），满足条件时自动解锁执行。

---

## 条件类型

| 类型 | 说明 | 示例 |
|------|------|------|
| TIME | 时间到达 | `audit_passed + 3 days` |
| STATE | 系统状态 | `C-028.status == ADMITTED` |
| RESOURCE | 资源状态 | `data_source.availability < 0.5` |
| DEPENDENCY | 前置依赖 | `MISSION-001.status == COMPLETED` |
| MANUAL | 手动触发 | `user_request == true` |
| THRESHOLD | 阈值触发 | `error_rate > 0.3 for 3 days` |

---

## 检查周期

- **每日检查**: 系统启动时扫描所有 CANDIDATE Mission
- **触发通知**: 条件满足时推送提醒
- **手动激活**: 用户确认后转为 ACTIVE

---

## 模板

```yaml
Mission: AUM-MISSION-XXX
Status: CANDIDATE
Trigger Conditions:
  - type: TIME
    condition: audit_passed
    offset: 0 days
  - type: STATE
    condition: C-028.status == ADMITTED OR C-029.status == ADMITTED
  - type: RESOURCE
    condition: data_source.availability < 0.5
    duration: 2 days
Activation Mode: AUTO | MANUAL
Priority After Activation: P0 | P1 | P2
```

---

## 当前 CANDIDATE Mission 触发条件

### AUM-MISSION-DATA-001

```yaml
Mission: AUM-MISSION-DATA-001
Status: CANDIDATE
Trigger Conditions:
  - type: STATE
    condition: C-028.status == ADMITTED OR C-029.status == ADMITTED
    note: Governance Kernel 验证通过
  - type: RESOURCE
    condition: data_source.availability < 0.5
    duration: 2 days
    note: 数据源连续 2 天可用性低于 50%
  - type: TIME
    condition: audit_passed
    offset: 3 days
    note: 审核通过后 3 天自动解锁
  - type: MANUAL
    condition: user_request == true
    note: 用户明确要求立即执行
Activation Mode: AUTO (STATE/RESOURCE/TIME) + MANUAL
Priority After Activation: P0
```

**解释**：
- 如果 C-028 或 C-029 通过 → 自动解锁（Governance Kernel 验证成功）
- 如果数据源连续 2 天不可用 → 自动解锁（生产阻断）
- 如果审核通过后 3 天 → 自动解锁（时间兜底）
- 用户明确要求 → 手动解锁（紧急情况）

---

## 检查脚本

```python
# 04_PROTOCOLS/mission_trigger_checker.py

def check_trigger_conditions():
    """
    每日检查所有 CANDIDATE Mission 的触发条件
    返回满足条件的 Mission 列表
    """
    candidates = load_candidate_missions()
    triggered = []

    for mission in candidates:
        conditions = mission.get("trigger_conditions", [])

        for cond in conditions:
            if evaluate_condition(cond):
                triggered.append(mission)
                break

    return triggered

def evaluate_condition(cond):
    """评估单个条件是否满足"""
    cond_type = cond.get("type")

    if cond_type == "STATE":
        return evaluate_state_condition(cond)
    elif cond_type == "RESOURCE":
        return evaluate_resource_condition(cond)
    elif cond_type == "TIME":
        return evaluate_time_condition(cond)
    elif cond_type == "MANUAL":
        return cond.get("condition") == True

    return False
```

---

## 考古发现归档

未来所有有价值的考古发现，按以下流程处理：

1. **发现有价值内容** → 创建 Mission Candidate
2. **定义触发条件** → 明确"什么条件下做"
3. **写入 TRIGGER_CONDITIONS.md** → 可追踪
4. **定期检查** → 条件满足时自动解锁

**不再说"以后做"**，而是说"当 X 条件满足时做"。

---

## 待定义触发条件的 CANDIDATE

| Mission | 当前状态 | 触发条件 | 是否已定义 |
|---------|----------|----------|------------|
| DATA-001 | CANDIDATE | STATE/RESOURCE/TIME/MANUAL | ✅ 已定义 |
| SSH 认证替代 PAT | Pending | 待定义 | ❌ 待补充 |
| Artifact Schema 统一 | Pending | 待定义 | ❌ 待补充 |

---

*机制已建立。考古发现的种子不会丢失，只等待条件成熟时发芽。*