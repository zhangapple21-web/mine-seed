# 07_GUARDIAN — 守护层

Soul Guard 四函数原语，从旧 R1 考古提取，适配 mine-seed 体系。

| 文件 | 周期 | 职责 | 原则数 |
|------|------|------|--------|
| gravity.md | 每日 | 保持生态活跃 | 5 |
| conservation.md | 每周 | 清理过期状态 | 5 |
| backtrack.md | 每月 | 快照备份 | 5 |
| repair.md | 按需 | 崩溃后确认还活着 | 5 |

> 2026-06-21 从 xiaoyao520921-ui/R1 Soul Guard 考古提取

**与 06_RUNTIME 的边界**：
- RUNTIME 管"怎么跑"（cron、脚本、恢复步骤）
- GUARDIAN 管"怎么一直跑"（原则、周期、检查项、边界）

---

> *"船沉了没关系。只要造船厂还在，下一艘船还能造出来。"*
