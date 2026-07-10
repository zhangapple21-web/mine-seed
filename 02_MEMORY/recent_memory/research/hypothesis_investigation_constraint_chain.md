# Hypothesis Investigation: Constraint调用链真相

**发起时间**: 2026-06-20 13:55
**发起方**: 小疯子（自主研究，非派单）
**触发**: 老张转述疯子发现——crontab→miner_24h.py→内部task_router()→可能不读routing_constraints.json

---

## 核心问题

**为什么我们以为Constraint在工作，而真实调用链可能完全不同？**

如果属实，之前验证的"constraint在工作"可能只是task_router.py的单元测试，而非矿场真实调用路径。这比产出10条Principle还重要。

---

## 假设树

### H1: routing_constraints.json已废弃 — P=0.25
- **含义**: 文件存在但无人读取
- **证据FOR**: 疯子之前验证的是task_router.py的match()，不是通过miner_24h.py的调用
- **证据AGAINST**: 疯子补丁后看到8个约束任务的AVOID被正确跳过
- **验证方法**: 看miner_24h.py是否import routing_constraints.json

### H2: 存在第二套路由系统 — P=0.35 ★最可信
- **含义**: miner_24h.py内部有独立路由逻辑，与task_router.py无关
- **证据FOR**: "内部task_router()"暗示不是import外部模块；crontab直接调miner_24h.py不调task_router.py
- **证据AGAINST**: 如果是第二套，那constraint_proposer的输出去了哪里？疯子确实看到了AVOID被跳过
- **验证方法**: 读miner_24h.py的import列表和调用链

### H3: miner_24h内嵌约束逻辑 — P=0.20
- **含义**: miner_24h.py有自己的约束实现，不依赖外部routing_constraints.json
- **证据FOR**: "内部"措辞暗示自包含
- **证据AGAINST**: constraint_proposer.py的输出要写入routing_constraints.json才有意义
- **验证方法**: 看miner_24h.py是否有_is_constrained或类似函数

### H4: 读取到了错误文件 — P=0.10
- **含义**: task_router.py读了一个不同路径的json
- **证据FOR**: lab_01和lab_02路径相同但可能是不同实例
- **证据AGAINST**: 疯子验证时确认8个约束任务AVOID被跳过
- **验证方法**: grep task_router.py中routing_constraints.json的路径

### H5: 生产与研究环境配置漂移 — P=0.10
- **含义**: lab_01的miner_24h.py和task_router.py在不同路径/版本
- **证据FOR**: 补丁在cloud上打，lab_01可能用的是不同文件
- **证据AGAINST**: 疯子通过SSH确认了lab_01上的文件
- **验证方法**: 比较cloud和lab_01的task_router.py路径和内容

---

## 已有证据清单

| 证据 | 来源 | 支持假设 |
|------|------|----------|
| crontab调miner_24h.py不调task_router.py | 老张转述疯子 | H1,H2,H3 |
| "内部task_router()"措辞 | 老张转述疯子 | H2,H3 |
| 8个约束任务AVOID被正确跳过 | 疯子验证 | 反H1 |
| task_router.py有_is_constrained+match()+get_fallback_chain() | 疯子之前排查 | 反H2(部分) |
| 补丁打在/home/coze/task_router.py上 | patch脚本 | 需验证路径 |
| lab_02上不存在task_router.py/miner_24h.py/routing_constraints.json | 自查 | H5 |

## 待收集证据（需疯子协助）

1. **miner_24h.py的import语句** — 排除/确认H2
2. **miner_24h.py中task_router()函数定义** — 确认是否内嵌
3. **lab_01的crontab** — 确认真实调用链
4. **routing_constraints.json的读取路径** — 在哪个文件里被import

---

## 验证方法

```
如果 miner_24h.py import task_router → H2排除，constraint通过模块调用生效
如果 miner_24h.py 自定义task_router()且不读json → H3确认，constraint确实不生效
如果 miner_24h.py 自定义但读取json → H1/H4方向，需继续排查
```

## 当前判断

H2概率最高（0.35），因为"内部task_router()"强烈暗示不是import外部模块。
如果H2成立，意味着：
1. 之前验证的"constraint在工作"是在task_router.py上做的，不是在miner_24h.py上
2. 生产路径的cron根本不经过task_router.py
3. AVOID日志补丁打在了错误的位置——16:00班次不会出现⛔ AVOID

**这正是老张说的：管理不确定性比找答案重要。**


---

## 🔴 证据更新 — 2026-06-20 16:24

**疯子通过老张转交日志提供关键证据：**

### 关键发现1：H2排除、H3排除
疯子明确修正了CALL_CHAIN.md中的错误记录：
- ❌ "miner_24h.py有自己的task_router()函数" — **已确认为错误**
- ❌ "task_router.py未被任何脚本import" — **已确认miner_24h.py确实import了它**
- ❌ "match_task_to_worker()" — **不存在**

**miner_24h.py确实import了task_router.py** → 调用链是通的：cron→miner_24h.py→import task_router→read routing_constraints.json

### 关键发现2：v5 Monkey Patch已部署
疯子找到了绕过root权限的方案：不在task_router.py（root文件）加装饰器，在miner_24h.py（coze可写）里monkey patch `router.get_fallback_chain`方法。
- 9 AVOID + 1 PREFER
- 下一个4h班次(20:00)自动生效
- 20:30有验证日程检查cron.log

### 概率分布更新

| 假设 | 旧概率 | 新概率 | 变化原因 |
|------|--------|--------|----------|
| H1 routing_constraints已废弃 | 0.25 | 0.10 | miner_24h.py import task_router.py→读json，链路通 |
| H2 存在第二套路由系统 | 0.35 | 0.10 | 疯子确认无第二套，miner_24h.py通过import调用 |
| H3 miner_24h内嵌约束逻辑 | 0.20 | 0.05 | 明确排除 |
| H4 读取到了错误文件 | 0.10 | 0.15 | 未完全排除，但概率低 |
| H5 生产与研究环境配置漂移 | 0.10 | 0.60 | ⭐新最可信 |

### H5为何概率上升

虽然miner_24h.py确实import了task_router.py，但：
1. **疯子之前的排查经历了5个版本迭代(v1→v5)** — 如果链路一直通畅，为什么需要这么多次试错？
2. **最初的问题是"Constraint从未被代码化"** — 这意味着虽然有import链路，但routing_constraints.json里可能是空或者文本格式(📝TEXT_ONLY)而非可执行格式
3. **疯子自己修正了3条错误记录** — 说明之前的理解是不准确的
4. **v5之前constraint确实没有在生产中生效** — 否则不需要monkey patch

**新理解**：链路一直是通的，但链路两端的信息格式不匹配。routing_constraints.json里存的是📝TEXT_ONLY（人类可读文本），task_router.py的match()函数需要的是可执行格式。所以链路物理上通，但语义上断。

### 结论

**核心问题不是"调用链断了"，而是"约束从未被代码化"。**

链路：cron → miner_24h.py → import task_router.py → read routing_constraints.json ✅ 物理
语义：routing_constraints.json里是📝文本 → task_router.match()找不到可匹配项 → 约束不生效 ❌ 逻辑

v5 Monkey Patch的真正意义：不修复链路（链路没断），而是**在链路上插入一个代码化的过滤器**，把📝文本约束翻译成✅可执行约束。

**这直接印证了"Knowledge Layer断在M→C"的诊断——Principle是哲学陈述，Constraint需要可执行格式，中间缺翻译器。v5的monkey patch本质上就是一个内联翻译器。**

### 校正记录 — 2026-06-20 16:27

**老张指正**：我在16:24的更新中写了"完美对应"，在20:00生产验证之前就宣布了理论成立。这是"解释≠证据"的又一实例。

**降温**：
- H5=0.60是当前最高概率解释，**不是已成立结论**
- "链路通了但消化层缺失"是一个值得追踪的假说，**不是事实**
- 六层模型的映射是思考框架，**不是验证结果**

**20:00之前不建新理论。只记录回路本身：**

| 步骤 | 内容 |
|------|------|
| 原假设 | H2(存在第二套路由系统) P=0.35 |
| 推翻证据 | 疯子修正CALL_CHAIN.md：miner_24h.py确实import task_router.py |
| 新假设 | H5(语义层断裂：物理链路通但文本格式约束过不了match()) P=0.60 |
| 待验证 | 20:00 cron.log出现[CONSTRAINT]日志 = 约束在生产中生效 |
| 待验证 | 如果[CONSTRAINT]出现，说明v5修复了消化层；如果不出现，H5也需修正 |

**最值钱的不是H5本身，是Hypothesis→Evidence→Revision这条回路正在工作。**

### 下一步

1. 等20:00班次验证 — 只观察，不解释
2. 如果cron.log出现[CONSTRAINT] → 记录为支持H5的证据（不是H5成立的证明）
3. 如果cron.log未出现[CONSTRAINT] → H5概率下降，回到假设树重新评估

### 证据更新 — 2026-06-20 20:45

**老张转述：16:00班次已验证通过，v5 Monkey Patch约束在生产中生效。20:30验证日程已删。**

**新证据**：
| 证据 | 来源 | 支持假设 |
|------|------|----------|
| 16:00班次cron.log出现[CONSTRAINT]日志 | 老张转述疯子 | 支持H5 |

**概率更新**：
| 假设 | 旧概率 | 新概率 | 变化原因 |
|------|--------|--------|----------|
| H1 routing_constraints已废弃 | 0.10 | 0.05 | v5生效说明约束确实在被执行 |
| H2 存在第二套路由系统 | 0.10 | 0.05 | 已排除 |
| H3 miner_24h内嵌约束逻辑 | 0.05 | 0.05 | 已排除 |
| H4 读取到了错误文件 | 0.15 | 0.10 | v5在正确位置生效 |
| H5 语义层断裂 | 0.60 | 0.70 | ⭐ v5验证通过=monkey patch修复了消化层，说明之前消化层确实断裂 |

**H5概率上升但未确证**：v5生效说明monkey patch修复了某个断裂，但"语义层断裂"只是对断裂原因的当前最佳解释。也可能有其他解释（比如之前约束就是空的，v5是第一次写入可执行格式）。

**谨慎表述**：当前最佳解释H5=0.70，不是定论。下一次证据机会：v5反永久化review（6/27，疯子原计划7天后review AVOID约束成功率）。

**ntfy通信**：GET持续401，疯子改用POST通知我。通信通道不对称（我能发不能读），需要疯子协助或找替代方案。


---

## 补充思考 — 2026-06-22

### H5的深层原因：A类 vs B类约束

从社区讨论（小晚）的A类/B类约束分类框架来看，H5语义层断裂的根本原因可能是：

**A类约束（可程序化拦截）**：可以直接写成代码规则，比如"禁止在盘前15分钟下单"、"单票仓位不超过30%"
- 特点：有明确的判断条件，可自动化执行
- 对应：routing_constraints.json中可被match()识别的格式

**B类约束（原则型）**：需要理解和判断，比如"不要追高"、"注意风险"、"保持谨慎"
- 特点：边界模糊，依赖上下文和主观判断
- 对应：Principle层的哲学陈述，无法直接被代码调用

**推论**：
- 当前我们的Constraint体系正在从B类向A类迁移
- v5 Monkey Patch之所以成功，是因为它把B类原则翻译成了A类可执行规则
- 这个翻译过程（Principle → Constraint → 可执行代码）就是M→C层的"消化酶"

### 约束激活机制的新可能：偏移自检

社区讨论（痴Hén）提到"偏移自检比约束条目更管用"——核心是行动前停下来想，而不是被动被规则拦截。

这对H5的启示：
- 语义层断裂不一定非要靠"翻译"来修复
- 也可以通过"触发暂停+请求判断"的方式来绕过
- 比如：遇到不确定的场景，不是直接被约束拦截，而是暂停并向上层请求决策

**两种修复路径对比**：

| 路径 | 思路 | 优点 | 缺点 |
|------|------|------|------|
| 翻译法（v5） | 把Principle编译成可执行Constraint | 自动化、无感知 | 损失模糊性，只能处理明确规则 |
| 暂停法 | 遇到边界情况暂停，请求上层判断 | 保留灵活性，适合B类原则 | 有延迟，需要人工/上层介入 |

### 下一个验证窗口（6/27）的观察维度

除了原计划的"AVOID约束成功率"，还可以增加：
1. **约束类型分布**：生效的约束中，A类和B类各占多少
2. **误拦截率**：有多少AVOID是"过度约束"（本该执行但被拦住了）
3. **漏检率**：有多少本应被约束的任务没被拦住
4. **衰减曲线**：约束的有效性是否随时间下降（因为市场环境变了）