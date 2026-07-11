#!/usr/bin/env python3
"""
QC-001: Question Center — 问题中心
====================================

公理根基:
  #013 知识是问题的答案, 问题是知识的种子
  #016 约束是经验的沉淀, 经验是问题的解答
  #025 演化不是增长, 而是更好地回答问题

执行语义:
  Question Center 是 R2 的第一公民, 管理认知闭环:
  
    Environment
        ↓
    Question (系统最值得弄清楚的事情)
        ↓
    Hypothesis (基于问题生成假设)
        ↓
    Experiment (验证假设的实验)
        ↓
    Evidence (收集证据)
        ↓
    Decision (做出决策)
        ↓
    Experience (沉淀经验)
        ↓
    Evolution (驱动演化)

数据结构:
  questions.json   — 问题池 (活跃/关闭/搁置)
  hypotheses.json  — 假设库 (待验证/验证中/已验证/已否定)
  experiments.json — 实验记录 (运行中/收集证据/已完成)
  decisions.json   — 决策记录 (已通过/已拒绝/等待更多证据)
  memory_index.json — 记忆索引 (关联已有记忆)

状态机:
  Question:   open → researching → answered → closed
  Hypothesis: proposed → testing → confirmed → rejected
  Experiment: planned → running → collecting → completed
  Decision:   pending → approved → rejected → deferred

架构集成:
  - 与 ace_core/core/memory_index.py 集成，复用现有记忆索引
  - DAG关系图: Question → Hypothesis → Experiment → Evidence → Decision
"""
import os, sys, json, argparse
from pathlib import Path
from datetime import datetime
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))
try:
    from local_miner import call_model
except:
    call_model = None

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "02_MEMORY" / "question_center"
DATA_DIR.mkdir(parents=True, exist_ok=True)

QUESTIONS_FILE = DATA_DIR / "questions.json"
HYPOTHESES_FILE = DATA_DIR / "hypotheses.json"
EXPERIMENTS_FILE = DATA_DIR / "experiments.json"
DECISIONS_FILE = DATA_DIR / "decisions.json"

MEMORY_INDEX_FILE = WORKSPACE / "02_MEMORY" / "memory_index_latest.json"


class QuestionCenter:
    """问题中心核心类"""

    def __init__(self):
        self._load_all()

    def _load_all(self):
        self.questions = self._load_json(QUESTIONS_FILE, [])
        self.hypotheses = self._load_json(HYPOTHESES_FILE, [])
        self.experiments = self._load_json(EXPERIMENTS_FILE, [])
        self.decisions = self._load_json(DECISIONS_FILE, [])

    def _load_json(self, path, default):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return default
        return default

    def _save_json(self, path, data):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _save_all(self):
        self._save_json(QUESTIONS_FILE, self.questions)
        self._save_json(HYPOTHESES_FILE, self.hypotheses)
        self._save_json(EXPERIMENTS_FILE, self.experiments)
        self._save_json(DECISIONS_FILE, self.decisions)

    def add_question(self, question_text, source="environment", priority="P1", capability="research"):
        qid = f"Q-{len(self.questions) + 1:03d}"
        question = {
            "qid": qid,
            "question": question_text,
            "source": source,
            "priority": priority,
            "capability": capability,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "hypotheses": [],
            "experiments": [],
            "decisions": [],
            "evidence": [],
        }
        self.questions.append(question)
        self._save_all()
        return qid

    def add_hypothesis(self, qid, hypothesis_text, confidence=0):
        h = {
            "hid": f"H-{len(self.hypotheses) + 1:03d}",
            "qid": qid,
            "hypothesis": hypothesis_text,
            "confidence": confidence,
            "status": "proposed",
            "created_at": datetime.now().isoformat(),
            "evidence": [],
        }
        self.hypotheses.append(h)
        for q in self.questions:
            if q["qid"] == qid and h["hid"] not in q["hypotheses"]:
                q["hypotheses"].append(h["hid"])
        self._save_all()
        return h["hid"]

    def add_experiment(self, hid, name, description, evidence_collected=[]):
        e = {
            "eid": f"EXP-{len(self.experiments) + 1:03d}",
            "hid": hid,
            "name": name,
            "description": description,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "evidence_collected": evidence_collected,
        }
        self.experiments.append(e)
        for h in self.hypotheses:
            if h["hid"] == hid:
                h["status"] = "testing"
        self._save_all()
        return e["eid"]

    def add_evidence(self, eid, evidence_text, weight=1):
        evidence = {
            "eid": eid,
            "text": evidence_text,
            "weight": weight,
            "added_at": datetime.now().isoformat(),
        }
        for e in self.experiments:
            if e["eid"] == eid:
                e["evidence_collected"].append(evidence)
                e["status"] = "collecting"
        for h in self.hypotheses:
            for eid_in_h in h.get("evidence", []):
                if eid_in_h == eid:
                    h["evidence"].append(evidence)
                    h["confidence"] = min(100, h.get("confidence", 0) + weight * 5)
        self._save_all()
        return evidence

    def add_decision(self, qid, decision_text, outcome="approved", rationale=""):
        d = {
            "did": f"D-{len(self.decisions) + 1:03d}",
            "qid": qid,
            "decision": decision_text,
            "outcome": outcome,
            "rationale": rationale,
            "created_at": datetime.now().isoformat(),
        }
        self.decisions.append(d)
        for q in self.questions:
            if q["qid"] == qid:
                q["status"] = "answered" if outcome == "approved" else "closed"
                q["decisions"].append(d["did"])
        self._save_all()
        return d["did"]

    def update_question_status(self, qid, status):
        for q in self.questions:
            if q["qid"] == qid:
                q["status"] = status
                q["last_seen"] = datetime.now().isoformat()
                break
        self._save_all()

    def update_experiment_status(self, eid, status):
        for e in self.experiments:
            if e["eid"] == eid:
                e["status"] = status
                break
        self._save_all()

    def update_hypothesis_confidence(self, hid, confidence):
        for h in self.hypotheses:
            if h["hid"] == hid:
                h["confidence"] = confidence
                h["status"] = "confirmed" if confidence >= 80 else "testing"
                break
        self._save_all()

    def get_open_questions(self):
        return [q for q in self.questions if q["status"] in ["open", "researching"]]

    def get_pending_decisions(self):
        return [d for d in self.decisions if d["outcome"] == "deferred"]

    def get_running_experiments(self):
        return [e for e in self.experiments if e["status"] in ["running", "collecting"]]

    def get_active_hypotheses(self):
        return [h for h in self.hypotheses if h["status"] in ["proposed", "testing"]]

    def generate_hypothesis(self, qid):
        """基于问题自动生成假设"""
        question = next((q for q in self.questions if q["qid"] == qid), None)
        if not question or not call_model:
            return None

        prompt = f"""你是 ACE 研究系统的假设生成器。

问题：{question['question']}

请基于这个问题，生成 2-3 个合理的假设。

格式要求：
每个假设一行，以 "- " 开头。
每个假设必须是可验证的陈述。

示例：
- Provider 401 错误是因为 API 密钥过期
- Provider 401 错误是因为请求格式不正确
- Provider 401 错误是因为服务端限流
"""
        result = call_model(prompt, max_tokens=200, capability="reasoning")
        if "error" in result:
            return None

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        hypotheses = []
        for line in content.strip().split("\n"):
            if line.strip().startswith("- "):
                h_text = line[2:].strip()
                hid = self.add_hypothesis(qid, h_text, confidence=30)
                hypotheses.append({"hid": hid, "hypothesis": h_text})
        return hypotheses

    def generate_experiment(self, hid):
        """基于假设自动生成实验方案"""
        hypothesis = next((h for h in self.hypotheses if h["hid"] == hid), None)
        if not hypothesis or not call_model:
            return None

        prompt = f"""你是 ACE 研究系统的实验设计器。

假设：{hypothesis['hypothesis']}

请设计一个实验来验证这个假设。

输出格式：
实验名称：[简短名称]
实验描述：[详细描述如何验证]

示例：
实验名称：API密钥有效性测试
实验描述：使用 curl 测试 API 密钥是否仍然有效，检查返回码是否为 401。
"""
        result = call_model(prompt, max_tokens=200, capability="reasoning")
        if "error" in result:
            return None

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        name = ""
        desc = ""
        for line in content.strip().split("\n"):
            if line.startswith("实验名称："):
                name = line[5:].strip()
            elif line.startswith("实验描述："):
                desc = line[5:].strip()

        if name and desc:
            eid = self.add_experiment(hid, name, desc)
            return {"eid": eid, "name": name, "description": desc}
        return None

    def get_current_state(self):
        """获取当前状态摘要，用于更新 CURRENT_STATE.md"""
        open_qs = self.get_open_questions()
        pending_decisions = self.get_pending_decisions()
        running_exps = self.get_running_experiments()
        active_hypotheses = self.get_active_hypotheses()

        return {
            "questions": {
                "total": len(self.questions),
                "open": len(open_qs),
                "list": open_qs[:5],
            },
            "hypotheses": {
                "total": len(self.hypotheses),
                "active": len(active_hypotheses),
                "list": active_hypotheses[:3],
            },
            "experiments": {
                "total": len(self.experiments),
                "running": len(running_exps),
                "list": running_exps[:3],
            },
            "decisions": {
                "total": len(self.decisions),
                "pending": len(pending_decisions),
                "list": pending_decisions[:5],
            },
        }

    def _load_memory_index(self):
        """加载现有记忆索引"""
        if MEMORY_INDEX_FILE.exists():
            try:
                data = json.loads(MEMORY_INDEX_FILE.read_text(encoding="utf-8"))
                return data.get("entries", [])
            except Exception:
                return []
        return []

    def search_related_memories(self, query, limit=5):
        """搜索相关记忆（复用现有记忆索引）"""
        entries = self._load_memory_index()
        results = []
        query_lower = query.lower()
        for entry in entries:
            text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
            if query_lower in text:
                results.append({
                    "id": entry.get("id", ""),
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "category": entry.get("category", ""),
                    "created_at": entry.get("created_at", ""),
                })
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results[:limit]

    def get_dag_graph(self):
        """
        获取认知闭环的 DAG 关系图:
        Question → Hypothesis → Experiment → Evidence → Decision
        
        返回格式:
        {
            "nodes": [...],
            "edges": [...]
        }
        """
        nodes = []
        edges = []
        node_ids = set()

        for q in self.questions:
            qid = q["qid"]
            if qid not in node_ids:
                node_ids.add(qid)
                nodes.append({
                    "id": qid,
                    "type": "question",
                    "label": q["question"][:30] + "..." if len(q["question"]) > 30 else q["question"],
                    "status": q["status"],
                    "priority": q["priority"],
                })

            for hid in q.get("hypotheses", []):
                h = next((h for h in self.hypotheses if h["hid"] == hid), None)
                if h and hid not in node_ids:
                    node_ids.add(hid)
                    nodes.append({
                        "id": hid,
                        "type": "hypothesis",
                        "label": h["hypothesis"][:25] + "..." if len(h["hypothesis"]) > 25 else h["hypothesis"],
                        "status": h["status"],
                        "confidence": h.get("confidence", 0),
                    })
                edges.append({"source": qid, "target": hid, "relation": "has_hypothesis"})

                for eid in [exp["eid"] for exp in self.experiments if exp.get("hid") == hid]:
                    e = next((e for e in self.experiments if e["eid"] == eid), None)
                    if e and eid not in node_ids:
                        node_ids.add(eid)
                        nodes.append({
                            "id": eid,
                            "type": "experiment",
                            "label": e["name"][:25] + "..." if len(e["name"]) > 25 else e["name"],
                            "status": e["status"],
                        })
                    edges.append({"source": hid, "target": eid, "relation": "tests_hypothesis"})

        for d in self.decisions:
            did = d["did"]
            qid = d["qid"]
            if did not in node_ids:
                node_ids.add(did)
                nodes.append({
                    "id": did,
                    "type": "decision",
                    "label": d["decision"][:25] + "..." if len(d["decision"]) > 25 else d["decision"],
                    "outcome": d["outcome"],
                })
            edges.append({"source": qid, "target": did, "relation": "resolved_by"})

        return {"nodes": nodes, "edges": edges}

    def get_top_questions(self, limit=3):
        """获取最高优先级的问题（P0优先，然后P1，再P2）"""
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        open_qs = self.get_open_questions()
        open_qs.sort(key=lambda x: (priority_order.get(x["priority"], 99), x.get("created_at", "")))
        return open_qs[:limit]

    def close_question(self, qid, reason=""):
        """关闭问题（标记为已回答或已关闭）"""
        for q in self.questions:
            if q["qid"] == qid:
                q["status"] = "closed"
                q["closed_reason"] = reason
                q["last_seen"] = datetime.now().isoformat()
                break
        self._save_all()

    def get_question_by_id(self, qid):
        """根据ID获取问题"""
        return next((q for q in self.questions if q["qid"] == qid), None)

    def get_hypothesis_by_id(self, hid):
        """根据ID获取假设"""
        return next((h for h in self.hypotheses if h["hid"] == hid), None)

    def get_experiment_by_id(self, eid):
        """根据ID获取实验"""
        return next((e for e in self.experiments if e["eid"] == eid), None)


def main():
    parser = argparse.ArgumentParser(description="QC-001 Question Center")
    subparsers = parser.add_subparsers(dest="action")

    p_add = subparsers.add_parser("add", help="Add question/hypothesis/experiment")
    p_add.add_argument("--question", help="Question text")
    p_add.add_argument("--priority", default="P1", choices=["P0", "P1", "P2"])
    p_add.add_argument("--hypothesis", help="Hypothesis text")
    p_add.add_argument("--qid", help="Question ID for hypothesis")

    p_list = subparsers.add_parser("list", help="List items")
    p_list.add_argument("--questions", action="store_true")
    p_list.add_argument("--hypotheses", action="store_true")
    p_list.add_argument("--experiments", action="store_true")
    p_list.add_argument("--decisions", action="store_true")

    p_gen = subparsers.add_parser("generate", help="Generate hypothesis/experiment")
    p_gen.add_argument("--hypothesis", help="Generate hypothesis for QID", metavar="QID")
    p_gen.add_argument("--experiment", help="Generate experiment for HID", metavar="HID")

    p_update = subparsers.add_parser("update", help="Update status")
    p_update.add_argument("--qid", help="Question ID")
    p_update.add_argument("--status", help="New status")
    p_update.add_argument("--eid", help="Experiment ID")
    p_update.add_argument("--hid", help="Hypothesis ID")
    p_update.add_argument("--confidence", type=int, help="Hypothesis confidence")

    p_graph = subparsers.add_parser("graph", help="Show DAG graph")
    p_graph.add_argument("--dag", action="store_true", help="Show DAG relation graph")

    p_search = subparsers.add_parser("search", help="Search related memories")
    p_search.add_argument("--query", required=True, help="Search query")
    p_search.add_argument("--limit", type=int, default=5, help="Result limit")

    p_close = subparsers.add_parser("close", help="Close question")
    p_close.add_argument("--qid", required=True, help="Question ID")
    p_close.add_argument("--reason", help="Close reason")

    args = parser.parse_args()
    qc = QuestionCenter()

    if args.action == "add":
        if args.question:
            qid = qc.add_question(args.question, priority=args.priority)
            print(f"Question added: {qid}")
        elif args.hypothesis and args.qid:
            hid = qc.add_hypothesis(args.qid, args.hypothesis)
            print(f"Hypothesis added: {hid}")

    elif args.action == "list":
        if args.questions:
            for q in qc.questions:
                print(f"{q['qid']} [{q['priority']}] {q['status']}: {q['question'][:80]}")
        elif args.hypotheses:
            for h in qc.hypotheses:
                print(f"{h['hid']} [{h['status']}] {h['confidence']}%: {h['hypothesis'][:80]}")
        elif args.experiments:
            for e in qc.experiments:
                print(f"{e['eid']} [{e['status']}]: {e['name']}")
        elif args.decisions:
            for d in qc.decisions:
                print(f"{d['did']} [{d['outcome']}]: {d['decision'][:80]}")

    elif args.action == "generate":
        if args.hypothesis:
            result = qc.generate_hypothesis(args.hypothesis)
            if result:
                print(f"Generated {len(result)} hypotheses:")
                for h in result:
                    print(f"  {h['hid']}: {h['hypothesis']}")
        elif args.experiment:
            result = qc.generate_experiment(args.experiment)
            if result:
                print(f"Generated experiment: {result['eid']} - {result['name']}")

    elif args.action == "update":
        if args.qid and args.status:
            qc.update_question_status(args.qid, args.status)
            print(f"Updated {args.qid} to {args.status}")
        elif args.eid and args.status:
            qc.update_experiment_status(args.eid, args.status)
            print(f"Updated {args.eid} to {args.status}")
        elif args.hid and args.confidence is not None:
            qc.update_hypothesis_confidence(args.hid, args.confidence)
            print(f"Updated {args.hid} confidence to {args.confidence}%")

    elif args.action == "graph":
        if args.dag:
            graph = qc.get_dag_graph()
            print("DAG Graph:")
            print(f"  Nodes: {len(graph['nodes'])}")
            print(f"  Edges: {len(graph['edges'])}")
            for node in graph["nodes"]:
                icon = "❓" if node["type"] == "question" else "🔍" if node["type"] == "hypothesis" else "🧪" if node["type"] == "experiment" else "⚖️"
                print(f"    {icon} {node['id']}: {node['label']} [{node.get('status', '')}]")
            for edge in graph["edges"]:
                print(f"    {edge['source']} → {edge['target']} ({edge['relation']})")

    elif args.action == "search":
        results = qc.search_related_memories(args.query, args.limit)
        print(f"Found {len(results)} related memories:")
        for r in results:
            print(f"  [{r['id']}] {r['title']}")
            print(f"      {r['summary'][:100]}...")
            print(f"      Category: {r['category']}")

    elif args.action == "close":
        qc.close_question(args.qid, args.reason)
        print(f"Question {args.qid} closed.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
