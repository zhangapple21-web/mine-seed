# 荐股系统状态报告
> 生成时间: 2026-07-13 16:18
> 状态: 正常运行

---

## 核心功能状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 数据源管理器 | ✅ | 5级自动降级（新浪→东财→腾讯→Baostock→akshare） |
| 审计系统 | ✅ | 推票后审计（矿工评估+规则引擎交叉验证） |
| 事件日志器 | ✅ | 时间感知，记录每日事件 |
| 表现追踪器 | ✅ | 多周期复核（T+1/T+7/T+15/T+30） |
| 策略管理器 | ✅ | Roundtable评审+Admission批准 |
| 自适应评分器 | ✅ | 动态权重调整+Evidence闭环 |

---

## 数据源状态

| 数据源 | 状态 | 优先级 | 延迟 |
|--------|------|--------|------|
| sina | ✅ | 1 | 0.16s |
| eastmoney | ❌ | 2 | - (502错误) |
| tencent | ✅ | 3 | 0.30s |
| baostock | ❌ | 4 | - (未安装) |
| akshare | ✅ | 5 | 0s |

---

## 审计状态

- 最近30天审计数: 3
- 平均评分: 72/100
- 评级分布: A=0, B=3, C=0, D=0

---

## 策略状态

- 当前策略: POLICY-001 v1
- 状态: approved
- 生效时间: 2026-07-13T15:09:45
- 核心规则:
  - 最低评分阈值: 40
  - 每日最多推荐: 2只
  - 多样性要求: 是
  - 去重周期: 7天

---

## 今日事件

| 时间 | 类型 | 消息 |
|------|------|------|
| 15:47:08 | RECOMMEND | 测试推荐2只股票 |

---

## 关键文件

| 文件 | 大小 | 状态 |
|------|------|------|
| performance_db.json | 2990 bytes | ✓ |
| current_policy.json | 883 bytes | ✓ |
| audit_results.json | 4643 bytes | ✓ |
| daily_events.json | 199 bytes | ✓ |

---

## 2026-07-13 完成的优化

### 新增功能
1. **推票后审计流程** - 矿工评估+规则引擎交叉验证
2. **多数据源管理** - 5级自动降级，不绑死腾讯
3. **时间感知系统** - 记录每日事件和系统状态
4. **Evidence闭环** - 审计结果用于策略优化
5. **缓存清理机制** - `--clean-cache` 参数

### 修复与升级
1. **lineage_review.py** - 修复路径问题，集成多数据源
2. **advisor_tracker.py** - 升级使用多数据源
3. **daily_runner.py** - 集成事件日志
4. **adaptive_scorer.py** - 添加审计Evidence集成

### 新增工具
1. **health_check.py** - 系统健康检查脚本
2. **advisor_diagnostic.py** - 增强诊断工具

---

## 运维命令

```bash
# 健康检查
python health_check.py

# 诊断报告
python advisor_diagnostic.py

# 缓存清理（保留7天）
python multi_data_source.py --clean-cache 7

# 事件时间线
python daily_event_logger.py --timeline 7

# 荐股引擎
python stock_advisor.py --test-mode
```

---

## 下次启动建议

1. 运行 `python health_check.py` 确认所有模块正常
2. 运行 `python advisor_diagnostic.py` 查看完整诊断报告
3. 检查 `daily_events.json` 了解系统历史事件
4. 查看数据源状态，确认自动降级正常工作

---

> 报告生成: 2026-07-13 16:18