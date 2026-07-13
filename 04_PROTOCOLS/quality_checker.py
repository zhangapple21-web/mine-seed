"""
Asset Quality Checker — 文明资产质量审查工具

基于 skill-creator 的三个核心特质：
- Testable（可测试）
- Iterable（可迭代）
- Routable（可调度）

每个特质满分 10 分，总分 30 分。
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


class QualityChecker:
    def __init__(self, lineage_path: str = None):
        if lineage_path is None:
            lineage_path = Path(__file__).parent.parent / "02_MEMORY" / "lineage" / "lineage_index.json"
        self.lineage_path = Path(lineage_path)
        self._load()

    def _load(self):
        with open(self.lineage_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.assets = self.data.get("assets", {})

    def assess_testable(self, asset: Dict[str, Any]) -> int:
        score = 0

        acceptance = asset.get("rebuild_hint", "")
        if acceptance and len(acceptance) > 10:
            score += 2
        if "可重建" in acceptance or "行可重建" in acceptance:
            score += 1

        evidence = asset.get("supporting_evidence", [])
        if len(evidence) >= 1:
            score += 2
        if len(evidence) >= 2:
            score += 1

        confidence = asset.get("confidence", "medium")
        if confidence == "high":
            score += 2

        origin_file = asset.get("origin_file", "")
        if origin_file:
            score += 1

        return min(score, 10)

    def assess_iterable(self, asset: Dict[str, Any]) -> int:
        score = 0

        gaps = asset.get("gaps", [])
        if len(gaps) >= 1:
            score += 2
        if len(gaps) >= 2:
            score += 1

        parent = asset.get("parent_asset")
        superseded = asset.get("superseded_by")
        supersedes = asset.get("supersedes")
        if parent or superseded or supersedes:
            score += 2

        dist_date = asset.get("distillation_date", "")
        if dist_date:
            score += 1

        dist_by = asset.get("distilled_by", "")
        if dist_by:
            score += 1

        origin_mission = asset.get("origin_mission", "")
        if origin_mission and not origin_mission.lower().startswith("unknown"):
            score += 2

        return min(score, 10)

    def assess_routable(self, asset: Dict[str, Any]) -> int:
        score = 0

        asset_id = asset.get("asset_id", "")
        if asset_id and len(asset_id) >= 3:
            score += 2

        cat = asset.get("category", "")
        valid_cats = ["公理层", "原则层", "治理层", "能力层", "角色层", "协议层", "认知层", "架构层"]
        if cat in valid_cats:
            score += 3

        name = asset.get("name", "")
        if name and len(name) >= 5:
            score += 2

        status = asset.get("status", "")
        if status in ["active", "reference_only"]:
            score += 2

        return min(score, 10)

    def assess_asset(self, asset_id: str) -> Dict[str, Any]:
        asset = self.assets.get(asset_id)
        if not asset:
            return {"error": "asset not found"}

        testable = self.assess_testable(asset)
        iterable = self.assess_iterable(asset)
        routable = self.assess_routable(asset)
        total = testable + iterable + routable

        grade = self.get_grade(total)

        return {
            "asset_id": asset_id,
            "name": asset.get("name"),
            "category": asset.get("category"),
            "status": asset.get("status"),
            "testable": testable,
            "iterable": iterable,
            "routable": routable,
            "total": total,
            "grade": grade,
            "pass": total >= 15,
            "routable_pass": total >= 20,
        }

    def get_grade(self, total: int) -> str:
        if total >= 25:
            return "★★★★★"
        elif total >= 20:
            return "★★★★☆"
        elif total >= 15:
            return "★★★☆☆"
        elif total >= 10:
            return "★★☆☆☆"
        else:
            return "★☆☆☆☆"

    def assess_all(self) -> List[Dict[str, Any]]:
        results = []
        for asset_id in sorted(self.assets.keys()):
            results.append(self.assess_asset(asset_id))
        return results

    def get_summary(self) -> Dict[str, Any]:
        results = self.assess_all()

        by_grade = {}
        for r in results:
            grade = r["grade"]
            by_grade[grade] = by_grade.get(grade, 0) + 1

        total_assets = len(results)
        total_score = sum(r["total"] for r in results)
        avg_testable = sum(r["testable"] for r in results) / total_assets
        avg_iterable = sum(r["iterable"] for r in results) / total_assets
        avg_routable = sum(r["routable"] for r in results) / total_assets

        return {
            "total_assets": total_assets,
            "avg_score": total_score / total_assets,
            "avg_testable": avg_testable,
            "avg_iterable": avg_iterable,
            "avg_routable": avg_routable,
            "by_grade": by_grade,
            "pass_count": sum(1 for r in results if r["pass"]),
            "routable_pass_count": sum(1 for r in results if r["routable_pass"]),
        }


def main():
    checker = QualityChecker()
    summary = checker.get_summary()
    results = checker.assess_all()

    print("=" * 70)
    print("Asset Quality Checker — 文明资产质量审查")
    print("=" * 70)

    print(f"\n[Summary]")
    print(f"  总资产数: {summary['total_assets']}")
    print(f"  平均分: {summary['avg_score']:.1f}/30")
    print(f"  可测试: {summary['avg_testable']:.1f}/10")
    print(f"  可迭代: {summary['avg_iterable']:.1f}/10")
    print(f"  可调度: {summary['avg_routable']:.1f}/10")
    print(f"  及格数: {summary['pass_count']}/{summary['total_assets']}")
    print(f"  可调度数: {summary['routable_pass_count']}/{summary['total_assets']}")

    print(f"\n[Grade Distribution]")
    for grade in ["★★★★★", "★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆"]:
        count = summary["by_grade"].get(grade, 0)
        percent = (count / summary["total_assets"]) * 100 if summary["total_assets"] > 0 else 0
        print(f"  {grade}: {count} ({percent:.0f}%)")

    print(f"\n[Detailed Results]")
    print(f"  {'ID':<15} {'Name':<30} {'Cat':<6} {'T':<3} {'I':<3} {'R':<3} {'Total':<6} {'Grade':<6}")
    print(f"  {'--':<15} {'----':<30} {'---':<6} {'-':<3} {'-':<3} {'-':<3} {'-----':<6} {'-----':<6}")
    for r in results:
        print(f"  {r['asset_id']:<15} {r['name'][:28]:<30} {r['category']:<6} {r['testable']:<3} {r['iterable']:<3} {r['routable']:<3} {r['total']:<6} {r['grade']:<6}")

    print(f"\n[Lowest Scores (<20)]")
    low = [r for r in results if r["total"] < 20]
    if low:
        for r in low:
            print(f"  ⚠ {r['asset_id']} ({r['name']}) — {r['total']}/30 ({r['grade']})")
    else:
        print("  ✅ 全部达标")

    print(f"\n[High Scores (≥25)]")
    high = [r for r in results if r["total"] >= 25]
    if high:
        for r in high:
            print(f"  ✨ {r['asset_id']} ({r['name']}) — {r['total']}/30 ({r['grade']})")
    else:
        print("  ⚠ 无")

    print("\n" + "=" * 70)
    print("审查完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
