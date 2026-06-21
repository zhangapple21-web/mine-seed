#!/usr/bin/env python3
"""
任务路由器 v2 - 从"谁分高谁上"到"任务画像匹配工人"
核心设计：
1. Task Classifier → 识别任务需求(requirements)
2. Worker Match → 按需求匹配工人画像(strengths/weaknesses)
3. Judge Layer → 裁判对比输出质量
4. Observation Log → 持久化经验数据链
5. Registry → 统一工人注册中心
"""
import json, time, os, threading, requests
from datetime import datetime

REGISTRY_FILE = "/home/coze/worker_registry.json"
OBSERVATION_FILE = "/home/coze/mine_output/observation_log.json"
JUDGE_FILE = "/home/coze/mine_output/judge_history.json"

API_BASE = os.environ.get("MINER_API_BASE", "http://localhost:3000/v1/chat/completions")
API_KEY = os.environ.get("MINER_API_KEY", "{{ONE_API_KEY}}")

# ==================== 任务画像定义 ====================
# 每种任务需要的capability → 匹配worker的strengths
TASK_PROFILES = {
    "slice_classification": {
        "requirements": ["classification", "extraction", "fast_response"],
        "avoid": [],  # 不需要的能力(匹配到weakness就降权)
        "max_latency": 30,
        "min_context": 8000,
        "strategy": "speed",
    },
    "persona_deep": {
        "requirements": ["deep_reasoning", "analysis", "long_context"],
        "avoid": [],
        "max_latency": 300,
        "min_context": 32000,
        "strategy": "quality",
    },
    "shadow_analysis": {
        "requirements": ["reasoning", "analysis", "structured_output"],
        "avoid": [],
        "max_latency": 300,
        "min_context": 16000,
        "strategy": "quality",
    },
    "routing_analysis": {
        "requirements": ["reasoning", "analysis", "coding"],
        "avoid": [],
        "max_latency": 300,
        "min_context": 16000,
        "strategy": "quality",
    },
    "slice_mining": {
        "requirements": ["analysis", "extraction", "coding"],
        "avoid": [],
        "max_latency": 300,
        "min_context": 16000,
        "strategy": "balanced",
    },
    "upgrade_analysis": {
        "requirements": ["reasoning", "analysis", "long_context"],
        "avoid": [],
        "max_latency": 300,
        "min_context": 16000,
        "strategy": "quality",
    },
    "canonical_v2": {
        "requirements": ["synthesis", "deep_reasoning", "long_context", "structured_output"],
        "avoid": ["latency"],  # 接受慢
        "max_latency": 600,
        "min_context": 64000,
        "strategy": "quality",
    },
}


class WorkerRegistry:
    """P0: 工人注册中心 — 所有工人信息从这里来，不写死"""
    def __init__(self):
        self.lock = threading.Lock()
        self.data = self._load()
    def _load(self):
        if os.path.exists(REGISTRY_FILE):
            with open(REGISTRY_FILE) as f:
                return json.load(f)
        return {"version": "1.0", "workers": {}}
    def _save(self):
        with open(REGISTRY_FILE, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    def get_alive(self, corps=None):
        """获取存活工人列表"""
        workers = []
        for wid, w in self.data["workers"].items():
            if w.get("status") != "alive":
                continue
            if corps and w.get("corps") != corps:
                continue
            workers.append((wid, w))
        return workers
    def get_worker(self, worker_id):
        return self.data["workers"].get(worker_id)
    def update_status(self, worker_id, status, reason=""):
        """更新工人状态"""
        with self.lock:
            if worker_id in self.data["workers"]:
                self.data["workers"][worker_id]["status"] = status
                if reason:
                    self.data["workers"][worker_id]["last_reason"] = reason
                self.data["workers"][worker_id]["last_update"] = datetime.now().isoformat()
                self._save()
    def update_stats(self, worker_id, elapsed, success):
        """更新工人运行时统计"""
        with self.lock:
            w = self.data["workers"].get(worker_id)
            if not w:
                return
            # 指数移动平均更新延迟
            alpha = 0.3
            w["avg_latency"] = round(w.get("avg_latency", 10) * (1 - alpha) + elapsed * alpha, 1)
            # 更新成功率
            sr = w.get("success_rate", 0.9)
            w["success_rate"] = round(sr * (1 - alpha) + (1.0 if success else 0.0) * alpha, 3)
            self._save()
    def report(self):
        """输出Registry状态"""
        lines = ["📋 Worker Registry 状态报告", "=" * 50]
        for corps in ["GLM", "NIM", "GitHub"]:
            workers = self.get_alive(corps=corps)
            alive = len(workers)
            total_rpm = sum(w.get("rpm", 0) for _, w in workers)
            emoji = {"GLM": "🚀", "NIM": "🏆", "GitHub": "🆓"}.get(corps, "?")
            lines.append(f"\n{emoji} {corps}军团: {alive}存活 | {total_rpm}RPM")
            for wid, w in workers:
                lines.append(f"  {wid}: lat={w.get('avg_latency',0):.1f}s sr={w.get('success_rate',0):.2f} {w.get('strengths',[])}")
        # 挂掉的
        dead = [(wid, w) for wid, w in self.data["workers"].items() if w.get("status") != "alive"]
        if dead:
            lines.append(f"\n💀 离线: {len(dead)}")
            for wid, w in dead:
                lines.append(f"  {wid}: {w.get('status')} - {w.get('last_reason','')}")
        return "\n".join(lines)


class ObservationLog:
    """P0: 观察层 — 任务→调用→结果→评估 的完整数据链"""
    def __init__(self):
        self.lock = threading.Lock()
        self.data = self._load()
    def _load(self):
        if os.path.exists(OBSERVATION_FILE):
            try:
                with open(OBSERVATION_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {"observations": [], "stats_by_task": {}, "stats_by_worker": {}}
    def _save(self):
        with open(OBSERVATION_FILE, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    def record(self, task_name, worker_id, model, corps, elapsed, success, 
               tokens_in=0, tokens_out=0, error_msg="", quality_score=None):
        """记录一次完整的观察"""
        entry = {
            "ts": datetime.now().isoformat(),
            "task": task_name,
            "worker_id": worker_id,
            "model": model,
            "corps": corps,
            "elapsed": round(elapsed, 2),
            "success": success,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "error": error_msg[:100] if error_msg else "",
            "quality": quality_score,  # Judge打的分
        }
        with self.lock:
            self.data["observations"].append(entry)
            # 只保留最近2000条
            if len(self.data["observations"]) > 2000:
                self.data["observations"] = self.data["observations"][-2000:]
            # 按任务统计
            ts = self.data["stats_by_task"]
            if task_name not in ts:
                ts[task_name] = {"total": 0, "success": 0, "avg_time": 0, "by_corps": {}}
            ts[task_name]["total"] += 1
            if success:
                ts[task_name]["success"] += 1
            old_avg = ts[task_name]["avg_time"]
            n = ts[task_name]["total"]
            ts[task_name]["avg_time"] = round(old_avg * (n-1)/n + elapsed/n, 1)
            if corps not in ts[task_name]["by_corps"]:
                ts[task_name]["by_corps"][corps] = {"total": 0, "success": 0}
            ts[task_name]["by_corps"][corps]["total"] += 1
            if success:
                ts[task_name]["by_corps"][corps]["success"] += 1
            # 按工人统计
            ws = self.data["stats_by_worker"]
            if worker_id not in ws:
                ws[worker_id] = {"total": 0, "success": 0, "avg_time": 0, "tasks": {}}
            ws[worker_id]["total"] += 1
            if success:
                ws[worker_id]["success"] += 1
            old_avg = ws[worker_id]["avg_time"]
            n = ws[worker_id]["total"]
            ws[worker_id]["avg_time"] = round(old_avg * (n-1)/n + elapsed/n, 1)
            if task_name not in ws[worker_id]["tasks"]:
                ws[worker_id]["tasks"][task_name] = 0
            ws[worker_id]["tasks"][task_name] += 1
            self._save()
        return entry
    def get_task_corps_winrate(self, task_name):
        """获取某任务各军团胜率"""
        ts = self.data.get("stats_by_task", {}).get(task_name, {}).get("by_corps", {})
        result = {}
        for corps, stats in ts.items():
            total = stats.get("total", 0)
            if total >= 3:  # 至少3次才有统计意义
                result[corps] = round(stats.get("success", 0) / total, 2)
        return result
    def report(self):
        lines = ["📊 Observation Log 汇总", "=" * 50]
        ts = self.data.get("stats_by_task", {})
        for task, stats in ts.items():
            sr = round(stats["success"]/max(1,stats["total"])*100, 0)
            lines.append(f"\n  {task}: {sr}%({stats['total']}次) avg={stats['avg_time']}s")
            for corps, cs in stats.get("by_corps", {}).items():
                csr = round(cs["success"]/max(1,cs["total"])*100, 0)
                lines.append(f"    {corps}: {csr}%({cs['total']}次)")
        return "\n".join(lines)


class TaskRouter:
    """P1: 任务路由器 — 按任务需求匹配工人画像 + O→E→C→R约束路由"""
    CONSTRAINT_FILE = "/home/coze/routing_constraints.json"

    def __init__(self, registry=None, observation=None):
        self.registry = registry or WorkerRegistry()
        self.observation = observation or ObservationLog()
        self._constraints = self._load_constraints()

    def _load_constraints(self):
        """加载路由约束：Observation→Experience→Constraint 产物"""
        if os.path.exists(self.CONSTRAINT_FILE):
            try:
                with open(self.CONSTRAINT_FILE) as f:
                    data = json.load(f)
                index = {}
                for rule in data.get("rules", []):
                    if rule.get("action") != "AVOID":
                        continue
                    conf = rule.get("confidence", "")
                    confirmed = rule.get("confirmed_ts") is not None
                    if (conf == "HIGH" and confirmed) or (conf == "MEDIUM" and confirmed):
                        task = rule["task"]
                        worker = rule["worker"]
                        index.setdefault(task, set()).add(worker)
                return index
            except Exception:
                pass
        return {}

    def _is_constrained(self, task_name, worker_id):
        """检查某个 task→worker 组合是否被约束(Constraint→Route)"""
        avoid_set = self._constraints.get(task_name, set())
        return worker_id in avoid_set
    def match(self, task_name, top_n=5):
        """
        核心路由：task requirements → worker strengths 匹配
        返回按匹配度排序的工人列表
        """
        profile = TASK_PROFILES.get(task_name, {
            "requirements": ["fast_response"],
            "avoid": [],
            "max_latency": 120,
            "min_context": 8000,
            "strategy": "balanced",
        })
        requirements = set(profile["requirements"])
        avoid = set(profile["avoid"])

        max_latency = profile["max_latency"]
        min_context = profile["min_context"]
        candidates = []
        for wid, w in self.registry.get_alive():
            # O→E→C→R: Constraint→Route 闭环 — 跳过被约束的组合
            if self._is_constrained(task_name, wid):
                print(f"  ⛔ AVOID: {task_name}→{wid} (constraint生效)")
                continue
            score = 0
            strengths = set(w.get("strengths", []))
            weaknesses = set(w.get("weaknesses", []))
            # 匹配度：需求∩优势
            matched = requirements & strengths
            score += len(matched) * 20  # 每匹配一个+20
            # 惩罚：需求∩劣势
            penalized = requirements & weaknesses
            score -= len(penalized) * 30  # 需求匹配到弱点-30
            # 避免：avoid∩优势 降权(不需要的优势没用)
            # 不扣分，只是不加
            # 延迟惩罚
            avg_lat = w.get("avg_latency", 10)
            if avg_lat > max_latency:
                score -= 20
            elif avg_lat < max_latency * 0.3:
                score += 10  # 快于预期加分
            # 成功率加成
            sr = w.get("success_rate", 0.9)
            score += int(sr * 20)
            # 上下文窗口检查
            ctx = w.get("context_window", 32000)
            if ctx < min_context:
                score -= 50  # 上下文不够重罚
            # 军团偏好：根据历史胜率
            corps_wr = self.observation.get_task_corps_winrate(task_name)
            corps = w.get("corps", "")
            if corps in corps_wr:
                score += int(corps_wr[corps] * 15)
            # 策略权重
            strategy = profile["strategy"]
            if strategy == "speed":
                score += max(0, 20 - avg_lat)  # 越快越好
            elif strategy == "quality":
                score += len(matched) * 5  # 匹配度更重要
            candidates.append((wid, w, score))
        candidates.sort(key=lambda x: -x[2])
        return candidates[:top_n]

    def check_anti_permanent(self):
        """反永久化：检查是否有约束到了review时间"""
        try:
            from constraint_proposer import check_review_schedule, process_review
            due = check_review_schedule()
            if due:
                # 加载最近观察数据
                from constraint_proposer import load_observations
                obs = load_observations()
                for rule in due:
                    process_review(rule, obs)
                # 保存更新后的约束
                from constraint_proposer import save_constraints
                import json
                with open('/home/coze/routing_constraints.json') as f:
                    constraints = json.load(f)
                save_constraints(constraints)
                pardoned = [r for r in constraints.get('rules', []) if r.get('review_status') == 'PARDONED']
                if pardoned:
                    print(f'🔓 反永久化：{len(pardoned)}条规则已洗白，从AVOID降级为MONITOR')
        except Exception as e:
            print(f'review检查异常(非致命): {e}')


    def get_fallback_chain(self, task_name):
        """获取任务的完整fallback链"""
        matched = self.match(task_name, top_n=10)
        if not matched:
            print(f"  ⚠️ fallback_chain为空: {task_name} (所有worker被AVOID或无可用)")
            return []
        return [(wid, w["model"]) for wid, w, score in matched]


class JudgeLayer:
    """P2: 裁判层 — 对比输出质量，积累胜率数据"""
    def __init__(self, observation=None):
        self.observation = observation or ObservationLog()
        self.lock = threading.Lock()
        self.history = self._load()
    def _load(self):
        if os.path.exists(JUDGE_FILE):
            try:
                with open(JUDGE_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {"comparisons": [], "win_rates": {}}
    def _save(self):
        with open(JUDGE_FILE, "w") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    def judge(self, task_name, output_a, worker_a, output_b, worker_b, prompt=""):
        """
        让裁判模型对比两个输出，判断谁更好
        用最快的GLM做裁判(因为只需要对比，不需要深度推理)
        """
        judge_prompt = f"""你是一个严格的质量裁判。对比以下两个AI对同一任务的输出，判断谁更好。

任务: {task_name}
原始提示词摘要: {prompt[:500]}

--- 输出A (Worker: {worker_a}) ---
{output_a[:1500]}

--- 输出B (Worker: {worker_b}) ---
{output_b[:1500]}

请严格按以下格式输出：
胜者: A 或 B 或 平局
理由: 一句话说明
质量分A: 1-10
质量分B: 1-10"""
        try:
            resp = requests.post(
                API_BASE,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "glm-4-flash",  # GLM做裁判，快+免费
                    "messages": [
                        {"role": "system", "content": "你是质量裁判。严格对比输出质量，给出公正判断。"},
                        {"role": "user", "content": judge_prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1
                },
                timeout=30
            )
            data = resp.json()
            if "choices" in data:
                result_text = data["choices"][0]["message"]["content"]
                # 解析结果
                winner = "平局"
                reason = ""
                qa, qb = 5, 5
                for line in result_text.split("\n"):
                    if "胜者" in line:
                        if "A" in line and "B" not in line:
                            winner = "A"
                        elif "B" in line and "A" not in line:
                            winner = "B"
                    elif "理由" in line:
                        reason = line.split(":", 1)[-1].strip() if ":" in line else line
                    elif "质量分A" in line:
                        try:
                            qa = int(''.join(c for c in line if c.isdigit()) or "5")
                        except:
                            pass
                    elif "质量分B" in line:
                        try:
                            qb = int(''.join(c for c in line if c.isdigit()) or "5")
                        except:
                            pass
                # 记录
                entry = {
                    "ts": datetime.now().isoformat(),
                    "task": task_name,
                    "worker_a": worker_a,
                    "worker_b": worker_b,
                    "winner": winner,
                    "reason": reason,
                    "quality_a": qa,
                    "quality_b": qb
                }
                with self.lock:
                    self.history["comparisons"].append(entry)
                    if len(self.history["comparisons"]) > 500:
                        self.history["comparisons"] = self.history["comparisons"][-500:]
                    # 更新胜率
                    wr = self.history["win_rates"]
                    if task_name not in wr:
                        wr[task_name] = {}
                    for wk in [worker_a, worker_b]:
                        if wk not in wr[task_name]:
                            wr[task_name][wk] = {"wins": 0, "losses": 0, "draws": 0}
                    if winner == "A":
                        wr[task_name][worker_a]["wins"] += 1
                        wr[task_name][worker_b]["losses"] += 1
                    elif winner == "B":
                        wr[task_name][worker_b]["wins"] += 1
                        wr[task_name][worker_a]["losses"] += 1
                    else:
                        wr[task_name][worker_a]["draws"] += 1
                        wr[task_name][worker_b]["draws"] += 1
                    self._save()
                return entry
        except Exception as e:
            return {"error": str(e)[:100], "winner": "error"}
        return {"winner": "unknown"}
    def get_worker_winrate(self, task_name, worker_id):
        """获取某工人在某任务的胜率"""
        wr = self.history.get("win_rates", {}).get(task_name, {}).get(worker_id, {})
        total = wr.get("wins", 0) + wr.get("losses", 0) + wr.get("draws", 0)
        if total == 0:
            return None
        return round(wr.get("wins", 0) / total, 2)
    def report(self):
        lines = ["⚖️ Judge Layer 胜率报告", "=" * 50]
        wr = self.history.get("win_rates", {})
        for task, workers in wr.items():
            lines.append(f"\n  {task}:")
            for wid, stats in sorted(workers.items(), key=lambda x: -(x[1].get("wins",0))):
                total = stats.get("wins",0) + stats.get("losses",0) + stats.get("draws",0)
                if total > 0:
                    wr_pct = round(stats.get("wins",0)/total*100)
                    lines.append(f"    {wid}: {wr_pct}%胜({total}场)")
        total_comparisons = len(self.history.get("comparisons", []))
        lines.append(f"\n  总对比次数: {total_comparisons}")
        return "\n".join(lines)


# ==================== 便捷接口 ====================
# 全局实例
registry = WorkerRegistry()
observation = ObservationLog()
router = TaskRouter(registry, observation)
judge = JudgeLayer(observation)

if __name__ == "__main__":
    print(registry.report())
    print("\n" + observation.report())
    # 测试任务路由
    print("\n🎯 任务路由测试:")
    for task in TASK_PROFILES:
        matched = router.match(task, top_n=3)
        print(f"\n  {task}:")
        for wid, w, score in matched:
            print(f"    {wid} ({w['corps']}) score={score} strengths={w.get('strengths',[])}")
    print("\n" + judge.report())
