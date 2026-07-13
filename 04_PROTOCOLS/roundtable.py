"""---
id: PROTO-007
type: protocol
title: "GOV-001 RoundTable — 人格芯片辩论协议"
status: active
source: "R2 Evolution: persona-based red team, fixed attack chain"
created: 2026-07-05
updated: 2026-07-12
confidence: 0.90
lineage:
  - C-007
  - OPS-005
  - CHIP-LINEAGE-001
related: [PROTO-004, PROTO-011, PROTO-012, PROTO-013]
tags: [governance, debate, persona_chip, router, fixed_chain]
archaeology:
  state: evolved
  previous_version: atomic arsenal + defense rules
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-007 (Governance by Debate)
"""
GOV-001: RoundTable — 人格芯片辩论协议
=========================================

架构哲学：
  武器库不增长，人格芯片是固定的。
  真正演化的是 Router —— 知道什么时候派谁上场。

架构：
  Proposal
      │
      ▼
  Router (调度人格)
      │
      ├── Skeptic    怀疑者   → 证据攻击
      ├── Engineer   工程师   → 执行攻击
      ├── Strategist 战略家   → 边界攻击
      ├── Economist  经济学家  → 成本攻击
      └── Guardian   守护者   → 约束攻击
      │
      ▼
  Blue Defense (Defense Case — 5问)
      │
      ▼
  Judge
      │
      ▼
  Experience

固定攻击链（永远五步，不多不少）：
  Step 1: Quick Strike    快速打击   → 结构/格式检查
  Step 2: Evidence Attack 证据攻击   → Skeptic 主责
  Step 3: Boundary Test   边界测试   → Strategist 主责
  Step 4: Stress Test     压力测试   → Engineer 主责
  Step 5: Kill Shot       致命一击   → Guardian 主责

Defense Case（蓝队永远回答5个问题）：
  1. Why it works?     为什么成立？
  2. Any evidence?     有没有证据？
  3. Any history?      有没有历史？
  4. Rollback plan?    有没有回滚？
  5. Side effects?     有没有副作用？
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))

WORKSPACE = Path(__file__).parent.parent
EXPERIENCE_DIR = WORKSPACE / "02_MEMORY" / "experience"


# ============================================================
# 五大人格芯片（Red Team Persona Chips）
# ============================================================
# 每片芯片 = 一种固定的攻击策略
# 不随时间增长，不自动学习新武器
# 演化的是 Router 如何调度它们
# ============================================================

PERSONA_CHIPS = {
    "skeptic": {
        "id": "P-SKEPTIC",
        "name": "Skeptic",
        "chinese_name": "怀疑者",
        "color": "🔴",
        "core_drive": "证据不足则不成立",
        "primary_attack": "evidence",
        "style": "严谨、追问证据、不接受模糊陈述",
        "attack_methods": [
            {"id": "evidence_missing", "name": "证据缺失",
             "desc": "缺乏实证支撑，更多是陈述而非论证",
             "check": lambda ctx: ("evidence" not in ctx.get("content", "").lower()
                                   and "证据" not in ctx.get("content", ""))},
            {"id": "metrics_missing", "name": "指标缺失",
             "desc": "没有可量化的指标，无法评估效果",
             "check": lambda ctx: not any(c.isdigit() for c in ctx.get("content", "")[:500])},
            {"id": "logic_gap", "name": "逻辑跳跃",
             "desc": "推理链条不完整，存在隐含假设",
             "check": lambda ctx: ("因此" not in ctx.get("content", "")
                                   and "所以" not in ctx.get("content", "")
                                   and "because" not in ctx.get("content", "").lower())},
        ],
    },
    "engineer": {
        "id": "P-ENGINEER",
        "name": "Engineer",
        "chinese_name": "工程师",
        "color": "🟠",
        "core_drive": "跑不起来都是空谈",
        "primary_attack": "execution",
        "style": "务实、关注可执行性、找实现漏洞",
        "attack_methods": [
            {"id": "no_impl_path", "name": "无实现路径",
             "desc": "只有目标没有方案，不知道怎么落地",
             "check": lambda ctx: ("方案" not in ctx.get("content", "")
                                   and "实现" not in ctx.get("content", "")
                                   and "行动" not in ctx.get("content", ""))},
            {"id": "single_point_failure", "name": "单点故障",
             "desc": "依赖单一组件或路径，没有冗余",
             "check": lambda ctx: ("fallback" not in ctx.get("content", "").lower()
                                   and "降级" not in ctx.get("content", "")
                                   and "冗余" not in ctx.get("content", ""))},
            {"id": "complexity_risk", "name": "复杂度风险",
             "desc": "引入新依赖或新抽象，增加系统复杂度",
             "check": lambda ctx: ("新增" in ctx.get("content", "")
                                   and ("模块" in ctx.get("content", "")
                                        or "依赖" in ctx.get("content", "")
                                        or "类" in ctx.get("content", "")))},
        ],
    },
    "strategist": {
        "id": "P-STRATEGIST",
        "name": "Strategist",
        "chinese_name": "战略家",
        "color": "🟣",
        "core_drive": "边界之外是什么？",
        "primary_attack": "boundary",
        "style": "全局视角、追问边界、考虑长期影响",
        "attack_methods": [
            {"id": "scope_creep", "name": "范围蔓延",
             "desc": "没有清晰的边界，可能越做越大",
             "check": lambda ctx: ("边界" not in ctx.get("content", "")
                                   and "范围" not in ctx.get("content", "")
                                   and "scope" not in ctx.get("content", "").lower())},
            {"id": "scaling_risk", "name": "扩展性风险",
             "desc": "放大10倍/100倍是否还成立？",
             "check": lambda ctx: ("扩展" not in ctx.get("content", "")
                                   and "scale" not in ctx.get("content", "").lower()
                                   and len(ctx.get("content", "")) < 2000)},
            {"id": "long_term_risk", "name": "长期风险",
             "desc": "短期可行但长期可能成为技术债",
             "check": lambda ctx: ("长期" not in ctx.get("content", "")
                                   and "演进" not in ctx.get("content", "")
                                   and "tech debt" not in ctx.get("content", "").lower())},
        ],
    },
    "economist": {
        "id": "P-ECONOMIST",
        "name": "Economist",
        "chinese_name": "经济学家",
        "color": "🟡",
        "core_drive": "投入产出比合理吗？",
        "primary_attack": "cost",
        "style": "量化思维、成本敏感、关注ROI",
        "attack_methods": [
            {"id": "cost_unknown", "name": "成本不明",
             "desc": "不知道要花多少时间/资源/钱",
             "check": lambda ctx: not any(c.isdigit() for c in ctx.get("content", ""))},
            {"id": "opportunity_cost", "name": "机会成本",
             "desc": "做这个就不能做别的，机会成本是什么？",
             "check": lambda ctx: ("替代" not in ctx.get("content", "")
                                   and "替代方案" not in ctx.get("content", "")
                                   and "tradeoff" not in ctx.get("content", "").lower())},
            {"id": "maintenance_cost", "name": "维护成本",
             "desc": "上线后谁来维护？维护成本多高？",
             "check": lambda ctx: ("维护" not in ctx.get("content", "")
                                   and "运维" not in ctx.get("content", "")
                                   and "maintenance" not in ctx.get("content", "").lower())},
        ],
    },
    "guardian": {
        "id": "P-GUARDIAN",
        "name": "Guardian",
        "chinese_name": "守护者",
        "color": "🟢",
        "core_drive": "不能违反约束和原则",
        "primary_attack": "constraint",
        "style": "守规矩、查合规、关注系统稳定性",
        "attack_methods": [
            {"id": "constraint_violation", "name": "约束冲突",
             "desc": "是否违反已知的约束或原则？",
             "check": lambda ctx: (any(f in ctx.get("path", "") for f in
                                        ["PRINCIPLES", "AGENTS", "bootstrap"])
                                   and "新增" in ctx.get("content", ""))},
            {"id": "stability_risk", "name": "稳定性风险",
             "desc": "改动是否影响系统稳定性？",
             "check": lambda ctx: ("核心" in ctx.get("content", "")
                                   and "修改" in ctx.get("content", ""))},
            {"id": "no_rollback", "name": "无回滚方案",
             "desc": "出问题了怎么回滚？",
             "check": lambda ctx: ("回滚" not in ctx.get("content", "")
                                   and "rollback" not in ctx.get("content", "").lower()
                                   and "恢复" not in ctx.get("content", ""))},
        ],
    },
}


# ============================================================
# 固定攻击链（永远五步，不多不少）
# ============================================================

FIXED_ATTACK_CHAIN = [
    {
        "step": 1,
        "name": "Quick Strike",
        "chinese": "快速打击",
        "primary_persona": "engineer",
        "supporting_personas": ["skeptic"],
        "focus": "结构/格式/表面问题",
        "goal": "快速过滤掉明显不行的提案",
    },
    {
        "step": 2,
        "name": "Evidence Attack",
        "chinese": "证据攻击",
        "primary_persona": "skeptic",
        "supporting_personas": ["economist"],
        "focus": "证据/数据/指标",
        "goal": "检验是否有真凭实据",
    },
    {
        "step": 3,
        "name": "Boundary Test",
        "chinese": "边界测试",
        "primary_persona": "strategist",
        "supporting_personas": ["guardian"],
        "focus": "边界/范围/长期影响",
        "goal": "探测边界和长期风险",
    },
    {
        "step": 4,
        "name": "Stress Test",
        "chinese": "压力测试",
        "primary_persona": "engineer",
        "supporting_personas": ["strategist", "economist"],
        "focus": "极端情况/复杂度/扩展性",
        "goal": "在压力下是否还成立",
    },
    {
        "step": 5,
        "name": "Kill Shot",
        "chinese": "致命一击",
        "primary_persona": "guardian",
        "supporting_personas": ["skeptic"],
        "focus": "约束/合规/致命缺陷",
        "goal": "最后检查：有没有原则性问题",
    },
]


# ============================================================
# Router：人格调度器
# ============================================================
# Router 的职责：根据提案类型，决定每一步派谁主攻
# 这是真正应该演化的部分 —— 调度策略可以学习，
# 但人格芯片本身是固定的
# ============================================================

class DebateRouter:
    """辩论调度器 —— 知道什么时候派谁上场"""

    def __init__(self):
        self.personas = PERSONA_CHIPS
        self.attack_chain = FIXED_ATTACK_CHAIN

    def classify_proposal(self, context: Dict[str, Any]) -> str:
        """判断提案类型，用于选择主攻人格"""
        content = context.get("content", "")
        path = context.get("path", "")
        source = context.get("source", "")

        # 约束/原则类 → Guardian 主攻
        if any(k in path for k in ["constraint", "PRINCIPLE", "protocol", "PROTO"]) or \
           any(k in content for k in ["约束", "原则", "合规", "违反"]):
            return "constraint_proposal"

        # 实现/工程类 → Engineer 主攻
        if any(k in path for k in ["engine", "worker", "data", "router"]) or \
           any(k in content for k in ["实现", "代码", "技术", "架构"]):
            return "engineering_proposal"

        # 研究/假设类 → Skeptic 主攻
        if source in ("question_center", "self_learning") or \
           any(k in content for k in ["假设", "研究", "探索", "猜想"]):
            return "research_proposal"

        # 战略/方向类 → Strategist 主攻
        if any(k in content for k in ["战略", "方向", "规划", "长期"]):
            return "strategy_proposal"

        # 默认：综合评估
        return "general_proposal"

    def select_primary_persona(self, step_idx: int, proposal_type: str) -> str:
        """为某一步选择主攻人格

        基础策略：按固定攻击链的 primary_persona
        调整策略：根据提案类型，在某些步骤换主攻
        """
        base_step = self.attack_chain[step_idx]
        primary = base_step["primary_persona"]

        # 根据提案类型微调
        if proposal_type == "constraint_proposal" and step_idx >= 3:
            primary = "guardian"  # 约束类提案，后期 Guardian 提前接管
        elif proposal_type == "engineering_proposal" and step_idx <= 2:
            primary = "engineer"  # 工程类提案，前几步 Engineer 猛攻
        elif proposal_type == "research_proposal" and step_idx == 1:
            primary = "skeptic"  # 研究类提案，上来就 Skeptic 查证据

        return primary

    def get_persona_for_step(self, step_idx: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取某一步的主攻人格信息"""
        proposal_type = self.classify_proposal(context)
        primary_id = self.select_primary_persona(step_idx, proposal_type)
        persona = self.personas.get(primary_id, self.personas["skeptic"])
        return {
            "persona_id": primary_id,
            "persona": persona,
            "proposal_type": proposal_type,
            "step": self.attack_chain[step_idx],
        }


# ============================================================
# 蓝队 Defense Case（永远回答5个问题）
# ============================================================

class DefenseCase:
    """蓝队防御答辩 —— 不是空口说支持，而是做 Defense Case"""

    DEFENSE_QUESTIONS = [
        ("why", "为什么成立？ — 核心理由和逻辑"),
        ("evidence", "有没有证据？ — 数据/案例/历史经验"),
        ("history", "有没有历史？ — 之前谁做过，结果如何"),
        ("rollback", "有没有回滚？ — 出问题了怎么办"),
        ("side_effects", "有没有副作用？ — 潜在风险和影响"),
    ]

    def build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """构建 Defense Case"""
        content = context.get("content", "")
        path = context.get("path", "")
        answers = {}
        strengths = []
        weaknesses = []

        # Q1: 为什么成立？
        has_structure = content.strip().startswith("#") or content.strip().startswith("---")
        has_core_logic = any(k in content for k in ["因此", "所以", "因为", "thus", "therefore"])
        answers["why"] = {
            "strength": "strong" if (has_structure and has_core_logic) else "weak",
            "details": "有清晰的结构和逻辑链条" if (has_structure and has_core_logic)
                       else "结构或逻辑不完整",
        }
        if has_structure:
            strengths.append("结构清晰")
        else:
            weaknesses.append("缺乏结构")

        # Q2: 有没有证据？
        has_evidence = "evidence" in content.lower() or "证据" in content
        has_metrics = any(c.isdigit() for c in content[:500])
        answers["evidence"] = {
            "strength": "strong" if (has_evidence and has_metrics) else
                        ("medium" if has_evidence or has_metrics else "weak"),
            "details": "有实证和量化指标" if (has_evidence and has_metrics)
                       else ("有部分证据" if has_evidence or has_metrics
                             else "缺乏实证支撑"),
        }
        if has_evidence:
            strengths.append("有证据支撑")
        else:
            weaknesses.append("缺乏证据")

        # Q3: 有没有历史？
        has_lineage = "lineage" in content.lower() or "related" in content.lower() or "关联" in content
        has_history = "历史" in content or "之前" in content
        answers["history"] = {
            "strength": "strong" if (has_lineage and has_history) else
                        ("medium" if has_lineage else "weak"),
            "details": "有明确世系和历史参考" if (has_lineage and has_history)
                       else ("有世系记录" if has_lineage else "缺乏历史参考"),
        }
        if has_lineage:
            strengths.append("可追溯")
        else:
            weaknesses.append("缺乏历史")

        # Q4: 有没有回滚？
        has_rollback = any(k in content for k in ["回滚", "降级", "fallback", "rollback"])
        has_redundancy = any(k in content for k in ["冗余", "备份", "容灾"])
        answers["rollback"] = {
            "strength": "strong" if (has_rollback or has_redundancy) else "weak",
            "details": "有回滚/降级方案" if (has_rollback or has_redundancy)
                       else "没有明确的回滚方案",
        }
        if has_rollback or has_redundancy:
            strengths.append("有回滚方案")
        else:
            weaknesses.append("无回滚方案")

        # Q5: 有没有副作用？
        has_side_effects = any(k in content for k in ["副作用", "风险", "代价", "tradeoff"])
        answers["side_effects"] = {
            "strength": "strong" if has_side_effects else "weak",
            "details": "考虑了副作用和权衡" if has_side_effects
                       else "没有讨论潜在副作用",
        }
        if has_side_effects:
            strengths.append("考虑了副作用")
        else:
            weaknesses.append("忽略副作用")

        # 计算防御强度
        strong_count = sum(1 for a in answers.values() if a["strength"] == "strong")
        defense_score = strong_count / len(answers)

        return {
            "questions": self.DEFENSE_QUESTIONS,
            "answers": answers,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "defense_score": round(defense_score, 2),
            "verdict": "strong" if defense_score >= 0.6 else ("medium" if defense_score >= 0.4 else "weak"),
        }


# ============================================================
# 辩论引擎
# ============================================================

class DebateEngine:
    """人格芯片辩论引擎"""

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        self.router = DebateRouter()
        self.defense_case = DefenseCase()
        self.debate_history: List[Dict[str, Any]] = []

    def debate_topic(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """对一个话题进行辩论 — 固定5步攻击链"""
        if context is None:
            context = {}

        debate_id = f"debate_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        start_time = datetime.now()

        proposal_type = self.router.classify_proposal(context)

        # 蓝队先做 Defense Case
        defense = self.defense_case.build(context)

        # 5步攻击链
        steps = []
        cumulative_damage = 0.0  # 红队累积伤害 0~1
        cumulative_defense = defense["defense_score"]  # 蓝队初始防御

        for step_idx, step_info in enumerate(FIXED_ATTACK_CHAIN):
            step_result = self._do_step(step_idx, step_info, topic, context, proposal_type)
            steps.append(step_result)

            # 累积伤害
            damage = step_result.get("damage", 0)
            cumulative_damage = min(1.0, cumulative_damage + damage * 0.2)

            # 如果某一步伤害为0，说明完全没打中，后续步骤伤害递减
            if damage == 0 and step_idx > 0:
                cumulative_damage *= 0.9  # 未命中，累积伤害衰减

            # 如果差距已经很大，提前结束（但至少走3步）
            if step_idx >= 2 and abs(cumulative_defense - cumulative_damage) > 0.5:
                break

        # 最终裁决
        final_score = cumulative_defense - cumulative_damage
        if final_score >= 0.2:
            verdict = "approved"
        elif final_score <= -0.2:
            verdict = "rejected"
        else:
            verdict = "pending"

        # 信心度：差距越大越有信心
        confidence = min(1.0, abs(final_score) * 2 + 0.2)

        # 提取关键论点
        key_points = []
        for step in steps:
            for arg in step.get("red_arguments", [])[:1]:
                key_points.append(f"🔴 {step['step_name']}: {arg[:50]}")
        for s in defense.get("strengths", [])[:2]:
            key_points.append(f"🔵 {s}")

        result = {
            "debate_id": debate_id,
            "topic": topic,
            "started_at": start_time.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "proposal_type": proposal_type,
            "steps_completed": len(steps),
            "steps_total": len(FIXED_ATTACK_CHAIN),
            "steps": steps,
            "defense_case": defense,
            "verdict": verdict,
            "confidence": round(confidence, 2),
            "cumulative_damage": round(cumulative_damage, 3),
            "cumulative_defense": round(cumulative_defense, 3),
            "final_score": round(final_score, 3),
            "key_points": key_points,
            "method": "persona_chip_based",
        }

        # 沉淀经验
        self._sediment_experience(result, context)
        self.debate_history.append(result)
        return result

    def _do_step(
        self,
        step_idx: int,
        step_info: Dict[str, Any],
        topic: str,
        context: Dict[str, Any],
        proposal_type: str,
    ) -> Dict[str, Any]:
        """执行攻击链的一步"""
        persona_info = self.router.get_persona_for_step(step_idx, context)
        persona = persona_info["persona"]
        primary_id = persona_info["persona_id"]

        # 主攻人格发起攻击
        red_arguments = []
        hits = 0
        total_attacks = 0

        for method in persona.get("attack_methods", []):
            total_attacks += 1
            try:
                if method["check"](context):
                    red_arguments.append(method["desc"])
                    hits += 1
            except Exception:
                pass

        # 助攻人格补一刀（最多1个）
        for supp_id in step_info.get("supporting_personas", [])[:1]:
            if supp_id == primary_id:
                continue
            supp_persona = PERSONA_CHIPS.get(supp_id)
            if not supp_persona:
                continue
            for method in supp_persona.get("attack_methods", [])[:1]:
                total_attacks += 1
                try:
                    if method["check"](context):
                        red_arguments.append(f"[{supp_persona['name']}] {method['desc']}")
                        hits += 0.5  # 助攻算半分
                        break
                except Exception:
                    pass

        # 计算这一步的伤害值
        damage = hits / max(total_attacks, 1) if total_attacks > 0 else 0

        return {
            "step": step_idx + 1,
            "step_name": step_info["chinese"],
            "step_english": step_info["name"],
            "focus": step_info["focus"],
            "primary_persona": primary_id,
            "primary_persona_name": persona["name"],
            "red_arguments": red_arguments,
            "hits": hits,
            "total_attacks": total_attacks,
            "damage": round(damage, 3),
        }

    def _sediment_experience(self, result: Dict[str, Any], context: Dict[str, Any]):
        """沉淀辩论经验"""
        try:
            EXPERIENCE_DIR.mkdir(parents=True, exist_ok=True)
            exp = {
                "type": "debate_result",
                "debate_id": result["debate_id"],
                "topic": result["topic"],
                "verdict": result["verdict"],
                "confidence": result["confidence"],
                "proposal_type": result["proposal_type"],
                "steps_completed": result["steps_completed"],
                "key_points": result.get("key_points", []),
                "defense_score": result["cumulative_defense"],
                "attack_damage": result["cumulative_damage"],
                "source": context.get("path", "") or context.get("source", ""),
                "timestamp": datetime.now().isoformat(),
                "analysis": f"辩论裁决: {result['verdict']} (置信度 {result['confidence']:.0%})。"
                           f"防御分 {result['cumulative_defense']:.2f} vs 伤害 {result['cumulative_damage']:.2f}",
            }
            fname = f"exp_debate_{result['debate_id']}.json"
            with open(EXPERIENCE_DIR / fname, "w", encoding="utf-8") as f:
                json.dump(exp, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def debate_asset(self, asset_path: str) -> Dict[str, Any]:
        """对一个文件资产进行辩论"""
        p = WORKSPACE / asset_path
        if not p.exists():
            return {"error": f"not found: {asset_path}"}
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return {"error": str(e)}

        context = {
            "path": asset_path,
            "content": content,
            "size": len(content),
            "lines": len(content.split("\n")),
            "source": "asset_file",
        }
        result = self.debate_topic(f"审议资产: {asset_path}", context)
        result["asset_path"] = asset_path
        return result

    def debate_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """对一个假设进行辩论"""
        context = {
            "content": hypothesis.get("hypothesis", hypothesis.get("description", "")),
            "path": f"question_center/{hypothesis.get('qid', 'unknown')}/{hypothesis.get('hid', 'unknown')}",
            "source": "question_center",
            "hypothesis_id": hypothesis.get("hid", ""),
            "question_id": hypothesis.get("qid", ""),
            "confidence": hypothesis.get("confidence", 0),
            "actions": hypothesis.get("actions", hypothesis.get("reinforce_actions", [])),
        }
        topic = f"评估假设: {hypothesis.get('hypothesis', hypothesis.get('description', 'unknown'))}"
        result = self.debate_topic(topic, context)
        result["hypothesis"] = hypothesis.get("hid", "")
        result["question"] = hypothesis.get("qid", "")
        return result

    def format_debate_report(self, result: Dict[str, Any]) -> str:
        """格式化辩论报告"""
        lines = []
        lines.append("=" * 64)
        lines.append(f"  🧠⚔️ DEBATE — {result.get('debate_id', '?')}")
        lines.append("=" * 64)
        lines.append(f"  议题: {result.get('topic', '?')}")
        lines.append(f"  类型: {result.get('proposal_type', '?')}")
        lines.append(f"  模式: 人格芯片 + 固定5步攻击链")
        lines.append(f"  步数: {result.get('steps_completed', '?')}/{result.get('steps_total', '?')}")
        lines.append(f"  耗时: {result.get('duration_seconds', 0):.2f}s")
        lines.append("")

        verdict = result.get("verdict", "?")
        if verdict == "approved":
            icon = "✅"
        elif verdict == "rejected":
            icon = "❌"
        else:
            icon = "⏳"
        lines.append(f"  裁决: {icon} {verdict.upper()}  (置信度 {result.get('confidence', 0):.0%})")
        lines.append(f"  防御: 🛡️ {result.get('cumulative_defense', 0):.2f}  "
                     f"vs  攻击: ⚔️ {result.get('cumulative_damage', 0):.2f}  "
                     f"→ 净值: {result.get('final_score', 0):+.2f}")
        lines.append("")

        # Defense Case
        dc = result.get("defense_case", {})
        lines.append(f"  🔵 Defense Case ({dc.get('verdict', '?')}):")
        answers = dc.get("answers", {})
        for qid, qtext in DefenseCase.DEFENSE_QUESTIONS:
            a = answers.get(qid, {})
            strength = a.get("strength", "?")
            s_icon = "✅" if strength == "strong" else ("⚠️" if strength == "medium" else "❌")
            lines.append(f"    {s_icon} Q:{qtext.split('—')[0].strip()}")
            lines.append(f"       {a.get('details', '')}")
        lines.append("")

        # 攻击链
        lines.append("  🔴 攻击链:")
        for step in result.get("steps", []):
            dmg = step.get("damage", 0)
            dmg_bar = "█" * int(dmg * 10) + "░" * (10 - int(dmg * 10))
            persona = PERSONA_CHIPS.get(step.get("primary_persona", ""), {})
            p_name = persona.get("chinese_name", step.get("primary_persona", "?"))
            lines.append(f"    Step {step['step']}: {step['step_name']}  "
                         f"({p_name} 主攻)")
            lines.append(f"           伤害: {dmg_bar} {dmg:.0%}")
            if step.get("red_arguments"):
                lines.append(f"           命中: {step['red_arguments'][0][:50]}")
        lines.append("")

        lines.append("  设计哲学:")
        lines.append("    武器库不增长 → 人格芯片是固定的")
        lines.append("    真正演化的是 Router → 知道什么时候派谁上场")
        lines.append("=" * 64)
        return "\n".join(lines)


# ============================================================
# Question Center 辩论集成
# ============================================================

def debate_open_questions(priority: str = "P0", max_debates: int = 3) -> Dict[str, Any]:
    """对 Question Center 中的高优先级问题发起辩论"""
    try:
        from question_center import QuestionCenter
        qc = QuestionCenter()
    except Exception:
        return {"error": "QuestionCenter not available"}

    engine = DebateEngine(use_llm=False)
    results = []
    debated = 0

    for q in qc.questions:
        if debated >= max_debates:
            break
        if q.get("status") != "open":
            continue
        q_prio = q.get("priority", "P2")

        # 优先级过滤
        if priority == "P0" and q_prio != "P0":
            continue
        if priority in ("P1", "P2") and q_prio == "P2":
            continue

        # 收集这个问题的所有假设
        question_hypos = [
            h for h in qc.hypotheses
            if h.get("hid") in q.get("hypotheses", [])
        ]

        # 如果没有假设，自动从问题文本生成一个默认假设
        if not question_hypos:
            default_hypo = {
                "hid": f"auto_{q['qid']}",
                "hypothesis": f"该问题确实需要关注并采取行动：{q['question']}",
                "confidence": 0.5,
                "status": "proposed",
            }
            question_hypos = [default_hypo]

        for hypo in question_hypos:
            if debated >= max_debates:
                break
            if hypo.get("status") in ("debated", "approved", "rejected",
                                       "debated_approved", "debated_rejected"):
                continue

            hypo_with_qid = dict(hypo)
            hypo_with_qid["qid"] = q["qid"]

            result = engine.debate_hypothesis(hypo_with_qid)
            results.append(result)
            debated += 1

            if not hypo.get("hid", "").startswith("auto_"):
                verdict = result.get("verdict", "pending")
                if verdict in ("approved", "rejected"):
                    hypo["status"] = f"debated_{verdict}"
                else:
                    hypo["status"] = "debated"
                qc._save_all()

    return {
        "total_debated": len(results),
        "priority_threshold": priority,
        "results": results,
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="GOV-001 RoundTable — 人格芯片辩论")
    parser.add_argument("--asset", help="审议文件资产")
    parser.add_argument("--topic", help="直接辩论一个话题")
    parser.add_argument("--hypothesis", help="辩论某个假设 (hid)")
    parser.add_argument("--question-center", action="store_true",
                        help="对 Question Center 的高优问题发起辩论")
    parser.add_argument("--priority", default="P0", choices=["P0", "P1", "P2"],
                        help="优先级阈值 (default: P0)")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--llm", action="store_true", help="使用 LLM 辅助辩论")
    args = parser.parse_args()

    engine = DebateEngine(use_llm=args.llm)

    if args.asset:
        result = engine.debate_asset(args.asset)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print(engine.format_debate_report(result))

    elif args.topic:
        result = engine.debate_topic(args.topic)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print(engine.format_debate_report(result))

    elif args.hypothesis:
        try:
            from question_center import QuestionCenter
            qc = QuestionCenter()
            hypo = next((h for h in qc.hypotheses if h.get("hid") == args.hypothesis), None)
            if not hypo:
                print(f"未找到假设: {args.hypothesis}")
                return
            result = engine.debate_hypothesis(hypo)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
            else:
                print(engine.format_debate_report(result))
        except Exception as e:
            print(f"Error: {e}")

    elif args.question_center:
        result = debate_open_questions(priority=args.priority)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print(f"辩论了 {result.get('total_debated', 0)} 个假设")
            for r in result.get("results", []):
                verdict = r.get("verdict", "?")
                icon = "✅" if verdict == "approved" else "❌" if verdict == "rejected" else "⏳"
                print(f"  {icon} {r.get('topic', '?')[:50]}... → {verdict}")

    else:
        parser.print_help()
        print()
        print("示例:")
        print("  python roundtable.py --asset 04_PROTOCOLS/self_learning_engine.py")
        print("  python roundtable.py --topic '是否应该引入多Agent架构？'")
        print("  python roundtable.py --question-center --priority P1")


if __name__ == "__main__":
    main()
