# 避免平滑消失原则（ACE 底层原则）

**定义**：
平滑消失 = 某个结构、决策、演化阶段被删除/覆盖后，从根上消失、无人知晓、无法追溯。

**ACE 的目标**：
不是"保存一切"，而是"不让任何东西从根上消失"。

---

## ACE 已有的防平滑消失机制

| 机制 | 作用 | 位置 |
|------|------|------|
| **graveyard/** | 被删除结构的坟墓，记录存在证据 | memory/graveyard/ |
| **backup/** | 被覆盖数据的快照备份 | memory/lexicon_backup_* |
| **lineage.py** | 结构的演化血缘，记录"从哪来、到哪去" | core/lineage.py |
| **08_ARCHAEOLOGY/** | 考古报告，记录演化阶段和决策理由 | 08_ARCHAEOLOGY/*.md |
| **mengpo_auto_records.jsonl** | 孟婆自动记录，每次删除都有日志 | memory/mengpo_auto_records.jsonl |
| **git history** | 代码的演化历史（如果项目在 git 下） | .git/ |

---

## 今日平滑消失风险检查

| 被删除的东西 | 风险等级 | 防护措施 |
|-------------|---------|---------|
| concept_miner.py v2 | 中（重写覆盖） | ✅ 已创建坟墓记录 |
| archaeology_report v1 | 低（升级替代） | ✅ 已创建坟墓记录 |
| 156个垃圾概念 | 低（清理删除） | ✅ 已有备份 lexicon_backup_before_cleanup_20260701.json |

---

## 每次删除必须做的事情（强制）

```
删除前：
  1. 创建备份（如果是数据）
  2. 记录删除理由

删除后：
  3. 在 graveyard/ 创建坟墓记录
  4. 填写：what_was_deleted、why_deleted、where_migrated、can_resurrect
  5. 如果是代码，用 git commit 保存旧版本

禁止：
  ❌ 无痕迹删除
  ❌ 无理由删除
  ❌ 无备份删除
  ❌ 无复活路径删除
```

---

## 墓碑格式（graveyard/*.json）

```json
{
  "graveyard_type": "结构类型",
  "deleted_at": "日期",
  "deleted_by": "删除者",
  "reason": "删除理由",
  "what_was_deleted": {
    "file": "文件路径",
    "version": "版本",
    "lines_count": "行数",
    "key_components": ["关键组件"]
  },
  "why_deleted": {
    "design_conflict": "设计冲突",
    "user_feedback": "用户反馈",
    "upgrade_goal": "升级目标"
  },
  "where_migrated": {
    "new_location": "新位置",
    "how_migrated": "如何迁移"
  },
  "can_resurrect": true/false,
  "resurrect_method": "复活方法",
  "archaeology_note": "考古说明（为什么这个东西永远存在）"
}
```

---

## 核心原则

> **任何一次删除、覆盖、断裂，都是在制造平滑消失。**
>
> **ACE 不会因为某个结构被替代而抹去它的存在证据。**
>
> **删除不是消失，是迁移到 graveyard。**
>
> **覆盖不是抹除，是留下快照。**
>
> **断裂不是遗忘，是被考古报告记录。**

---

## 文件位置

此原则文件：`mine-seed/04_CONSTRAINT/avoid_smooth_disappearance.md`
坟墓目录：`ace_runtime/06_RUNTIME/ace/data/memory/graveyard/`
备份目录：`ace_runtime/06_RUNTIME/ace/data/memory/lexicon_backup_*`
考古报告：`ace_runtime/08_ARCHAEOLOGY/*.md`