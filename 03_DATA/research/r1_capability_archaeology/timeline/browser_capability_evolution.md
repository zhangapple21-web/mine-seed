# Browser Capability Evolution Map

**考古日期**: 2026-07-14  
**考古人**: ACE Capability Archaeology Engine  
**任务**: AUM-MISSION-ARCH-019 — Capability Archaeology

---

## 一、能力演化时间线（1995~2026）

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          BROWSER CAPABILITY EVOLUTION                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1995  ── IE COM ────────────────────────────────────────────────────────────►│
│          │                                                                      │
│          │ 能力: DOM 读取 + ActiveX 控件调用                                     │
│          │ 思想: 浏览器 = 操作系统扩展                                           │
│          ▼                                                                      │
│  2004  ── Selenium 1.0 ─────────────────────────────────────────────────────►│
│          │                                                                      │
│          │ 能力: 网页自动化 + 多浏览器支持 + 测试框架                            │
│          │ 思想: Browser = Test Automation Platform                            │
│          ▼                                                                      │
│  2011  ── Chrome DevTools Protocol (CDP) ──────────────────────────────────►│
│          │                                                                      │
│          │ 能力: 协议级控制 + 性能分析 + 调试器                                  │
│          │ 思想: Browser = Remote Control Target                              │
│          ▼                                                                      │
│  2015  ── Puppeteer ─────────────────────────────────────────────────────────►│
│          │                                                                      │
│          │ 能力: Headless 模式 + 截图 + PDF + 页面交互                          │
│          │ 思想: Browser = Programmable Renderer                             │
│          ▼                                                                      │
│  2020  ── Playwright ─────────────────────────────────────────────────────────►│
│          │                                                                      │
│          │ 能力: 跨浏览器统一 API + 自动等待 + 网络拦截                          │
│          │ 思想: Browser = Consistent Automation Interface                    │
│          ▼                                                                      │
│  2023  ── Claude Code Browser Use ──────────────────────────────────────────►│
│          │                                                                      │
│          │ 能力: AI 驱动的浏览器操作 + 视觉理解 + 任务级指令                    │
│          │ 思想: Browser = Reality Interface                                 │
│          ▼                                                                      │
│  2025  ── MCP (Model Context Protocol) ─────────────────────────────────────►│
│          │                                                                      │
│          │ 能力: 标准工具调用协议 + 多传输支持 + OAuth 认证                      │
│          │ 思想: Tool = Capability Bus                                        │
│          ▼                                                                      │
│  2026  ── WebMCP ───────────────────────────────────────────────────────────►│
│          │                                                                      │
│          │ 能力: 浏览器内运行 MCP + WASM 插件 + 无服务器                        │
│          │ 思想: Browser = Capability Runtime                                 │
│          ▼                                                                      │
│  未来   ── Capability Layer ─────────────────────────────────────────────────►│
│                                                                                 │
│          能力: Reality Read / Reality Write / Reality Observe / Verify / Replay │
│          思想: Capability = Abstraction, Browser = Implementation              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、能力阶段详解

### 阶段 1：网页读取（1995~2004）

| 技术 | 能力边界 | 思想沉淀 |
|------|---------|---------|
| IE COM | DOM 读取、ActiveX 控件 | 浏览器 = 操作系统扩展 |
| HTTP 客户端 | 网页内容抓取 | 网页 = 数据源 |

### 阶段 2：DOM 控制（2004~2011）

| 技术 | 能力边界 | 思想沉淀 |
|------|---------|---------|
| Selenium 1.0 | 元素定位、表单填写、点击 | Browser = Test Automation |
| Greasemonkey/Tampermonkey | 页面脚本注入 | Web = Programmable |

### 阶段 3：自动化（2011~2015）

| 技术 | 能力边界 | 思想沉淀 |
|------|---------|---------|
| CDP | 协议级控制、性能分析、调试 | Browser = Remote Target |
| PhantomJS | Headless 渲染 | Browser = Engine |

### 阶段 4：Browser Automation（2015~2020）

| 技术 | 能力边界 | 思想沉淀 |
|------|---------|---------|
| Puppeteer | Headless、截图、PDF、网络拦截 | Browser = Programmable Renderer |
| Selenium WebDriver | 标准化 Web 自动化 API | Automation = Standardized |

### 阶段 5：Playwright（2020~2023）

| 技术 | 能力边界 | 思想沉淀 |
|------|---------|---------|
| Playwright | 跨浏览器、自动等待、录制 | Browser = Consistent Interface |

### 阶段 6：AI 驱动（2023~2025）

| 技术 | 能力边界 | 思想沉淀 |
|------|---------|---------|
| Claude Code Browser Use | AI 视觉理解、任务级操作 | Browser = Reality Interface |
| Browser MCP | 标准工具协议、安全沙箱 | Tool = Protocol |

### 阶段 7：能力总线（2025~ ）

| 技术 | 能力边界 | 思想沉淀 |
|------|---------|---------|
| MCP | 多传输、OAuth、权限控制 | Tool = Capability Bus |
| WebMCP | 浏览器内运行、WASM | Browser = Runtime |
| Capability Layer | 能力抽象、实现无关 | Capability = Abstraction |

---

## 三、能力抽象层级

```
┌──────────────────────────────────────────────────────┐
│                 Capability Layer                      │
│  Reality Read / Reality Write / Reality Observe       │
│  Reality Verify / Reality Replay / Reality Search     │
│  Reality Capture                                     │
├──────────────────────────────────────────────────────┤
│                 Interface Layer                       │
│  Browser / Desktop / Android / Telegram / API / SSH  │
│  MCP / Robot                                         │
├──────────────────────────────────────────────────────┤
│                 Implementation Layer                  │
│  Playwright / Selenium / Puppeteer / CDP / MCP       │
│  HTTP / WebSocket / stdio                            │
└──────────────────────────────────────────────────────┘
```

---

**报告完成时间**: 2026-07-14  
**状态**: Draft
