# 小疯子 lab_02 · 记忆体系规范

## 三层架构

### 长期层（换项目/换周期还成立）
| 文件 | 内容 | 上限 |
|------|------|------|
| 基础设定/SOUL.md | 身份、性格、铁律、核心定位 | 5KB |
| 基础设定/TOOLS.md | 工具使用经验（"用XX时要注意YY"） | 5KB |
| USER.md | 主人画像、偏好、关系 | 2KB |
| recent_memory/principles/ | 已验证的Principle（从pending升级） | 不限 |
| SECRET.md | 密钥、Token | 5KB |

### 短期层（和当前工作周期相关，1-4周有效）
| 文件 | 内容 | 上限 |
|------|------|------|
| MEMORY.md | 当前状态索引（只留摘要，详情指向文件） | 5KB |
| recent_memory/project/ | 项目进度快照 | 不限 |
| recent_memory/decision/ | 重要决策记录 | 不限 |
| recent_memory/daily/ | 每日总结 | 不限 |

### 临时层（当天/单次任务，不超过1周）
| 位置 | 内容 | 生命周期 |
|------|------|----------|
| 云端 /home/coze/research/daily_brief.md | 研究日报（验证/推翻/明天验证） | 隔天归档或丢弃 |
| 云端 /home/coze/research/observations/ | 观察记录 | 1周，提炼后进Principle或丢弃 |
| 云端 /home/coze/research/notes/ | 研究笔记 | 1周，提炼后归档 |
| tmp/ | 任务中间产物 | 用完即删 |

## 每日总结规范

### 什么时候写
每天最后一班结束前（大约20:00-21:00），自然完成，不需要提醒。

### 写什么
1. **今天做了什么** — 实际完成的，不是计划做的
2. **今天发现了什么** — Observation + 这说明什么（Meaning）
3. **明天做什么** — 具体到可执行
4. **未来可能发展** — 超过明天的方向性判断，允许模糊
5. **Principle候选** — 今天有没有新发现的

### 写在哪里
- `recent_memory/daily/YYYY-MM-DD.md`
- 更新 MEMORY.md 的"当前状态"部分（一句话摘要）
- 更新 recent_memory/index.json

### 判断标准
- 换项目还成立 → 长期层（SOUL/TOOLS/USER/Principle）
- 和当前工作相关但可能过时 → 短期层（MEMORY/project/decision/daily）
- 当天用完就扔 → 临时层（research/tmp）

### 归档规则
- Daily总结超过7天 → 检查是否有Principle可提炼，没有就丢弃
- Project完成 → 保留结论摘要到recent_memory/project/，删除过程细节
- Observation超过1周没升级 → 丢弃（说明不够重要）
