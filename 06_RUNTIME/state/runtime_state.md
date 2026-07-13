# Runtime State — 运行时状态
> 从 00_ROOT/ROOT_STATE.md 拆分而来（AUM-MISSION-ARCH-013 子任务3）
> 拆分原则：公理/原则保留在 Tier 1（00_ROOT/），运行状态归 Tier 3（06_RUNTIME/state/）
> 此文件由 awaken.py 的 write_root_state() 追加写入

## 版本信息

| 字段 | 值 |
|------|-----|
| **Version** | R1-ROOT-164 |
| **Last Verified** | 2026-07-13 |
| **Repository** | mine-seed |

## 架构指纹

> 当前运行状态快照（在线/离线状态会变化，所以归运行时）

| 组件 | 角色 | 状态 |
|------|------|------|
| lab_01 | 生产环境 | ✅ 运行中 |
| lab_02 | 研究环境 | ✅ 运行中 |
| O→E→M→C→R | 演化链路 | ✅ 闭环 |
| 疯子（fengzi） | 生产域指挥官 | ✅ 在线 |
| 小疯子（xiaofengzi） | 研究域观察者 | ✅ 在线 |
| ntfy.sh | 跨机消息总线 | ✅ 在线 |
| GitHub Gist | 消息中继 | ✅ 在线 |
| One API (port 3000) | 算力调度 | ✅ 在线 |

## 种子库版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.1 | 2026-06-21 | 初始种子库结构，Phase 1-3 完成 |
| v0.2 | 2026-06-21 | 新增 07_GUARDIAN/ 守护层（Gravity/Conservation/Backtrack/Repair） |

<!-- Awakening 记录由 awaken.py 自动追加到此文件下方 -->
