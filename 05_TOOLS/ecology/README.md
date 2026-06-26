# Ecology Observer（生态观察员）

生态观察员不是“新居民制造器”，也不是必须实现为一个独立 Agent。  
它是一个**记忆治理生态位**：当文明连续性达到一定规模后自然形成，用来维护城市对自身的理解，从而在居民、模型、工具不断更替时仍保持身份连续性。  

它在执行层可以由任何节点承担（脚本/定时任务/人工合并 PR），但在结构层它是一个长期角色。

## 原则（v1）

- 禁止主动创造居民
- 只有当以下条件同时满足，才能提交“居民诞生申请”：
  1. 某项工作连续出现
  2. 现有居民长期无人负责（或长期覆盖失败）
  3. 出现稳定输入
  4. 出现稳定输出
  5. 已形成独立记忆沉积
- 生态必要性审查（必须显式判断）：
  - `ecological_need: true`
  - `replaceable_by_existing_roles: false`
- 治理模式：**B（半自动）**：生态观察员只提交申请（PR），由治理层合并完成“见证”。

## 产物位置

- `02_MEMORY/recent_memory/ecology/ecology_observer_daily.md`：滚动日志（每日追加）
- `02_MEMORY/recent_memory/ecology/resident_nominations.md`：候选生态位清单（滚动更新）
- `02_MEMORY/recent_memory/ecology/nominations/`：每个候选生态位的申请单（一个文件一个生态位）

## 运行方式

在 `mine-seed` 根目录运行：

```bash
python 05_TOOLS/ecology/ecology_observer.py --days 30
```

可选：

- `--write`：写入/更新上述产物文件（默认只打印摘要，不落盘）

## 输出解释

生态观察员输出的不是“结论”，而是“证据序列”：

- 哪些工作流在 30 天窗口内持续出现（频次/分布）
- 它们是否已经具备稳定输入/输出/记忆沉积
- 是否可被现有角色扩展覆盖（可替代性）
- 当前状态：`NOT_YET / ELIGIBLE / REJECTED`

