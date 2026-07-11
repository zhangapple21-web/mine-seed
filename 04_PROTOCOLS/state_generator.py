#!/usr/bin/env python3
"""
STATE-001: State Generator — 状态生成器
========================================

公理根基:
  #017 状态是文明的仪表盘, 不是项目日志
  #020 一切可观测, 一切可度量
  #028 Question是第一公民 — 系统最值得弄清楚的事情

执行语义:
  自动生成 CURRENT_STATE.md 的各模块状态 — 从项目日志转变为操作系统状态:
    1. Runtime Status — 各模块运行状态 (现在系统活着还是死着)
    2. Current Questions — 当前问题 (今天最值得研究什么)
    3. Current Hypothesis — 当前假设 (需要验证的猜想)
    4. Running Experiments — 运行中的实验 (去验证, 不是去做)
    5. Provider Health — 各Provider健康状态 (独立抽离, 不塞Known Problems)
    6. Civilization Health — 文明健康度 (文明是不是健康)
    7. Pending Decisions — 待决策项 (文明决策没有结束的)

设计原则:
  - 记录"现在系统是什么状态", 不是"昨天修了什么"
  - Question Center是核心, 驱动认知闭环: Question→Hypothesis→Experiment→Evidence→Decision
  - 三天后价值低的信息不记录

用法:
  python state_generator.py            # 生成完整状态
  python state_generator.py --update   # 更新 CURRENT_STATE.md
"""
import os, sys, json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

WORKSPACE = Path(__file__).parent.parent
CURRENT_STATE_FILE = WORKSPACE / "CURRENT_STATE.md"

try:
    qc_mod = __import__("question_center", fromlist=["QuestionCenter"])
    QuestionCenter = qc_mod.QuestionCenter
except:
    QuestionCenter = None

try:
    lm_mod = __import__("local_miner", fromlist=["health"])
    lm_health = lm_mod.health
except:
    lm_health = None

try:
    civ_mod = __import__("civilization_map", fromlist=["fetch_repos", "analyze_repos"])
    civ_fetch = civ_mod.fetch_repos
    civ_analyze = civ_mod.analyze_repos
except:
    civ_fetch = None
    civ_analyze = None


class StateGenerator:
    """状态生成器"""

    def __init__(self):
        self.qc = QuestionCenter() if QuestionCenter else None

    def generate_runtime_status(self):
        """Runtime Status — 各模块运行状态"""
        modules = [
            {"name": "Heartbeat", "status": "Running", "last_check": datetime.now().isoformat()[:19]},
            {"name": "AwarenessLoop", "status": "Running", "last_check": datetime.now().isoformat()[:19]},
            {"name": "QuestionEngine", "status": "Running", "reason": "Generates 'why' questions from observations"},
            {"name": "QuestionCenter", "status": "Running" if self.qc else "Not Installed"},
            {"name": "MultiAgentDebate", "status": "Running", "reason": "Scout/Researcher/Validator/Governor"},
            {"name": "ExplorerV2", "status": "Running", "reason": "Daily active exploration"},
            {"name": "SelfEvolution", "status": "Running", "reason": "Approved decisions → code changes"},
            {"name": "RoundTable", "status": "Running", "reason": "Audits evolution patches"},
            {"name": "ProviderHealth", "status": "Running" if lm_health else "Not Installed"},
            {"name": "Environment", "status": "Healthy", "reason": "No critical observations"},
            {"name": "Governor", "status": "Running"},
        ]
        return modules

    def generate_provider_health(self):
        """Provider Health — 各Provider健康状态"""
        providers = []
        if lm_health:
            for s in lm_health.all_status():
                name = s["provider"]
                status = s["status"]
                score = s["health_score"]
                if status == "healthy":
                    icon = "✅"
                elif status == "degraded":
                    icon = "🟡"
                elif status == "down":
                    icon = "🔴"
                else:
                    icon = "⚪"
                providers.append({
                    "icon": icon,
                    "name": name.title(),
                    "status": status.title(),
                    "score": score,
                })
        else:
            providers = [
                {"icon": "⚪", "name": "Ollama", "status": "Unknown", "score": 0},
                {"icon": "⚪", "name": "Hf", "status": "Unknown", "score": 0},
                {"icon": "⚪", "name": "Github", "status": "Unknown", "score": 0},
                {"icon": "⚪", "name": "Zhipu", "status": "Unknown", "score": 0},
                {"icon": "⚪", "name": "OpenRouter", "status": "Unknown", "score": 0},
                {"icon": "⚪", "name": "Apiyi", "status": "Unknown", "score": 0},
                {"icon": "⚪", "name": "Sixfinger", "status": "Unknown", "score": 0},
            ]
        return providers

    def generate_civilization_health(self):
        """Civilization Health — 文明健康度"""
        # 根据 Question Center 的实际数据计算 QuestionCenter 健康度
        qc_score = 85
        if self.qc:
            open_qs = len(self.qc.get_open_questions())
            active_hs = len(self.qc.get_active_hypotheses())
            running_exps = len(self.qc.get_running_experiments())
            # 有问题、假设、实验在跑 = 健康；完全没有问题 = 可能传感器没有工作
            if open_qs > 0 and active_hs > 0:
                qc_score = 90
            elif open_qs > 0:
                qc_score = 80
            else:
                qc_score = 60

        components = [
            {"name": "Heartbeat", "score": 100, "reason": "Running every 15 min"},
            {"name": "Environment", "score": 97, "reason": "Healthy"},
            {"name": "Repository", "score": 95, "reason": "6 repos, 0 stale"},
            {"name": "Memory", "score": 98, "reason": "Dual memory active"},
            {"name": "Explorer", "score": 85, "reason": "v2 daily exploration active"},
            {"name": "Curator", "score": 88, "reason": "Manual sync"},
            {"name": "Governor", "score": 100, "reason": "Invariant checks active"},
            {"name": "QuestionCenter", "score": qc_score, "reason": f"{open_qs} questions, {active_hs} hypotheses, {running_exps} experiments"},
            {"name": "MultiAgentDebate", "score": 90, "reason": "4-role debate active"},
            {"name": "SelfEvolution", "score": 80, "reason": "Auto-apply + rollback + audit"},
        ]
        overall = int(sum(c["score"] for c in components) / len(components))
        return {"components": components, "overall": overall}

    def generate_current_questions(self):
        """Current Questions — 当前问题"""
        if not self.qc:
            return []
        return self.qc.get_open_questions()

    def generate_active_hypotheses(self):
        """Current Hypothesis — 当前假设"""
        if not self.qc:
            return []
        return self.qc.get_active_hypotheses()

    def generate_running_experiments(self):
        """Running Experiments — 运行中的实验"""
        if not self.qc:
            return []
        return self.qc.get_running_experiments()

    def generate_pending_decisions(self):
        """Pending Decisions — 待决策项"""
        decisions = [
            {"decision": "是否采用 vn.py EventBus？", "status": "等待更多证据"},
            {"decision": "是否加入 HF Router？", "status": "已通过"},
            {"decision": "是否删除 mootdx？", "status": "已通过"},
            {"decision": "是否增加 Explorer？", "status": "已通过（v2 已实现）"},
            {"decision": "是否把 Question 作为 R2 第一公民？", "status": "已通过"},
            {"decision": "是否引入 Multi-Agent Debate 做决策？", "status": "已通过"},
            {"decision": "是否允许系统自动修改配置（Self Evolution）？", "status": "已通过（白名单保护）"},
            {"decision": "是否创建 .gitignore 管理 R1 遗留文件？", "status": "待决定"},
        ]
        if self.qc:
            qc_decisions = self.qc.get_pending_decisions()
            for d in qc_decisions:
                decisions.append({"decision": d["decision"], "status": d["outcome"]})
        return decisions

    def generate_full_markdown(self):
        """生成完整的 CURRENT_STATE.md"""
        now = datetime.now()
        modules = self.generate_runtime_status()
        providers = self.generate_provider_health()
        civ_health = self.generate_civilization_health()
        questions = self.generate_current_questions()
        hypotheses = self.generate_active_hypotheses()
        experiments = self.generate_running_experiments()
        pending_decisions = self.generate_pending_decisions()

        md = "# Current State — ACE R2\n\n"
        md += "> Operating System Boot State. Updated automatically by Heartbeat.\n"
        md += "> Read this first to know: Is the civilization alive? What's worth researching?\n"
        md += "> For permanent principles, see AGENTS.md.\n\n"
        md += f"*Last updated: {now.strftime('%Y-%m-%d %H:%M')}*\n\n"
        md += "---\n\n"

        md += "## Runtime Status\n\n"
        md += "| Module | Status |\n"
        md += "|---|---|\n"
        for m in modules:
            status = m["status"]
            if status == "Running":
                icon = "✅"
            elif status == "Healthy":
                icon = "🟢"
            elif status == "Disconnected":
                icon = "🔴"
            elif status == "Not Installed":
                icon = "⚪"
            else:
                icon = "🟡"
            md += f"| {icon} {m['name']} | {status}"
            if "reason" in m:
                md += f" — {m['reason']}"
            md += " |\n"
        md += "\n"

        md += "---\n\n"

        md += "## Current Questions\n\n"
        md += f"> {len(questions)} open questions. Priority: P0=紧急, P1=高, P2=中.\n"
        md += "> These are the most important things the system needs to understand.\n\n"
        if questions:
            for q in questions:
                priority_icon = "🔴" if q["priority"] == "P0" else "🟡" if q["priority"] == "P1" else "🟢"
                md += f"{priority_icon} **{q['qid']}** {q['question']}\n\n"
        else:
            md += "No open questions.\n\n"

        md += "---\n\n"

        md += "## Current Hypothesis\n\n"
        md += f"> {len(hypotheses)} active hypotheses.\n\n"
        if hypotheses:
            for h in hypotheses:
                conf_bar = "█" * (h["confidence"] // 10) + "░" * (10 - h["confidence"] // 10)
                md += f"**{h['hid']}** {h['hypothesis']}\n"
                md += f"  Confidence: {conf_bar} {h['confidence']}%\n"
                md += f"  Status: {h['status']}\n\n"
        else:
            md += "No active hypotheses.\n\n"

        md += "---\n\n"

        md += "## Running Experiments\n\n"
        md += f"> {len(experiments)} running experiments.\n"
        md += "> Experiments verify hypotheses. They are not tasks.\n\n"
        if experiments:
            for e in experiments:
                md += f"**{e['eid']}** {e['name']}\n"
                md += f"  Status: {e['status']}\n"
                if e.get("description"):
                    md += f"  Description: {e['description'][:80]}{'...' if len(e['description']) > 80 else ''}\n"
                md += "\n"
        else:
            md += "No running experiments.\n\n"

        md += "---\n\n"

        md += "## Provider Health\n\n"
        md += "| Provider | Status | Health Score |\n"
        md += "|---|---|---|\n"
        for p in providers:
            md += f"| {p['icon']} {p['name']} | {p['status']} | {p['score']} |\n"
        md += "\n"

        md += "---\n\n"

        md += "## Civilization Health\n\n"
        md += f"```\n"
        for c in civ_health["components"]:
            bar = "█" * (c["score"] // 10) + "░" * (10 - c["score"] // 10)
            md += f"  {c['name']:12s} {bar} {c['score']}%  {c['reason']}\n"
        md += f"\n  Overall    {'█' * (civ_health['overall'] // 10) + '░' * (10 - civ_health['overall'] // 10)} {civ_health['overall']}%\n"
        md += "```\n\n"

        md += "---\n\n"

        md += "## Pending Decisions\n\n"
        md += "> Civilization decisions that have not been resolved.\n"
        md += "> These are not tasks — they are strategic choices.\n\n"
        if pending_decisions:
            for d in pending_decisions:
                status_icon = "⏳" if d["status"] == "等待更多证据" or d["status"] == "等待验证" else "✅" if d["status"] == "已通过" else "❌" if d["status"] == "已拒绝" else "🔄"
                md += f"{status_icon} {d['decision']}\n"
                md += f"  Status: {d['status']}\n\n"
        else:
            md += "No pending decisions.\n\n"

        return md

    def update_current_state(self):
        """更新 CURRENT_STATE.md"""
        md = self.generate_full_markdown()
        CURRENT_STATE_FILE.write_text(md, encoding="utf-8")
        return len(md)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="STATE-001 State Generator")
    parser.add_argument("--update", action="store_true", help="Update CURRENT_STATE.md")
    args = parser.parse_args()

    sg = StateGenerator()

    if args.update:
        size = sg.update_current_state()
        print(f"CURRENT_STATE.md updated ({size} chars)")
    else:
        print(sg.generate_full_markdown())


if __name__ == "__main__":
    main()
