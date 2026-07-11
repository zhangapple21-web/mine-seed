#!/usr/bin/env python3
"""
QE-002: Question Engine — 问题生成引擎
=========================================

核心区别:
  旧 QuestionGenerator: 基于硬规则从 Observation 映射到 Question
  新 QuestionEngine:   基于 LLM 理解 Observation 的上下文，生成"为什么值得调查"的问题

执行语义:
  输入: Observation + 系统当前状态 + 历史问题池
  输出: Question 候选列表，每个问题包含:
    - question: 为什么/是什么/是否
    - motivation: 为什么这个问题值得现在研究
    - approach: 建议的研究路径
    - expected_value: 预期收益
    - priority: P0/P1/P2
    - capability: 需要哪种能力来回答

去重策略:
  - 语义去重: 基于 Observation 的 source+category+title 生成 fingerprint
  - 历史去重: 如果相似问题已在 Question Center 且状态为 open/researching，则更新而不是新建
  - 问题不是按 category 一对一，而是按"异常"一对一
"""
import os, sys, json, hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from local_miner import call_model
from question_center import QuestionCenter

WORKSPACE = Path(__file__).parent.parent


class QuestionEngine:
    """问题生成引擎 — 把 Observation 变成值得研究的问题"""

    # 低价值 category — 即使观察到也不生成问题
    IGNORED_CATEGORIES = {"provider_ok", "models_available", "git_log"}

    # 默认优先级映射（可被 LLM 覆盖）
    DEFAULT_PRIORITY = {
        "provider_down": "P0",
        "provider_missing": "P0",
        "module_missing": "P0",
        "heartbeat_failure": "P0",
        "api_error": "P1",
        "config_change": "P1",
        "stale_repo": "P1",
        "file_deleted": "P1",
        "new_files": "P2",
        "file_change": "P2",
        "trending_repo": "P2",
    }

    def __init__(self, qc: Optional[QuestionCenter] = None):
        self.qc = qc or QuestionCenter()

    def _fingerprint(self, obs: dict) -> str:
        """为 Observation 生成语义指纹，用于去重"""
        text = f"{obs.get('source', '')}:{obs.get('category', '')}:{obs.get('title', '')}"
        return hashlib.md5(text.encode("utf-8")).hexdigest()[:12]

    def _load_recent_state(self) -> str:
        """加载最近系统状态摘要"""
        state_file = WORKSPACE / "CURRENT_STATE.md"
        if state_file.exists():
            content = state_file.read_text(encoding="utf-8")
            # 只取前 3000 字符，避免 prompt 过长
            return content[:3000]
        return "No CURRENT_STATE.md available."

    def _load_open_questions(self) -> List[Dict]:
        """加载当前开放问题，避免重复生成"""
        return self.qc.get_open_questions()

    def generate(self, observation: dict) -> Optional[Dict[str, Any]]:
        """从单个 Observation 生成问题"""
        category = observation.get("category", "")
        if category in self.IGNORED_CATEGORIES:
            return None

        fingerprint = self._fingerprint(observation)

        # 检查是否已存在相似开放问题
        open_qs = self._load_open_questions()
        for q in open_qs:
            # 如果已有问题的来源 observation 指纹相同，则更新而非新建
            if q.get("source_fingerprint") == fingerprint:
                return {
                    "action": "update_existing",
                    "qid": q["qid"],
                    "reason": "Similar question already open",
                }

        # 构建 prompt
        state_summary = self._load_recent_state()
        open_questions_text = "\n".join([
            f"- {q['qid']} [{q['priority']}]: {q['question']}"
            for q in open_qs[:10]
        ]) or "No open questions."

        prompt = f"""你是 ACE 自主研究系统的 Question Engine。

你的任务：基于环境观察，生成一个值得系统自主研究的问题。

不是简单描述观察，而是要追问"为什么"、"这意味着什么"、"我们应该弄清楚什么"。

## 系统当前状态
{state_summary}

## 当前已开放的问题（避免重复）
{open_questions_text}

## 新的环境观察
```json
{json.dumps(observation, ensure_ascii=False, indent=2)}
```

## 输出格式
请严格按以下 JSON 格式输出（只输出 JSON，不要有 markdown 代码块）:
{{
  "question": "具体问题，以'为什么'、'是什么'、'是否应该'开头",
  "motivation": "为什么这个问题现在值得研究？不研究会怎么样？",
  "approach": "建议的研究路径：查什么、比什么、验证什么",
  "expected_value": "回答这个问题后，系统能获得什么？",
  "priority": "P0/P1/P2 之一",
  "capability": "需要的能力：research/archaeology/reasoning/one_shot 之一"
}}

判定优先级标准：
- P0: 系统可能中断、数据无法获取、安全/资金风险
- P1: 影响系统效率、发现新的重要机会、需要配置/架构决策
- P2: 观察性、探索性、可延后研究

如果观察不值得研究，输出：{{"skip": true, "reason": "..."}}
"""

        result = call_model(prompt, max_tokens=400, capability="reasoning")
        if "error" in result:
            # LLM 失败时回退到默认规则
            return self._fallback_generate(observation, fingerprint)

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            # 清理可能的 markdown 代码块
            if content.strip().startswith("```"):
                lines = content.strip().split("\n")
                content = "\n".join(lines[1:-1])
            parsed = json.loads(content.strip())
        except Exception:
            # 解析失败也回退
            return self._fallback_generate(observation, fingerprint)

        if parsed.get("skip"):
            return None

        priority = parsed.get("priority", self.DEFAULT_PRIORITY.get(category, "P2"))
        capability = parsed.get("capability", "research")

        return {
            "question": parsed["question"],
            "motivation": parsed.get("motivation", ""),
            "approach": parsed.get("approach", ""),
            "expected_value": parsed.get("expected_value", ""),
            "priority": priority,
            "capability": capability,
            "source_observation": observation,
            "source_fingerprint": fingerprint,
            "timestamp": datetime.now().isoformat(),
        }

    def _fallback_generate(self, observation: dict, fingerprint: str) -> Dict[str, Any]:
        """LLM 失败时的回退规则"""
        category = observation.get("category", "")
        title = observation.get("title", "")
        priority = self.DEFAULT_PRIORITY.get(category, "P2")

        motivations = {
            "provider_down": "数据源不可用会导致系统依赖该数据的功能失败",
            "provider_missing": "缺少关键依赖可能使部分模块无法运行",
            "module_missing": "核心模块缺失会中断 Runtime",
            "file_deleted": "文件删除可能是误操作，需要确认是否影响系统",
            "new_files": "新文件可能包含未治理的原始数据或新资产",
            "file_change": "文件变更可能破坏不变量或引入新行为",
            "config_change": "配置变更会改变系统行为，需要审计",
            "stale_repo": "仓库停滞说明 curator 或同步机制可能失效",
            "api_error": "API 错误会影响 Provider 路由和 fallback 链",
            "trending_repo": "外部趋势可能给 ACE 能力图谱带来新机会",
        }

        return {
            "question": f"为什么 {title}？是否需要处理？",
            "motivation": motivations.get(category, "环境观察出现异常，需要理解原因"),
            "approach": "检查相关日志、配置文件、历史状态，必要时调用 Researcher 深入分析",
            "expected_value": "避免系统中断或错过重要机会",
            "priority": priority,
            "capability": "research",
            "source_observation": observation,
            "source_fingerprint": fingerprint,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_batch(self, observations: List[dict]) -> List[Dict[str, Any]]:
        """批量生成问题，自动去重"""
        results = []
        seen_fingerprints = set()

        for obs in observations:
            fingerprint = self._fingerprint(obs)
            if fingerprint in seen_fingerprints:
                continue
            seen_fingerprints.add(fingerprint)

            q = self.generate(obs)
            if q and q.get("action") != "update_existing":
                results.append(q)

        return results

    def push_to_question_center(self, question_candidates: List[Dict[str, Any]]) -> List[str]:
        """把生成的问题推入 Question Center"""
        created = []
        for q in question_candidates:
            qid = self.qc.add_question(
                question_text=q["question"],
                source="question_engine",
                priority=q["priority"],
                capability=q["capability"],
            )
            # 更新问题的元数据
            for item in self.qc.questions:
                if item["qid"] == qid:
                    item["motivation"] = q.get("motivation", "")
                    item["approach"] = q.get("approach", "")
                    item["expected_value"] = q.get("expected_value", "")
                    item["source_fingerprint"] = q.get("source_fingerprint", "")
                    item["source_observation"] = q.get("source_observation", {})
                    break
            self.qc._save_all()
            created.append(qid)
        return created


def main():
    parser = argparse.ArgumentParser(description="QE-002 Question Engine")
    parser.add_argument("--observation", help="Single observation JSON string")
    parser.add_argument("--observations-file", help="File with observations JSON array")
    parser.add_argument("--push", action="store_true", help="Push generated questions to Question Center")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    engine = QuestionEngine()

    if args.observation:
        observations = [json.loads(args.observation)]
    elif args.observations_file:
        observations = json.loads(Path(args.observations_file).read_text(encoding="utf-8"))
    else:
        # 默认读取最新 situation
        situation_file = WORKSPACE / "02_MEMORY" / "environment" / "latest_situation.json"
        if situation_file.exists():
            situation = json.loads(situation_file.read_text(encoding="utf-8"))
            observations = situation.get("all_observations", [])
        else:
            observations = []

    candidates = engine.generate_batch(observations)

    if args.push:
        created = engine.push_to_question_center(candidates)
        print(f"Created {len(created)} questions: {created}")
    elif args.json:
        print(json.dumps(candidates, ensure_ascii=False, indent=2))
    else:
        print(f"Generated {len(candidates)} questions:")
        for q in candidates:
            print(f"\n[{q['priority']}] {q['question']}")
            print(f"  Motivation: {q['motivation']}")
            print(f"  Approach: {q['approach']}")


if __name__ == "__main__":
    main()
