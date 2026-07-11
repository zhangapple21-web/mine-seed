# MineField Dashboard

矿场状态监控面板，浏览器打开就能看。

## 数据接口

所有数据通过公网 API 实时获取，**无需本地搭后端，浏览器直连 fetch 即可**。

### 基准 URL
```
https://data-r1.shares.zrok.io
```

### 接口清单

| 接口 | 返回 | 用途 |
|------|------|------|
| `GET /status` | 整体状态（存活/死亡矿工、信号数、约束数、最后班次时间等） | 顶部门户指标 |
| `GET /mine/summary` | 最新班次结果（7个任务状态、耗时、军团统计） | 班次状态面板 |
| `GET /mine/workers` | 31名矿工完整画像（模型、军团、状态、成功率、延迟、长处短板） | Worker排行榜 |
| `GET /mine/observations` | 1181条观测总览 + 各worker统计（总数/成功/成功率）+ 最近500条 | 历史趋势 |
| `GET /mine/experience` | 经验池（约束、规则等） | 约束看板 |
| `GET /mine/fitness` | 适应度日志最新19条 | 健康度趋势 |
| `GET /shared/constraints` | 21条约束完整信息 | 约束详情 |
| `GET /shared/signals` | 17条信号因子 | 信号面板 |

所有接口均返回 JSON，已配置 `Access-Control-Allow-Origin: *`，前端直接 fetch 即可。

## 功能模块

### 1. 🟢 状态总览（顶部）
- 存活/死亡矿工数（25/31）
- 信号因子数（17）
- 约束规则数（21）
- 最后班次时间
- 最后信号发现时间
- 整体健康度（绿色/黄色/红色）

### 2. 📊 Worker排行榜
- 按成功率排序的矿工列表
- 每个矿工：worker_id、模型名、军团(GLM/NIM/GitHub)、状态(alive/dead)、成功率、平均延迟
- 颜色标识：绿=alive，灰=dead
- 可点击查看详情

### 3. ⚡ 最新班次
- 7个任务各自状态（✅/❌）
- 每个任务的耗时和执行worker
- 裁判层胜率（nim_mistral_675b 91%等）
- 军团利用统计

### 4. 📈 历史趋势
- 基于1181条观测的折线图
- 整体成功率趋势
- 各worker的效率走势
- 每日/班次维度的健康度变化

### 5. 🛡️ 约束看板
- 21条约束列表
- 状态：ACTIVE/PROBATION/PARDONED
- review时间
- 对应task/worker

### 6. ⚠️ 信号面板
- 17条信号因子列表
- 类别（momentum/quality等）
- IC值
- 最新ACCEPT状态

## 技术建议

**推荐方案：纯前端单页（一个HTML搞定）**
- HTML + CSS + JS，不用框架
- 图表用 ECharts CDN（`https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js`）
- 数据全部 fetch 公网API
- 深色主题，矿场风

**可选升级：**
- React/Vue + Vite（如果TRAE对框架支持更好）
- 分多个组件文件

**不做的：**
- ❌ 不加后端 （数据已通过公网API提供）
- ❌ 不加数据库
- ❌ 不加登录/auth
- ❌ 不搞SSR

## 开发步骤

1. 拉仓库：`git clone` mine-seed 仓库
2. 在 `dashboard/` 目录下开工
3. 写 `index.html`（或 React 项目）
4. 直接 `fetch('https://data-r1.shares.zrok.io/mine/summary')` 拿数据
5. 浏览器 `file://` 打开就能调试（CORS已开）
6. 开发完成后push到仓库

## 交付标准

- [ ] 单HTML文件（或纯前端工程），浏览器打开立即可用
- [ ] 6个模块完整实现
- [ ] 深色主题，视觉舒适
- [ ] 响应式，窗口缩小也能看
- [ ] 数据刷新机制（自动轮询/手动刷新）

## 数据示例

```json
GET /status
{
  "alive_count": 25,
  "dead_count": 6,
  "signal_count": 17,
  "last_mine_time": "21:06",
  "constraints": {...},
  "top_workers": [...]
}

GET /mine/summary
{
  "results": [
    {"task": "切片分类统计", "status": "✅", "file": "..."},
    {"task": "人格深度分析", "status": "✅", "file": "..."},
    ...
  ]
}
```
