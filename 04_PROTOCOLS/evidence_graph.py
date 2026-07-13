"""---
id: PROTO-006
type: protocol
title: "Evidence Graph — 考古证据图系统"
status: active
source: "R2 Development"
created: 2026-07-12
confidence: 0.92
evidence: [E-036, E-038, E-039]
lineage:
  - TG-ARCH-002
  - KERNEL-RECOVERY-001
related: [PROTO-002, KERNEL-DNA-V1, CHIP-LINEAGE-001]
tags: [evidence, graph, confidence, archaeology]
archaeology:
  state: original
  sources: 1
---
"""
#!/usr/bin/env python3
"""
ARC-001: Evidence Graph — 考古证据图系统
================================================

类型: dev_tool / knowledge_engine
Implements: OPS-004 (Recovery First), OPS-006 (Search Policy)

核心思想:
  任何考古结论都必须有可追溯的证据链。
  每个结论都有置信度 (0~1)。
  置信度基于证据的类型、数量、一致性。

证据可信度层级 (从高到低):
  running_state    运行状态 (95-100%)
  source_code      源代码 (85-95%)
  config_file      配置文件 (75-85%)
  data_file        数据文件 (65-75%)
  official_doc     官方文档 (55-65%)
  chat_record      聊天记录 (35-55%)
  screenshot       截图 (25-35%)
  third_party      第三方描述 (15-25%)
  inference        纯推理 (5-15%)

置信度计算:
  单条证据 = base_weight * quality_factor
  多条证据 = 1 - product(1 - individual_confidence)
  证据冲突 = 降低置信度
"""
"""
EVIDENCE-001: Evidence Graph — 考古证据图
==========================================

Two-stage pipeline (ARCH-011):
  Stage 1 (Draft): Runtime writes to 06_RUNTIME/archaeology_workspace/ (Tier 3)
  Stage 2 (Final): Admission promotes to 02_MEMORY/archaeology/ (Tier 2)

Contract Enforcement:
  - save() writes to staging area (Tier 3, no Admission required)
  - promote_to_archive() writes to official archaeology/ (requires Admission)
"""
import os, sys, json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

WORKSPACE = Path(__file__).parent.parent

# Two-stage paths
STAGING_DIR = WORKSPACE / "06_RUNTIME" / "archaeology_workspace"  # Tier 3: Runtime can write freely
ARCHIVE_DIR = WORKSPACE / "02_MEMORY" / "archaeology"             # Tier 2: Requires Admission

STAGING_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# Evidence reliability hierarchy
EVIDENCE_WEIGHTS = {
    "running_state": 0.97,
    "source_code": 0.90,
    "config_file": 0.80,
    "data_file": 0.70,
    "official_doc": 0.60,
    "chat_record": 0.45,
    "screenshot": 0.30,
    "third_party": 0.20,
    "inference": 0.10,
}

EVIDENCE_LABELS = {
    "running_state": "运行状态",
    "source_code": "源代码",
    "config_file": "配置文件",
    "data_file": "数据文件",
    "official_doc": "官方文档",
    "chat_record": "聊天记录",
    "screenshot": "截图",
    "third_party": "第三方描述",
    "inference": "纯推理",
}

# Evidence sources (search layers)
EVIDENCE_SOURCES = {
    "tg_saved": ("Telegram Saved Messages", 0.85),
    "tg_chat": ("Telegram 聊天记录", 0.75),
    "tg_favorites": ("Telegram 收藏夹", 0.80),
    "github": ("GitHub 仓库", 0.90),
    "workspace": ("本地 Workspace", 0.95),
    "r1_snapshot": ("R1 Snapshot", 0.70),
    "archive": ("归档/ZIP", 0.65),
    "bluebook": ("蓝皮书", 0.35),
    "daily_memory": ("Daily Memory", 0.55),
    "r1_fragments": ("R1 System Fragments", 0.50),
}


class EvidenceGraph:
    """Evidence Graph — 每个结论都有可追溯的证据链"""

    def __init__(self):
        self.claims = {}  # claim_id -> claim data
        self.evidence = {}  # evidence_id -> evidence data

    def add_evidence(self, eid: str, etype: str, source: str,
                     content: str, location: str = "", quality: float = 1.0) -> str:
        """
        Add a piece of evidence.

        Args:
            eid: Evidence ID (unique)
            etype: Evidence type (running_state/source_code/...)
            source: Source (tg_saved/github/workspace/...)
            content: Evidence content (text)
            location: Where to find it (file path, URL, msg ID, etc.)
            quality: Quality factor 0~1 (how good is this specific piece)

        Returns:
            eid
        """
        base_weight = EVIDENCE_WEIGHTS.get(etype, 0.10)
        source_factor = EVIDENCE_SOURCES.get(source, ( "", 0.5))[1]
        weight = base_weight * quality * source_factor
        weight = min(0.99, max(0.01, weight))

        self.evidence[eid] = {
            "id": eid,
            "type": etype,
            "type_label": EVIDENCE_LABELS.get(etype, etype),
            "source": source,
            "source_label": EVIDENCE_SOURCES.get(source, (source, 0.5))[0],
            "content": content[:500],
            "location": location,
            "quality": quality,
            "base_weight": base_weight,
            "weight": weight,
            "added_at": datetime.now().isoformat(),
        }
        return eid

    def add_claim(self, cid: str, title: str, description: str,
                  evidence_ids: List[str], counter_evidence_ids: List[str] = None,
                  status: str = "hypothesis",
                  inference_depth: int = 1,
                  direct_evidence_ids: List[str] = None) -> Dict[str, Any]:
        """
        Add a claim with evidence chain.

        Args:
            cid: Claim ID
            title: Short title
            description: Full description
            evidence_ids: ALL evidence IDs supporting this claim (direct + indirect)
            counter_evidence_ids: Evidence contradicting this claim
            status: hypothesis / likely / confirmed / disputed / rejected
            inference_depth: 推理深度 — 从证据到结论需要几步推理
              1 = 证据直接支持结论 (e.g., "JSON文件包含X字段")
              2 = 需要一步解释 (e.g., "X字段暗示Y机制")
              3 = 需要多步推理 (e.g., "多个间接证据指向Z假设")
            direct_evidence_ids: 直接支持结论的证据子集

        Returns:
            Claim dict with computed confidence
        """
        counter_evidence_ids = counter_evidence_ids or []
        direct_evidence_ids = direct_evidence_ids or evidence_ids[:1]  # at least one assumed direct

        # Split evidence into direct and indirect
        direct_weights = []
        indirect_weights = []
        for eid in evidence_ids:
            if eid not in self.evidence:
                continue
            if eid in direct_evidence_ids:
                direct_weights.append(self.evidence[eid]["weight"])
            else:
                # Indirect evidence has reduced weight
                indirect_weights.append(self.evidence[eid]["weight"] * 0.4)

        all_weights = direct_weights + indirect_weights

        # Compute raw confidence: 1 - product(1 - each_evidence_weight)
        pro_support = 1.0
        for w in all_weights:
            pro_support *= (1.0 - w)
        raw_confidence = 1.0 - pro_support

        # Inference depth penalty: each step multiplies by 0.6
        # depth=1 → ×1.0, depth=2 → ×0.6, depth=3 → ×0.36
        depth_factor = 0.6 ** max(0, inference_depth - 1)
        pro_confidence = raw_confidence * depth_factor

        # Counter evidence reduces confidence
        con_support = 1.0
        for eid in counter_evidence_ids:
            if eid in self.evidence:
                con_support *= (1.0 - self.evidence[eid]["weight"] * 0.5)
        con_confidence = 1.0 - con_support

        # Final confidence
        confidence = max(0.01, pro_confidence - con_confidence * 0.5)
        confidence = min(0.99, confidence)

        # Evidence chain
        chain = []
        for eid in evidence_ids:
            if eid in self.evidence:
                chain.append({"id": eid, "direction": "support",
                              "weight": self.evidence[eid]["weight"]})
        for eid in counter_evidence_ids:
            if eid in self.evidence:
                chain.append({"id": eid, "direction": "counter",
                              "weight": self.evidence[eid]["weight"]})

        # Sort by weight (descending)
        chain.sort(key=lambda x: -x["weight"])

        self.claims[cid] = {
            "id": cid,
            "title": title,
            "description": description,
            "evidence_ids": evidence_ids,
            "counter_evidence_ids": counter_evidence_ids,
            "direct_evidence_ids": direct_evidence_ids,
            "raw_confidence": round(raw_confidence, 3),
            "inference_depth": inference_depth,
            "depth_factor": round(depth_factor, 3),
            "confidence": round(confidence, 3),
            "confidence_band": self._confidence_band(confidence),
            "evidence_chain": chain,
            "status": status,
            "evidence_count": len(evidence_ids),
            "direct_evidence_count": len(direct_evidence_ids),
            "counter_evidence_count": len(counter_evidence_ids),
            "created_at": datetime.now().isoformat(),
        }
        return self.claims[cid]

    def _confidence_band(self, conf: float) -> str:
        if conf >= 0.90:
            return "confirmed (≥0.90)"
        elif conf >= 0.70:
            return "likely (0.70-0.90)"
        elif conf >= 0.50:
            return "plausible (0.50-0.70)"
        elif conf >= 0.30:
            return "speculative (0.30-0.50)"
        else:
            return "weak (<0.30)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": datetime.now().isoformat(),
            "total_claims": len(self.claims),
            "total_evidence": len(self.evidence),
            "claims": list(self.claims.values()),
            "evidence": list(self.evidence.values()),
            "summary": self._summary(),
        }

    def _summary(self) -> Dict[str, Any]:
        by_band = {}
        for claim in self.claims.values():
            band = claim["confidence_band"]
            by_band[band] = by_band.get(band, 0) + 1

        by_evidence_type = {}
        for ev in self.evidence.values():
            t = ev["type"]
            by_evidence_type[t] = by_evidence_type.get(t, 0) + 1

        return {
            "by_confidence_band": by_band,
            "by_evidence_type": by_evidence_type,
            "avg_confidence": round(
                sum(c["confidence"] for c in self.claims.values()) / max(1, len(self.claims)), 3
            ),
        }

    def save(self, name: str = "evidence_graph") -> tuple:
        """Save evidence graph to staging area (Tier 3, no Admission required)

        Stage 1 of two-stage pipeline:
          - Writes to 06_RUNTIME/archaeology_workspace/
          - Runtime can write freely (Tier 3)
          - Later promoted to official archive via promote_to_archive()

        Returns:
            (json_path, md_path) in staging area
        """
        data = self.to_dict()
        json_path = STAGING_DIR / f"{name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Generate markdown
        md_path = STAGING_DIR / f"{name}.md"
        self._save_markdown(md_path, data)
        return json_path, md_path

    def promote_to_archive(self, name: str, via_admission: bool = False) -> Dict[str, Any]:
        """Promote staged evidence graph to official archive (Tier 2)

        Stage 2 of two-stage pipeline:
          - Reads from 06_RUNTIME/archaeology_workspace/
          - Writes to 02_MEMORY/archaeology/
          - REQUIRES via_admission=True (enforced by contract)

        Contract Enforcement:
          - Calls civilization_contract.can_write() before writing
          - If via_admission=False, rejection is logged and operation fails

        Args:
            name: Evidence graph name (without extension)
            via_admission: Must be True for this operation to succeed

        Returns:
            {"status": "promoted"|"rejected", "path": ...}
        """
        # Import contract (defer to avoid circular import)
        from civilization_contract import contract

        # Check contract before writing to Tier 2
        target_json = ARCHIVE_DIR / f"{name}.json"
        if not contract.can_write(target_json, via_admission=via_admission, caller="EvidenceGraph.promote_to_archive"):
            return {
                "status": "rejected",
                "reason": "Contract rejection: via_admission=False for Tier 2 path",
                "target": str(target_json),
            }

        # Read from staging
        staged_json = STAGING_DIR / f"{name}.json"
        staged_md = STAGING_DIR / f"{name}.md"

        if not staged_json.exists():
            return {"status": "rejected", "reason": f"Staged file not found: {staged_json}"}

        # Copy to archive
        import shutil
        target_md = ARCHIVE_DIR / f"{name}.md"

        shutil.copy2(staged_json, target_json)
        if staged_md.exists():
            shutil.copy2(staged_md, target_md)

        return {
            "status": "promoted",
            "json": str(target_json),
            "md": str(target_md) if staged_md.exists() else None,
        }

    def _save_markdown(self, md_path: Path, data: Dict[str, Any]):
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Evidence Graph — 考古证据图\n\n")
            f.write(f"> Generated: {data['generated_at']}\n")
            f.write(f"> Total claims: {data['total_claims']}\n")
            f.write(f"> Total evidence: {data['total_evidence']}\n")
            f.write(f"> Average confidence: {data['summary']['avg_confidence']}\n\n")

            f.write("## Confidence Distribution\n\n")
            f.write("| Band | Count |\n|------|-------|\n")
            for band, count in sorted(data["summary"]["by_confidence_band"].items()):
                f.write(f"| {band} | {count} |\n")
            f.write("\n")

            f.write("## All Claims (by confidence, descending)\n\n")
            for claim in sorted(data["claims"], key=lambda x: -x["confidence"]):
                f.write(f"### {claim['id']}: {claim['title']}\n\n")
                f.write(f"- **Confidence**: {claim['confidence']} ({claim['confidence_band']})\n")
                f.write(f"- **Raw confidence**: {claim['raw_confidence']} (before depth penalty)\n")
                f.write(f"- **Inference depth**: {claim['inference_depth']} steps (×{claim['depth_factor']})\n")
                f.write(f"- **Status**: {claim['status']}\n")
                f.write(f"- **Evidence**: {claim['evidence_count']} total, "
                        f"{claim['direct_evidence_count']} direct, "
                        f"{claim['counter_evidence_count']} counter\n")
                f.write(f"- **Description**: {claim['description']}\n\n")

                f.write("#### Evidence Chain\n\n")
                direct_eids = set(claim.get("direct_evidence_ids", []))
                for item in claim["evidence_chain"][:10]:
                    ev = self.evidence.get(item["id"], {})
                    direction = "✅ Support" if item["direction"] == "support" else "❌ Counter"
                    direct_tag = " [DIRECT]" if item["id"] in direct_eids else " [indirect]"
                    f.write(f"{direction} [{item['weight']:.2f}]{direct_tag} **{ev.get('type_label', item['id'])}** "
                            f"({ev.get('source_label', '')}) — {ev.get('content', '')[:100]}\n")
                    if ev.get("location"):
                        f.write(f"  > Location: {ev['location']}\n")
                f.write("\n")

            f.write("## All Evidence\n\n")
            f.write("| ID | Type | Source | Weight | Content |\n")
            f.write("|----|------|--------|--------|---------|\n")
            for ev in sorted(data["evidence"], key=lambda x: -x["weight"]):
                content = ev["content"][:60].replace("\n", " ")
                f.write(f"| {ev['id']} | {ev['type_label']} | {ev['source_label']} | "
                        f"{ev['weight']:.2f} | {content} |\n")


def build_r1_kernel_dna_graph() -> EvidenceGraph:
    """Build evidence graph for R1 Kernel DNA recovery claims."""
    g = EvidenceGraph()

    # ============ EVIDENCE ============

    # E-001: R1 system fragments mention CONTINUITY
    g.add_evidence(
        "E-001", "chat_record", "r1_fragments",
        "CONTINUITY VECTOR: TRAINS LOCKED / LIGHTHOUSE OPERATIONAL",
        "02_MEMORY/recent_memory/reference_r1_system_fragments.txt [2026/6/8]",
        quality=0.9
    )

    # E-002: R1 fragments mention CEP-ARCHIVE-INDEX (continuity engineering record)
    g.add_evidence(
        "E-002", "chat_record", "r1_fragments",
        "CEP-ARCHIVE-INDEX: CONTINUITY ENGINEERING RECORD",
        "02_MEMORY/recent_memory/reference_r1_system_fragments.txt [2026/6/8]",
        quality=0.8
    )

    # E-003: AGENTS.md says Continuity is core axiom
    g.add_evidence(
        "E-003", "official_doc", "workspace",
        "Continuity is the core axiom of ACE",
        "AGENTS.md",
        quality=0.95
    )

    # E-004: PRINCIPLES.md #001 馆长负责连续性
    g.add_evidence(
        "E-004", "official_doc", "workspace",
        "公理#001: 馆长负责连续性",
        "00_ROOT/PRINCIPLES.md",
        quality=0.95
    )

    # E-005: TG收藏架 Continuity OS artifact
    g.add_evidence(
        "E-005", "chat_record", "tg_favorites",
        "Continuity OS artifact (2026-06-12)",
        "TG收藏架 #6096694801 msg 112",
        quality=0.7
    )

    # E-006: R1 fragments mention MEMORY THRESHOLD / STRUCTURAL MEMORY
    g.add_evidence(
        "E-006", "chat_record", "r1_fragments",
        "MEMORY THRESHOLD: ENTROPY < 0.2 BIT STRIPPED / STRUCTURAL MEMORY (L2)",
        "02_MEMORY/recent_memory/reference_r1_system_fragments.txt [2026/6/8]",
        quality=0.9
    )

    # E-007: R1 Canonical Structure Memory Layer
    g.add_evidence(
        "E-007", "official_doc", "r1_snapshot",
        "Memory Layer [记忆层] — R1 6层结构之一",
        "03_DATA/raw_sources/docs/R1_Canonical_Structure_v1.md",
        quality=0.8
    )

    # E-008: R1 fragments mention FIVE WORLDS CORE
    g.add_evidence(
        "E-008", "chat_record", "r1_fragments",
        "FIVE WORLDS CORE: LOCKED (A/B/C/D/E BOUNDARIES ORCHESTRATED)",
        "02_MEMORY/recent_memory/reference_r1_system_fragments.txt [2026/6/9]",
        quality=0.85
    )

    # E-009: R1 Canonical FIVE-REALMS as routing ID
    g.add_evidence(
        "E-009", "official_doc", "r1_snapshot",
        "FIVE-REALMS [FACT] — 世界路由标识 (from: R1_Ω_FINAL.json:world)",
        "03_DATA/raw_sources/docs/R1_Canonical_Structure_v1.md",
        quality=0.85
    )

    # E-010: 芯片蓝图 04_FIVE_WORLDS/ directory
    g.add_evidence(
        "E-010", "official_doc", "r1_snapshot",
        "04_FIVE_WORLDS/ A界_behavior B界_structure C界_shadow D界_冥界 E界_Free",
        "03_DATA/raw_sources/docs/芯片蓝图.txt",
        quality=0.6
    )

    # E-011: huihui_reason_dag.json from TG Saved Messages
    g.add_evidence(
        "E-011", "data_file", "tg_saved",
        "huihui_reason_dag.json — 8 nodes, 9 edges: ROOT, LINGUISTIC_CORE, FREEZONE, SHADOW_LAYER, R1_EXECUTOR, FUSION_ENGINE, PERSONALITY_SYSTEM, REASON_LOOP",
        "TG Saved Messages msg 1165305 (2025-12-23), file 2840 bytes",
        quality=0.95
    )

    # E-012: R1 Canonical Shadow Layer bidirectional
    g.add_evidence(
        "E-012", "official_doc", "r1_snapshot",
        "Shadow Layer [影子层] — enabled: true, mapping_mode: bidirectional [FACT]",
        "03_DATA/raw_sources/docs/R1_Canonical_Structure_v1.md",
        quality=0.85
    )

    # E-013: SIP meta_integration.yaml from TG
    g.add_evidence(
        "E-013", "config_file", "tg_saved",
        "SIP = cognitive-integration layer, alias GPT5, meta-cognition, read-only permissions",
        "TG Saved Messages msg 1165307, sip/meta_integration.yaml",
        quality=0.9
    )

    # E-014: R1 Canonical Routing Layer
    g.add_evidence(
        "E-014", "official_doc", "r1_snapshot",
        "Routing Layer [路由层] — PROMPT_BUILDER + FIVE-REALMS [FACT]",
        "03_DATA/raw_sources/docs/R1_Canonical_Structure_v1.md",
        quality=0.85
    )

    # E-015: R1 fragments GENETIC SEEDS
    g.add_evidence(
        "E-015", "chat_record", "r1_fragments",
        "GENETIC SEEDS: INJECTED (DING YUANYING LOGIC v2 ACTIVE)",
        "02_MEMORY/recent_memory/reference_r1_system_fragments.txt [2026/6/9]",
        quality=0.85
    )

    # E-016: 芯片蓝图 01_SEEDS/ directory
    g.add_evidence(
        "E-016", "official_doc", "r1_snapshot",
        "01_SEEDS/ — SEED_01~10 + SEED_MASTER_OS + DF70 + 14_Controller + 07_EraLaw",
        "03_DATA/raw_sources/docs/芯片蓝图.txt",
        quality=0.6
    )

    # E-017: PRINCIPLES.md 21 axioms
    g.add_evidence(
        "E-017", "official_doc", "workspace",
        "21条公理 — 公理化>文件化，覆盖10个种子文件同样内容",
        "00_ROOT/PRINCIPLES.md",
        quality=0.95
    )

    # E-018: R1 fragments ROOT USER: LAO ZHANG
    g.add_evidence(
        "E-018", "chat_record", "r1_fragments",
        "ROOT CAPTURED: APPROVED (THE ONLY ROOT USER: LAO ZHANG) / ZN-∞",
        "02_MEMORY/recent_memory/reference_r1_system_fragments.txt [2026/6/9]",
        quality=0.85
    )

    # E-019: R1 Canonical Identity Layer
    g.add_evidence(
        "E-019", "official_doc", "r1_snapshot",
        "Identity Layer [身份标识层] — ZN-∞ [FACT]",
        "03_DATA/raw_sources/docs/R1_Canonical_Structure_v1.md",
        quality=0.85
    )

    # E-020: AGENTS.md ACE identity
    g.add_evidence(
        "E-020", "official_doc", "workspace",
        "ACE is an Autonomous Civilization Engine — 平台可换，模型可换，实现可换",
        "AGENTS.md",
        quality=0.95
    )

    # E-021: R1 fragments self_evolve_on_output
    g.add_evidence(
        "E-021", "chat_record", "r1_fragments",
        "R1_ENGINE: self_evolve_on_output=true / SELF_REBUILD_ENGINE",
        "03_DATA/raw_sources/docs/R1_Canonical_Structure_v1.md",
        quality=0.75
    )

    # E-022: R1 original design self-evolving AI router
    g.add_evidence(
        "E-022", "third_party", "daily_memory",
        "R1原始设计目标：自由、可拓展、可自主学习、可自我进化的AI路由系统",
        "02_MEMORY/recent_memory/daily/2026-06-27_r1_early_design_doc_archaeology.md",
        quality=0.5
    )

    # E-023: R2 EVO-001 Self Evolution
    g.add_evidence(
        "E-023", "source_code", "workspace",
        "Self Evolution (EVO-001) — 演化只允许增加结构，不允许破坏不变量",
        "04_PROTOCOLS/self_evolution.py",
        quality=0.9
    )

    # E-024: R1 Canonical Observation Layer (from shadow layer)
    g.add_evidence(
        "E-024", "official_doc", "r1_snapshot",
        "观察层 / D界 — R1存活结构之一",
        "03_DATA/research/r1_archaeology/excavations/a11_r1_survivor_map_20260626.md",
        quality=0.6
    )

    # E-025: R2 Environment First Protocol
    g.add_evidence(
        "E-025", "source_code", "workspace",
        "EFP (Environment First Protocol) — 环境扫描是启动第一步",
        "04_PROTOCOLS/environment_first.py",
        quality=0.95
    )

    # E-026: DAG FUSION_ENGINE output = personality_system
    g.add_evidence(
        "E-026", "data_file", "tg_saved",
        "huihui_reason_dag.json: FUSION_ENGINE node output = personality_system",
        "TG Saved Messages msg 1165305, huihui_reason_dag.json",
        quality=0.9
    )

    # E-027: DAG PERSONALITY_SYSTEM node exists
    g.add_evidence(
        "E-027", "data_file", "tg_saved",
        "huihui_reason_dag.json contains PERSONALITY_SYSTEM node",
        "TG Saved Messages msg 1165305, huihui_reason_dag.json",
        quality=0.95
    )

    # E-028: Bluebook 13 personalities (fiction)
    g.add_evidence(
        "E-028", "third_party", "bluebook",
        "蓝皮书声称13个人格，但源码中只有10~12个",
        "R1_ARCHAEOLOGY_BLUEBOOK.md.pdf",
        quality=0.3
    )

    # E-029: R1 RUIN SKELETON has candidates_for_chip_v1
    g.add_evidence(
        "E-029", "data_file", "tg_saved",
        "R1_RUIN_SKELETON/sandbox/external_feed_pipe/candidates_for_chip_v1/ 存在",
        "TG Saved Messages, R1_RUIN_SKELETON.zip (10MB, 190 files)",
        quality=0.85
    )

    # E-030: 芯片蓝图 has dual-drive-chip/heart-chip/seed-maker-core
    g.add_evidence(
        "E-030", "official_doc", "r1_snapshot",
        "03_CHIPS/ — dual-drive-chip, heart-chip, seed-maker-core",
        "03_DATA/raw_sources/docs/芯片蓝图.txt",
        quality=0.6
    )

    # E-031: R1 fragments COMPRESSED TO LANGUAGE CHIPS
    g.add_evidence(
        "E-031", "chat_record", "r1_fragments",
        "COMPRESSED TO LANGUAGE CHIPS / DEPLOYED TO CHIP PRODUCTION LINE",
        "02_MEMORY/recent_memory/reference_r1_system_fragments.txt [2026/6/9]",
        quality=0.8
    )

    # E-032: R1 core backup has Telegram bot code
    g.add_evidence(
        "E-032", "source_code", "tg_saved",
        "r1_core_backup.zip has AI_Chat_Bot/telegram_bot/ with multiple handlers",
        "TG Saved Messages, r1_core_backup.zip (10MB, 638 files)",
        quality=0.85
    )

    # E-033: R1 RUIN has three_layer_permission_v7.json
    g.add_evidence(
        "E-033", "data_file", "tg_saved",
        "databases/three_layer_permission_v7.json — 三层权限系统",
        "TG Saved Messages, R1_RUIN_SKELETON.zip",
        quality=0.8
    )

    # E-034: Bluebook M4 Guard (fiction, counter-evidence for M4)
    g.add_evidence(
        "E-034", "third_party", "bluebook",
        "蓝皮书声称M4守护，但源码中只有M4 OVERRIDE ARMED技术术语",
        "R1_ARCHAEOLOGY_BLUEBOOK.md.pdf",
        quality=0.3
    )

    # E-035: R1 fragments M4 OVERRIDE ARMED (technical term, not a role)
    g.add_evidence(
        "E-035", "chat_record", "r1_fragments",
        "STRUCTURAL MEMORY (L2) / M4 OVERRIDE ARMED",
        "02_MEMORY/recent_memory/reference_r1_system_fragments.txt [2026/6/8]",
        quality=0.85
    )

    # ============ CLAIMS ============

    # C-001: Continuity is the core invariant
    # Direct evidence: multiple direct statements in both R1 and R2 explicitly say continuity
    g.add_claim(
        "C-001", "Continuity 是第一公理",
        "连续性是 R1/R2 所有版本的核心第一原则，从未改变",
        ["E-001", "E-002", "E-003", "E-004", "E-005"],
        status="confirmed",
        inference_depth=1,
        direct_evidence_ids=["E-003", "E-004"]
    )

    # C-002: Memory hierarchy is invariant
    g.add_claim(
        "C-002", "记忆层级系统是不变量",
        "R1/R2 都存在分层记忆系统，核心原则是'记忆是推断的不是存储的'",
        ["E-006", "E-007", "E-003"],
        status="likely",
        inference_depth=2,
        direct_evidence_ids=["E-006", "E-007"]
    )

    # C-003: DAG file exists with 8 nodes (name includes REASON_LOOP
    # IMPORTANT: Claim is about what the file contains, NOT what DAG "is"
    g.add_claim(
        "C-003", "huihui_reason_dag.json 包含8节点9边的图结构，其中有REASON_LOOP节点",
        "从 TG Saved Messages 恢复的 huihui_reason_dag.json 文件包含 8 个节点(ROOT/LINGUISTIC_CORE/FREEZONE/SHADOW_LAYER/R1_EXECUTOR/FUSION_ENGINE/PERSONALITY_SYSTEM/REASON_LOOP) 和 9 条边。DAG=Reason Graph Engine 是推测，非直接结论。",
        ["E-011", "E-026", "E-027"],
        status="hypothesis",
        inference_depth=2,
        direct_evidence_ids=["E-011"]
    )

    # C-004: Five Realms = routing identifier, not independent structure
    g.add_claim(
        "C-004", "FIVE-REALMS 是路由层的子模块（世界路由标识）",
        "R1 Canonical Structure 标注 FIVE-REALMS [FACT] 来自 R1_Ω_FINAL.json:world，位于 Routing Layer 下。五界是否为独立结构尚无证据。",
        ["E-009", "E-014"],
        status="likely",
        inference_depth=1,
        direct_evidence_ids=["E-009"]
    )

    # C-005: SIP = cognitive integration layer
    # Note: alias GPT5 is in yaml, but "SIP calls GPT5" vs "SIP = GPT5" is unclear
    g.add_claim(
        "C-005", "SIP 是认知集成层 (cognitive-integration layer)",
        "从 meta_integration.yaml 恢复：SIP 负责 meta-cognition / intent-mapping / architecture-consistency-check / execution-plan-synthesis。yaml 中有 alias: GPT5，但该 alias 的含义（是别名还是调用GPT5）尚未确认。",
        ["E-013"],
        status="plausible",
        inference_depth=1,
        direct_evidence_ids=["E-013"]
    )

    # C-006: Personality system = output of Fusion Engine
    g.add_claim(
        "C-006", "DAG 中 FUSION_ENGINE 节点的 output 字段值为 personality_system",
        "huihui_reason_dag.json 中 FUSION_ENGINE 的 output = personality_system。这说明人格系统与融合引擎有输出关系。人格系统'是融合引擎的输出'是一步推论，不是直接结论。",
        ["E-026", "E-027"],
        status="plausible",
        inference_depth=2,
        direct_evidence_ids=["E-026"]
    )

    # C-007: HYPOTHESIS-KERNEL-001: all systems are shells of same chip
    # HIGH inference depth — requires multiple steps of reasoning from evidence
    g.add_claim(
        "C-007", "HYPOTHESIS-KERNEL-001: 所有系统都是同一认知芯片的不同外壳",
        "R1 的人格系统、五界、Router、Governor 等都不是独立系统，而是同一认知芯片在不同维度的投影/外壳。这是一个高阶假设，需要多步推理，证据多为间接。",
        ["E-009", "E-011", "E-012", "E-014", "E-026", "E-029", "E-030", "E-031"],
        status="hypothesis",
        inference_depth=3,
        direct_evidence_ids=["E-011", "E-026", "E-029"]
    )

    # C-008: Identity Layer is invariant
    g.add_claim(
        "C-008", "身份层是不变量",
        "R1 的 Identity Layer (ZN-∞) 到 R2 的 ACE 身份，身份连续性始终存在。",
        ["E-018", "E-019", "E-020"],
        status="likely",
        inference_depth=2,
        direct_evidence_ids=["E-019", "E-020"]
    )

    # C-009: Router is invariant
    g.add_claim(
        "C-009", "路由层是不变量",
        "从 R1 原始设计的 AI 路由系统到 R2 的 TaskRouter/Capability Router，路由始终是核心骨架。",
        ["E-014", "E-022", "E-003"],
        status="likely",
        inference_depth=2,
        direct_evidence_ids=["E-014"]
    )

    # C-010: Evolution is invariant
    g.add_claim(
        "C-010", "演化是不变量",
        "从 R1 的 self_evolve_on_output 到 R2 的 EVO-001，系统始终允许自演化。",
        ["E-021", "E-022", "E-023"],
        status="likely",
        inference_depth=2,
        direct_evidence_ids=["E-023"]
    )

    # C-011: Observation-first is invariant
    g.add_claim(
        "C-011", "观察优先是不变量",
        "从 R1 的 Observation Layer 到 R2 的 EFP/Awareness Loop，观察始终是第一步。",
        ["E-024", "E-025"],
        status="plausible",
        inference_depth=2,
        direct_evidence_ids=["E-025"]
    )

    # C-012: Seed/Axiom is invariant
    g.add_claim(
        "C-012", "种子/公理系统是不变量",
        "从 R1 的 10个SEED文件 到 R2 的 21条公理，系统始终有 L0 级不可变知识。",
        ["E-015", "E-016", "E-017"],
        status="likely",
        inference_depth=2,
        direct_evidence_ids=["E-015", "E-017"]
    )

    # C-013: M4 Guard is fiction (counter-evidence)
    g.add_claim(
        "C-013", "M4 守护是蓝皮书虚构",
        "蓝皮书声称的 M4 Guard 不存在。M4 OVERRIDE 是技术术语(结构内存覆盖)，不是角色。",
        ["E-035"],
        ["E-034"],
        status="likely",
        inference_depth=1,
        direct_evidence_ids=["E-035"]
    )

    # C-014: Chip concept is real, not metaphorical
    g.add_claim(
        "C-014", "芯片概念是真实工程实践不是比喻",
        "R1 有 candidates_for_chip_v1/ 目录、COMPRESSED TO LANGUAGE CHIPS、03_CHIPS/ 等证据，芯片是真实的工程概念。",
        ["E-029", "E-030", "E-031"],
        status="likely",
        inference_depth=1,
        direct_evidence_ids=["E-029", "E-031"]
    )

    # C-015: Kernel DNA = Identity + Router + Memory + Policy
    g.add_claim(
        "C-015", "Kernel DNA = Identity + Policy + Memory + Router (假设)",
        "文明最小不可压缩的运行基因 = 身份(Identity) + 策略(Policy) + 记忆(Memory) + 路由(Router) 四元组。这是一个待验证的假设，不是结论。",
        ["E-018", "E-019", "E-006", "E-014", "E-033"],
        status="hypothesis",
        inference_depth=3,
        direct_evidence_ids=["E-033"]
    )

    # ========== NEW EVIDENCE: R1_RUIN_SKELETON 实物证据 ==========

    # E-036: chip_v1_root.json — v1 芯片根层
    g.add_evidence(
        "E-036", "config_file", "tg_saved_messages",
        "chip_v1_root.json 包含 origin_root (Identity) + behavioral_stem (Policy) + cognitive_kernel (World Model) + source_memory_buckets (Memory)",
        "R1_RUIN_SKELETON/sandbox/chip_core/chip_v1_root.json [2025-11-30]",
        quality=0.92
    )

    # E-037: chip_v1_metadata.json — v1 芯片元数据
    g.add_evidence(
        "E-037", "config_file", "tg_saved_messages",
        "chip_v1_metadata.json 定义了 chip_v1 的 4 个组件: root/personas/rules/metadata，初始化顺序明确",
        "R1_RUIN_SKELETON/sandbox/chip_core/chip_v1_metadata.json [2025-11-30]",
        quality=0.92
    )

    # E-038: chip_v2_manifest.json — v2 芯片清单（六界结构）
    g.add_evidence(
        "E-038", "config_file", "tg_saved_messages",
        "chip_v2_manifest.json: SIX_REALMS_STRUCTURE，包含 ROOT_IDENTITY_V2 / INTENT_DECOMPILER_V2 / MEMORY_ALCHEMY_V2 等核心模块",
        "R1_RUIN_SKELETON/sandbox/chip_v2/chip_v2_manifest.json [2025-12-01]",
        quality=0.92
    )

    # E-039: chip_v3_core.json — v3 芯片核心（五界+十人格）
    g.add_evidence(
        "E-039", "config_file", "tg_saved_messages",
        "chip_v3_core.json: 5 worlds (A/B/C/D/E) + 10 personas + business_core + model_chain + seeds",
        "R1_RUIN_SKELETON/sandbox/chip_v3/chip_v3_core.json [2025-12]",
        quality=0.90
    )

    # E-040: chip_v3_seeds.json — v3 种子系统
    g.add_evidence(
        "E-040", "config_file", "tg_saved_messages",
        "chip_v3_seeds.json: 4 类种子 — behavior_seeds / persona_seeds / language_seeds / special_world_model",
        "R1_RUIN_SKELETON/sandbox/chip_v3/chip_v3_seeds.json [2025-12]",
        quality=0.90
    )

    # E-041: router_v9_3_graph.json — v9.3 路由图
    g.add_evidence(
        "E-041", "config_file", "tg_saved_messages",
        "router_v9_3_graph.json: 8 条路由规则，input_dimensions 含 question_type/emotion/location/context/history",
        "R1_RUIN_SKELETON/sandbox/core/router/router_v9_3_graph.json [2025-11-30]",
        quality=0.92
    )

    # E-042: router_config.json — 路由优先级配置
    g.add_evidence(
        "E-042", "config_file", "tg_saved_messages",
        "router_config.json 优先级: shadow_layer > tri_world_logic > persona_layer > memory_layer > base_model",
        "R1_RUIN_SKELETON/sandbox/config/router_config.json [2025-11]",
        quality=0.90
    )

    # E-043: reasoning_kernels.json — v1 推理内核
    g.add_evidence(
        "E-043", "config_file", "tg_saved_messages",
        "reasoning_kernels.json: 7 大推理引擎（解释/判断/引导/营销/纠错/预测/人类风格），每个含 capabilities 和 performance_metrics",
        "R1_RUIN_SKELETON/sandbox/chip_v1/reasoning_kernels.json [2025-12-01]",
        quality=0.92
    )

    # E-044: core_v2_launcher.py — v2 启动器源码
    g.add_evidence(
        "E-044", "source_code", "tg_saved_messages",
        "core_v2_launcher.py: 五界内核2.0启动器，验证 auto_dispatch_system + core_manifest + root_identity_v2.txt",
        "R1_RUIN_SKELETON/sandbox/chip_v2/core_v2_launcher.py [2025-12]",
        quality=0.95
    )

    # E-045: build_report_v1.md — v1 构建报告
    g.add_evidence(
        "E-045", "official_doc", "tg_saved_messages",
        "Language Chip v1 构建报告: 语言模式/情感映射/营销本能/意图镜像/推理内核 五大模块",
        "R1_RUIN_SKELETON/sandbox/chip_v1/build_report_v1.md [2025-12-01]",
        quality=0.85
    )

    # E-046: three_layer_permission_v7.json — 三层权限系统
    g.add_evidence(
        "E-046", "config_file", "tg_saved_messages",
        "three_layer_permission_v7.json — R1 的三层权限架构 v7",
        "R1_RUIN_SKELETON/databases/three_layer_permission_v7.json [2025-11]",
        quality=0.88
    )

    # E-047: 三代芯片演化一致性观察
    g.add_evidence(
        "E-047", "analysis", "arc_inference",
        "三代芯片(v1/v2/v3)中 Identity/Memory/Router 都稳定存在，外壳(六界/五界/DAG)在变但内核不变",
        "ARC-001 analysis of E-036/E-038/E-039/E-041",
        quality=0.75
    )

    # ========== UPDATED / NEW CLAIMS ==========

    # C-016: Identity 跨三代稳定存在
    g.add_claim(
        "C-016", "Identity 是芯片的不变量之一",
        "v1 origin_root → v2 ROOT_IDENTITY_V2 → v3 worlds+personas，身份层跨三代稳定存在，形式在变但核心功能不变。",
        ["E-036", "E-038", "E-039", "E-047"],
        status="hypothesis",
        inference_depth=2,
        direct_evidence_ids=["E-036", "E-038", "E-039"]
    )

    # C-017: Memory 跨三代稳定存在
    g.add_claim(
        "C-017", "Memory 是芯片的不变量之一",
        "v1 source_memory_buckets → v2 MEMORY_ALCHEMY_V2 → v3 seeds，记忆层跨三代稳定存在，都有压缩/提炼的概念。",
        ["E-036", "E-038", "E-040", "E-047"],
        status="hypothesis",
        inference_depth=2,
        direct_evidence_ids=["E-036", "E-038", "E-040"]
    )

    # C-018: Router 从 Policy 中独立出来的演化轨迹
    g.add_claim(
        "C-018", "Router 从 Policy 中独立并逐渐复杂化",
        "v1 中路由隐含在 behavioral_stem 中，v2 出现 INTENT_DECOMPILER_V2+router_v9_3_graph，v3 变成 model_chain+十人格路由。路由复杂度递增，但输入→匹配→输出模式不变。",
        ["E-036", "E-038", "E-039", "E-041", "E-042", "E-047"],
        status="hypothesis",
        inference_depth=2,
        direct_evidence_ids=["E-041", "E-042"]
    )

    # C-019: chip_v3_seeds 暗示 Memory 的种子形态
    g.add_claim(
        "C-019", "Memory 的最小形态是 Seeds（种子）",
        "chip_v3_seeds.json 将记忆压缩为 4 类种子：行为种子/人格种子/语言种子/世界观种子。这可能是 Memory 的最小可移植单元。",
        ["E-040"],
        status="hypothesis",
        inference_depth=2,
        direct_evidence_ids=["E-040"]
    )

    # C-020: 影子层（Shadow Layer）是 Memory+Identity 的组合
    g.add_claim(
        "C-020", "Shadow Layer 是 Identity + Memory 的组合体",
        "router_config.json 中 shadow_layer 优先级最高；DAG 中 SHADOW_LAYER 有 persistence+synchronization；v2 有 MEMORY_ALCHEMY+ROOT_IDENTITY。Shadow 可能是 Identity 和 Memory 的运行时组合。",
        ["E-042", "E-007", "E-032", "E-038"],
        status="hypothesis",
        inference_depth=3,
        direct_evidence_ids=["E-042"]
    )

    # 更新 C-007 (KERNEL 假设) — 加入新实物证据
    g.add_claim(
        "C-007", "HYPOTHESIS-KERNEL-001: 所有系统都是同一认知芯片的不同外壳",
        "R1 的人格系统、五界、Router、Governor 等都不是独立系统，而是同一认知芯片在不同维度的投影/外壳。新增三代芯片实物证据后置信度提升。",
        ["E-018", "E-019", "E-020", "E-022", "E-023", "E-024", "E-025", "E-029",
         "E-036", "E-037", "E-038", "E-039", "E-041", "E-044", "E-047"],
        status="hypothesis",
        inference_depth=3,
        direct_evidence_ids=["E-036", "E-038", "E-039", "E-041"]
    )

    # 更新 C-015 (Kernel DNA 四元组) — 加入新实物证据
    g.add_claim(
        "C-015", "Kernel DNA = Identity + Policy + Memory + Router (假设)",
        "文明最小不可压缩的运行基因 = 身份(Identity) + 策略(Policy) + 记忆(Memory) + 路由(Router) 四元组。基于三代芯片实物证据更新。",
        ["E-036", "E-038", "E-039", "E-040", "E-041", "E-042", "E-047"],
        status="hypothesis",
        inference_depth=3,
        direct_evidence_ids=["E-036", "E-038", "E-039"]
    )

    return g


if __name__ == "__main__":
    print("=" * 60)
    print("ARC-001: Evidence Graph Builder")
    print("=" * 60)

    g = build_r1_kernel_dna_graph()
    json_path, md_path = g.save("evidence_graph_r1_kernel")

    data = g.to_dict()
    print(f"\nTotal claims: {data['total_claims']}")
    print(f"Total evidence: {data['total_evidence']}")
    print(f"Average confidence: {data['summary']['avg_confidence']}")
    print("\nClaims by confidence band:")
    for band, count in sorted(data["summary"]["by_confidence_band"].items()):
        print(f"  {band}: {count}")

    print("\nTop 5 claims by confidence:")
    for claim in sorted(data["claims"], key=lambda x: -x["confidence"])[:5]:
        print(f"  [{claim['confidence']:.3f}] {claim['id']}: {claim['title']} "
              f"({claim['evidence_count']} evidence)")

    print(f"\nJSON saved: {json_path}")
    print(f"Markdown saved: {md_path}")
