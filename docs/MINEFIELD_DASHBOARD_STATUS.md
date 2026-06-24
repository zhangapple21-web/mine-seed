# MineField Dashboard：交接与现状

这份文档用于把“MineField Dashboard”的**现状**和**待补齐项**固化下来，避免口头交接丢失。

## 同事描述的交付物（目前未在仓库中定位到）

你贴的项目总结里提到的这些产物，在当前 `mine-seed` 工作区里没有找到：

- `dashboard/index.html`
- `dashboard/app.js`
- `dashboard/styles.css`
- `minefield-dashboard.zip`

如果这些文件存在于云电脑/其他目录/其他分支，请后续补拷贝到仓库里（建议放到 `dashboard/` 或 `docs/dashboard/`）。

## 仓库里实际存在的“仪表盘”

`mine-seed` 当前已经内置了一个简易仪表盘页面：

- 入口实现：`04_PROTOCOLS/shared_api.py` 的 `build_dashboard()`  
- 路径：`/` 或 `/dashboard`  
- 刷新：页面内 `setTimeout(..., 30000)` 每 30 秒整页刷新  
- 形态：后端拼接 HTML（非 ECharts），用于快速概览状态/约束/事件/效率 TOP

它更像“运维观测页”，而不是你描述的那个“纯前端 + ECharts 的 6 模块监控面板”。

## 同事总结中提到的数据源（可作为目标口径）

同事总结里对外暴露的 API 入口口径如下（zrok share）：

- `https://data-r1.shares.zrok.io/mine/summary`
- `https://data-r1.shares.zrok.io/mine/observations`
- `https://data-r1.shares.zrok.io/mine/workers`
- `https://data-r1.shares.zrok.io/mine/experience`
- `https://data-r1.shares.zrok.io/mine/fitness`
- `https://data-r1.shares.zrok.io/shared/constraints`
- `https://data-r1.shares.zrok.io/shared/signals`
- （兼容）`https://data-r1.shares.zrok.io/status`

这份口径可以作为“前端大屏版 Dashboard”的目标接口合同。

## 建议的下一步（我会按这个方向维护）

1. **先把交付物找回来**：优先找到 `minefield-dashboard.zip` 或 `dashboard/` 三件套的真实位置，并提交到 `mine-seed`。
2. **明确两套 Dashboard 的定位**：
   - `shared_api.py` 的 `/dashboard`：保留为轻量运维页（不追求复杂图表）。
   - “纯前端 + ECharts”的 Dashboard：作为独立静态站点（可放 `dashboard/`，或单独子目录/子仓库）。
3. **补齐文档**：补 `dashboard/README.md`（启动方式、接口说明、截图/模块说明、刷新策略）。

