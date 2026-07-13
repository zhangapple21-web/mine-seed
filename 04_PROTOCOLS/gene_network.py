"""---
id: PROTO-017
type: protocol
title: "GENE-002 Gene Network — 微效基因网络"
status: active
source: "R2: inspired by '微效基因网络' concept"
created: 2026-07-12
confidence: 0.85
lineage:
  - PROTO-014 (Seed Archive)
  - PROTO-016 (Nature Reserve)
tags: [gene, network, mutation, risk, constraint]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-001 (Continuity Principle)
"""
GENE-002: Gene Network — 微效基因网络
=======================================

理念来源：
  "智力由成百上千个微效基因网络共同决定，
   改动单一编码极易引发系统性崩溃。"

核心思想：
  系统的每一条约束、原则、配置都是一个"微效基因"。
  它们不是孤立的，而是形成网络——一个基因的变化可能影响其他基因。

  就像生物学中：
  - 单基因突变 → 可能引发 cascading failure
  - 多基因协同 → 系统才稳定
  - 基因网络图 → 理解基因间依赖关系

微效基因的三层：
  1. Principle Gene — 原则基因（为什么存在）
  2. Constraint Gene — 约束基因（不能做什么）
  3. Config Gene — 配置基因（参数怎么设）

突变风险评估：
  - 任何基因修改前，评估对依赖链的影响
  - 高风险突变 → 必须人工确认
  - 中风险突变 → 需要红蓝战队辩论
  - 低风险突变 → 可以自动执行
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple

WORKSPACE = Path(__file__).parent.parent


# ============================================================
# 微效基因定义
# ============================================================

class Gene:
    """单个微效基因"""

    def __init__(self, gid: str, name: str, gene_type: str,
                 source: str, description: str = "", severity: str = "should"):
        self.gid = gid
        self.name = name
        self.gene_type = gene_type  # principle / constraint / config
        self.source = source        # 文件路径
        self.description = description
        self.severity = severity    # must / should / may
        self.dependencies: Set[str] = set()  # 依赖的其他基因 ID
        self.dependents: Set[str] = set()    # 被哪些基因依赖

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gid": self.gid,
            "name": self.name,
            "type": self.gene_type,
            "source": self.source,
            "description": self.description,
            "severity": self.severity,
            "dependencies": sorted(self.dependencies),
            "dependents": sorted(self.dependents),
        }


class GeneNetwork:
    """微效基因网络"""

    def __init__(self):
        self.genes: Dict[str, Gene] = {}
        self._scan_genes()

    def _scan_genes(self):
        """从系统文件中扫描所有微效基因"""
        # 1. 扫描约束
        self._scan_constraints()
        # 2. 扫描原则
        self._scan_principles()
        # 3. 扫描配置
        self._scan_configs()
        # 4. 推断依赖关系
        self._infer_dependencies()

    def _scan_constraints(self):
        """从 CONSTRAINT_LEDGER.md 扫描约束基因"""
        ledger = WORKSPACE / "03_DATA" / "CONSTRAINTS" / "CONSTRAINT_LEDGER.md"
        if not ledger.exists():
            return
        content = ledger.read_text(encoding="utf-8")
        # 匹配约束条目，支持两种格式：
        # 1. 标题格式: ## C-001: xxx 或 ### C-001
        # 2. 表格格式: | RC-001 | xxx | ... |
        pattern1 = r'^#{1,4}\s+(C-\d+):\s*(.+)$'
        for match in re.finditer(pattern1, content, re.MULTILINE):
            cid = match.group(1)
            name = match.group(2).strip()
            gene = Gene(
                gid=cid,
                name=name,
                gene_type="constraint",
                source="03_DATA/CONSTRAINTS/CONSTRAINT_LEDGER.md",
                description=name,
                severity="must",
            )
            self.genes[cid] = gene

        # 表格格式: | RC-001 | *→gh_r1 AVOID | manual | 疯子 | ✅ ACTIVE |
        pattern2 = r'^\|\s*(RC-\d+)\s*\|\s*(.+?)\s*\|'
        for match in re.finditer(pattern2, content, re.MULTILINE):
            cid = match.group(1)
            name = match.group(2).strip()
            if cid not in self.genes:
                gene = Gene(
                    gid=cid,
                    name=name,
                    gene_type="constraint",
                    source="03_DATA/CONSTRAINTS/CONSTRAINT_LEDGER.md",
                    description=name,
                    severity="must",
                )
                self.genes[cid] = gene

        # 也扫描 routing_constraints.json
        rc_path = WORKSPACE / "03_DATA" / "CONSTRAINTS" / "routing_constraints.json"
        if rc_path.exists():
            try:
                rc = json.loads(rc_path.read_text(encoding="utf-8"))
                if isinstance(rc, dict):
                    for key, val in rc.items():
                        gid = f"RC-{key}"
                        if gid not in self.genes:
                            gene = Gene(
                                gid=gid,
                                name=str(key),
                                gene_type="config",
                                source="03_DATA/CONSTRAINTS/routing_constraints.json",
                                description=str(val)[:100] if val else "",
                                severity="should",
                            )
                            self.genes[gid] = gene
            except Exception:
                pass

    def _scan_principles(self):
        """从 PRINCIPLES.md 扫描原则基因"""
        principles_file = WORKSPACE / "00_ROOT" / "PRINCIPLES.md"
        if not principles_file.exists():
            return
        content = principles_file.read_text(encoding="utf-8")
        # 匹配多种格式：
        # 1. 编号格式: ## P-001: xxx 或 ### Principle 1
        # 2. 中文标题: ## 核心公理 或 ### 域映射
        # 3. 列表项: - 原则内容
        pattern1 = r'^#{1,4}\s+(?:P-\d+|Principle\s+\d+)[:\s]*(.+)$'
        for i, match in enumerate(re.finditer(pattern1, content, re.MULTILINE)):
            pid = f"P-{i+1:03d}"
            name = match.group(1).strip()
            gene = Gene(
                gid=pid,
                name=name,
                gene_type="principle",
                source="00_ROOT/PRINCIPLES.md",
                description=name,
                severity="must",
            )
            self.genes[pid] = gene

        # 匹配中文标题格式: ## 核心公理 / ### 域映射 等
        pattern2 = r'^#{2,3}\s+(.+)$'
        for i, match in enumerate(re.finditer(pattern2, content, re.MULTILINE)):
            name = match.group(1).strip()
            # 跳过已有编号的
            if name.startswith("P-") or name.startswith("Principle"):
                continue
            pid = f"P-CN-{i+1:03d}"
            if pid not in self.genes:
                gene = Gene(
                    gid=pid,
                    name=name,
                    gene_type="principle",
                    source="00_ROOT/PRINCIPLES.md",
                    description=name,
                    severity="must",
                )
                self.genes[pid] = gene

    def _scan_configs(self):
        """扫描配置基因"""
        config_files = [
            ("04_PROTOCOLS/provider_config.json", "CFG-PROVIDER"),
            ("04_PROTOCOLS/explorer_topics.json", "CFG-EXPLORER"),
        ]
        for path_str, prefix in config_files:
            path = WORKSPACE / path_str
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    for key in data:
                        gid = f"{prefix}-{key}"
                        gene = Gene(
                            gid=gid,
                            name=f"{prefix}: {key}",
                            gene_type="config",
                            source=path_str,
                            description=f"Config key: {key}",
                            severity="may",
                        )
                        self.genes[gid] = gene
            except Exception:
                pass

    def _infer_dependencies(self):
        """推断基因间的依赖关系

        规则：
          - Constraint 引用的文件如果包含 Principle，则依赖该 Principle
          - Config 如果服务于某个 Constraint，则依赖该 Constraint
          - 同源文件内的基因互相弱依赖
        """
        # 按源文件分组
        by_source: Dict[str, List[str]] = {}
        for gid, gene in self.genes.items():
            by_source.setdefault(gene.source, []).append(gid)

        # 同源文件的基因互相弱依赖
        for source, gids in by_source.items():
            if len(gids) > 1:
                for gid in gids:
                    for other in gids:
                        if gid != other:
                            self.genes[gid].dependencies.add(other)
                            self.genes[other].dependents.add(gid)

        # Constraint 依赖 Principle（类型层级）
        constraints = [g for g in self.genes.values() if g.gene_type == "constraint"]
        principles = [g for g in self.genes.values() if g.gene_type == "principle"]
        for c in constraints:
            for p in principles:
                # 如果约束名包含原则关键词，建立依赖
                c_words = set(c.name.lower().split())
                p_words = set(p.name.lower().split())
                overlap = c_words & p_words
                # 过滤掉太短的词
                overlap = {w for w in overlap if len(w) > 3}
                if overlap:
                    c.dependencies.add(p.gid)
                    p.dependents.add(c.gid)

    def get_gene(self, gid: str) -> Optional[Gene]:
        return self.genes.get(gid)

    def list_genes(self, gene_type: Optional[str] = None) -> List[Gene]:
        if gene_type:
            return [g for g in self.genes.values() if g.gene_type == gene_type]
        return list(self.genes.values())

    def get_dependency_chain(self, gid: str, depth: int = 3) -> Dict[str, Any]:
        """获取基因的依赖链

        返回该基因依赖的所有上游基因（递归到指定深度）
        """
        if gid not in self.genes:
            return {"gid": gid, "error": "gene not found"}

        visited = set()
        chain = []

        def _walk(gene_id: str, current_depth: int):
            if current_depth >= depth or gene_id in visited:
                return
            visited.add(gene_id)
            gene = self.genes.get(gene_id)
            if not gene:
                return
            for dep_id in gene.dependencies:
                if dep_id in visited:
                    continue
                dep_gene = self.genes.get(dep_id)
                if dep_gene:
                    chain.append({
                        "gid": dep_id,
                        "name": dep_gene.name,
                        "type": dep_gene.gene_type,
                        "depth": current_depth + 1,
                    })
                    _walk(dep_id, current_depth + 1)

        _walk(gid, 0)
        return {"gid": gid, "upstream": chain}

    def assess_mutation_risk(self, gid: str, change_desc: str = "") -> Dict[str, Any]:
        """评估基因突变风险

        返回风险等级和受影响的基因列表
        """
        if gid not in self.genes:
            return {"gid": gid, "risk": "unknown", "error": "gene not found"}

        gene = self.genes[gid]
        upstream = self.get_dependency_chain(gid)
        downstream_count = len(gene.dependents)
        upstream_count = len(upstream.get("upstream", []))

        # 风险评估逻辑
        risk_score = 0
        risk_factors = []

        # 基因类型权重
        type_weights = {"principle": 30, "constraint": 20, "config": 5}
        type_weight = type_weights.get(gene.gene_type, 10)
        risk_score += type_weight
        if type_weight >= 20:
            risk_factors.append(f"核心{gene.gene_type}基因（权重{type_weight}）")

        # 严重程度权重
        if gene.severity == "must":
            risk_score += 20
            risk_factors.append("severity=must（不可违反）")
        elif gene.severity == "should":
            risk_score += 10
            risk_factors.append("severity=should")

        # 下游依赖权重
        if downstream_count > 0:
            risk_score += downstream_count * 5
            risk_factors.append(f"{downstream_count} 个基因依赖此基因")

        # 上游依赖权重
        if upstream_count > 0:
            risk_score += upstream_count * 3
            risk_factors.append(f"{upstream_count} 个上游基因")

        # 确定风险等级
        if risk_score >= 40:
            risk_level = "critical"
            action = "必须人工确认，不可自动执行"
        elif risk_score >= 20:
            risk_level = "high"
            action = "需要红蓝战队辩论后执行"
        elif risk_score >= 10:
            risk_level = "medium"
            action = "需要验证后执行"
        else:
            risk_level = "low"
            action = "可以自动执行"

        return {
            "gid": gid,
            "gene_name": gene.name,
            "gene_type": gene.gene_type,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "downstream_dependents": sorted(gene.dependents),
            "upstream_dependencies": upstream.get("upstream", []),
            "recommended_action": action,
            "change_description": change_desc,
            "timestamp": datetime.now().isoformat(),
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_genes": len(self.genes),
            "principles": len([g for g in self.genes.values() if g.gene_type == "principle"]),
            "constraints": len([g for g in self.genes.values() if g.gene_type == "constraint"]),
            "configs": len([g for g in self.genes.values() if g.gene_type == "config"]),
            "total_dependencies": sum(len(g.dependencies) for g in self.genes.values()),
        }


# 模块级单例
network = GeneNetwork()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gene Network — 微效基因网络")
    parser.add_argument("--summary", action="store_true", help="查看基因网络摘要")
    parser.add_argument("--list", type=str, choices=["principle", "constraint", "config"],
                        help="列出指定类型的基因")
    parser.add_argument("--chain", type=str, help="查看基因依赖链")
    parser.add_argument("--risk", type=str, help="评估基因突变风险")
    args = parser.parse_args()

    if args.summary:
        print(json.dumps(network.get_summary(), ensure_ascii=False, indent=2))
    elif args.list:
        genes = network.list_genes(args.list)
        for g in genes:
            print(f"  {g.gid}: {g.name} [{g.severity}] ← {g.source}")
    elif args.chain:
        result = network.get_dependency_chain(args.chain)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.risk:
        result = network.assess_mutation_risk(args.risk)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
