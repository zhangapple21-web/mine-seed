#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-007
"""
ENV-002: Environment Awareness Loop — 环境感知闭环
====================================================

核心区别：
  旧：扫描 → 结束
  新：扫描 → 为什么？→ 需要调查吗？→ 自动生成Task → 自动派Miner → 自动RoundTable

闭环：
  Environment
      ↓
  Observation (Sensor)
      ↓
  Question (为什么不正常？需要调查吗？)
      ↓
  Task (自动生成)
      ↓
  Research (Miner + call_model)
      ↓
  Report (研究结果)
      ↓
  RoundTable (审议)
      ↓
  Experience (沉淀)
      ↓
  Repository

用法：
  python awareness_loop.py              # 完整闭环
  python awareness_loop.py --scan-only  # 只扫描+提问，不执行
  python awareness_loop.py --json       # JSON输出
"""
import os, sys, json, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from environment_sensor import EnvironmentSensor, SituationBuilder, Observation
from local_miner import call_model, health, list_capabilities, CAPABILITY_GRAPH

WORKSPACE = Path(__file__).parent.parent
EXPERIENCE_DIR = WORKSPACE / "02_MEMORY" / "experience"


class QuestionGenerator:
    """从 Observation 生成 Question — 不是扫描完就结束，而是问'为什么'"""

    # 规则：什么样的 Observation 需要调查
    INVESTIGATE_RULES = {
        "provider_down": {
            "question": "数据源 {detail} 不可用，是否需要切换到备用源？",
            "capability": "research",
            "priority": "P0",
        },
        "provider_missing": {
            "question": "关键依赖 {detail} 未安装，是否影响系统运行？",
            "capability": "research",
            "priority": "P0",
        },
        "module_missing": {
            "question": "核心模块 {detail} 缺失，是否需要恢复？",
            "capability": "research",
            "priority": "P0",
        },
        "file_deleted": {
            "question": "文件被删除 {detail}，是否是误删？",
            "capability": "research",
            "priority": "P1",
        },
        "trending_repo": {
            "question": "GitHub 发现 {detail}，是否与 ACE 能力图谱相关？值得考古吗？",
            "capability": "archaeology",
            "priority": "P2",
        },
        "api_error": {
            "question": "API 错误 {detail}，是否需要切换 Provider？",
            "capability": "reasoning",
            "priority": "P1",
        },
        # 扩展规则 — 让系统对常见变化也产生问题
        "new_files": {
            "question": "发现 {detail} — 这些新文件是否需要纳入治理？是否包含未蒸馏的原始数据？",
            "capability": "research",
            "priority": "P2",
        },
        "file_change": {
            "question": "文件变更 {detail} — 是否符合演化约束？是否破坏不变量？",
            "capability": "reasoning",
            "priority": "P2",
        },
        "config_change": {
            "question": "配置变更 {detail} — 是否影响系统行为？是否需要审计？",
            "capability": "reasoning",
            "priority": "P1",
        },
        "stale_repo": {
            "question": "仓库 {detail} 长时间未更新，是否需要恢复同步？curator 是否挂了？",
            "capability": "research",
            "priority": "P1",
        },
        "heartbeat_failure": {
            "question": "Heartbeat 失败 {detail} — 系统是否在运行？入口脚本是否正常？",
            "capability": "reasoning",
            "priority": "P0",
        },
    }

    def generate(self, observation: dict) -> dict | None:
        """从 Observation 生成 Question，如果不需要调查则返回 None"""
        category = observation.get("category", "")
        rule = self.INVESTIGATE_RULES.get(category)
        if not rule:
            return None

        detail_str = observation.get("title", "")
        question_text = rule["question"].format(detail=detail_str)

        return {
            "question": question_text,
            "capability": rule["capability"],
            "priority": rule["priority"],
            "source_observation": observation,
            "timestamp": datetime.now().isoformat(),
        }


class TaskDispatcher:
    """自动派单 — 把 Question 变成 Miner Task"""

    def execute(self, question: dict) -> dict:
        """执行研究任务"""
        capability = question.get("capability", "research")
        prompt = f"""你是 ACE 自主研究系统的研究员。

环境传感器发现了以下情况，需要你分析：

问题：{question['question']}

观察详情：
{json.dumps(question.get('source_observation', {}), ensure_ascii=False, indent=2)}

请分析：
1. 这个情况是否需要立即处理？
2. 如果需要处理，建议的方案是什么？
3. 是否需要人工介入？

请用简洁的中文回答（不超过200字）。
"""

        result = call_model(prompt, max_tokens=300, capability=capability)
        if "error" in result:
            return {
                "status": "failed",
                "error": result.get("errors", result.get("error")),
                "question": question["question"],
            }

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {
            "status": "ok",
            "question": question["question"],
            "analysis": content,
            "provider": result.get("provider"),
            "model": result.get("model"),
            "capability": capability,
            "latency_ms": result.get("latency_ms"),
            "timestamp": datetime.now().isoformat(),
        }


class ExperienceSediment:
    """经验沉淀 — 把研究结果存入 Experience"""

    def __init__(self):
        self.dir = EXPERIENCE_DIR
        self.dir.mkdir(parents=True, exist_ok=True)

    def save(self, report: dict):
        """保存经验"""
        filename = f"exp_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
        filepath = self.dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        return filename


class AwarenessLoop:
    """环境感知闭环 — 把所有已有能力连接起来"""

    def __init__(self):
        self.sensor = EnvironmentSensor()
        self.builder = SituationBuilder()
        self.question_gen = QuestionGenerator()
        self.dispatcher = TaskDispatcher()
        self.experience = ExperienceSediment()
        self.pending_json = WORKSPACE / "02_MEMORY" / "pending_tasks.json"
        self.tasks_md = WORKSPACE / "02_MEMORY" / "tasks.md"

    def _save_pending_tasks(self, pending_tasks: list):
        """把 P2 待办任务保存到 pending_tasks.json + tasks.md
        - JSON: 结构化存储，支持去重（基于 question 文本）
        - MD: 人类可读，追加到 Awareness Loop Pending 段落
        """
        # 1. 读取已有 JSON（去重基准）
        existing = []
        if self.pending_json.exists():
            try:
                existing = json.loads(self.pending_json.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = []
            except Exception:
                existing = []
        existing_keys = {t.get("dedup_key", t.get("question", "")) for t in existing}

        # 2. 追加新任务（基于 dedup_key 去重）
        new_added = 0
        for t in pending_tasks:
            key = t.get("dedup_key", t.get("question", ""))
            if key not in existing_keys:
                existing.append(t)
                existing_keys.add(key)
                new_added += 1
            # 如果 dedup_key 已存在，更新 question 文本（数字可能变化）但不算新增
            elif key != "unknown":
                for i, old_t in enumerate(existing):
                    if old_t.get("dedup_key") == key:
                        existing[i]["question"] = t["question"]
                        existing[i]["last_seen"] = t["timestamp"]
                        break

        # 3. 写 JSON
        self.pending_json.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 4. 同步到 tasks.md（重建 Awareness Loop 段落）
        marker_begin = "<!-- AWARENESS_LOOP_PENDING_BEGIN -->"
        marker_end = "<!-- AWARENESS_LOOP_PENDING_END -->"

        old_md = ""
        if self.tasks_md.exists():
            old_md = self.tasks_md.read_text(encoding="utf-8")

        # 构建新段落
        pending_section = ""
        if existing:
            pending_section = f"\n{marker_begin}\n## Awareness Loop Pending Tasks\n\n"
            pending_section += f"> Auto-generated by AwarenessLoop. {len(existing)} pending (P2) tasks.\n\n"
            pending_section += "| # | Priority | Capability | Question | Status | Timestamp |\n"
            pending_section += "|---|---|---|---|---|---|\n"
            for i, t in enumerate(existing, 1):
                q_short = t["question"].replace("|", "/")[:120]
                pending_section += f"| {i} | {t['priority']} | {t.get('capability', '-')} | {q_short} | {t.get('status', 'pending')} | {t.get('timestamp', '-')[:19]} |\n"
            pending_section += f"\n{marker_end}\n"

        # 替换或追加
        if marker_begin in old_md:
            # 替换旧段落
            start = old_md.index(marker_begin) - 1  # 包含前一个换行
            end = old_md.index(marker_end) + len(marker_end)
            # 保留 marker 前的内容（去掉前导换行再加回来）
            before = old_md[:start] if start >= 0 else old_md
            after = old_md[end:].lstrip("\n") if end < len(old_md) else ""
            new_md = before + pending_section + after
        else:
            # 追加到末尾
            new_md = old_md.rstrip("\n") + "\n" + pending_section

        self.tasks_md.write_text(new_md, encoding="utf-8")
        return new_added

    def run(self, scan_only: bool = False) -> dict:
        """执行完整闭环"""
        print(f"[AWARENESS LOOP] Start @ {datetime.now().isoformat()}")

        # Step 1: 感知
        print("  [1] Scanning environment...")
        observations = self.sensor.scan_all(sources=["local", "providers"])
        situation = self.builder.build(observations)
        print(f"      → {situation['total_observations']} observations, {situation['new_observations']} new, {len(situation['high_priority'])} high priority")

        # Step 2: 提问
        print("  [2] Generating questions...")
        questions = []
        for obs in situation.get("all_observations", []):
            q = self.question_gen.generate(obs)
            if q:
                questions.append(q)
        print(f"      → {len(questions)} questions generated")
        for q in questions:
            print(f"        [{q['priority']}] {q['question'][:80]}")

        if scan_only or not questions:
            return {
                "step": "scan+question",
                "situation": situation,
                "questions": questions,
            }

        # Step 3: 自动派单（P0/P1 立即执行，P2 记录为待办）
        print("  [3] Dispatching tasks...")
        reports = []
        pending_tasks = []
        for q in questions:
            if q["priority"] == "P0" or q["priority"] == "P1":
                print(f"        EXECUTE [{q['priority']}] {q['question'][:60]}")
                report = self.dispatcher.execute(q)
                reports.append(report)
                if report["status"] == "ok":
                    print(f"          → {report['provider']}: {report['analysis'][:100]}")
                else:
                    print(f"          → FAILED: {report.get('error')}")
            elif q["priority"] == "P2":
                # P2 不立即执行，记录为待办任务
                # dedup_key 基于 observation category，避免数字变化导致重复
                obs_cat = q.get("source_observation", {}).get("category", "unknown")
                pending_tasks.append({
                    "question": q["question"],
                    "capability": q["capability"],
                    "priority": q["priority"],
                    "status": "pending",
                    "dedup_key": obs_cat,
                    "timestamp": datetime.now().isoformat(),
                })
                print(f"        PENDING [{q['priority']}] {q['question'][:60]}")

        # 把 P2 待办写入 tasks.md + pending_tasks.json
        if pending_tasks:
            new_added = self._save_pending_tasks(pending_tasks)
            print(f"      → {new_added} new pending tasks saved ({len(pending_tasks)} total this run)")

        # Step 4: 经验沉淀
        print("  [4] Sedimenting experience...")
        saved = []
        for r in reports:
            if r["status"] == "ok":
                fname = self.experience.save(r)
                saved.append(fname)
                print(f"        Saved: {fname}")

        # Step 5: Provider Health 摘要
        print("  [5] Provider Health:")
        for s in health.all_status():
            print(f"        {s['provider']:12s} status={s['status']:12s} score={s['health_score']}")

        print(f"[AWARENESS LOOP] Done @ {datetime.now().isoformat()}")

        return {
            "step": "full_loop",
            "situation": situation,
            "questions": questions,
            "reports": reports,
            "experiences_saved": saved,
            "provider_health": health.all_status(),
        }


def main():
    parser = argparse.ArgumentParser(description="ENV-002 Environment Awareness Loop")
    parser.add_argument("--scan-only", action="store_true", help="Only scan+question, no execution")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    loop = AwarenessLoop()
    result = loop.run(scan_only=args.scan_only)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
