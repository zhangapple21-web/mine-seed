#!/usr/bin/env python3
"""
EXP-002: Explorer v2 — 主动探索者
===================================

核心区别:
  旧 Explorer: 被动扫描已知来源（GitHub trending / RSS / PyPI）
  新 Explorer: 每天主动选择一个探索主题，进行"小世界考古"，生成研究问题

执行语义:
  1. 从主题池随机选择一个今日主题
  2. 在 GitHub 搜索相关项目（GitHub API）
  3. 筛选高价值项目（stars / relevance / 最近活跃）
  4. 生成 Exploration Report：这个项目对 ACE 有什么用？
  5. 把报告推入 Question Center 作为候选问题
  6. 经过 Multi-Agent Debate 审议是否吸收

主题池:
  - provider router / model routing
  - event bus / message queue
  - memory index / graph memory
  - DAG / workflow engine
  - multi-agent debate / swarm intelligence
  - self-evolution / self-modifying code
  - capability graph / skill registry
  - quantization / local LLM optimization
  - knowledge distillation / archaeology

输出:
  02_MEMORY/exploration/exploration_YYYYMMDD.json
  02_MEMORY/exploration/exploration_YYYYMMDD.md
"""
import os, sys, json, random, urllib.request, urllib.error, urllib.parse, argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from local_miner import call_model
from question_center import QuestionCenter

WORKSPACE = Path(__file__).parent.parent
EXPLORATION_DIR = WORKSPACE / "02_MEMORY" / "exploration"
EXPLORATION_DIR.mkdir(parents=True, exist_ok=True)

# 探索主题池 — 每个主题对应 ACE 当前或未来可能需要的能力
TOPIC_POOL = [
    {
        "id": "T-001",
        "name": "Provider Router / Model Routing",
        "keywords": ["llm router", "model routing", "fallback chain", "provider health"],
        "capability_ref": "llm_inference",
        "why_for_ace": "ACE 已经实现了 Provider Civilization，可以借鉴外部路由框架的健康检查策略",
    },
    {
        "id": "T-002",
        "name": "Event Bus / Message Queue",
        "keywords": ["event bus", "message queue", "pub sub", "event driven"],
        "capability_ref": "event_bus",
        "why_for_ace": "ACE 需要把传感器、问题引擎、辩论室、执行器连接起来，Event Bus 是核心基础设施",
    },
    {
        "id": "T-003",
        "name": "Memory Index / Graph Memory",
        "keywords": ["memory index", "graph memory", "knowledge graph", "memory retrieval"],
        "capability_ref": "memory",
        "why_for_ace": "ACE 的记忆系统需要更强的关联检索能力，避免重复解决问题",
    },
    {
        "id": "T-004",
        "name": "DAG / Workflow Engine",
        "keywords": ["dag workflow", "workflow engine", "task graph", "pipeline"],
        "capability_ref": "workflow",
        "why_for_ace": "Question→Hypothesis→Experiment→Evidence→Decision 需要 DAG 表达依赖关系",
    },
    {
        "id": "T-005",
        "name": "Multi-Agent Debate / Swarm Intelligence",
        "keywords": ["multi agent debate", "swarm intelligence", "agent consensus", "role playing llm"],
        "capability_ref": "multi_agent",
        "why_for_ace": "ACE 正在构建 Scout/Researcher/Validator/Governor 辩论机制，需要参考外部实现",
    },
    {
        "id": "T-006",
        "name": "Self-Evolution / Self-Modifying Code",
        "keywords": ["self modifying code", "self improving ai", "auto refactoring", "code evolution"],
        "capability_ref": "evolution",
        "why_for_ace": "R2 目标是让系统自己修改自己，需要学习安全和可回滚的自我演化模式",
    },
    {
        "id": "T-007",
        "name": "Capability Graph / Skill Registry",
        "keywords": ["skill registry", "capability graph", "tool registry", "agent capability"],
        "capability_ref": "capability_graph",
        "why_for_ace": "ACE 的 Capability Graph 是核心抽象，可以借鉴插件系统的设计",
    },
    {
        "id": "T-008",
        "name": "Local LLM Optimization / Quantization",
        "keywords": ["llama.cpp", "gguf quantization", "local llm inference", "ollama"],
        "capability_ref": "local_inference",
        "why_for_ace": "Ollama 是 ACE Provider 之一，需要持续跟踪本地模型优化技术",
    },
    {
        "id": "T-009",
        "name": "Knowledge Distillation / Archaeology",
        "keywords": ["knowledge distillation", "code archaeology", "legacy modernization"],
        "capability_ref": "archaeology",
        "why_for_ace": "ACE 的核心方法论是'考古不是搬家是炼金'，需要学习更好的蒸馏技术",
    },
    {
        "id": "T-010",
        "name": "Civilization Simulation / Digital Garden",
        "keywords": ["digital garden", "knowledge management", "second brain", "civilization simulation"],
        "capability_ref": "civilization",
        "why_for_ace": "ACE 把自己视为一个文明引擎，需要借鉴数字花园和文明模拟的思想",
    },
]


class GitHubSearcher:
    """GitHub 项目搜索"""

    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN", "")

    def search(self, query: str, per_page: int = 10) -> List[Dict[str, Any]]:
        """搜索 GitHub 仓库"""
        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page={per_page}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "ACE-Explorer-v2")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")

        try:
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
        except urllib.error.HTTPError as e:
            if e.code == 403:
                return [{"error": "GitHub API rate limited"}]
            return [{"error": f"HTTP {e.code}"}]
        except Exception as e:
            return [{"error": str(e)}]


class ExplorerV2:
    """主动探索者 v2"""

    def __init__(self):
        self.qc = QuestionCenter()
        self.gh = GitHubSearcher()

    def pick_today_topic(self) -> Dict[str, Any]:
        """选择今日主题 — 优先选择近期没探索过的"""
        history = self._load_history()
        explored_topics = {h.get("topic_id") for h in history[-30:]}

        candidates = [t for t in TOPIC_POOL if t["id"] not in explored_topics]
        if not candidates:
            candidates = TOPIC_POOL

        return random.choice(candidates)

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载最近探索历史"""
        files = sorted(EXPLORATION_DIR.glob("exploration_*.json"))
        history = []
        for f in files[-30:]:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                history.append({
                    "date": data.get("date"),
                    "topic_id": data.get("topic", {}).get("id"),
                    "topic_name": data.get("topic", {}).get("name"),
                })
            except Exception:
                pass
        return history

    def search_github_for_topic(self, topic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """为主题搜索 GitHub 项目"""
        all_results = []
        for kw in topic["keywords"][:3]:  # 每个主题用前 3 个关键词搜索
            results = self.gh.search(kw, per_page=5)
            for r in results:
                if "error" in r:
                    return results  # 直接返回错误
                # 去重
                if not any(x.get("full_name") == r.get("full_name") for x in all_results):
                    all_results.append(r)
            if len(all_results) >= 10:
                break
        return all_results[:10]

    def filter_projects(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """筛选高质量项目"""
        scored = []
        for p in projects:
            score = 0
            stars = p.get("stargazers_count", 0)
            if stars > 1000:
                score += 30
            elif stars > 100:
                score += 20
            elif stars > 10:
                score += 10

            # 最近更新加分
            updated = p.get("updated_at", "")
            if updated:
                try:
                    updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    if datetime.now(updated_dt.tzinfo) - updated_dt < timedelta(days=30):
                        score += 20
                    elif datetime.now(updated_dt.tzinfo) - updated_dt < timedelta(days=90):
                        score += 10
                except Exception:
                    pass

            # 有描述加分
            if p.get("description"):
                score += 10

            scored.append({
                "full_name": p.get("full_name"),
                "html_url": p.get("html_url"),
                "stars": stars,
                "description": p.get("description", "")[:200],
                "updated_at": updated,
                "language": p.get("language", ""),
                "score": score,
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:5]

    def generate_report(self, topic: Dict[str, Any], projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成探索报告"""
        if not projects:
            return {
                "topic": topic,
                "projects": [],
                "findings": "No relevant projects found on GitHub today.",
                "question_for_ace": None,
                "timestamp": datetime.now().isoformat(),
            }

        # 用 LLM 分析这些项目对 ACE 的价值
        prompt = f"""你是 ACE 文明的 Explorer（探索者）。

今日探索主题：{topic['name']}
主题对 ACE 的价值：{topic['why_for_ace']}

发现的相关项目：
```json
{json.dumps(projects, ensure_ascii=False, indent=2)}
```

请输出 JSON：
{{
  "findings": "对这些项目的整体分析，不超过 300 字",
  "most_relevant_project": "最值得关注的一个项目名称",
  "question_for_ace": "基于这次探索，ACE 应该研究什么问题？以'为什么'、'是否应该'开头",
  "absorb_recommendation": "absorb/defer/reject — 是否值得把这个问题纳入 ACE 研究",
  "rationale": "推荐理由，不超过 150 字"
}}
"""
        result = call_model(prompt, max_tokens=600, capability="research")
        if "error" in result:
            # 失败时生成基础报告
            return {
                "topic": topic,
                "projects": projects,
                "findings": f"发现 {len(projects)} 个相关项目，但 LLM 分析失败",
                "most_relevant_project": projects[0]["full_name"] if projects else None,
                "question_for_ace": f"是否应该研究 {topic['name']} 对 ACE 的借鉴价值？",
                "absorb_recommendation": "defer",
                "rationale": "需要更多分析",
                "timestamp": datetime.now().isoformat(),
            }

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            if content.strip().startswith("```"):
                lines = content.strip().split("\n")
                content = "\n".join(lines[1:-1])
            parsed = json.loads(content.strip())
        except Exception:
            parsed = {}

        return {
            "topic": topic,
            "projects": projects,
            "findings": parsed.get("findings", "无法解析分析结果"),
            "most_relevant_project": parsed.get("most_relevant_project", projects[0]["full_name"] if projects else None),
            "question_for_ace": parsed.get("question_for_ace", f"{topic['name']} 对 ACE 有什么借鉴价值？"),
            "absorb_recommendation": parsed.get("absorb_recommendation", "defer"),
            "rationale": parsed.get("rationale", ""),
            "timestamp": datetime.now().isoformat(),
        }

    def save_report(self, report: Dict[str, Any]) -> Path:
        """保存报告到 02_MEMORY/exploration/"""
        date_str = datetime.now().strftime("%Y%m%d")
        json_path = EXPLORATION_DIR / f"exploration_{date_str}.json"
        md_path = EXPLORATION_DIR / f"exploration_{date_str}.md"

        # JSON
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        # Markdown
        md = f"# Exploration Report: {report['topic']['name']}\n\n"
        md += f"**Date**: {report['timestamp'][:10]}\n\n"
        md += f"**Topic ID**: {report['topic']['id']}\n\n"
        md += f"**Why for ACE**: {report['topic']['why_for_ace']}\n\n"
        md += f"## Findings\n\n{report['findings']}\n\n"
        md += f"## Question for ACE\n\n> {report['question_for_ace']}\n\n"
        md += f"## Recommendation\n\n**{report['absorb_recommendation'].upper()}** — {report['rationale']}\n\n"
        md += "## Projects Found\n\n"
        md += "| Project | Stars | Language | Updated | Description |\n"
        md += "|---|---|---|---|---|\n"
        for p in report["projects"]:
            md += f"| [{p['full_name']}]({p['html_url']}) | {p['stars']} | {p['language']} | {p['updated_at'][:10] if p['updated_at'] else '-'} | {p['description'].replace('|', '/')[:80]} |\n"

        md_path.write_text(md, encoding="utf-8")

        return json_path

    def push_to_question_center(self, report: Dict[str, Any]) -> Optional[str]:
        """如果推荐 absorb，把问题推入 Question Center"""
        if report.get("absorb_recommendation") != "absorb":
            return None

        question = report.get("question_for_ace")
        if not question:
            return None

        qid = self.qc.add_question(
            question_text=question,
            source=f"explorer:{report['topic']['id']}",
            priority="P2",
            capability="archaeology",
        )

        # 附加元数据
        for q in self.qc.questions:
            if q["qid"] == qid:
                q["exploration_topic"] = report["topic"]
                q["exploration_projects"] = report["projects"]
                q["exploration_report_file"] = f"02_MEMORY/exploration/exploration_{datetime.now().strftime('%Y%m%d')}.md"
                break
        self.qc._save_all()
        return qid

    def run(self, topic_id: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """执行一次探索"""
        print(f"\n[EXPLORER v2] Start @ {datetime.now().isoformat()}")

        topic = self.pick_today_topic() if topic_id is None else next(
            (t for t in TOPIC_POOL if t["id"] == topic_id), None
        )
        if not topic:
            return {"error": f"Topic {topic_id} not found"}

        print(f"  Today's topic: {topic['id']} — {topic['name']}")

        # 搜索
        print("  Searching GitHub...")
        raw_projects = self.search_github_for_topic(topic)
        if raw_projects and "error" in raw_projects[0]:
            error_msg = raw_projects[0]["error"]
            print(f"  GitHub error: {error_msg}")
            report = {
                "topic": topic,
                "projects": [],
                "findings": f"GitHub search failed: {error_msg}",
                "question_for_ace": f"是否应该重新设计 {topic['name']} 的探索策略？",
                "absorb_recommendation": "defer",
                "rationale": "外部搜索失败，需要备用方案",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            projects = self.filter_projects(raw_projects)
            print(f"  Filtered {len(projects)} projects")

            report = self.generate_report(topic, projects)
            print(f"  Report generated: {report.get('absorb_recommendation')}")

        # 保存
        saved_path = self.save_report(report)
        print(f"  Saved: {saved_path}")

        # 推入 Question Center
        if not dry_run:
            qid = self.push_to_question_center(report)
            if qid:
                print(f"  Pushed to Question Center: {qid}")
                report["qid"] = qid

        print(f"[EXPLORER v2] Done")
        return report


def main():
    parser = argparse.ArgumentParser(description="EXP-002 Explorer v2")
    parser.add_argument("--topic", help="Explore specific topic ID")
    parser.add_argument("--dry-run", action="store_true", help="Do not push to Question Center")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    explorer = ExplorerV2()
    report = explorer.run(topic_id=args.topic, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"\nTopic: {report['topic']['name']}")
        print(f"Recommendation: {report.get('absorb_recommendation', 'defer')}")
        print(f"Question: {report.get('question_for_ace', 'N/A')}")


if __name__ == "__main__":
    main()
