# CONTRACT-001: Runtime-Civilization Interface Contract

> **Mission**: AUM-MISSION-ARCH-010
> **Created**: 2026-07-13
> **Source**: 028_ace_civilization_os.md — Runtime → Civilization (只读), Civilization ← Runtime (经 Admission)
> **Enforcer**: civilization_contract.py (PROTO-029)

---

## 1. 核心规则

| 规则 | 说明 |
|------|------|
| Runtime → Civilization | **只读**。Runtime 可以自由读取 Civilization 层的所有内容。 |
| Civilization ← Runtime | **写入必须经 Admission**。Runtime 产出要进入 Civilization 层，必须通过 Admission Engine 审查。 |
| 直接写入 = 违规 | 任何 Runtime 代码直接写 Civilization 受保护路径且未经 `can_write(path, via_admission=True)` 确认，即为契约违规。 |

---

## 2. Civilization 受保护路径范围

### Tier 1：严格文明区（任何写入都需 Admission）

| 路径 | 内容 | 写入方式 |
|------|------|---------|
| `00_ROOT/` | 公理、原则、宣言、治理架构等全部文件 | 仅经 Admission + Nature Reserve 双重检查 |
| `00_ROOT/PRINCIPLES.md` | R2 原则库（含 DFP-001） | 同上 |
| `00_ROOT/MANIFESTO.md` | 系统宣言 | 同上 |
| `00_ROOT/GOVERNANCE.md` | 治理架构 | 同上 |
| `00_ROOT/ARCHITECTURE.md` | 架构文档 | 同上 |
| `00_ROOT/ARCHITECTURE_REAL.md` | 实际架构 | 同上 |
| `00_ROOT/LETTER_TO_FUTURE_TRAE.md` | 致未来 TRAE 的信 | 同上 |
| `00_ROOT/LETTER_TO_RUNTIME.md` | 致 Runtime 的信 | 同上 |
| `00_ROOT/ROOT_STATE.md` | 根状态记录 | 同上 |
| `00_ROOT/AUTONOMOUS_LOOP_FRAMEWORK.md` | 自主循环框架 | 同上 |
| `00_ROOT/README.md` | 根目录说明 | 同上 |
| `02_MEMORY/civilization_assets/` | 28+ 个文明资产文档 | 仅经 Admission 审查 |
| `02_MEMORY/civilization_assets/001_provider_watchdog.md` | Provider Watchdog 资产 | 同上 |
| `02_MEMORY/civilization_assets/...` | 其余 27 个资产文档 | 同上 |
| `02_MEMORY/civilization_assets/ASSET_INDEX.md` | 资产索引 | 同上 |
| `02_MEMORY/lineage/` | 血缘索引和报告 | 仅经 Admission 审查 |
| `02_MEMORY/lineage/lineage_index.json` | 血缘索引文件 | 同上 |
| `02_MEMORY/lineage/L∞_lineage.md` | L∞ 演化报告 | 同上 |

### Tier 2：文明遗产区（可追加，修改已有内容需 Admission）

| 路径 | 内容 | 写入方式 |
|------|------|---------|
| `02_MEMORY/archaeology/` | 考古发现和证据 | 追加新文件允许；修改已有文件需 Admission |

### Tier 3：Runtime 运营区（自由读写，不需要 Admission）

| 路径 | 内容 | 说明 |
|------|------|------|
| `02_MEMORY/environment/` | 环境观测数据 | Runtime 运营数据 |
| `02_MEMORY/heartbeat/` | 心跳记录 | Runtime 运营数据 |
| `02_MEMORY/diary/` | 日记 | Runtime 运营数据 |
| `02_MEMORY/ops_logs/` | 运维日志 | Runtime 运营数据 |
| `02_MEMORY/self_loop/` | 自循环状态 | Runtime 运营数据 |
| `02_MEMORY/recovery/` | 恢复数据 | Runtime 运营数据 |
| `02_MEMORY/question_center/` | 问题中心 | Runtime 运营数据 |
| `02_MEMORY/advisor_tracker/` | 股票跟踪 | Runtime 运营数据 |
| `02_MEMORY/exploration/` | 探索报告 | Runtime 运营数据 |
| `02_MEMORY/civilization_audit/` | 审计记录 | Runtime 运营数据 |
| `02_MEMORY/experience/` | 经验记录 | Runtime 运营数据（追加模式） |
| `02_MEMORY/tg_sessions/` | TG 会话 | Runtime 运营数据 |
| **`06_RUNTIME/archaeology_workspace/`** | **考古暂存区** | **两阶段落盘：先写暂存区，经 Admission 后提升到 `02_MEMORY/archaeology/`** |
| `04_PROTOCOLS/` | Runtime 协议层 | Runtime 自有目录 |
| `03_DATA/` | 运行时数据 | Runtime 自有目录 |
| `05_TOOLS/` | 工具层 | Runtime 自有目录 |
| `06_RUNTIME/` | 运行时引擎 | Runtime 自有目录 |

---

## 3. 操作规则

### 3.1 Runtime 读取 Civilization

- **默认允许**。所有 `can_read()` 调用返回 `True`。
- 无需额外审批。
- 示例：`heartbeat.py` 读取 `00_ROOT/PRINCIPLES.md` — 合规。

### 3.2 Runtime 写入 Civilization

- **必须调用 `can_write(path, via_admission=True)`** 确认。
- `via_admission=True` 意味着写入经过了 Admission Engine 审查。
- `via_admission=False` 时，`can_write()` 返回 `False` 并记录违规。
- **不调用 `can_write()` 也是违规**（属于代码规范问题，无法自动检测，需代码审查发现）。

### 3.3 合法写入通道

| 通道 | 说明 |
|------|------|
| `AdmissionEngine.review_asset()` → `Repository.add()` → `RepositoryStore.save()` | 新资产准入的合法路径 |
| `Nature Reserve` 对 `00_ROOT/` 的基线更新 | 需人工确认 + `establish_baseline()` |

---

## 4. 违规记录方式

### 4.1 日志格式

违规写入通过 Python `logging` 模块记录，格式：

```
[CONTRACT-VIOLATION] {ISO8601时间戳} | caller={调用者} | path={目标路径} | operation=write | via_admission=False | zone={tier1/tier2}
```

### 4.2 违规记录结构

```json
{
  "timestamp": "2026-07-13T13:40:50.500830",
  "caller": "module_name",
  "path": "/absolute/path/to/file",
  "operation": "write",
  "via_admission": false,
  "zone": "tier1",
  "decision": "rejected"
}
```

### 4.3 查询方式

- `contract.get_violations()` — 获取当前会话的所有违规记录
- `python civilization_contract.py --violations` — 命令行查看
- `python civilization_contract.py --check <path>` — 查看路径所属区域

---

## 5. 与现有机制的关系

| 机制 | 与 Contract 的关系 |
|------|-------------------|
| **Nature Reserve** | Reserve 保护的是"不可变文件"（L1/L2/L3 列表），Contract 保护的是"写入通道"（不经 Admission 不可写）。Reserve 是文件级保护，Contract 是路径级保护。两者互补。 |
| **Admission Engine** | Admission 是写入 Civilization 的合法审查通道。Contract 检查 `via_admission` 标记来确认写入是否经过 Admission。 |
| **Governor** | Governor 检查删除和修改操作的合规性。Contract 检查写入操作的通道合规性。两者互补。 |

---

## 6. CONTRACT.md 放置位置说明

**CONTRACT.md 放在 `04_PROTOCOLS/` 下**，理由：

1. 契约检查是 Runtime 层职责（Runtime 负责执行边界检查）
2. 放在 `02_MEMORY/civilization_assets/` 会导致循环：契约文档自己写入 Civilization 受保护区需要自身授权
3. `04_PROTOCOLS/` 是所有 Runtime 协议的规范位置
4. 通过 `civilization_contract.py` 中的 `CIV_TIER1_PATHS` 和 `CIV_TIER2_PATHS` 定义，契约的约束范围已代码化，不依赖文档位置
