#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-010
"""
DEB-001: Multi-Agent Debate — 多智能体辩论
============================================

核心思想:
  不是单个 AI 做决策，而是多个角色分别调查、提出方案、互相验证，
  最后由 Governor 综合决策。

角色:
  - Scout:     发现者，提出"我们应该做什么"
  - Researcher: 研究者，收集证据和外部信息
  - Validator:  验证者，评估证据可信度
  - Governor:   治理者，综合三方意见做最终决策

输入:
  一个来自 Question Center 的问题

输出:
  {
    "question": "...",
    "qid": "Q-001",
    "opinions": [
      {"role": "scout", "proposal": "...", "confidence": 70, "risks": [...]},
      {"role": "researcher", "evidence": [...], "confidence": 65, "conclusion": "..."},
      {"role": "validator", "verdict": "partial", "confidence": 55, "concerns": [...]}
    ],
    "decision": "approved/rejected/deferred",
    "rationale": "...",
    "action": "建议执行的动作"
  }

集成:
  - 与 Question Center 联动：辩论结果生成 Decision
  - 与 RoundTable 联动：最终决策需经过 RoundTable 审计
  - 与 Self Evolution 联动：approved 的决策可能触发代码变更
"""
import os, sys, json, argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from local_miner import call_model
from question_center import QuestionCenter

WORKSPACE = Path(__file__).parent.parent


class Agent:
    """单个智能体角色"""

    def __init__(self, role: str, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt

    def think(self, question: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """基于问题生成角色意见"""
        prompt = f"""{self.system_prompt}

## 当前问题
```json
{json.dumps(question, ensure_ascii=False, indent=2)}
```

## 额外上下文
{context}

## 输出格式
请严格按以下 JSON 格式输出（只输出 JSON）:
{{
  "role": "{self.role}",
  "proposal": "你的核心建议（ scout 必填）",
  "evidence": ["证据1", "证据2"],
  "conclusion": "你的结论（ researcher/validator 必填）",
  "confidence": 0-100,
  "risks": ["风险1"],
  "concerns": ["concern1"]
}}

confidence 标准:
- 90-100: 证据充分，高度确信
- 70-89: 有证据支持，少量不确定性
- 50-69: 证据不足，但有合理推断
- 30-49: 高度不确定，建议暂缓
- 0-29: 证据矛盾或风险过高，建议拒绝
"""
        result = call_model(prompt, max_tokens=500, capability="reasoning")
        if "error" in result:
            return {
                "role": self.role,
                "error": result.get("errors", result.get("error")),
                "confidence": 0,
            }

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            if content.strip().startswith("```"):
                lines = content.strip().split("\n")
                content = "\n".join(lines[1:-1])
            parsed = json.loads(content.strip())
            parsed["role"] = self.role
            parsed["provider"] = result.get("provider")
            parsed["model"] = result.get("model")
            return parsed
        except Exception as e:
            return {
                "role": self.role,
                "raw_response": content,
                "parse_error": str(e),
                "confidence": 0,
            }


class Scout(Agent):
    """Scout: 提出行动方案"""

    def __init__(self):
        super().__init__("scout", """你是 ACE 文明中的 Scout（侦察兵/开拓者）。

你的职责：
1. 基于问题，提出 1-3 个具体可行的行动方案
2. 评估每个方案的收益、成本和风险
3. 推荐最优方案并说明理由

你关注的是"我们应该做什么"。
""")


class Researcher(Agent):
    """Researcher: 收集证据"""

    def __init__(self):
        super().__init__("researcher", """你是 ACE 文明中的 Researcher（研究员/考古学家）。

你的职责：
1. 基于问题，分析已有证据和可能的信息来源
2. 如果涉及代码/配置，说明应该检查什么
3. 如果涉及外部世界，说明应该搜索/借鉴什么
4. 给出结论：这个问题目前是否清楚？还需要什么信息？

你关注的是"我们知道什么，还需要知道什么"。

注意：你目前无法主动联网搜索，只能基于已有知识和问题上下文分析。
""")


class Validator(Agent):
    """Validator: 验证方案"""

    def __init__(self):
        super().__init__("validator", """你是 ACE 文明中的 Validator（验证者/质量监督）。

你的职责：
1. 不直接提出方案，而是审查 Scout 和 Researcher 的意见
2. 找出逻辑漏洞、证据不足、风险被低估的地方
3. 评估：如果按 Scout 的方案执行，失败概率有多高？
4. 给出 verdict：approve / reject / defer（需要更多证据）

你关注的是"这个方案真的可靠吗"。
""")


class Governor:
    """Governor: 综合决策"""

    def decide(self, question: Dict[str, Any], opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于三方意见做最终决策"""
        prompt = f"""你是 ACE 文明中的 Governor（治理者/最终决策者）。

你的职责：综合 Scout、Researcher、Validator 的意见，做出最终决策。

## 问题
```json
{json.dumps(question, ensure_ascii=False, indent=2)}
```

## 各方意见
```json
{json.dumps(opinions, ensure_ascii=False, indent=2)}
```

## 输出格式
请严格按以下 JSON 格式输出（只输出 JSON）:
{{
  "decision": "approved/rejected/deferred",
  "rationale": "不超过 200 字的决策理由",
  "action": "如果 approved，下一步具体执行什么？如果 deferred，还需要什么证据？",
  "priority": "P0/P1/P2"
}}

decision 标准：
- approved: 至少两方 confidence >= 70，且 Validator 没有重大 concerns
- rejected: Validator confidence < 40，或存在无法接受的系统性风险
- deferred: 证据不足，需要 Researcher 补充后再审
"""
        result = call_model(prompt, max_tokens=400, capability="reasoning")
        if "error" in result:
            return self._fallback_decide(question, opinions)

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            if content.strip().startswith("```"):
                lines = content.strip().split("\n")
                content = "\n".join(lines[1:-1])
            parsed = json.loads(content.strip())
            parsed["provider"] = result.get("provider")
            parsed["model"] = result.get("model")
            return parsed
        except Exception:
            return self._fallback_decide(question, opinions)

    def _fallback_decide(self, question: Dict[str, Any], opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """LLM 失败时的规则化决策"""
        confidences = [o.get("confidence", 0) for o in opinions if "error" not in o]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        validator = next((o for o in opinions if o.get("role") == "validator"), {})
        validator_conf = validator.get("confidence", 0)

        if avg_conf >= 70 and validator_conf >= 60:
            decision = "approved"
        elif validator_conf < 40:
            decision = "rejected"
        else:
            decision = "deferred"

        return {
            "decision": decision,
            "rationale": f"平均置信度 {avg_conf:.0f}，Validator 置信度 {validator_conf}。LLM 决策失败，使用规则回退。",
            "action": "根据 decision 执行或补充证据",
            "priority": question.get("priority", "P2"),
        }


class DebateRoom:
    """辩论室 — 组织多智能体辩论"""

    def __init__(self):
        self.scout = Scout()
        self.researcher = Researcher()
        self.validator = Validator()
        self.governor = Governor()
        self.qc = QuestionCenter()

    def _apply_anti_overfit(self, opinions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """反过拟合检查（C-001/C-002/C-003）"""
        for op in opinions:
            if "error" in op or op.get("confidence", 0) == 0:
                continue

            # C-001: 复杂度惩罚 — 信号/证据数量>5时扣confidence
            evidence_count = len(op.get("evidence", []))
            risks_count = len(op.get("risks", []))
            concerns_count = len(op.get("concerns", []))
            total_signals = evidence_count + risks_count + concerns_count
            if total_signals > 5:
                penalty = (total_signals - 5) * 10
                original = op.get("confidence", 50)
                op["confidence"] = max(0, original - penalty)
                op["anti_overfit"] = {
                    "rule": "C-001_complexity_cap",
                    "signals": total_signals,
                    "penalty": penalty,
                    "original_confidence": original,
                }

            # C-003: 脆弱性检测 — 如果只有1条证据，标记fragile
            if evidence_count <= 1 and op.get("confidence", 0) >= 70:
                op["fragile"] = True
                op["confidence"] = max(0, op["confidence"] - 15)
                op.setdefault("anti_overfit", {})
                op["anti_overfit"]["fragile"] = True
                op["anti_overfit"]["fragile_reason"] = "Only 1 evidence, conclusion may be fragile"

        return opinions

    def debate(self, question: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """对一个问题进行完整辩论"""
        print(f"\n[DEBATE] {question.get('qid', '?')} — {question.get('question', '')[:60]}")

        # 1. Scout 提方案
        scout_opinion = self.scout.think(question, context)
        print(f"  Scout: confidence={scout_opinion.get('confidence', 0)}")

        # 2. Researcher 查证据
        researcher_opinion = self.researcher.think(question, context)
        print(f"  Researcher: confidence={researcher_opinion.get('confidence', 0)}")

        # 3. Validator 审查（看到 Scout 和 Researcher 的意见）
        debate_context = context + "\n\n## Scout Opinion\n" + json.dumps(scout_opinion, ensure_ascii=False, indent=2)
        debate_context += "\n\n## Researcher Opinion\n" + json.dumps(researcher_opinion, ensure_ascii=False, indent=2)
        validator_opinion = self.validator.think(question, debate_context)
        print(f"  Validator: confidence={validator_opinion.get('confidence', 0)}")

        opinions = [scout_opinion, researcher_opinion, validator_opinion]

        # 4. 反过拟合检查（C-001/C-002/C-003）
        opinions = self._apply_anti_overfit(opinions)

        # 5. Governor 决策
        decision = self.governor.decide(question, opinions)
        print(f"  Governor: {decision.get('decision')} | {decision.get('action', '')[:80]}")

        result = {
            "qid": question.get("qid", ""),
            "question": question.get("question", ""),
            "timestamp": datetime.now().isoformat(),
            "opinions": opinions,
            "decision": decision.get("decision", "deferred"),
            "rationale": decision.get("rationale", ""),
            "action": decision.get("action", ""),
            "priority": decision.get("priority", question.get("priority", "P2")),
        }

        # 5. 同步到 Question Center
        self._sync_to_question_center(question, result)

        return result

    def _sync_to_question_center(self, question: Dict[str, Any], debate_result: Dict[str, Any]):
        """把辩论结果写入 Question Center"""
        qid = question.get("qid")
        if not qid:
            return

        # 添加为证据
        evidence_text = (
            f"Multi-Agent Debate: decision={debate_result['decision']}. "
            f"Rationale: {debate_result['rationale']}. "
            f"Action: {debate_result['action']}"
        )

        # 找到相关的 experiment 或创建新证据
        # 简单起见，作为问题本身的 evidence
        for q in self.qc.questions:
            if q["qid"] == qid:
                q.setdefault("evidence", []).append({
                    "type": "debate",
                    "text": evidence_text,
                    "opinions": [
                        {"role": o.get("role"), "confidence": o.get("confidence")}
                        for o in debate_result["opinions"]
                    ],
                    "added_at": datetime.now().isoformat(),
                })
                # 如果决策是 approved，生成假设或推进状态
                if debate_result["decision"] == "approved":
                    q["status"] = "researching"
                elif debate_result["decision"] == "rejected":
                    q["status"] = "closed"
                break
        self.qc._save_all()

        # 添加决策记录
        if debate_result["decision"] in ["approved", "rejected"]:
            self.qc.add_decision(
                qid=qid,
                decision_text=debate_result["action"],
                outcome=debate_result["decision"],
                rationale=debate_result["rationale"],
            )

    def debate_batch(self, questions: List[Dict[str, Any]], context: str = "") -> List[Dict[str, Any]]:
        """批量辩论"""
        results = []
        for q in questions:
            try:
                r = self.debate(q, context)
                results.append(r)
            except Exception as e:
                results.append({
                    "qid": q.get("qid", ""),
                    "error": str(e),
                    "decision": "error",
                })
        return results


def main():
    parser = argparse.ArgumentParser(description="DEB-001 Multi-Agent Debate")
    parser.add_argument("--qid", help="Debate a specific question by QID")
    parser.add_argument("--batch", type=int, default=3, help="Debate N open questions")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    qc = QuestionCenter()
    room = DebateRoom()

    if args.qid:
        question = next((q for q in qc.questions if q["qid"] == args.qid), None)
        if not question:
            print(f"Question {args.qid} not found")
            return
        results = [room.debate(question)]
    else:
        open_qs = qc.get_open_questions()[:args.batch]
        results = room.debate_batch(open_qs)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print(f"Debate Results: {len(results)} questions")
        print(f"{'='*60}")
        for r in results:
            print(f"\n{r.get('qid')} → {r.get('decision')}")
            print(f"  Action: {r.get('action', '')}")


if __name__ == "__main__":
    main()
