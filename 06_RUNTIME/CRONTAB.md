# CRONTAB 配置说明
> 种子库 — 系统骨架

---

## Cron 任务

```
# 矿场v5 — 每4小时
0 */4 * * * cd /home/coze && bash miner_cron.sh >> mine_output/cron.log 2>&1

# 信号发现 — 每6小时（2,6,10,14,18,22）
30 2,6,10,14,18,22 * * * cd /home/coze && bash signal_cron.sh >> mine_output/cron.log 2>&1

# 档案官 — 每天 20:04
4 20 * * * cd /home/coze && bash archivist_cron.sh >> mine_output/cron.log 2>&1

# 共享API保活 — 每分钟
* * * * * /home/coze/shared_api.py 保活监控 >> /dev/null 2>&1

# 跨机心跳 — 每小时
0 * * * * cd /home/coze && python3 lab_ntfy.py ping >> /dev/null 2>&1
```

## Coze Calendar 日程（非cron）

| 任务 | 时间 | 说明 |
|------|------|------|
| Stock Advisor | 开盘日 08:15 | 早盘建议推送 |
| Dragon Leader | 开盘日 09:30/13:30/14:50 | 龙头识别×3 |
| 矿场v5 | 每4h | 自动挖矿 |
| 信号发现 | 每6h | 信号轮询 |

## 重要说明

- 所有脚本假设运行在 `/home/coze/` 目录下
- cron日志统一写入 `mine_output/cron.log`
- 锁机制已在 `miner_cron.sh` 中实现
- @reboot 使用系统服务或进程保活替代
