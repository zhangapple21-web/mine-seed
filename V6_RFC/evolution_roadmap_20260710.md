# ACE Evolution Roadmap — 2026-07-10

## 今日成果

| # | 成果 | 文件 |
|---|------|------|
| 1 | Data Plane 审计 + 4个bug修复 | stock_advisor.py, dragon_leader_v2.py, stock_query.py |
| 2 | Runtime 调度能力审计 | 确认 Miner 可扩展为通用 Provider Router |
| 3 | vn.py 结构考古 | V6_RFC/vnpy_archaeology.md |
| 4 | Environment Sensor + SituationBuilder | 04_PROTOCOLS/environment_sensor.py |
| 5 | Local Miner v2 多源 fallback | 04_PROTOCOLS/local_miner.py |

## 明日任务（P0）

### 开发优先级变更

```
旧：新增模型 > 新增数据源 > 新增 Agent
新：Capability > Routing > Observation > Experience > 新增模型
```

重点从"增加能力"切换到"让已有能力协同工作"。

### TASK-001：Model Registry

建立统一模型注册表，按 Capability 索引：

```yaml
models:
  ollama-qwen-vl:
    provider: ollama
    capabilities: [vision, summarize, archaeology, code]
    priority: 1  # 本地优先

  github-gpt4omini:
    provider: github
    capabilities: [reasoning, coding, debate]
    priority: 2

  glm-flash:
    provider: zhipu
    capabilities: [fast, chinese, summarize]
    priority: 3

  openrouter-llama:
    provider: openrouter
    capabilities: [debate, long_context]
    priority: 4
```

### TASK-002：统一 call_model 接口

禁止直接调用 `call_github()` / `call_zhipu()` / `call_ollama()`。

统一：
```python
call_model(capability="code_review")
```

Router 根据 Model Registry 自动选择 Provider。

### TASK-003：Provider Health

每个 Provider 维护：
- Latency（平均延迟）
- SuccessRate（成功率）
- LastHeartbeat（最后心跳时间）

Heartbeat 自动更新。不要等失败了才知道。

### TASK-004：矿工角色分化

```
Scout      → GitHub/RSS 扫描，发现资产
Researcher → 深度考古，拆结构
Validator  → 交叉验证，打分
Reporter   → 生成日报
```

每个角色调用不同 capability 的模型。

### TASK-005：Environment Sensor 接入 Model Router

```
Sensor 发现 GitHub Trending
  → 自动生成 Observation
    → 交给 Miner（Researcher 考古）
      → RoundTable 审议
        → 决定是否进入 Repository
```

全链路自动化，不人为触发。

## 不做

- ❌ 不下载新模型
- ❌ 不接新 Provider
- ❌ 不写新 Agent

## 已有资产清单

| 资产 | 状态 |
|------|------|
| 本地 Ollama (qwen2.5-vl-abliterated:7b) | ✅ 已接通 |
| GitHub Models (gpt-4o-mini等) | ✅ 已接通 |
| Zhipu GLM (glm-4-flash) | ✅ 已接通 |
| OpenRouter (llama-3.3-70b free) | ✅ 已接通 |
| NVIDIA NIM (16 key 轮询) | ✅ 已有(ace_gateway.py) |
| Miner (task_router_v2) | ✅ 已有 |
| Scheduler (heartbeat) | ✅ 已有 |
| RoundTable | ✅ 已有 |
| EnvironmentSensor | ✅ 今日新建 |
| Repository | ✅ 已有 |
