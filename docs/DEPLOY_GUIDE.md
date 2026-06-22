# 约束代码化部署指南

**日期**: 2026-06-20
**状态**: 🟡 部署v2执行中（硬编码策略，不依赖外部JSON）

## 部署前检查清单

- [ ] computer_use可正常连接lab_01
- [ ] 确认miner_24h.py当前内容（特别是match_task_to_worker函数签名和return语句）
- [ ] 确认routing_constraints.json当前内容（预期是空壳模板）
- [ ] 确认当前没有班次在运行（避免修改运行中的脚本）

## 部署文件

1. **deploy_constraints.py** → `/app/data/所有对话/主对话/mine_output/deploy_constraints.py`
   - file_to_url: https://www.coze.cn/s/jN1fKAx_YxE/
   - 功能：备份→写新约束JSON→注入约束过滤代码→验证语法

2. **routing_constraints_v3.json** → `/app/data/所有对话/主对话/mine_output/routing_constraints_v3.json`
   - file_to_url: https://www.coze.cn/s/xMY62idr4-Y/
   - 内容：9 AVOID + 1 PREFER（8条pending待确认）

## 约束内容

### AVOID (9条)
| ID | Task | Worker | Reason |
|---|---|---|---|
| RC-001 | * | gh_r1 | 全任务禁入 canonical_v2 8败 |
| RC-002 | * | nim_ultra_550b | 全任务禁入 9败 |
| RC-003 | * | gh_4o | 全量淘汰 胜率20% |
| RC-004 | persona_deep | nim_mistral_675b | 3败 |
| RC-005 | canonical_v2 | gh_r1 | 27次失败 |
| RC-006 | canonical_v2 | nim_ultra_550b | 5次失败 |
| RC-007 | persona_deep | nim_ultra_550b | 4次失败 |
| RC-014 | signal_mean_reversion | glm_4_flash | Fitness Map毒组合 |
| RC-015 | signal_volume_price_divergence | glm_4_flash | Fitness Map毒组合 |

### PREFER (1条)
| ID | Task | Worker | Reason |
|---|---|---|---|
| RC-016 | signal_mean_reversion | nim_deepseek | Fitness Map偏好 |

### Pending (8条 - 待确认target worker)
RC-008/009/010/011/012/013/017/018

## 部署步骤

```bash
# Step 1: 在lab_01上下载并执行部署脚本
curl -sL https://www.coze.cn/s/jN1fKAx_YxE/ -o /tmp/dc.py
python3 /tmp/dc.py

# Step 2: 验证文件已修改
grep "Constraint Filter" /home/coze/miner_24h.py
cat /home/coze/routing_constraints.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'avoids={len(d[\"avoids\"])}, prefers={len(d[\"prefers\"])}')"

# Step 3: 等待下一个4h班次，检查cron.log
grep CONSTRAINT /home/coze/mine_output/cron.log

# Step 4: 更新Constraint Ledger状态
# 📝 TEXT_ONLY → ⚙️ CODED → ✅ ACTIVE
```

## 回滚方案

如果部署后出问题：
```bash
# 恢复miner_24h.py
cp /home/coze/miner_24h.py.bak.* /home/coze/miner_24h.py

# 恢复routing_constraints.json
cp /home/coze/routing_constraints.json.bak.* /home/coze/routing_constraints.json
```

## 风险评估

- **低风险**：注入代码有try/except兜底，即使约束JSON读取出错也不会crash
- **低风险**：备份文件自动创建，可随时回滚
- **中风险**：如果match_task_to_worker()的参数名不是task_type/best_worker/WORKER_PROFILES，注入代码可能无法正确读取。需确认函数签名
- **注意**：coze用户对miner_24h.py有写权限，无需root

## 验证标准

1. `python3 -c "import ast; ast.parse(open('/home/coze/miner_24h.py').read())"` 通过
2. routing_constraints.json包含avoids和prefers键
3. 下一个班次cron.log出现`[CONSTRAINT]`日志
4. 首次AVOID触发后更新Constraint Ledger为✅ ACTIVE

## v2策略变更（2026-06-20 14:20）

**问题**: v1部署报 `PermissionError: /home/coze/routing_constraints.json` — root创建的文件coze用户无写权限
**解决**: v2策略将约束直接硬编码进miner_24h.py，完全不依赖外部JSON文件
**文件**: deploy_constraints_v2.py → URL: https://www.coze.cn/s/xAdbnIoaCx0/

### v2 vs v1
| 项目 | v1 | v2 |
|---|---|---|
| 约束存储 | routing_constraints.json | 硬编码进Python |
| 外部依赖 | 需要JSON文件可读可写 | 无 |
| 更新方式 | 改JSON文件 | 改代码重新注入 |
| 权限要求 | coze需写JSON | 只需写miner_24h.py |
| 状态 | ❌ 权限拒绝 | ✅ 执行中 |