# Capability Implementation Mapping

**考古日期**: 2026-07-14  
**考古人**: ACE Capability Archaeology Engine  
**任务**: AUM-MISSION-ARCH-019 — Capability Archaeology  

---

## 一、映射原则

### 1.1 核心原则

```
Capability = Abstraction
Implementation = Technology
```

| 原则 | 说明 |
|------|------|
| **一对多** | 一个 Capability 可以有多个实现 |
| **可替换** | 实现可以随时替换，不影响 Capability 定义 |
| **可扩展** | 新实现可以随时加入，不修改 Capability 定义 |
| **向后兼容** | 旧实现可以继续使用，逐步迁移到新实现 |

### 1.2 映射结构

```
Capability
    │
    ├── Browser Implementation
    │       ├── Playwright
    │       ├── Selenium
    │       ├── Puppeteer
    │       └── CDP
    │
    ├── API Implementation
    │       ├── HTTP
    │       ├── WebSocket
    │       ├── GraphQL
    │       └── gRPC
    │
    ├── Desktop Implementation
    │       ├── AutoHotkey
    │       ├── PyAutoGUI
    │       └── Robot Framework
    │
    ├── Messaging Implementation
    │       ├── Telegram
    │       ├── Discord
    │       └── Email
    │
    ├── MCP Implementation
    │       ├── Browser MCP
    │       ├── GitHub MCP
    │       └── Memory MCP
    │
    └── File System Implementation
            ├── Local Files
            ├── Cloud Storage
            └── Database
```

---

## 二、完整映射表

### CAP-001：Reality Read

| 实现类型 | 技术 | 状态 | 适用场景 | 备注 |
|----------|------|------|---------|------|
| Browser | Playwright | ⚠️ 待评估 | 复杂网页读取 | 推荐 |
| Browser | Selenium | ✅ 已验证 | 兼容性要求高 | R1 使用 |
| Browser | Puppeteer | ⚠️ 待评估 | Chrome 专用 | 轻量 |
| Browser | CDP | ⚠️ 待评估 | 协议级控制 | 底层 |
| API | HTTP Client | ✅ 已验证 | REST API | 通用 |
| API | GraphQL | ⚠️ 待评估 | 复杂查询 | 高效 |
| File System | Local Files | ✅ 已验证 | 本地文件读取 | 基础 |
| File System | Database | ✅ 已验证 | 结构化数据 | SQLite |
| MCP | Browser MCP | ⚠️ 待评估 | 标准化网页读取 | 新方案 |
| MCP | Memory MCP | ✅ 已验证 | 知识库读取 | 当前使用 |

### CAP-002：Reality Write

| 实现类型 | 技术 | 状态 | 适用场景 | 备注 |
|----------|------|------|---------|------|
| Browser | Playwright | ⚠️ 待评估 | 网页表单提交 | 推荐 |
| Browser | Selenium | ✅ 已验证 | 兼容性要求高 | R1 使用 |
| API | HTTP Client | ✅ 已验证 | REST API | 通用 |
| Desktop | AutoHotkey | ✅ 已验证 | Windows 自动化 | R1 使用 |
| Desktop | PyAutoGUI | ⚠️ 待评估 | 跨平台 | 备选 |
| Messaging | Telegram Bot | ✅ 已验证 | 消息发送 | R1 使用 |
| MCP | GitHub MCP | ✅ 已验证 | 文件写入 | 当前使用 |
| File System | Local Files | ✅ 已验证 | 本地文件写入 | 基础 |

### CAP-003：Reality Observe

| 实现类型 | 技术 | 状态 | 适用场景 | 备注 |
|----------|------|------|---------|------|
| Browser | Playwright | ⚠️ 待评估 | 网页变化监控 | 推荐 |
| Browser | CDP | ⚠️ 待评估 | 实时监控 | 底层 |
| Messaging | Telegram | ✅ 已验证 | 频道消息监控 | R1 使用 |
| File System | Watchdog | ✅ 已验证 | 文件变化监控 | 当前使用 |
| API | WebSocket | ✅ 已验证 | 实时数据推送 | 通用 |
| MCP | Browser MCP | ⚠️ 待评估 | 标准化监控 | 新方案 |
| Internal | ShadowObserver | ✅ 已验证 | 矿工观察 | R2 使用 |

### CAP-004：Reality Verify

| 实现类型 | 技术 | 状态 | 适用场景 | 备注 |
|----------|------|------|---------|------|
| Browser | Playwright | ⚠️ 待评估 | 网页内容验证 | 推荐 |
| Browser | Selenium | ✅ 已验证 | 兼容性要求高 | 备选 |
| API | HTTP Client | ✅ 已验证 | API 返回验证 | 通用 |
| Internal | ShadowObserver | ✅ 已验证 | 矿工输出验证 | R2 使用 |
| MCP | Browser MCP | ⚠️ 待评估 | 标准化验证 | 新方案 |

### CAP-005：Reality Replay

| 实现类型 | 技术 | 状态 | 适用场景 | 备注 |
|----------|------|------|---------|------|
| File System | Repository | ✅ 已验证 | 历史记录查询 | R2 使用 |
| API | HTTP Client | ⚠️ 待评估 | API 调用重放 | 备选 |
| Browser | Playwright | ⚠️ 待评估 | 网页操作重放 | 推荐 |
| Internal | Execution Log | ✅ 已验证 | 命令执行重放 | R2 使用 |

### CAP-006：Reality Search

| 实现类型 | 技术 | 状态 | 适用场景 | 备注 |
|----------|------|------|---------|------|
| Browser | Playwright | ⚠️ 待评估 | 网页搜索 | 推荐 |
| API | HTTP Client | ✅ 已验证 | API 搜索 | 通用 |
| File System | SQLite | ✅ 已验证 | 本地数据库搜索 | 当前使用 |
| MCP | Memory MCP | ✅ 已验证 | 知识库搜索 | 当前使用 |
| Internal | KnowledgeService | ✅ 已验证 | 文明资产搜索 | R2 使用 |

### CAP-007：Reality Capture

| 实现类型 | 技术 | 状态 | 适用场景 | 备注 |
|----------|------|------|---------|------|
| Browser | Playwright | ⚠️ 待评估 | 网页截图/录屏 | 推荐 |
| Browser | Puppeteer | ⚠️ 待评估 | 页面截图/PDF | 备选 |
| Desktop | PyAutoGUI | ⚠️ 待评估 | 屏幕截图 | 备选 |
| API | HTTP Client | ✅ 已验证 | 网络请求捕获 | 基础 |
| File System | Local Files | ✅ 已验证 | 日志捕获 | 基础 |

---

## 三、实现生命周期

### 3.1 实现状态定义

| 状态 | 说明 | 行动 |
|------|------|------|
| ✅ 已验证 | 经过测试，可生产使用 | 优先使用 |
| ⚠️ 待评估 | 需要进一步测试和评估 | 谨慎使用 |
| ❌ 淘汰 | 不再推荐使用 | 逐步迁移 |
| 📋 规划中 | 计划实现 | 等待 |

### 3.2 技术淘汰列表

| 技术 | 淘汰原因 | 替代方案 |
|------|---------|---------|
| IE COM | 浏览器已淘汰 | Playwright |
| Selenium | API 复杂，维护成本高 | Playwright |
| PhantomJS | 已停止维护 | Playwright/Puppeteer |
| AutoHotkey | 平台依赖，非标准 | PyAutoGUI/Playwright |

### 3.3 技术推荐列表

| 技术 | 推荐原因 | 适用场景 |
|------|---------|---------|
| Playwright | 跨浏览器、统一 API、自动等待 | 所有浏览器自动化场景 |
| HTTP Client | 通用、标准化、轻量 | 所有 API 交互场景 |
| SQLite | 文件系统优先、零配置、轻量 | 所有本地数据存储 |
| MCP | 标准化协议、安全沙箱、多传输 | 所有工具调用场景 |

---

## 四、关键决策记录

### 4.1 MCP 是否只是 Browser？

**结论：不是。**

MCP 是 Tool Capability Bus，Browser MCP 只是 MCP 的一种实现。

**证据：**
- MCP 支持 7 种传输类型（stdio、sse、http、ws、sdk、claudeai-proxy、in-process）
- Browser MCP 只是 HTTP/SSE 传输的一种应用
- MCP 的核心价值是标准化工具调用协议

### 4.2 Browser 是否应该成为 Capability？

**结论：不应该。**

Browser 是 Reality Interface 的一种实现，不应该成为 Capability 定义。

**证据：**
- Capability 定义是能力抽象，不依赖具体实现
- Browser 可以被 Desktop、API、MCP 等替代
- Capability 应该定义"做什么"，而不是"怎么做"

### 4.3 如果今天 Browser 消失，文明还能不能继续？

**结论：可以，但部分能力会降级。**

**分析：**
- Reality Read：可以通过 API、文件系统、数据库替代
- Reality Write：可以通过 API、文件系统、消息系统替代
- Reality Observe：可以通过 API、文件系统监控替代
- Reality Verify：可以通过 API、内部验证替代
- Reality Replay：可以通过 Repository 替代
- Reality Search：可以通过数据库、知识库替代
- Reality Capture：需要其他实现（如 Desktop 截图）

**影响：**
- 网页相关功能会失效
- 但核心能力不会丢失
- 文明可以继续演进

---

**报告完成时间**: 2026-07-14  
**状态**: Draft
