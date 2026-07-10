# CRONTAB 配置说明
> 种子库 — 系统骨架 | 最后更新: 2026-06-25

---

## Cron 任务（生产环境实际运行）

```bash
# 矿场v5 — 每4小时
0 */4 * * * cd /home/coze && bash miner_cron.sh >> mine_output/cron.log 2>&1

# 信号发现 — 每6小时（02:30,06:30,10:30,14:30,18:30,22:30）
30 2,6,10,14,18,22 * * * cd /home/coze && bash signal_cron.sh >> mine_output/signals/signal_cron.log 2>&1

# 档案官 — 每天 20:04
4 20 * * * cd /home/coze && bash archivist_cron.sh

# 共享API保活 — @reboot + 每分钟保活监控
@reboot cd /home/coze && python3 shared_api.py > shared_api.log 2>&1 &
* * * * * pgrep -f shared_api.py > /dev/null || (cd /home/coze && python3 shared_api.py > shared_api.log 2>&1 &)

# 跨机心跳 — 每小时
0 * * * * cd /home/coze && python3 lab_ntfy.py ping >> lab_ntfy.log 2>&1

# 隧道守护 — 每5分钟
*/5 * * * * /usr/local/bin/tunnel_guardian.sh >/dev/null 2>&1
```

## Coze Calendar 日程（非cron）

| 任务 | 频率 | 说明 |
|------|------|------|
| Stock Advisor | 开盘日 08:00/09:25/10:00 | 三时间窗策略 |
| Dragon Leader v2 | 每日 | 龙头识别双轨验证 |
| 矿场v5 | 每4h | 自动挖矿 |
| 信号发现 | 每6h | 信号轮询 |
| 矿工日报 | 每日21:30 | 记忆蒸馏 |
| TRAE巡逻 | 每日9:00 | 代码库PR/commit检查 |
| 种子归档 | 每日/每班次 | 同步运行时数据到仓库 |

## Windows 适配

本地工作区路径：`C:\Users\User\ace_workspace\mine-seed`

PowerShell 运行脚本位于 `06_RUNTIME/windows/`：

| 任务 | 脚本 | 配置方式 |
|------|------|----------|
| 矿场v5 | `run_miner.ps1` | Task Scheduler 每4小时 |
| 信号发现 | `run_signals.ps1` | Task Scheduler 每6小时 |
| 档案官 | `run_archivist.ps1` | Task Scheduler 每天 20:04 |
| 共享API保活 | `run_shared_api.ps1` | Task Scheduler 开机+每分钟 |
| 跨机心跳 | `run_heartbeat.ps1` | Task Scheduler 每小时 |

一键注册所有任务（管理员 PowerShell）：
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
. C:\Users\User\ace_workspace\mine-seed\06_RUNTIME\windows\setup_tasks.ps1
```

## 重要说明

- 所有脚本假设运行在 `/home/coze/` 目录下
- 矿场v5: 锁机制已在 `miner_cron.sh` 中实现
- 信号发现: 独立日志 `mine_output/signals/signal_cron.log`
- 共享API: 双保险（@reboot + 每分钟保活）
- 隧道守护: systemd Restart=always + crontab 5分钟兜底
- zrok service: 使用bash -c包装 → Restart=always必须（非on-failure）
