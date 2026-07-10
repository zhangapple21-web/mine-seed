# RFC-ENV-001: ACE Environment Layer

状态：DRAFT
日期：2026-07-10
依赖：OPS-005 (Self-Loop), GOV-001 (RoundTable), heartbeat.py

---

## 一、问题

ACE 当前是"被动响应"系统：用户输入 → 处理 → 输出。

heartbeat 每15分钟扫描本地文件，但：
- 不扫描外部环境（GitHub/PyPI/Internet）
- 不形成 Situation（今日态势报告）
- 不自动触发考古任务
- self_loop 的 discovery/candidate 步骤是空壳

## 二、目标

增加两个层：

```
Environment Layer (传感器)
    ↓
Perception Layer (态势构建)
    ↓
[现有] RoundTable → Task → Miner → Repository
```

使 ACE 能够：
1. 持续感知环境变化（本地 + GitHub + 模型 + 数据源）
2. 自动生成 Situation Report
3. 当发现与能力图谱相关的变化时，触发 RoundTable 审议
4. 无人参与，自动生成考古任务

## 三、架构

### 3.1 EnvironmentSensor

```python
class EnvironmentSensor:
    """环境传感器 — 持续感知环境变化"""

    def scan_local(self) -> list[Observation]:
        """扫描本地资产变更"""
        # git status / 文件修改时间 / 模块健康检查

    def scan_github(self) -> list[Observation]:
        """扫描 GitHub 环境变化"""
        # watch list 仓库的新 release/PR/Issue
        # trending 仓库

    def scan_models(self) -> list[Observation]:
        """扫描模型可用性"""
        # GitHub Models / OpenRouter 新增模型
        # 已有模型可用率

    def scan_providers(self) -> list[Observation]:
        """扫描数据源健康度"""
        # akshare/腾讯/东财 可用性检测

    def scan_all(self) -> list[Observation]:
        """全量扫描"""
        return self.scan_local() + self.scan_github() + self.scan_models() + self.scan_providers()
```

### 3.2 SituationBuilder

```python
class SituationBuilder:
    """态势构建器 — 将原始观察聚合成态势报告"""

    def build(self, observations: list[Observation]) -> Situation:
        """生成今日态势报告"""
        # 1. 去重（与上次扫描对比）
        # 2. 分类（local/github/model/provider）
        # 3. 评分（与能力图谱的相关度）
        # 4. 生成 Situation JSON
```

### 3.3 Observation 数据结构

```python
@dataclass
class Observation:
    source: str          # "local" | "github" | "model" | "provider"
    category: str        # "file_change" | "new_repo" | "new_model" | "provider_down"
    severity: str        # "info" | "warning" | "critical"
    title: str           # 简短描述
    detail: dict         # 详细信息
    capability_ref: str  # 关联的 ACE capability（如 "stock_data", "llm_inference"）
    timestamp: str       # ISO 时间
```

### 3.4 Situation 数据结构

```json
{
    "date": "2026-07-10",
    "summary": "发现3个值得关注的变化",
    "observations": [...],
    "high_priority": [...],
    "capability_gaps": ["event_bus", "risk_engine"],
    "recommended_actions": [
        {"action": "archaeology", "target": "vnpy/vnpy", "reason": "Gateway模式与Provider抽象相关"},
        {"action": "fix", "target": "dragon_leader_v2.py", "reason": "重复率40%"}
    ]
}
```

## 四、与现有系统集成

```
EnvironmentSensor.scan_all()
    ↓
SituationBuilder.build()
    ↓
Situation (JSON)
    ↓
RoundTable.roundtable(situation)  ← 已有
    ↓
Governor.check_invariant()        ← 已有
    ↓
Task System (自动生成考古任务)    ← 已有
    ↓
Miner.execute()                   ← 已有
    ↓
Repository (沉淀)                 ← 已有
```

## 五、扫描策略

| 传感器 | 频率 | 数据源 | 预算 |
|--------|------|--------|------|
| local | 每次 heartbeat (15min) | git status + 文件检查 | 0 |
| github | 每日1次 | GitHub API (trending + watch list) | 10 API calls |
| models | 每日1次 | GitHub Models API + OpenRouter API | 2 API calls |
| providers | 每次 heartbeat | akshare/腾讯/东财 健康检测 | 3 API calls |

## 六、实现计划

### Phase 1: 最小可用版本（本次）
- 实现 EnvironmentSensor（local + providers + github trending）
- 实现 SituationBuilder（去重 + 分类 + 生成报告）
- 输出 Situation JSON 到 02_MEMORY/environment/

### Phase 2: 接入 RoundTable
- Situation 中的 high_priority 项自动提交 RoundTable 审议
- RoundTable 输出 approved/rejected

### Phase 3: 自动任务生成
- approved 项自动生成考古任务
- 任务进入 Miner 队列

## 七、不做什么
- 不做网页爬虫（只用 API）
- 不做实时监控（频率最高15分钟）
- 不做 LLM 自动分析（Phase 1 纯规则）
- 不破坏现有 heartbeat/self_loop 代码
