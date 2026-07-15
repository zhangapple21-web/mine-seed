#!/usr/bin/env python3
"""
ARCH-023：Knowledge Activation Engine

Repository First Policy：
    Question → Repository → Memory MCP → Activated Knowledge → Need External? → Discovery → Internet

状态机：
    Discovered → Indexed → Classified → Learned → Activated → Validated → Distilled

Priority Score：
    Novelty(30%) + Reuse(25%) + MissionRelated(20%) + Recency(15%) + EvidenceQuality(10%)
"""

import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / "02_MEMORY"
INDEX_DIR = WORKSPACE / "03_INDEX"
PROTOCOLS_DIR = WORKSPACE / "04_PROTOCOLS"

ASSET_INDEX_FILE = INDEX_DIR / "ASSET_INDEX.md"
ASSET_DB_FILE = INDEX_DIR / "asset_index.json"


@dataclass
class Asset:
    asset_id: str
    title: str
    type: str
    status: str
    priority_score: float = 0.0
    tags: List[str] = None
    source: str = ""
    created_at: str = ""
    updated_at: str = ""
    activated_by: str = ""
    validated_by: str = ""
    distilled_to: str = ""
    content_path: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PriorityScorer:
    """优先级评分器"""

    WEIGHTS = {
        "novelty": 0.3,
        "reuse": 0.25,
        "mission_related": 0.2,
        "recency": 0.15,
        "evidence_quality": 0.1,
    }

    def __init__(self):
        pass

    def score(self, asset: Asset, current_mission: Optional[str] = None) -> float:
        """计算优先级分数"""
        scores = {
            "novelty": self._score_novelty(asset),
            "reuse": self._score_reuse(asset),
            "mission_related": self._score_mission_related(asset, current_mission),
            "recency": self._score_recency(asset),
            "evidence_quality": self._score_evidence_quality(asset),
        }

        total = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        return round(total, 3)

    def _score_novelty(self, asset: Asset) -> float:
        """新颖度：新发现的知识得分更高"""
        if asset.status == "discovered":
            return 1.0
        if asset.status == "indexed":
            return 0.8
        return 0.3

    def _score_reuse(self, asset: Asset) -> float:
        """复用价值：已有标签越多，复用价值越高"""
        tag_count = len(asset.tags) if asset.tags else 0
        return min(tag_count / 10, 1.0)

    def _score_mission_related(self, asset: Asset, current_mission: Optional[str]) -> float:
        """与当前 Mission 的相关性"""
        if not current_mission:
            return 0.5
        if current_mission.lower() in asset.title.lower():
            return 1.0
        for tag in asset.tags:
            if tag.lower() in current_mission.lower():
                return 0.8
        return 0.2

    def _score_recency(self, asset: Asset) -> float:
        """时效性：越新越优先"""
        try:
            created = datetime.fromisoformat(asset.created_at)
            age_days = (datetime.now() - created).days
            if age_days == 0:
                return 1.0
            if age_days <= 7:
                return 0.8
            if age_days <= 30:
                return 0.5
            return 0.2
        except:
            return 0.5

    def _score_evidence_quality(self, asset: Asset) -> float:
        """证据质量：来源可信度"""
        source = asset.source.lower()
        if any(s in source for s in ["github", "arxiv", "arxiv.org", "official"]):
            return 1.0
        if any(s in source for s in ["blog", "medium", "article"]):
            return 0.7
        if any(s in source for s in ["twitter", "social", "chat"]):
            return 0.4
        return 0.5


class LearningQueue:
    """学习队列，按优先级排序"""

    def __init__(self):
        self.scorer = PriorityScorer()
        self.assets: List[Asset] = []
        self._load()

    def _load(self):
        if ASSET_DB_FILE.exists():
            try:
                with open(ASSET_DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.assets = [Asset(**item) for item in data]
            except:
                self.assets = []

    def _save(self):
        ASSET_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ASSET_DB_FILE, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in self.assets], f, ensure_ascii=False, indent=2)

    def add_asset(self, title: str, type: str = "knowledge", source: str = "", 
                  tags: Optional[List[str]] = None, content_path: str = "") -> str:
        """添加资产到队列"""
        asset_id = str(uuid.uuid4())[:8]
        asset = Asset(
            asset_id=asset_id,
            title=title,
            type=type,
            status="discovered",
            source=source,
            tags=tags or [],
            content_path=content_path,
        )
        asset.priority_score = self.scorer.score(asset)
        self.assets.append(asset)
        self._save()
        return asset_id

    def get_queue(self, current_mission: Optional[str] = None) -> List[Asset]:
        """获取排序后的队列"""
        for asset in self.assets:
            asset.priority_score = self.scorer.score(asset, current_mission)
        return sorted(self.assets, key=lambda x: x.priority_score, reverse=True)

    def update_status(self, asset_id: str, new_status: str, by: str = ""):
        """更新资产状态"""
        for asset in self.assets:
            if asset.asset_id == asset_id:
                asset.status = new_status
                asset.updated_at = datetime.now().isoformat()
                if new_status == "activated":
                    asset.activated_by = by
                elif new_status == "validated":
                    asset.validated_by = by
                elif new_status == "distilled":
                    asset.distilled_to = by
                self._save()
                return True
        return False

    def get_unactivated(self) -> List[Asset]:
        """获取未激活的资产"""
        return [a for a in self.assets if a.status not in ["activated", "validated", "distilled"]]

    def get_activated(self) -> List[Asset]:
        """获取已激活的资产"""
        return [a for a in self.assets if a.status in ["activated", "validated", "distilled"]]

    def get_by_status(self, status: str) -> List[Asset]:
        """按状态获取资产"""
        return [a for a in self.assets if a.status == status]

    def scan_directory(self, directory: Path, asset_type: str = "knowledge") -> int:
        """扫描目录，发现未登记的资产"""
        count = 0
        existing_titles = {a.title.lower() for a in self.assets}
        
        for filepath in directory.rglob("*.md"):
            rel_path = filepath.relative_to(WORKSPACE)
            title = filepath.stem
            if title.lower() not in existing_titles:
                self.add_asset(
                    title=title,
                    type=asset_type,
                    source=str(rel_path),
                    content_path=str(rel_path),
                )
                count += 1
                existing_titles.add(title.lower())
        
        return count

    def update_index_md(self):
        """更新 ASSET_INDEX.md 中的资产列表"""
        if not ASSET_INDEX_FILE.exists():
            return

        with open(ASSET_INDEX_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        begin_marker = "<!-- ASSET_LIST_BEGIN -->"
        end_marker = "<!-- ASSET_LIST_END -->"

        if begin_marker not in content or end_marker not in content:
            return

        queue = self.get_queue()
        
        table = "\n| # | ID | Title | Type | Status | Priority | Tags |\n"
        table += "|---|---|---|---|---|---|---|\n"
        
        for i, asset in enumerate(queue, 1):
            tags_str = ", ".join(asset.tags[:3]) if asset.tags else "-"
            table += f"| {i} | {asset.asset_id} | {asset.title} | {asset.type} | {asset.status} | {asset.priority_score} | {tags_str} |\n"

        start_idx = content.index(begin_marker) + len(begin_marker)
        end_idx = content.index(end_marker)
        
        new_content = content[:start_idx] + "\n" + table + "\n" + content[end_idx:]
        
        with open(ASSET_INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)


class KnowledgeActivationEngine:
    """知识激活引擎"""

    def __init__(self):
        self.queue = LearningQueue()

    def auto_discover(self) -> Dict[str, Any]:
        """自动发现未激活资产（Agent 启动时调用）"""
        results = {
            "scanned_directories": [],
            "new_assets_found": 0,
            "unactivated_count": 0,
            "activated_count": 0,
        }

        scan_dirs = [
            (MEMORY_DIR / "experience", "observation"),
            (MEMORY_DIR / "discovery_queue", "knowledge"),
            (PROTOCOLS_DIR, "protocol"),
            (WORKSPACE / "05_REPORTS", "knowledge"),
        ]

        for dir_path, asset_type in scan_dirs:
            if dir_path.exists():
                found = self.queue.scan_directory(dir_path, asset_type)
                results["scanned_directories"].append(str(dir_path.relative_to(WORKSPACE)))
                results["new_assets_found"] += found

        results["unactivated_count"] = len(self.queue.get_unactivated())
        results["activated_count"] = len(self.queue.get_activated())
        
        self.queue.update_index_md()
        
        return results

    def activate_top(self, count: int = 5, current_mission: str = "") -> List[Asset]:
        """激活优先级最高的 N 个资产"""
        queue = self.queue.get_queue(current_mission)
        unactivated = [a for a in queue if a.status not in ["activated", "validated", "distilled"]]
        
        activated = []
        for asset in unactivated[:count]:
            self.queue.update_status(asset.asset_id, "activated", by=current_mission)
            activated.append(asset)
        
        self.queue.update_index_md()
        return activated

    def get_repo_knowledge(self, query: str) -> List[Asset]:
        """从 Repository 检索知识（Repository First Policy 核心）"""
        queue = self.queue.get_queue()
        activated = [a for a in queue if a.status in ["activated", "validated", "distilled"]]
        
        results = []
        query_lower = query.lower()
        for asset in activated:
            if query_lower in asset.title.lower():
                results.append(asset)
            elif any(query_lower in tag.lower() for tag in asset.tags):
                results.append(asset)
        
        return sorted(results, key=lambda x: x.priority_score, reverse=True)

    def needs_external(self, query: str) -> bool:
        """判断是否需要外部 Discovery"""
        repo_results = self.get_repo_knowledge(query)
        return len(repo_results) == 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Knowledge Activation Engine")
    parser.add_argument("--discover", action="store_true", help="自动发现未激活资产")
    parser.add_argument("--activate", type=int, default=0, help="激活优先级最高的 N 个资产")
    parser.add_argument("--query", type=str, help="检索知识")
    parser.add_argument("--list", action="store_true", help="列出所有资产")
    parser.add_argument("--status", type=str, help="按状态筛选")
    
    args = parser.parse_args()
    
    engine = KnowledgeActivationEngine()
    
    if args.discover:
        result = engine.auto_discover()
        print(f"[Knowledge Activation] 自动发现完成")
        print(f"  扫描目录: {', '.join(result['scanned_directories'])}")
        print(f"  新发现资产: {result['new_assets_found']}")
        print(f"  未激活: {result['unactivated_count']}")
        print(f"  已激活: {result['activated_count']}")
    
    if args.activate > 0:
        activated = engine.activate_top(args.activate)
        print(f"[Knowledge Activation] 激活了 {len(activated)} 个资产:")
        for asset in activated:
            print(f"  - {asset.title} ({asset.asset_id})")
    
    if args.query:
        results = engine.get_repo_knowledge(args.query)
        print(f"[Knowledge Activation] 检索 '{args.query}' 结果:")
        for asset in results:
            print(f"  - {asset.title} (priority: {asset.priority_score})")
        if not results:
            print("  → 需要外部 Discovery")
    
    if args.list:
        queue = engine.queue.get_queue()
        print(f"[Knowledge Activation] 资产列表 ({len(queue)}):")
        for asset in queue:
            print(f"  [{asset.status}] {asset.title} - priority: {asset.priority_score}")
    
    if args.status:
        assets = engine.queue.get_by_status(args.status)
        print(f"[Knowledge Activation] 状态 '{args.status}' 的资产 ({len(assets)}):")
        for asset in assets:
            print(f"  - {asset.title} (priority: {asset.priority_score})")


if __name__ == "__main__":
    main()