# miner_24h.py 真实架构调查

## 已确认事实（2026-06-20 14:55）

### 1. crontab入口
```
0 */4 * * * /home/coze/miner_cron.sh >> /home/coze/mine_output/cron.log 2>&1
```

### 2. miner_cron.sh内容
```bash
#!/bin/bash
LOCKFILE="/tmp/miner_shift.lock"
# ... 加锁逻辑 ...
source /home/coze/miner_env.sh
cd /home/coze
python3 miner_24h.py $(date +%H)
```

### 3. miner_24h.py函数结构（2026-06-20 15:00 完整确认）

**没有 match_task_to_worker 函数！**
**没有 task_router 函数！**

#### 核心调度链（🔑 这是约束注入的正确位置）
```
各任务函数 → call_model(prompt, task_name) → router.get_fallback_chain(task_name) → chain遍历 → stream_call(model, messages) → API
```

#### call_model函数（line 86）关键逻辑：
```python
def call_model(prompt, task_name, max_retries=2, ...):
    # 按任务路由：不传model_type，传task_name
    # Router自动匹配最合适的工人
    chain = router.get_fallback_chain(task_name)
    if not chain:
        # fallback：直接走GLM兜底
        chain = [("glm_flash", "glm-4-flash"), ("glm_air", "glm-4-air")]
    for worker_id, model in chain:
        w = registry.get_worker(worker_id)
        if not w: continue
        if w.get("status") != "alive": continue
        for attempt in range(max_retries):
            try:
                result, err = _stream_call(model, messages, ...)
                # ... 429限速重试 / 成功返回 / 错误处理
```

#### 已知独立任务函数（从return语句推断）：
- `slice_classification` → `return save_result("slice_classification", result)`
- `persona_deep` → `return save_result("persona_deep", result)`
- `shadow_analysis` → `return save_result("shadow_analysis", result)`
- `routing_analysis` → `return save_result("routing_analysis", result)`
- `slice_mining` → `return save_result("slice_mining", result)`
- `upgrade_analysis` → `return save_result("upgrade_analysis", result)`
- `canonical_v2` → `return save_result("canonical_v2", result)`

#### 辅助/底层函数：
- `stream_call(model, messages, max_tokens, temperature, timeout)` — line 26，底层API调用
- `_stream_call` — 内部流式调用
- `call_model_judge` — 裁判函数
- `log` — 日志
- `save_result` — 保存结果
- `load_r1_data` — 加载R1数据

### 4. 🔑🔑🔑 约束注入的正确位置

**之前追错的地方**：试图在miner_24h.py里找match_task_to_worker()，不存在
**正确的注入点**：`router.get_fallback_chain(task_name)` — 这才是调度层

两种策略：
1. **修改router对象的方法**：在get_fallback_chain返回后过滤AVOID worker
2. **在call_model里加过滤**：chain获取后，在for循环前加约束检查

策略2更安全——不修改router对象，只在call_model里加几行代码
