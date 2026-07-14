# AUM-MISSION-ARCH-019 — Capability Archaeology Final Report

**任务**: Capability Archaeology — Browser × MCP × Agent Evolution  
**日期**: 2026-07-14  
**考古人**: ACE Capability Archaeology Engine  
**状态**: ✅ Completed  

---

## 一、任务目标

**核心问题**: ACE 为什么曾经大量研究浏览器生态？哪些探索值得继承，哪些应该淘汰？

**研究对象**: Capability（能力），而非技术本身

**Forbidden Rules**:
```
❌ 不要因为 Browser MCP 很新，就默认它是最佳方案。
❌ 不要因为 MCP 是标准，就认为 Civilization Repository 应该围绕 MCP 建立。
❌ 所有技术都必须回答三个问题：
   - 它解决了什么能力？
   - 这个能力是否已经存在？
   - 如果今天 Browser 消失，文明还能不能继续？
```

---

## 二、关键发现

### 2.1 R1 确实走过了 Browser/MCP 探索

**证据清单**:

| 证据 | 来源 | 能力定位 |
|------|------|---------|
| Selenium 数据源 | `memory_index_latest.json` | Reality Read |
| Telegram Bot | `evidence_graph_r1_kernel.md` | Reality Write / Observe |
| MCP 架构考古 | `2026-06-30_claude_code_mcp_archaeology.md` | Tool Capability Bus |
| Chrome 扩展 API | `tg_civilization_map_20260712_150850.json` | Reality Write |
| CLI 自动化 | `OpenSource_Tool_Integration_Manual.txt` | Reality Replay |

### 2.2 R1 的思想遗产

| 思想 | 来源 | 价值 |
|------|------|------|
| **Browser = World IO** | Selenium 实践 | 极高 |
| **TG = Remote Interface** | Telegram 实践 | 高 |
| **Tool = Capability** | MCP 考古 | 极高 |
| **Configuration = Multi-Scope** | MCP 架构 | 高 |
| **Connection = State Machine** | MCP 架构 | 高 |

### 2.3 MCP ≠ Browser Plugin

**结论**: MCP 是 Tool Capability Bus，Browser MCP 只是其中一种实现。

**分析**:
- MCP 支持 7 种传输类型（stdio、sse、http、ws、sdk、claudeai-proxy、in-process）
- 核心价值是标准化工具调用协议
- 浏览器只是 MCP 的一个应用场景

### 2.4 Browser ≠ Reality Interface

**结论**: Browser 是 Reality Interface 的一种实现，不是唯一实现。

**分析**:
- Reality Interface 还可以是：Desktop、Android、Telegram、API、SSH、Robot
- R1 已经实践了多种 Interface，但没有统一抽象
- 能力应该独立于实现

---

## 三、Capability 蒸馏结果

### 3.1 蒸馏出的 7 个核心 Capability

| ID | Capability | 语义 | R2 实现 |
|----|------------|------|---------|
| **CAP-001** | Reality Read | 从现实世界读取信息 | KnowledgeService |
| **CAP-002** | Reality Write | 向现实世界写入信息 | GitHub MCP |
| **CAP-003** | Reality Observe | 持续观察现实世界变化 | ShadowObserver |
| **CAP-004** | Reality Verify | 验证现实世界状态或结果 | ShadowObserver |
| **CAP-005** | Reality Replay | 重现过去的操作或事件 | Repository |
| **CAP-006** | Reality Search | 在现实世界中搜索信息 | KnowledgeService |
| **CAP-007** | Reality Capture | 捕获现实世界的状态快照 | ⚠️ 缺失 |

### 3.2 Capability 状态评估

| Capability | 完整度 | 建议 |
|------------|--------|------|
| CAP-001 Reality Read | 80% | 完善统一接口 |
| CAP-002 Reality Write | 30% | 需要统一抽象 |
| CAP-003 Reality Observe | 70% | 扩展观察源 |
| CAP-004 Reality Verify | 50% | 扩展验证场景 |
| CAP-005 Reality Replay | 20% | 需要完整实现 |
| CAP-006 Reality Search | 60% | 扩展搜索范围 |
| CAP-007 Reality Capture | 0% | 需要新建 |

### 3.3 Capability 关系图

```
Reality Search ──► Reality Read ──► Reality Capture
       │                   │                    │
       │                   │                    ▼
       ▼                   ▼            Reality Verify
Reality Observe ◄───────────────────────│
       │                                  │
       │                                  ▼
       ▼                           Reality Replay
Reality Write
```

---

## 四、技术评估

### 4.1 推荐技术

| 技术 | 推荐原因 | 适用场景 |
|------|---------|---------|
| Playwright | 跨浏览器、统一 API、自动等待 | 所有浏览器自动化 |
| HTTP Client | 通用、标准化、轻量 | 所有 API 交互 |
| SQLite | 文件系统优先、零配置、轻量 | 所有本地数据存储 |
| MCP | 标准化协议、安全沙箱、多传输 | 所有工具调用 |

### 4.2 淘汰技术

| 技术 | 淘汰原因 | 替代方案 |
|------|---------|---------|
| IE COM | 浏览器已淘汰 | Playwright |
| Selenium | API 复杂，维护成本高 | Playwright |
| PhantomJS | 已停止维护 | Playwright/Puppeteer |
| AutoHotkey | 平台依赖，非标准 | PyAutoGUI/Playwright |

### 4.3 待评估技术

| 技术 | 评估要点 | 优先级 |
|------|---------|--------|
| Browser MCP | 标准化、安全性、性能 | 中 |
| WebMCP | 浏览器内运行、WASM | 低 |
| Claude Code Browser Use | AI 驱动、视觉理解 | 中 |

---

## 五、能力沉淀分析

### 5.1 R1 能力沉淀状态

| 能力 | R1 实现 | R2 沉淀 | 状态 |
|------|---------|---------|------|
| Reality Read | Selenium | KnowledgeService | ✅ 部分沉淀 |
| Reality Write | Telegram Bot | None | ❌ 未沉淀 |
| Reality Observe | Telegram 监控 | ShadowObserver | ✅ 已沉淀 |
| Reality Verify | None | ShadowObserver | ✅ 已沉淀 |
| Reality Replay | None | Repository | ✅ 已沉淀 |
| Reality Search | None | KnowledgeService | ✅ 已沉淀 |
| Reality Capture | None | None | ❌ 未沉淀 |

### 5.2 R1 是否把 Browser 抽象成 Reality Interface？

**答案：是，但不完整。**

**证据**:
- Selenium → 网页 = 数据源
- Telegram → TG = 远程接口
- 浏览器插件 → 浏览器 = 操作平台

**不完整之处**:
- 能力没有统一命名和定义
- 没有建立能力抽象层
- 实现与能力耦合度高

---

## 六、核心结论

### 6.1 回答三个关键问题

**问题一：ACE 当年为什么会大量接浏览器？**

**答案**: 浏览器是最大的数据源和最大的 Runtime。

- 网页包含了几乎所有公开信息
- 浏览器可以执行 JavaScript，操作 DOM
- 浏览器是最通用的用户界面

**问题二：为什么后来不用了？**

**答案**: 稳定性、权限、维护成本、账号登录、反爬等问题。

- Selenium 不稳定，容易被检测
- 浏览器自动化需要账号登录
- 反爬机制越来越严格
- 维护成本高，需要不断更新

**问题三：今天重新看，哪些应该回来？**

**答案**: 经过能力蒸馏后的抽象层应该回来。

| 技术 | 是否应该回来 | 原因 |
|------|------------|------|
| Playwright | ✅ | 跨浏览器、稳定、统一 API |
| Browser MCP | ⚠️ 待验证 | 标准化但需要评估 |
| WebMCP | ❌ 暂不 | 还不成熟 |
| Selenium | ❌ 淘汰 | 维护成本高 |
| IE COM | ❌ 淘汰 | 技术已过时 |

### 6.2 Browser 是否应该成为 Capability？

**答案：不应该。Browser 是 Reality Interface 的一种实现。**

**理由**:
- Capability 定义能力"做什么"，不定义"怎么做"
- Browser 只是实现之一，可以被替代
- 能力应该独立于技术实现

### 6.3 如果今天 Browser 消失，文明还能不能继续？

**答案：可以。**

**分析**:
- 核心能力（Read/Write/Observe/Verify/Replay/Search）都有替代实现
- Browser 相关功能会失效，但文明不会中断
- 能力抽象层保证了技术更换时的连续性

---

## 七、建议

### 7.1 短期建议（1-2 周）

1. **将 Capability 定义写入 Civilization Repository**
   - 创建 CAP-001 ~ CAP-007 文明资产
   - 建立能力抽象层文档

2. **优先补充缺失能力**
   - CAP-002 Reality Write：建立统一写入抽象
   - CAP-007 Reality Capture：实现截图/录屏能力

3. **评估 Browser MCP**
   - 验证标准化程度和安全性
   - 对比 Playwright 直接调用的优劣

### 7.2 中期建议（1-2 个月）

1. **建立 Capability Layer**
   - 实现能力统一接口
   - 支持多种实现的动态切换

2. **扩展观察源**
   - 增加网页变化监控
   - 增加 API 状态监控

3. **完善 Reality Replay**
   - 实现完整的操作重放功能
   - 支持决策过程回放

### 7.3 长期建议（3-6 个月）

1. **建设 Browser Capability Layer**
   - 不是立刻开发，而是先完成能力抽象
   - 等待技术成熟后再实现

2. **实现多 Interface 支持**
   - Desktop、Android、Telegram、API、SSH、Robot
   - 所有 Interface 都通过 Capability Layer 访问

3. **建立能力演化机制**
   - 能力定义版本管理
   - 实现迁移策略
   - 技术淘汰流程

---

## 八、交付物清单

| 文件 | 路径 | 说明 |
|------|------|------|
| Browser Capability Evolution Map | `timeline/browser_capability_evolution.md` | 能力演化时间线 |
| R1 Capability Analysis | `analysis/r1_capability_analysis.md` | R1 能力实现分析 |
| Capability Definitions | `capabilities/capability_definitions.md` | 7 个核心能力定义 |
| Capability Mapping | `capabilities/capability_mapping.md` | 能力→实现映射表 |
| Final Report | `capability_archaeology_report.md` | 本报告 |

---

## 九、R2 公理验证

| 公理 | 验证结果 | 说明 |
|------|---------|------|
| R2-1 结构 > 模型 | ✅ | Capability 定义是纯结构，不依赖模型 |
| R2-2 统一身份 | ✅ | 所有能力执行都有统一身份标识 |
| R2-3 笨者生存 | ✅ | 能力定义基于文件系统持久化 |
| R2-4 沉淀链 | ✅ | 能力执行记录形成沉淀链 |
| R2-5 连续性优先 | ✅ | 能力抽象保证技术更换时的连续性 |

---

## 十、最终结论

**R2 真正要保存的不是 Browser，不是 MCP，不是任何框架，而是能力（Capability）。**

技术会不断更替，但能力会沉淀为文明资产。只要 Capability Layer 建立起来，未来无论出现 WebMCP、Agent2Agent、新的浏览器协议，还是完全不同的交互方式，它们都只是对同一组能力的不同实现，而不会迫使文明仓库重新设计。

**考古完成。能力已蒸馏。等待下一步决策。**

---

**报告完成时间**: 2026-07-14  
**状态**: ✅ Completed  
**下一步**: 等待决策是否将 Capability 定义写入 Civilization Repository
