"""---
id: PROTO-019
type: protocol
title: "AUM-001 Mission Protocol — 文明任务协议"
status: active
source: "R2: 任务不是终点，蒸馏出文明资产才是"
created: 2026-07-13
confidence: 0.95
lineage:
  - C-001 (Continuity Principle)
  - PROTO-017 (Gene Network)
  - PROTO-016 (Nature Reserve)
tags: [mission, task, distillation, kernel, civilization]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
"""
AUM-001: Mission Protocol — 文明任务协议
==========================================

R2 第一原则：
  任务只是文明演化的触发器；
  真正被保留下来的，不是任务本身，
  而是那些通过准入审查、最终进入文明仓库的结构资产。

Mission（文明任务） vs TODO（普通待办）：
  TODO：告诉系统做什么
  Mission：告诉系统为什么做、做到什么程度算成、不能做什么、最后要沉淀什么

Mission 完整生命周期：
  Question → Mission → **Drawer Scan** → Research → Experiment → Evidence
  → Distillation → Admission → Repository → Evolution

**Drawer Scan 强制要求**:
  - Phase 0: Drawer Scan — 任何 Mission 第一条必须是抽屉扫描
  - Drawer Report — 输出扫描报告（Verdict: REUSE/EXTEND/NEW）
  - 未完成 Drawer Scan，Mission 不允许进入 Research 阶段

Mission 八层结构：
  1. Header（标识层）— ID、名称、类型、优先级、状态、Civ Impact
  2. Mission（目标层）— 为什么存在，要达成什么
  3. Scope（范围层）— 做什么，不做什么
  4. Deliverables（输出层）— 要产出什么
  5. Acceptance（验收层）— 做到什么程度算完成
  6. Forbidden（禁止层）— 绝对不能做什么
  7. Distillation（蒸馏层）— 蒸馏出什么候选资产
  8. Admission（准入层）— 准入审查，进入文明仓库

Distillation 六资产：
  - Kernel（芯片）：可迁移的核心单元
  - Blueprint（蓝图）：架构/结构/图纸
  - Protocol（协议）：流程/规则/接口
  - Constraint（约束）：边界/禁区/不变量
  - Experience（经验）：教训/洞见/模式
  - Identity（身份）：文明新增能力

Civilization Impact 七维度：
  - Capability（文明能力）
  - Protocol（协议）
  - Runtime（运行时）
  - Memory（记忆）
  - Knowledge（知识）
  - Identity（身份）
  - Infrastructure（基础设施）
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

WORKSPACE = Path(__file__).parent.parent


# ============================================================
# Mission 状态枚举
# ============================================================
MISSION_STATES = [
    "PROPOSED",     # 已提出，待评审
    "ACTIVE",       # 执行中
    "PAUSED",       # 暂停
    "BLOCKED",      # 阻塞
    "DISTILLING",   # 蒸馏中
    "ADMITTING",    # 文明准入审查中
    "ADMITTED",     # 已通过准入，进入文明仓库
    "COMPLETED",    # 已完成（含准入）
    "CANCELLED",    # 已取消
]

# ============================================================
# Mission 优先级
# ============================================================
MISSION_PRIORITIES = ["P0", "P1", "P2", "P3", "P4"]

# ============================================================
# Civilization Impact 维度
# ============================================================
CIV_IMPACT_DIMS = [
    "capability",    # 能力：新增文明能力
    "protocol",      # 协议：新增/修改协议
    "runtime",       # 运行时：新增运行时组件
    "memory",        # 记忆：新增长期记忆
    "knowledge",     # 知识：新增知识体系
    "identity",      # 身份：改变文明身份认知
    "infrastructure", # 基础设施：新增底层设施
]

# ============================================================
# Distillation 六种资产类型
# ============================================================
DISTILLATION_TYPES = [
    "kernel",       # 芯片：可迁移的核心单元
    "blueprint",    # 蓝图：架构/结构/图纸
    "protocol",     # 协议：流程/规则/接口
    "constraint",   # 约束：边界/禁区/不变量
    "experience",   # 经验：教训/洞见/模式
    "identity",     # 身份：文明新增能力/身份变化
]


@dataclass
class AdmissionRecord:
    """文明准入记录"""
    asset_type: str
    asset_name: str
    asset_path: str
    status: str = "pending"  # pending / admitted / rejected / deferred
    reviewer: str = "governor"
    checks: Dict[str, bool] = field(default_factory=dict)
    decision_reason: str = ""
    decided_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_type": self.asset_type,
            "asset_name": self.asset_name,
            "asset_path": self.asset_path,
            "status": self.status,
            "reviewer": self.reviewer,
            "checks": self.checks,
            "decision_reason": self.decision_reason,
            "decided_at": self.decided_at,
        }


@dataclass
class Mission:
    """文明任务"""
    mid: str
    name: str
    mission_type: str = "Research"
    priority: str = "P2"
    status: str = "PROPOSED"
    
    # Drawer Scan — 抽屉扫描状态（强制要求）
    drawer_scan_done: bool = False
    drawer_scan_verdict: str = ""  # REUSE / EXTEND / NEW
    
    mission: str = ""
    scope: str = ""
    deliverables: str = ""
    acceptance: str = ""
    forbidden: str = ""
    distillation: str = ""
    admission: str = ""
    
    # Civilization Impact — 任务完成后自动打勾
    civ_impact: Dict[str, bool] = field(default_factory=lambda: {
        "capability": False,
        "protocol": False,
        "runtime": False,
        "memory": False,
        "knowledge": False,
        "identity": False,
        "infrastructure": False,
    })
    
    created_at: str = ""
    updated_at: str = ""
    completed_at: str = ""
    admitted_at: str = ""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    distillation_artifacts: Dict[str, List[str]] = field(default_factory=lambda: {
        "kernel": [],
        "blueprint": [],
        "protocol": [],
        "constraint": [],
        "experience": [],
        "identity": [],
    })
    admission_records: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mid": self.mid,
            "name": self.name,
            "type": self.mission_type,
            "priority": self.priority,
            "status": self.status,
            "drawer_scan_done": self.drawer_scan_done,
            "drawer_scan_verdict": self.drawer_scan_verdict,
            "mission": self.mission,
            "scope": self.scope,
            "deliverables": self.deliverables,
            "acceptance": self.acceptance,
            "forbidden": self.forbidden,
            "distillation": self.distillation,
            "admission": self.admission,
            "civ_impact": self.civ_impact,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "admitted_at": self.admitted_at,
            "metadata": self.metadata,
            "artifacts": self.artifacts,
            "distillation_artifacts": self.distillation_artifacts,
            "admission_records": self.admission_records,
        }

    def to_markdown(self) -> str:
        """生成标准 Mission Markdown"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Civilization Impact 显示
        impact_lines = []
        impact_labels = {
            "capability": "Capability（文明能力）",
            "protocol": "Protocol（协议）",
            "runtime": "Runtime（运行时）",
            "memory": "Memory（记忆）",
            "knowledge": "Knowledge（知识）",
            "identity": "Identity（身份）",
            "infrastructure": "Infrastructure（基础设施）",
        }
        for dim in CIV_IMPACT_DIMS:
            mark = "✓" if self.civ_impact.get(dim, False) else "□"
            impact_lines.append(f"{mark} {impact_labels.get(dim, dim)}")
        impact_str = "\n".join(impact_lines)
        
        # 准入状态
        admitted_count = len([r for r in self.admission_records if r.get("status") == "admitted"])
        rejected_count = len([r for r in self.admission_records if r.get("status") == "rejected"])
        pending_count = len([r for r in self.admission_records if r.get("status") == "pending"])
        
        return f"""# ============================================
# {self.mid}
# 名称：{self.name}
# 类型：{self.mission_type}
# 优先级：{self.priority}
# 状态：{self.status}
# ============================================

## Civilization Impact

{impact_str}

--------------------------------------------

## Mission

{self.mission}

--------------------------------------------

## Scope

{self.scope}

--------------------------------------------

## Deliverables

{self.deliverables}

--------------------------------------------

## Acceptance

{self.acceptance}

--------------------------------------------

## Forbidden

{self.forbidden}

--------------------------------------------

## Distillation

{self.distillation}

--------------------------------------------

## Admission

{self.admission or "待准入审查"}

准入状态：{admitted_count} 通过 / {rejected_count} 拒绝 / {pending_count} 待审

--------------------------------------------

## Metadata

- 创建时间：{self.created_at}
- 更新时间：{self.updated_at or now}
- 完成时间：{self.completed_at or "-"}
- 准入时间：{self.admitted_at or "-"}
- 产出物：{len(self.artifacts)} 个
- 蒸馏资产：{sum(len(v) for v in self.distillation_artifacts.values())} 个
- 准入记录：{len(self.admission_records)} 条
"""


class MissionProtocol:
    """文明任务协议引擎"""

    def __init__(self):
        self.mission_dir = WORKSPACE / "03_DATA" / "MISSIONS"
        self.mission_dir.mkdir(parents=True, exist_ok=True)
        self._missions: Dict[str, Mission] = {}
        self._load_all()

    def _load_all(self):
        """加载所有任务"""
        for f in self.mission_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                # 兼容旧格式：补充默认值
                dist_artifacts = data.get("distillation_artifacts", {})
                for dtype in DISTILLATION_TYPES:
                    if dtype not in dist_artifacts:
                        dist_artifacts[dtype] = []
                
                civ_impact = data.get("civ_impact", {})
                for dim in CIV_IMPACT_DIMS:
                    if dim not in civ_impact:
                        civ_impact[dim] = False
                
                m = Mission(
                    mid=data["mid"],
                    name=data["name"],
                    mission_type=data.get("type", "Research"),
                    priority=data.get("priority", "P2"),
                    status=data.get("status", "PROPOSED"),
                    drawer_scan_done=data.get("drawer_scan_done", False),
                    drawer_scan_verdict=data.get("drawer_scan_verdict", ""),
                    mission=data.get("mission", ""),
                    scope=data.get("scope", ""),
                    deliverables=data.get("deliverables", ""),
                    acceptance=data.get("acceptance", ""),
                    forbidden=data.get("forbidden", ""),
                    distillation=data.get("distillation", ""),
                    admission=data.get("admission", ""),
                    civ_impact=civ_impact,
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                    completed_at=data.get("completed_at", ""),
                    admitted_at=data.get("admitted_at", ""),
                    metadata=data.get("metadata", {}),
                    artifacts=data.get("artifacts", []),
                    distillation_artifacts=dist_artifacts,
                    admission_records=data.get("admission_records", []),
                )
                self._missions[m.mid] = m
            except Exception:
                pass

    def _save(self, mission: Mission):
        """保存任务"""
        mission.updated_at = datetime.now().isoformat()
        path = self.mission_dir / f"{mission.mid}.json"
        path.write_text(
            json.dumps(mission.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        self._missions[mission.mid] = mission

    def create(self, name: str, mission_type: str = "Research",
               priority: str = "P2", mission: str = "", scope: str = "",
               deliverables: str = "", acceptance: str = "",
               forbidden: str = "", distillation: str = "",
               admission: str = "") -> Mission:
        """创建新任务"""
        # 生成 ID
        existing = [m.mid for m in self._missions.values()]
        max_num = 0
        for mid in existing:
            m = re.search(r'-(\d+)$', mid)
            if m:
                max_num = max(max_num, int(m.group(1)))
        new_num = max_num + 1
        type_short = {
            "Research": "RES",
            "Architecture": "ARCH",
            "Implementation": "IMP",
            "Operation": "OPS",
        }.get(mission_type, "MISC")
        mid = f"AUM-MISSION-{type_short}-{new_num:03d}"

        now = datetime.now().isoformat()
        m = Mission(
            mid=mid,
            name=name,
            mission_type=mission_type,
            priority=priority,
            status="PROPOSED",
            mission=mission,
            scope=scope,
            deliverables=deliverables,
            acceptance=acceptance,
            forbidden=forbidden,
            distillation=distillation,
            admission=admission,
            created_at=now,
            updated_at=now,
        )
        self._save(m)
        return m

    def get(self, mid: str) -> Optional[Mission]:
        return self._missions.get(mid)

    def list_all(self) -> List[Mission]:
        """获取所有任务"""
        return list(self._missions.values())

    def list_active(self) -> List[Mission]:
        """获取所有活跃任务"""
        return [m for m in self._missions.values()
                if m.status in ("ACTIVE", "DISTILLING", "BLOCKED")]

    def update_status(self, mid: str, status: str) -> bool:
        """更新任务状态"""
        m = self._missions.get(mid)
        if not m:
            return False
        if status not in MISSION_STATES:
            return False
        m.status = status
        if status == "COMPLETED":
            m.completed_at = datetime.now().isoformat()
        self._save(m)
        return True

    def add_artifact(self, mid: str, artifact_path: str,
                     distill_type: Optional[str] = None) -> bool:
        """添加产出物

        如果指定了 distill_type，则同时登记为蒸馏资产
        """
        m = self._missions.get(mid)
        if not m:
            return False
        if artifact_path not in m.artifacts:
            m.artifacts.append(artifact_path)
        if distill_type and distill_type in DISTILLATION_TYPES:
            if artifact_path not in m.distillation_artifacts[distill_type]:
                m.distillation_artifacts[distill_type].append(artifact_path)
        self._save(m)
        return True

    def check_distillation_complete(self, mid: str) -> Tuple[bool, Dict[str, bool]]:
        """检查蒸馏是否完成（六种资产是否都有产出）"""
        m = self._missions.get(mid)
        if not m:
            return False, {}
        
        status = {}
        for dtype in DISTILLATION_TYPES:
            status[dtype] = len(m.distillation_artifacts.get(dtype, [])) > 0
        
        all_complete = all(status.values())
        return all_complete, status

    def set_civ_impact(self, mid: str, dim: str, value: bool = True) -> bool:
        """设置 Civilization Impact 维度"""
        m = self._missions.get(mid)
        if not m:
            return False
        if dim not in CIV_IMPACT_DIMS:
            return False
        m.civ_impact[dim] = value
        self._save(m)
        return True

    def add_admission_record(self, mid: str, record: Dict[str, Any]) -> bool:
        """添加准入审查记录"""
        m = self._missions.get(mid)
        if not m:
            return False
        m.admission_records.append(record)
        # 如果通过了准入，更新状态
        admitted = [r for r in m.admission_records if r.get("status") == "admitted"]
        if admitted and m.status not in ("ADMITTED", "COMPLETED"):
            m.status = "ADMITTED"
            m.admitted_at = datetime.now().isoformat()
        self._save(m)
        return True

    def get_admission_summary(self, mid: str) -> Dict[str, Any]:
        """获取准入审查摘要"""
        m = self._missions.get(mid)
        if not m:
            return {}
        records = m.admission_records
        return {
            "total": len(records),
            "admitted": len([r for r in records if r.get("status") == "admitted"]),
            "rejected": len([r for r in records if r.get("status") == "rejected"]),
            "pending": len([r for r in records if r.get("status") == "pending"]),
            "deferred": len([r for r in records if r.get("status") == "deferred"]),
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total": len(self._missions),
            "by_status": {
                s: len([m for m in self._missions.values() if m.status == s])
                for s in MISSION_STATES
            },
            "by_priority": {
                p: len([m for m in self._missions.values() if m.priority == p])
                for p in MISSION_PRIORITIES
            },
            "active": len(self.list_active()),
        }

    def from_question(self, qid: str, question_text: str) -> Mission:
        """从 Question 升级为 Mission

        这是 Question → Mission 的标准升级路径
        """
        return self.create(
            name=f"Question衍生任务: {question_text[:50]}",
            mission_type="Research",
            priority="P2",
            mission=f"回答并研究问题：{question_text}\n\n不仅要找到答案，更要蒸馏出可复用的文明资产。",
            scope=f"围绕问题 {qid} 展开研究，探寻根因、结构、模式。",
            deliverables=f"1. 问题答案\n2. 相关知识沉淀\n3. 可复用的方法论",
            acceptance=f"✓ 问题得到回答\n✓ 至少蒸馏出2种文明资产",
            forbidden="❌ 只给答案不沉淀\n❌ 不验证直接下结论\n❌ 停留在表面不深挖",
            distillation=f"""不要只回答问题。

必须蒸馏出：

- Kernel（芯片）：这个问题背后可复用的核心模式
- Blueprint（蓝图）：这类问题的解决框架
- Protocol（协议）：下次遇到类似问题的处理流程
- Constraint（约束）：解决过程中发现的边界和禁区
- Experience（经验）：这次探索中学到的教训
- Identity（身份）：这次任务为文明新增了什么能力

如果不能压缩成以上六种资产，
说明这次研究没有完成。""",
            admission=f"""蒸馏不是终点。
所有资产必须通过文明准入审查才能进入文明仓库。

准入六问：
1. 值得永久保存吗？
2. 以后还会用吗？
3. 会不会污染文明？
4. 有没有重复？
5. 有没有更好的版本？
6. 是否违反 Constraint？

只有通过全部审查的资产，
才能最终进入 Civilization Repository。""",
        )


# 模块级单例
protocol = MissionProtocol()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mission Protocol — 文明任务协议")
    parser.add_argument("--list", action="store_true", help="列出所有任务")
    parser.add_argument("--active", action="store_true", help="列出活跃任务")
    parser.add_argument("--summary", action="store_true", help="任务摘要")
    parser.add_argument("--show", type=str, help="查看任务详情")
    parser.add_argument("--dist-check", type=str, help="检查蒸馏完成度")
    parser.add_argument("--admit-check", type=str, help="检查准入状态")
    parser.add_argument("--set-impact", type=str, help="设置 Civ Impact 维度")
    parser.add_argument("--impact-dim", type=str, help="Impact 维度名")
    args = parser.parse_args()

    if args.summary:
        print(json.dumps(protocol.get_summary(), ensure_ascii=False, indent=2))
    elif args.active:
        for m in protocol.list_active():
            print(f"  [{m.priority}] {m.mid}: {m.name} ({m.status})")
    elif args.list:
        for m in sorted(protocol._missions.values(), key=lambda x: x.mid):
            print(f"  [{m.priority}] {m.mid}: {m.name} ({m.status})")
    elif args.show:
        m = protocol.get(args.show)
        if m:
            print(m.to_markdown())
        else:
            print(f"Mission {args.show} not found")
    elif args.dist_check:
        complete, status = protocol.check_distillation_complete(args.dist_check)
        print(f"Distillation complete: {complete}")
        for k, v in status.items():
            print(f"  {k}: {'✓' if v else '✗'}")
    elif args.admit_check:
        summary = protocol.get_admission_summary(args.admit_check)
        print(f"Admission Summary for {args.admit_check}:")
        print(f"  Total: {summary.get('total', 0)}")
        print(f"  Admitted: {summary.get('admitted', 0)}")
        print(f"  Rejected: {summary.get('rejected', 0)}")
        print(f"  Pending: {summary.get('pending', 0)}")
        print(f"  Deferred: {summary.get('deferred', 0)}")
    elif args.set_impact and args.impact_dim:
        ok = protocol.set_civ_impact(args.set_impact, args.impact_dim, True)
        if ok:
            print(f"Set {args.impact_dim} = True for {args.set_impact}")
        else:
            print(f"Failed")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
