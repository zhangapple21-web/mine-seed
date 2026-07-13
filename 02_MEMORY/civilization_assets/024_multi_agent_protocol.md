# Asset: Multi-Agent Protocol（多 Agent 协作协议）

**Name**: Multi-Agent Protocol（多 Agent 协作协议）

**Origin Repository**: r1-continuity-backup

**Purpose**: 定义多个智能体维护同一个知识仓库时的协作规则，防止知识分叉和重复劳动。

**Problem It Solves**: 多个 Agent 同时工作时，会出现"大家都觉得已经做了，但没人真的做"的情况，导致知识分叉、重复提交、状态不一致。

**Core Structure**:
- 核心原则：聊天记录不是长期存储，仓库才是事实来源（Source of Truth）
- 四条规则：决策必须落地 / 写入前必须检查 / 写入要可追溯 / 不允许"隐藏知识"
- Repository Health Check：5 项检查（已提交/已索引/已版本化/已交叉引用/可被发现）
- Repository Curator：单一同步入口，60 分钟防抖，本地优先

**Constraint**: 重要决策 24 小时内必须入库；写入前必须检查重复。

**Evidence**: r1-continuity-backup/governance/multi_agent_protocol.md

**Can Rebuild**: ✅ 80 行可重建——四条规则 + Health Check 函数 + Curator 接口

**Can Replace**: ✅ 规则可调整，核心原则不变

**Can Delete**: ⚠️ 删除会导致多 Agent 协作混乱，但单 Agent 场景不受影响

**Distillation**:

Multi-Agent Protocol 的核心洞察是"聊天是工作台，仓库是真相源"。在多 Agent 场景下，最危险的不是做得少，而是重复做和互相等待。四条规则层层设防：决策落地确保产出不丢失，写入前检查防止重复，可追溯确保责任清晰，不允许隐藏知识防止信息不对称。Repository Curator 的设计则解决了并发写入问题——单一入口 + 防抖 + 本地优先。这是多人（多 Agent）协作的基本法则。
