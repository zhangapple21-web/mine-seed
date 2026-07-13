"""
---
id: PROTO-011
type: protocol
title: "Civilization Fingerprint — Chip Recovery Engine"
status: active
source: "Civilization Genome Mapping + Structure Layer Upgrade"
created: 2026-07-12
confidence: 0.85
lineage:
  - CONCEPT-001
  - PROTO-002
  - CHIP-LINEAGE-001
related: [PROTO-002, PROTO-009, CONCEPT-001]
tags: [fingerprint, chip_recovery, structure, genome]
archaeology:
  state: evolved
  sources: 2
---
Civilization Fingerprint — Chip Recovery Engine.

三层结构：
  Gene Layer      → 关键词检测（快速筛查）
  Structure Layer → 连接关系检测（架构识别）
  Chip Layer      → 芯片恢复（核心单元提取）

用法:
    python civilization_fingerprint.py <directory>
    python civilization_fingerprint.py --json <directory>
"""

import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Tuple


# ============================================================
# Layer 1: Gene Markers（基因标记）
# ============================================================

GENE_MARKERS = {
    "identity": {
        "keywords": ["identity", "IDENTITY", "root_identity", "origin_root", "身份", "人格", "persona", "Personality", "soul", "SOUL"],
        "weight": 2.0,
    },
    "memory": {
        "keywords": ["memory", "MEMORY", "记忆", "shadow", "SHADOW", "影子层", "buckets", "MEMORY_ALCHEMY", "experience", "经验"],
        "weight": 2.0,
    },
    "router": {
        "keywords": ["router", "Router", "路由", "INTENT_DECOMPILER", "model_chain", "capability_router", "worker_registry", "调度"],
        "weight": 2.0,
    },
    "execution": {
        "keywords": ["execution", "executor", "执行", "worker", "Worker", "task", "任务", "runner", "运行"],
        "weight": 1.5,
    },
    "governance": {
        "keywords": ["governor", "Governor", "治理", "debate", "辩论", "roundtable", "圆桌", "decision", "决策", "constitution", "宪章"],
        "weight": 1.5,
    },
    "observer": {
        "keywords": ["observer", "Observer", "观察", "Curator", "curator", "馆长", "感知", "perception"],
        "weight": 1.5,
    },
    "persona": {
        "keywords": ["persona", "personality", "人格", "角色", "十人格", "agent", "Agent"],
        "weight": 1.5,
    },
    "world": {
        "keywords": ["world", "World", "五界", "六界", "realm", "BATTLE_ARENA", "FREE_ZONE", "NETHER_REALM", "ROOT_LAYER"],
        "weight": 1.5,
    },
    "seed": {
        "keywords": ["seed", "Seed", "种子", "growth_seed", "business_core", "seeds"],
        "weight": 1.5,
    },
    "question": {
        "keywords": ["question", "Question", "问题", "hypothesis", "假设", "HYPOTHESIS", "QID", "Q-0"],
        "weight": 1.5,
    },
    "constraint": {
        "keywords": ["constraint", "Constraint", "约束", "C-0", "canonical", "retention", "principle", "原则"],
        "weight": 1.5,
    },
    "protocol": {
        "keywords": ["protocol", "Protocol", "协议", "PROTO-", "heartbeat", "心跳"],
        "weight": 1.0,
    },
    "chip": {
        "keywords": ["chip", "Chip", "芯片", "KERNEL", "kernel", "manifest", "manifesto", "DNA", "dna"],
        "weight": 2.0,
    },
    "evolution": {
        "keywords": ["evolution", "演化", "self_evolution", "self_healing", "自愈", "进化", "mutation", "变异"],
        "weight": 1.8,
    },
    "interface": {
        "keywords": ["interface", "接口", "api", "API", "endpoint", "mcp", "MCP", "notification", "tg_push", "messaging"],
        "weight": 1.5,
    },
    "protocol_": {
        "keywords": ["protocol", "Protocol", "协议", "PROTO-", "constraint", "约束", "C-0", "spec", "规范"],
        "weight": 1.5,
    },
    "signal": {
        "keywords": ["signal", "Signal", "信号", "stock", "Stock", "行情", "trading", "交易", "market", "市场", "price", "价格", "advisor", "推荐"],
        "weight": 1.5,
    },
    "data": {
        "keywords": ["data", "Data", "数据", "database", "存储", "dataset", "数据平面", "data_plane", "provider", "Provider", "数据源"],
        "weight": 1.5,
    },
}


# ============================================================
# Layer 2: Structure Patterns（结构模式）
# 每个模式是一组"共同出现的关键词"，代表一种架构连接关系
# ============================================================

STRUCTURE_PATTERNS = {
    "identity_memory_execution": {
        "name": "Identity→Memory→Execution",
        "description": "身份→记忆→执行 三元结构",
        "gene_set": {"identity", "memory", "execution"},
        "weight": 2.0,
    },
    "observe_think_act": {
        "name": "Observe→Think→Act",
        "description": "观察→思考→行动 感知-行动环",
        "gene_set": {"observer", "question", "execution"},
        "weight": 1.8,
    },
    "router_worker": {
        "name": "Router→Worker",
        "description": "路由调度→工作执行 分工结构",
        "gene_set": {"router", "execution"},
        "weight": 1.5,
    },
    "memory_feedback": {
        "name": "Memory Feedback",
        "description": "记忆反馈循环（执行→记忆→再执行）",
        "gene_set": {"memory", "execution", "evolution"},
        "weight": 1.8,
    },
    "governance_loop": {
        "name": "Governance Loop",
        "description": "治理闭环（观察→决策→执行→反馈）",
        "gene_set": {"governance", "observer", "execution", "memory"},
        "weight": 2.0,
    },
    "persona_router": {
        "name": "Persona Router",
        "description": "多人格路由结构",
        "gene_set": {"persona", "router", "identity"},
        "weight": 1.8,
    },
    "chip_triple": {
        "name": "Chip Triple (I+M+R)",
        "description": "芯片三元组（Identity + Memory + Router）",
        "gene_set": {"identity", "memory", "router"},
        "weight": 2.5,
    },
    "world_layers": {
        "name": "World Layers",
        "description": "多层世界结构",
        "gene_set": {"world", "persona", "memory"},
        "weight": 1.5,
    },
    "self_evolution": {
        "name": "Self Evolution",
        "description": "自演化系统（能修改自身代码/规则）",
        "gene_set": {"evolution", "governance", "memory"},
        "weight": 2.0,
    },
    "dna_lineage": {
        "name": "DNA + Lineage",
        "description": "带血统追踪的 DNA 系统",
        "gene_set": {"chip", "memory", "evolution"},
        "weight": 1.5,
    },
    "interface_io": {
        "name": "Interface I/O",
        "description": "输入输出接口系统（API/消息/通知）",
        "gene_set": {"interface", "execution"},
        "weight": 1.5,
    },
    "protocol_stack": {
        "name": "Protocol Stack",
        "description": "协议规范栈（约束+协议+原则）",
        "gene_set": {"protocol_", "constraint", "governance"},
        "weight": 1.8,
    },
    "signal_pipeline": {
        "name": "Signal Pipeline",
        "description": "信号处理流水线（数据采集→分析→输出）",
        "gene_set": {"signal", "data", "execution"},
        "weight": 1.8,
    },
    "data_provider": {
        "name": "Data Provider Chain",
        "description": "数据提供链（Provider→数据平面→消费方）",
        "gene_set": {"data", "router", "execution"},
        "weight": 1.5,
    },
    "evolution_loop": {
        "name": "Evolution Loop",
        "description": "演化闭环（经验→决策→变更→验证→新经验）",
        "gene_set": {"evolution", "memory", "governance", "execution"},
        "weight": 2.0,
    },
}


# ============================================================
# Layer 3: Chip Definitions（芯片定义）
# 每个芯片由一组 Gene + Structure 模式组成
# ============================================================

CHIP_DEFINITIONS = {
    "identity_chip": {
        "name": "Identity Chip",
        "chinese": "身份芯片",
        "description": "系统的自我认知与人格核心",
        "required_genes": ["identity"],
        "supporting_genes": ["persona", "chip", "world"],
        "structures": ["persona_router", "chip_triple"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "memory_chip": {
        "name": "Memory Chip",
        "chinese": "记忆芯片",
        "description": "记忆存储、压缩、检索与反馈系统",
        "required_genes": ["memory"],
        "supporting_genes": ["observer", "evolution", "chip"],
        "structures": ["memory_feedback", "chip_triple", "dna_lineage"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "router_chip": {
        "name": "Router Chip",
        "chinese": "路由芯片",
        "description": "意图解析、任务分发与能力匹配",
        "required_genes": ["router"],
        "supporting_genes": ["execution", "question"],
        "structures": ["router_worker", "chip_triple", "persona_router"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "execution_chip": {
        "name": "Execution Chip",
        "chinese": "执行芯片",
        "description": "任务执行、Worker 管理与运行时",
        "required_genes": ["execution"],
        "supporting_genes": ["router", "protocol"],
        "structures": ["router_worker", "memory_feedback", "governance_loop"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "governance_chip": {
        "name": "Governance Chip",
        "chinese": "治理芯片",
        "description": "决策、辩论、规则制定与自我约束",
        "required_genes": ["governance"],
        "supporting_genes": ["constraint", "protocol", "evolution"],
        "structures": ["governance_loop", "self_evolution"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "persona_chip": {
        "name": "Persona Chip",
        "chinese": "人格芯片",
        "description": "多人格系统与角色切换",
        "required_genes": ["persona"],
        "supporting_genes": ["identity", "router", "world"],
        "structures": ["persona_router", "world_layers"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "observer_chip": {
        "name": "Observer Chip",
        "chinese": "观察芯片",
        "description": "环境感知、状态监控与信息采集",
        "required_genes": ["observer"],
        "supporting_genes": ["memory", "question"],
        "structures": ["observe_think_act", "governance_loop"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "kernel_chip": {
        "name": "Kernel Chip",
        "chinese": "内核芯片",
        "description": "Identity + Memory + Router 完整三元组",
        "required_genes": ["identity", "memory", "router"],
        "supporting_genes": ["chip", "execution", "evolution"],
        "structures": ["chip_triple", "self_evolution", "dna_lineage"],
        "gene_weight": 0.5,
        "structure_weight": 0.35,
        "quality_weight": 0.15,
    },
    "interface_chip": {
        "name": "Interface Chip",
        "chinese": "接口芯片",
        "description": "外部输入输出接口（API/MCP/通知/消息）",
        "required_genes": ["interface"],
        "supporting_genes": ["execution", "router"],
        "structures": ["interface_io", "router_worker"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "protocol_chip": {
        "name": "Protocol Chip",
        "chinese": "协议芯片",
        "description": "约束规范与协议执行系统",
        "required_genes": ["protocol_"],
        "supporting_genes": ["constraint", "governance", "evolution"],
        "structures": ["protocol_stack", "governance_loop"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "signal_chip": {
        "name": "Signal Chip",
        "chinese": "信号芯片",
        "description": "信号采集、分析与推荐系统",
        "required_genes": ["signal"],
        "supporting_genes": ["data", "execution", "interface"],
        "structures": ["signal_pipeline", "data_provider"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "data_chip": {
        "name": "Data Chip",
        "chinese": "数据芯片",
        "description": "数据平面、Provider管理与数据流转",
        "required_genes": ["data"],
        "supporting_genes": ["execution", "router", "signal"],
        "structures": ["data_provider", "signal_pipeline"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
    "evolution_chip": {
        "name": "Evolution Chip",
        "chinese": "演化芯片",
        "description": "自演化、自修复与系统进化系统",
        "required_genes": ["evolution"],
        "supporting_genes": ["memory", "governance", "chip"],
        "structures": ["evolution_loop", "self_evolution", "dna_lineage"],
        "gene_weight": 0.4,
        "structure_weight": 0.4,
        "quality_weight": 0.2,
    },
}


def score_to_stars(score: float) -> str:
    """分数转星级（0-5星）— 采用更严格的阈值，让分布有层次感"""
    if score >= 0.92:
        return "★★★★★"
    elif score >= 0.82:
        return "★★★★☆"
    elif score >= 0.65:
        return "★★★☆☆"
    elif score >= 0.45:
        return "★★☆☆☆"
    elif score >= 0.25:
        return "★☆☆☆☆"
    else:
        return "☆☆☆☆☆"


def scan_gene_layer(root: Path, max_files: int = 5000) -> Tuple[Dict[str, int], Dict[str, set], int]:
    """Layer 1: 扫描基因标记。

    Returns:
        (gene_counts, gene_file_sets, files_scanned)
        - gene_counts: 每个基因的总出现次数
        - gene_file_sets: 每个基因出现在哪些文件里（相对路径集合）
        - files_scanned: 扫描的文件数
    """
    gene_counts = defaultdict(int)
    gene_file_sets = defaultdict(set)
    files_scanned = 0
    file_extensions = {".py", ".md", ".json", ".yaml", ".yml", ".txt", ".toml", ".cfg", ".js", ".ts", ".rs", ".go"}

    for fpath in root.rglob("*"):
        if files_scanned >= max_files:
            break
        if not fpath.is_file():
            continue
        if fpath.suffix not in file_extensions:
            continue
        if fpath.stat().st_size > 500_000:
            continue

        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        files_scanned += 1
        combined_text = f"{fpath.name}\n{content}"
        lower_text = combined_text.lower()
        rel_path = str(fpath.relative_to(root))

        for gene_name, gene_info in GENE_MARKERS.items():
            gene_count = 0
            for kw in gene_info["keywords"]:
                gene_count += lower_text.count(kw.lower())
            if gene_count > 0:
                gene_counts[gene_name] += gene_count
                gene_file_sets[gene_name].add(rel_path)

    return dict(gene_counts), dict(gene_file_sets), files_scanned


def detect_structure_layer(
    gene_counts: Dict[str, int],
    gene_file_sets: Dict[str, set],
    files_scanned: int,
) -> Dict[str, Dict[str, Any]]:
    """Layer 2: 检测结构模式。

    基于文件级共现来判断架构连接关系：
    - 多个基因在同一文件中出现 → 它们之间有连接
    - 共现文件越多 → 结构越强
    """
    present_genes = set(gene_counts.keys())
    structures = {}

    for pattern_id, pattern in STRUCTURE_PATTERNS.items():
        gene_set = pattern["gene_set"]
        found = gene_set & present_genes
        coverage = len(found) / len(gene_set) if gene_set else 0

        # 计算文件级共现强度：所有基因共同出现的文件数 / 最少基因的文件数
        if len(found) >= 2:
            common_files = None
            min_files = float('inf')
            for g in found:
                files = gene_file_sets.get(g, set())
                if common_files is None:
                    common_files = set(files)
                else:
                    common_files &= files
                min_files = min(min_files, len(files))

            cooccurrence_ratio = len(common_files) / min_files if min_files > 0 else 0
            intensity = coverage * 0.4 + cooccurrence_ratio * 0.6
        elif len(found) == 1:
            intensity = coverage * 0.3
        else:
            intensity = 0.0

        intensity = min(1.0, intensity)

        structures[pattern_id] = {
            "name": pattern["name"],
            "description": pattern["description"],
            "coverage": round(coverage, 2),
            "intensity": round(intensity, 2),
            "cooccurrence_files": len(common_files) if len(found) >= 2 else 0,
            "found_genes": list(found),
            "missing_genes": list(gene_set - found),
            "weight": pattern["weight"],
            "score": round(intensity * pattern["weight"], 2),
            "present": intensity >= 0.3,
        }

    return structures


def recover_chip_layer(
    gene_counts: Dict[str, int],
    gene_file_sets: Dict[str, set],
    structures: Dict[str, Dict[str, Any]],
    files_scanned: int,
) -> Dict[str, Dict[str, Any]]:
    """Layer 3: 芯片恢复。

    基于 Gene + Structure 综合评分，判断能恢复出哪些芯片。
    """
    chips = {}

    present_gene_types = len(gene_counts)

    # 计算每个基因的"相对强度"（基于文件数的相对排名）
    gene_file_counts = {g: len(fs) for g, fs in gene_file_sets.items()}
    max_gene_files = max(gene_file_counts.values()) if gene_file_counts else 1
    gene_strength = {g: gene_file_counts[g] / max_gene_files for g in gene_file_counts}

    # 结构按强度排序，用于计算结构相对强度
    struct_intensities = {pid: p["intensity"] for pid, p in structures.items() if p["present"]}
    max_struct_intensity = max(struct_intensities.values()) if struct_intensities else 1

    for chip_id, chip_def in CHIP_DEFINITIONS.items():
        required = chip_def["required_genes"]
        supporting = chip_def["supporting_genes"]
        structure_ids = chip_def["structures"]

        # 1. Gene Score（基因分）
        #    - presence: 基因是否存在（0/1）
        #    - strength: 基因的相对强度（文件数相对最大值的比例）
        #    权重：strength 更重要（0.7），因为"有多普遍"比"有没有"更能代表恢复程度
        required_presence = 0.0
        required_strength = 0.0
        for g in required:
            if g in gene_counts:
                required_presence += 1.0
                required_strength += gene_strength.get(g, 0)
        required_presence = required_presence / len(required) if required else 0
        required_strength = required_strength / len(required) if required else 0
        required_final = required_presence * 0.3 + required_strength * 0.7

        supporting_presence = 0.0
        supporting_strength = 0.0
        if supporting:
            for g in supporting:
                if g in gene_counts:
                    supporting_presence += 1.0
                    supporting_strength += gene_strength.get(g, 0)
            supporting_presence = supporting_presence / len(supporting)
            supporting_strength = supporting_strength / len(supporting)
            supporting_final = supporting_presence * 0.3 + supporting_strength * 0.7
        else:
            supporting_final = 0.0

        gene_score = required_final * 0.7 + supporting_final * 0.3

        # 2. Structure Score（结构分）
        #    - coverage: 相关结构存在的比例
        #    - avg_intensity: 存在结构的平均相对强度
        #    权重：intensity 更重要（0.7），结构强度比"有没有"更能代表架构成熟度
        struct_present = 0
        struct_total_intensity = 0.0
        for sid in structure_ids:
            if sid in structures and structures[sid]["present"]:
                struct_present += 1
                struct_total_intensity += structures[sid]["intensity"] / max_struct_intensity

        if structure_ids:
            struct_coverage = struct_present / len(structure_ids)
            struct_avg_intensity = struct_total_intensity / struct_present if struct_present > 0 else 0
            struct_score = struct_coverage * 0.3 + struct_avg_intensity * 0.7
        else:
            struct_score = 0.0

        # 3. Quality Score（芯片专属质量）
        #    - 基因富集度：该芯片相关基因的强度总和 / 所有基因强度总和
        #    - 结构匹配度：相关结构强度 / 所有结构强度
        #    - 核心度：required 基因的平均强度（越高说明越核心）
        chip_genes = set(required) | set(supporting)
        chip_gene_strength = sum(gene_strength.get(g, 0) for g in chip_genes)
        total_gene_strength = sum(gene_strength.values())
        gene_enrichment = chip_gene_strength / total_gene_strength if total_gene_strength > 0 else 0
        gene_enrichment = min(1.0, gene_enrichment * 3)

        present_structs = {pid: p for pid, p in structures.items() if p["present"]}
        chip_struct_strength = sum(p["intensity"] for sid in structure_ids if sid in present_structs for p in [present_structs[sid]])
        total_struct_strength = sum(p["intensity"] for p in present_structs.values())
        struct_enrichment = chip_struct_strength / total_struct_strength if total_struct_strength > 0 else 0
        struct_enrichment = min(1.0, struct_enrichment * 3)

        core_strength = 0.0
        if required:
            core_strength = sum(gene_strength.get(g, 0) for g in required) / len(required)

        quality_score = (gene_enrichment * 0.4 + struct_enrichment * 0.3 + core_strength * 0.3)

        # 综合评分 — 提高 structure 权重（结构比关键词更能代表真实架构）
        total_score = (
            gene_score * chip_def["gene_weight"]
            + struct_score * chip_def["structure_weight"]
            + quality_score * chip_def["quality_weight"]
        )
        total_score = round(total_score, 3)

        stars = score_to_stars(total_score)
        recoverable = total_score >= 0.35

        chips[chip_id] = {
            "name": chip_def["name"],
            "chinese": chip_def["chinese"],
            "description": chip_def["description"],
            "score": total_score,
            "stars": stars,
            "recoverable": recoverable,
            "gene_score": round(gene_score, 3),
            "structure_score": round(struct_score, 3),
            "quality_score": round(quality_score, 3),
            "required_genes_present": [g for g in required if gene_counts.get(g, 0) > 0],
            "required_genes_missing": [g for g in required if gene_counts.get(g, 0) == 0],
            "structures_present": [sid for sid in structure_ids if structures.get(sid, {}).get("present", False)],
            "structures_missing": [sid for sid in structure_ids if not structures.get(sid, {}).get("present", False)],
        }

    return chips


def generate_repair_plan(result: Dict[str, Any]) -> Dict[str, Any]:
    """基于芯片恢复结果，生成修复建议清单。

    分析每个芯片的短板（基因弱/结构弱/质量低），给出针对性的修复方向。
    """
    chips = result.get("chip_layer", {})
    sorted_chips = sorted(chips.items(), key=lambda x: x[1]["score"])

    repair_plan = {
        "summary": {
            "total_chips": len(chips),
            "high_confidence": sum(1 for c in chips.values() if c["score"] >= 0.82),
            "medium_confidence": sum(1 for c in chips.values() if 0.65 <= c["score"] < 0.82),
            "low_confidence": sum(1 for c in chips.values() if c["score"] < 0.65),
            "priority_chips": [],
        },
        "repairs": [],
    }

    # 修复建议模板
    repair_templates = {
        "gene_weak": {
            "type": "gene_strengthening",
            "title": "基因强化",
            "description": "核心基因文件覆盖率不足，需要增加相关模块的存在感",
            "actions": [
                "在核心模块中增加相关基因的命名一致性",
                "补充缺失的辅助基因模块",
                "在协议/文档中明确该芯片的职责边界",
            ],
        },
        "struct_weak": {
            "type": "structure_reinforcement",
            "title": "结构加固",
            "description": "相关架构模式强度不足，模块间连接关系需要加强",
            "actions": [
                "梳理芯片内各模块的调用关系，增加跨模块协作",
                "建立芯片专属的事件/消息通道",
                "补充芯片内部的闭环反馈机制",
            ],
        },
        "quality_low": {
            "type": "quality_improvement",
            "title": "质量提升",
            "description": "芯片在系统中的富集度和核心度偏低",
            "actions": [
                "将该芯片的能力提升到核心路径中",
                "增加与其他核心芯片的交互接口",
                "建立芯片专属的健康监控和指标",
            ],
        },
        "missing_genes": {
            "type": "gene_completion",
            "title": "基因补全",
            "description": "存在必需基因缺失",
            "actions": [
                "优先实现缺失的核心基因模块",
                "参考高星级芯片的基因结构进行补全",
                "先做最小可用版本，再逐步增强",
            ],
        },
        "missing_structures": {
            "type": "structure_completion",
            "title": "结构补全",
            "description": "存在关键架构模式缺失",
            "actions": [
                "设计并实现缺失的架构模式",
                "从相关芯片中复用成熟的结构模式",
                "先建立骨架，再填充细节",
            ],
        },
    }

    for chip_id, chip in sorted_chips:
        score = chip["score"]
        if score >= 0.85:
            continue

        issues = []
        actions = []

        # 诊断短板
        gene_score = chip["gene_score"]
        struct_score = chip["structure_score"]
        quality_score = chip["quality_score"]

        if chip["required_genes_missing"]:
            issues.append("missing_genes")
            actions.append(f"补全缺失基因: {', '.join(chip['required_genes_missing'])}")
        elif gene_score < 0.75:
            issues.append("gene_weak")
            actions.append(f"强化核心基因（当前基因分: {gene_score:.2f}）")

        if chip["structures_missing"]:
            issues.append("missing_structures")
            actions.append(f"补全缺失结构: {', '.join(chip['structures_missing'])}")
        elif struct_score < 0.80:
            issues.append("struct_weak")
            actions.append(f"加固架构模式（当前结构分: {struct_score:.2f}）")

        if quality_score < 0.50:
            issues.append("quality_low")
            actions.append(f"提升芯片核心度（当前质量分: {quality_score:.2f}）")

        if not issues:
            continue

        # 优先级判定
        if score < 0.65:
            priority = "P0"
        elif score < 0.75:
            priority = "P1"
        else:
            priority = "P2"

        # 汇总修复建议
        repair_detail = {
            "chip_id": chip_id,
            "chip_name": chip["name"],
            "chinese": chip["chinese"],
            "current_score": score,
            "current_stars": chip["stars"],
            "priority": priority,
            "issues": issues,
            "diagnosis": {
                "gene_score": gene_score,
                "structure_score": struct_score,
                "quality_score": quality_score,
            },
            "missing_genes": chip["required_genes_missing"],
            "missing_structures": chip["structures_missing"],
            "actions": actions,
            "repair_templates": [repair_templates[i] for i in issues if i in repair_templates],
            "estimated_effort": len(issues) * 2,
        }

        repair_plan["repairs"].append(repair_detail)

        if priority in ("P0", "P1"):
            repair_plan["summary"]["priority_chips"].append({
                "chip_id": chip_id,
                "name": chip["name"],
                "priority": priority,
                "score": score,
            })

    # 按优先级排序
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    repair_plan["repairs"].sort(key=lambda x: (priority_order.get(x["priority"], 99), x["current_score"]))

    return repair_plan


def format_repair_plan(plan: Dict[str, Any]) -> str:
    """格式化修复建议报告"""
    lines = []
    lines.append("=" * 64)
    lines.append("  CHIP REPAIR PLAN — 芯片修复路线图")
    lines.append("=" * 64)
    lines.append("")

    s = plan["summary"]
    lines.append(f"  总芯片数: {s['total_chips']}")
    lines.append(f"  高置信 (≥4星): {s['high_confidence']}")
    lines.append(f"  中置信 (3星): {s['medium_confidence']}")
    lines.append(f"  低置信 (<3星): {s['low_confidence']}")
    lines.append("")

    if s["priority_chips"]:
        lines.append("━" * 64)
        lines.append("  优先级芯片（P0 + P1）")
        lines.append("━" * 64)
        lines.append("")
        for pc in s["priority_chips"]:
            lines.append(f"  [{pc['priority']}] {pc['name']:20s}  {pc['score']:.3f}")
        lines.append("")

    lines.append("━" * 64)
    lines.append("  修复详情")
    lines.append("━" * 64)
    lines.append("")

    for r in plan["repairs"]:
        lines.append(f"  [{r['priority']}] {r['chip_name']} ({r['chinese']})")
        lines.append(f"       当前: {r['current_stars']}  {r['current_score']:.3f}")
        lines.append(f"       问题: {', '.join(r['issues'])}")
        d = r["diagnosis"]
        lines.append(f"       诊断: 基因={d['gene_score']:.2f}  结构={d['structure_score']:.2f}  质量={d['quality_score']:.2f}")
        if r["missing_genes"]:
            lines.append(f"       缺失基因: {', '.join(r['missing_genes'])}")
        if r["missing_structures"]:
            lines.append(f"       缺失结构: {', '.join(r['missing_structures'])}")
        lines.append(f"       预估工作量: ~{r['estimated_effort']} 人天")
        lines.append("")
        for action in r["actions"]:
            lines.append(f"       → {action}")
        lines.append("")

    lines.append("=" * 64)
    return "\n".join(lines)


def scan_directory(directory: str, max_files: int = 5000) -> Dict[str, Any]:
    """扫描目录，生成三层文明指纹 + 芯片恢复结果。

    Returns:
        {
            "directory": str,
            "files_scanned": int,
            "gene_layer": {gene: count},
            "structure_layer": {pattern_id: {...}},
            "chip_layer": {chip_id: {...}},
            "summary": {...}
        }
    """
    root = Path(directory)
    if not root.exists():
        return {"error": f"Directory not found: {directory}"}

    # Layer 1: Gene
    gene_counts, gene_file_sets, files_scanned = scan_gene_layer(root, max_files)

    # Layer 2: Structure
    structures = detect_structure_layer(gene_counts, gene_file_sets, files_scanned)

    # Layer 3: Chip Recovery
    chips = recover_chip_layer(gene_counts, gene_file_sets, structures, files_scanned)

    # 汇总
    recoverable_chips = [cid for cid, c in chips.items() if c["recoverable"]]
    high_confidence_chips = [cid for cid, c in chips.items() if c["score"] >= 0.75]
    sorted_chips = sorted(chips.items(), key=lambda x: x[1]["score"], reverse=True)

    present_structures = [pid for pid, p in structures.items() if p["present"]]

    summary = {
        "files_scanned": files_scanned,
        "genes_detected": len(gene_counts),
        "structures_detected": len(present_structures),
        "chips_recoverable": len(recoverable_chips),
        "chips_high_confidence": len(high_confidence_chips),
        "top_chip": sorted_chips[0][0] if sorted_chips else None,
        "top_chip_name": sorted_chips[0][1]["name"] if sorted_chips else None,
        "top_chip_stars": sorted_chips[0][1]["stars"] if sorted_chips else "☆☆☆☆☆",
    }

    return {
        "directory": str(root),
        "files_scanned": files_scanned,
        "gene_layer": gene_counts,
        "structure_layer": structures,
        "chip_layer": chips,
        "present_structures": present_structures,
        "recoverable_chips": recoverable_chips,
        "high_confidence_chips": high_confidence_chips,
        "sorted_chips": sorted_chips,
        "summary": summary,
    }


def format_report(result: Dict[str, Any]) -> str:
    """格式化三层报告"""
    lines = []
    lines.append("=" * 64)
    lines.append("  Civilization Fingerprint — Chip Recovery Engine")
    lines.append("=" * 64)
    lines.append(f"  Directory: {result.get('directory', 'N/A')}")
    lines.append(f"  Files scanned: {result.get('files_scanned', 0)}")
    lines.append("")

    # === Chip Layer (最核心，放在最前面) ===
    lines.append("━" * 64)
    lines.append("  CHIP LAYER — Recovered Chips")
    lines.append("━" * 64)
    lines.append("")

    sorted_chips = result.get("sorted_chips", [])
    for chip_id, chip in sorted_chips:
        if not chip["recoverable"]:
            continue
        stars = chip["stars"]
        score = chip["score"]
        lines.append(f"  {stars}  {chip['name']:20s}  ({score:.2f})  —  {chip['chinese']}")
        lines.append(f"        {chip['description']}")
        if chip["required_genes_missing"]:
            lines.append(f"        缺失基因: {', '.join(chip['required_genes_missing'])}")
        if chip["structures_present"]:
            struct_names = [STRUCTURE_PATTERNS[s]["name"] for s in chip["structures_present"] if s in STRUCTURE_PATTERNS]
            if struct_names:
                lines.append(f"        架构模式: {', '.join(struct_names)}")
        lines.append("")

    unrecoverable = [(cid, c) for cid, c in sorted_chips if not c["recoverable"]]
    if unrecoverable:
        lines.append(f"  不可恢复 ({len(unrecoverable)}):")
        for cid, c in unrecoverable:
            lines.append(f"    ☆☆☆☆☆ {c['name']:20s}  ({c['score']:.2f})")
        lines.append("")

    # === Structure Layer ===
    lines.append("━" * 64)
    lines.append("  STRUCTURE LAYER — Architecture Patterns")
    lines.append("━" * 64)
    lines.append("")

    structures = result.get("structure_layer", {})
    struct_sorted = sorted(structures.items(), key=lambda x: x[1]["score"], reverse=True)
    for pid, p in struct_sorted:
        if not p["present"]:
            continue
        bar = "█" * int(p["intensity"] * 30)
        co_files = p.get("cooccurrence_files", 0)
        lines.append(f"  ✓ {p['name']:24s}  {p['intensity']:.2f}  {bar}  [{co_files} files]")
        lines.append(f"    {p['description']}")
        if p["missing_genes"]:
            lines.append(f"    缺失: {', '.join(p['missing_genes'])}")
    lines.append("")

    # === Gene Layer ===
    lines.append("━" * 64)
    lines.append("  GENE LAYER — Detected Markers")
    lines.append("━" * 64)
    lines.append("")

    gene_layer = result.get("gene_layer", {})
    gene_sorted = sorted(gene_layer.items(), key=lambda x: x[1], reverse=True)
    max_count = gene_sorted[0][1] if gene_sorted else 1
    for gname, gcount in gene_sorted:
        bar_len = int(gcount / max_count * 30)
        bar = "▓" * bar_len
        weight = GENE_MARKERS.get(gname, {}).get("weight", 1.0)
        lines.append(f"  {gname:16s} ({gcount:5d})  {bar}  w={weight}")
    lines.append("")

    # === Summary ===
    lines.append("=" * 64)
    s = result.get("summary", {})
    lines.append(f"  Genes: {s.get('genes_detected', 0)}/{len(GENE_MARKERS)}")
    lines.append(f"  Structures: {s.get('structures_detected', 0)}/{len(STRUCTURE_PATTERNS)}")
    lines.append(f"  Recoverable Chips: {s.get('chips_recoverable', 0)}/{len(CHIP_DEFINITIONS)}")
    lines.append(f"  Top Chip: {s.get('top_chip_name', 'N/A')}  {s.get('top_chip_stars', '')}")
    lines.append("=" * 64)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Civilization Fingerprint — Chip Recovery Engine")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--max-files", type=int, default=5000, help="Max files to scan")
    args = parser.parse_args()

    result = scan_directory(args.directory, args.max_files)

    if "error" in result:
        print(result["error"])
        return

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
