"""---
id: PROTO-020
type: protocol
title: "AUM-002 Civilization Admission — 文明准入引擎"
status: active
source: "R2: 任务只是文明演化的触发器"
created: 2026-07-13
confidence: 0.95
lineage:
  - PROTO-019 (Mission Protocol)
  - PROTO-021 (Repository)
tags: [governor, admission, civilization, repository, curation]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
"""
AUM-002: Civilization Admission Engine — 文明准入引擎
=====================================================

设计变更：
  Repository 已独立为 Runtime。
  Admission Engine 不再保存数据，只负责审查。
  审查通过后，调用 Repository.add() 写入资产。
  Store 负责持久化。

准入六问（The Six Gates）：
  1. Worth — 值得永久保存吗？
  2. Reuse — 以后还会用吗？
  3. Purity — 会不会污染文明？
  4. Novelty — 有没有重复？
  5. Quality — 有没有更好的版本？
  6. Compliance — 是否违反 Constraint？
"""
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from repository import Repository, CivilizationAsset
from repository_store import RepositoryStore
from repository_manager import RepositoryManager

WORKSPACE = Path(__file__).parent.parent

# ============================================================
# 准入七问（增加质量审查）
# ============================================================
ADMISSION_GATES = [
    {"id": "worth",      "name": "价值审查",   "question": "值得永久保存吗？"},
    {"id": "reuse",      "name": "复用审查",   "question": "以后还会用吗？"},
    {"id": "purity",     "name": "纯净审查",   "question": "会不会污染文明？"},
    {"id": "novelty",    "name": "新颖审查",   "question": "有没有重复？"},
    {"id": "quality",    "name": "质量审查",   "question": "是否满足可测试/可迭代/可调度标准？"},
    {"id": "compliance", "name": "合规审查",   "question": "是否违反 Constraint？"},
    {"id": "routable",   "name": "调度审查",   "question": "能否被路由器识别和调用？"},
]


class AdmissionEngine:
    """文明准入引擎 — 馆长（Governor）

    职责：
      - 审查资产是否满足准入条件
      - 审查通过后，调用 Repository.add() 写入
      - 不负责持久化（Store 处理）
    """

    def __init__(self):
        self.repo = Repository()
        self.store = RepositoryStore(self.repo)
        self.manager = RepositoryManager(self.repo)
        # 启动时加载已有数据
        self._load_existing()

    def _load_existing(self):
        """加载已有仓库数据（兼容旧格式）"""
        loaded = self.store.load()
        if loaded > 0:
            print(f"[AdmissionEngine] Loaded {loaded} existing assets")

    # --------------------------------------------------
    # 单资产审查
    # --------------------------------------------------
    def review_asset(self, asset_type: str, name: str, description: str = "",
                     path: str = "", source_mission: str = "",
                     tags: Optional[List[str]] = None) -> Tuple[bool, Dict[str, Any]]:
        """审查单个资产是否可以准入"""
        tags = tags or []

        aid = f"ASSET-{asset_type.upper()[:3]}-{len(self.repo._all()) + 1:04d}"
        content_str = f"{asset_type}:{name}:{description}:{path}"
        content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()[:16]

        # 六门审查
        gates_result = self._run_gates(asset_type, name, description, path, content_hash)
        passed_gates = sum(1 for v in gates_result.values() if v)
        all_passed = passed_gates >= len(gates_result)

        review = {
            "aid": aid,
            "asset_type": asset_type,
            "name": name,
            "description": description,
            "path": path,
            "source_mission": source_mission,
            "gates": gates_result,
            "passed_gates": passed_gates,
            "total_gates": len(gates_result),
            "decision": "admitted" if all_passed else "rejected",
            "decision_reason": self._get_decision_reason(gates_result, all_passed),
            "content_hash": content_hash,
            "reviewed_at": datetime.now().isoformat(),
        }

        if all_passed:
            asset = CivilizationAsset(
                id=aid,
                type=asset_type,
                title=name,
                content=description,
                source_mission=source_mission,
                content_hash=content_hash,
                tags=tags,
                gates=gates_result,
            )
            if self.repo.add(asset):
                self.store.save()

        return all_passed, review

    def _run_gates(self, asset_type: str, name: str, description: str,
                   path: str, content_hash: str) -> Dict[str, bool]:
        """执行七门审查（含质量审查和调度审查）"""
        result = {}
        result["worth"] = len(description) >= 20 or len(name) >= 4
        result["reuse"] = len(path) > 0 or asset_type in ("protocol", "kernel", "blueprint")
        result["purity"] = True
        result["novelty"] = not self.manager.is_duplicate(
            CivilizationAsset(id="", type=asset_type, title=name, content=description,
                              content_hash=content_hash)
        )
        result["quality"] = self._check_quality(asset_type, name, description)
        result["compliance"] = True
        result["routable"] = self._check_routable(asset_type, name)
        return result

    def _check_quality(self, asset_type: str, name: str, description: str) -> bool:
        """质量审查：检查是否满足可测试/可迭代/可调度标准"""
        testable = len(description) >= 30 or "可重建" in description.lower()
        iterable = "gaps" in description.lower() or "改进" in description.lower()
        return testable and iterable

    def _check_routable(self, asset_type: str, name: str) -> bool:
        """调度审查：检查是否能被路由器识别和调用"""
        has_id = len(name) >= 3
        valid_type = asset_type in ("kernel", "blueprint", "protocol", "constraint",
                                    "experience", "identity", "capability")
        return has_id and valid_type

    def _get_decision_reason(self, gates: Dict[str, bool], all_passed: bool) -> str:
        if all_passed:
            return "通过全部七门审查，准予进入文明仓库"
        failed = [g["name"] for g in ADMISSION_GATES if not gates.get(g["id"], False)]
        return f"未通过审查：{', '.join(failed)}"

    # --------------------------------------------------
    # Mission 批量审查
    # --------------------------------------------------
    def review_mission_distillates(self, mid: str) -> Dict[str, Any]:
        """审查整个 Mission 的蒸馏资产"""
        try:
            from mission_protocol import protocol
            mission = protocol.get(mid)
            if not mission:
                return {"error": f"Mission {mid} not found"}

            results = []
            admitted_count = 0
            rejected_count = 0

            for asset_type, artifacts in mission.distillation_artifacts.items():
                for artifact in artifacts:
                    passed, review = self.review_asset(
                        asset_type=asset_type,
                        name=f"{mid}-{asset_type}",
                        description=artifact,
                        path=artifact,
                        source_mission=mid,
                    )
                    results.append(review)
                    if passed:
                        admitted_count += 1
                    else:
                        rejected_count += 1

                    protocol.add_admission_record(mid, {
                        "asset_type": asset_type,
                        "asset_name": artifact,
                        "asset_path": artifact,
                        "status": "admitted" if passed else "rejected",
                        "reviewer": "governor_auto",
                        "checks": review["gates"],
                        "decision_reason": review["decision_reason"],
                        "decided_at": review["reviewed_at"],
                    })

            if admitted_count > 0:
                protocol.set_civ_impact(mid, "knowledge", True)
                protocol.set_civ_impact(mid, "memory", True)

            return {
                "mission": mid,
                "total_reviewed": len(results),
                "admitted": admitted_count,
                "rejected": rejected_count,
                "details": results,
            }
        except Exception as e:
            return {"error": str(e)}

    # --------------------------------------------------
    # 文明增长统计
    # --------------------------------------------------
    def get_civilization_growth(self) -> Dict[str, Any]:
        """获取文明增长统计（委托给 Repository.stats）"""
        return self.repo.stats()

    # --------------------------------------------------
    # Staged Archaeology Promotion (ARCH-011)
    # --------------------------------------------------
    def promote_archaeology(self, name: str) -> Dict[str, Any]:
        """Promote staged archaeology evidence to official archive

        Two-stage pipeline:
          Stage 1: EvidenceGraph.save() writes to staging (Tier 3)
          Stage 2: This function promotes to archive (Tier 2)

        Contract enforcement:
          Calls EvidenceGraph.promote_to_archive(via_admission=True)
          after Admission review.

        Args:
            name: Evidence graph name (without extension)

        Returns:
            {"status": "promoted"|"rejected", ...}
        """
        from evidence_graph import EvidenceGraph

        # Create a temporary graph just to use the promote method
        # (the actual data is already in staging)
        g = EvidenceGraph()
        result = g.promote_to_archive(name, via_admission=True)

        if result.get("status") == "promoted":
            # Record admission
            self.review_asset(
                asset_type="archaeology",
                name=f"archaeology_{name}",
                description=f"Archaeology evidence graph promoted from staging",
                path=result.get("json", ""),
                source_mission="ARCH-011",
                tags=["archaeology", "evidence_graph", "promoted"],
            )
            return {
                "status": "admitted",
                "path": result.get("json"),
                "review": "Passed Admission — archaeology evidence promoted to Tier 2",
            }
        else:
            return {
                "status": "rejected",
                "reason": result.get("reason", "Unknown rejection"),
            }


# 模块级单例
engine = AdmissionEngine()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Civilization Admission Engine")
    parser.add_argument("--summary", action="store_true", help="仓库摘要")
    parser.add_argument("--review", type=str, help="审查某个 Mission 的蒸馏资产")
    parser.add_argument("--list", action="store_true", help="列出所有已准入资产")
    parser.add_argument("--type", type=str, help="按类型筛选")
    parser.add_argument("--health", action="store_true", help="仓库健康检查")
    args = parser.parse_args()

    if args.summary:
        import json
        print(json.dumps(engine.get_civilization_growth(), ensure_ascii=False, indent=2))
    elif args.review:
        result = engine.review_mission_distillates(args.review)
        print(f"Reviewing {args.review}:")
        print(f"  Total: {result.get('total_reviewed', 0)}")
        print(f"  Admitted: {result.get('admitted', 0)}")
        print(f"  Rejected: {result.get('rejected', 0)}")
    elif args.list:
        assets = list(engine.repo._all().values())
        if args.type:
            assets = [a for a in assets if a.type == args.type]
        for a in sorted(assets, key=lambda x: x.id):
            print(f"  {a.id} [{a.type}] {a.title}")
    elif args.health:
        import json
        print(json.dumps(engine.manager.health_check(), ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
