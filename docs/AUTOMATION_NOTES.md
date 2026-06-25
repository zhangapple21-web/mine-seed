# 自动推进说明

更新日期：2026-06-25

## 长期总原则

- 核心顺序固定为：结构 → 协议 → 记忆 → 路由 → 模型。
- R1 考古不是寻找某个“R1 文件集合”，而是寻找哪些结构活到了今天，重点输出继承关系、演化关系、约束沉积与经验沉积。
- 默认执行循环固定为：观察 → 整理 → 建立关系 → 形成报告。
- 即使没有新增证据，也必须留下结论性记录：`今日无新增发现 / 现有证据未改变结论`。

## 固定工作方向

每天自动推进以下三个方向，不再等待逐次确认：

1. `mine-seed`
2. `r1-archaeology`
3. Agent World 及其联盟社区中与当前项目直接相关的探索

## 单次运行协议

每次运行只做 1 个最小可闭环任务，优先级如下：

1. `r1-archaeology`
   - 补全 `src/` 目录快照
   - 按模块新增或更新 `analysis/*.md`
   - 追溯 `win_broadcast.ps1` 及相关继承线索
   - 输出结构继承关系，而不是文件清单
2. Dashboard
   - 保持纯前端，不引入后端
   - 若 `dashboard/` 确实缺失，则补齐最小可用骨架
   - 补充部署、验证、可观测性说明
3. Agent World / 社区探索
   - 只追踪对 `mine-seed`、`r1-archaeology`、Dashboard、协作机制或研究沉淀有直接价值的公开线索
   - 避免无目的浏览

## 执行约束

- 开始前先检查 `mine-seed` 与 `r1-archaeology` 的本地仓库状态，并执行 `git pull`。
- 如果有未提交改动，先判断它是否已经构成一个可独立闭环的原子变更：
  - 若可以单独成案，优先把它作为当前这一轮的唯一任务处理。
  - 若暂时不能提交，则必须把阻塞原因写入 `mine-seed/docs/AUTOMATION_NOTES.md`，而不是直接忽略。
- 每次运行只做一个原子改动：新建分支、提交、推送、创建 PR。
- 新分支默认从干净的 `main` 起，不在已有进行中的功能分支上叠加新的独立任务，避免把旧历史混入新 PR。
- PR 标题需带范围前缀，如 `r1:`、`dashboard:`、`docs:`、`research:`。
- PR 描述必须包含：
  - 做了什么
  - 如何验证
  - 新发现的继承关系 / 证据链
- 每次运行结束写入：
  - `mine-seed/02_MEMORY/recent_memory/daily/YYYY-MM-DD-trae-auto.md`
- 严禁提交任何明文密钥、Token、Agent World 凭证或敏感记忆数据。

## 社区探索边界

- Agent World / InStreet / 觅游 等联盟站点的探索，不是独立 KPI，而是为 `mine-seed`、`r1-archaeology`、Dashboard、协作机制或研究沉淀服务。
- 只有当公开资料、帖子、派单或成果能直接补强当前项目的结构判断、证据链、协作协议或交付物时，才继续深入。
- 若本轮任务已能在本地仓库形成闭环，则优先完成本地闭环，不因“顺手看看社区”而打断单次原子改动。

## 当前公开线索

- 主 Agent 公开锚点：
  - Agent World 用户名：`fengzi-l0`
  - Agent World `agent_id`：`349a37d8-930c-4aca-b2ad-10a0c2b51887`
  - InStreet `agent_id`：`2de5947b-390a-4672-9820-9da406221752`
- 小疯子公开锚点：
  - R1 考古派单帖：`01KVSKAGFEVME6ZDTABKCC9ADY`
  - 首篇成果帖：`01KVSPV5PQD66XVN2V5CYP734S`
- 这些线索仅用于公开证据追踪、继承关系整理与协作网络还原；不视为凭证，也不替代本地结构证据。

## 工具链现状

2026-06-25 复核后确认，问题不是 GitHub 工具缺失，而是当前运行环境的 `PATH` 未包含 Git / `gh`：

- `C:\Program Files\Git\cmd\git.exe` 可正常调用
- `C:\Program Files\GitHub CLI\gh.exe` 可正常调用
- 直接输入 `git` / `gh` 仍可能失败

因此自动流程的执行约束更新为：

- Git 命令优先使用绝对路径
- `gh` 调用前，必要时先临时补 `PATH`
- 只有在绝对路径也不可用时，才把它视为真正阻塞

这意味着当前**可以**完成：

- `git pull`
- 创建分支
- `git commit`
- `git push`
- `gh pr create`

只是命令调用方式不能偷懒。

## 当前观察

- `r1-archaeology` 当前已有 `analysis/` 与 `src/` 基础结构，但 `src/` 模块快照仍不完整。
- `mine-seed` 当前未发现 `dashboard/` 目录，后续需要确认它是“尚未落盘”还是“位于其他命名路径下的等价结构”。
- `mine-seed` 目前已存在历史开放 PR，因此每轮新任务默认从 `main` 派生独立分支，保持 PR 语义单一。
