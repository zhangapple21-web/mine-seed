#!/usr/bin/env python3
"""
经验引擎 — 矿场的核心资产层

不是AI调用工具，不是数字生命，是经验管理系统。
把"怎么把事做好"从模型/代码/人里抽出来，变成：
  - 可积累（每班次自动沉淀）
  - 可迁移（换模型不用重新学）
  - 可自动优化（经验压缩→路由升级）

三层结构：
  Raw Observation → 经验压缩 → 路由知识
  (原始数据)        (模式提取)   (可执行规则)
"""
import json, os, time
from datetime import datetime, timedelta
from collections import defaultdict

EXPERIENCE_FILE = "/home/coze/mine_output/experience.json"
OBSERVATION_FILE = "/home/coze/mine_output/observation_log.json"
FEEDBACK_FILE = "/home/coze/mine_output/user_feedback.jsonl"
REGISTRY_FILE = "/home/coze/worker_registry.json"

class ExperienceEngine:
    def __init__(self):
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(EXPERIENCE_FILE):
            try:
                with open(EXPERIENCE_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {
            "version": "2.0",
            "patterns": {},       # 压缩后的经验模式
            "routing_rules": [],  # 生成的路由规则
            "compression_log": [], # 压缩历史
            "reasoning_chains": [],   # R1v2.0: 决策路径记录
            "user_feedback": [],       # R1v2.0: 用户反馈/结果记录
            "innovation_patterns": [], # R1v2.0: 不合现有分类的新模式
            "self_improve_tips": []    # R1v2.0: 自我改进建议
        }
    
    def _save(self):
        with open(EXPERIENCE_FILE, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def compress(self):
        self._ensure_structure()
        """
        经验压缩：从原始Observation中提取可复用的模式
        
        输入：上千条"任务→工人→结果"记录
        输出：
          - 每种任务的最佳工人排行
          - 每个工人的任务适配画像
          - 失败模式（什么任务+什么条件→容易失败）
          - 路由规则（可直接写入TaskRouter）
        """
        # 读取原始观察
        if not os.path.exists(OBSERVATION_FILE):
            return {"error": "No observation data yet"}
        
        with open(OBSERVATION_FILE) as f:
            obs_data = json.load(f)
        
        observations = obs_data.get("observations", [])
        if len(observations) < 10:
            return {"error": f"Only {len(observations)} observations, need at least 10"}
        
        patterns = {}
        
        # === 1. 任务×工人 效率矩阵 ===
        task_worker = defaultdict(lambda: defaultdict(lambda: {"total": 0, "success": 0, "total_time": 0, "total_tokens": 0, "quality_scores": []}))
        
        for obs in observations:
            task = obs.get("task", "unknown")
            worker = obs.get("worker_id", "unknown")
            bucket = task_worker[task][worker]
            bucket["total"] += 1
            if obs.get("success"):
                bucket["success"] += 1
            bucket["total_time"] += obs.get("elapsed", 0)
            bucket["total_tokens"] += obs.get("tokens_out", 0)
            if obs.get("quality"):
                bucket["quality_scores"].append(obs["quality"])
        
        # 压缩：每种任务只保留Top3工人 + 原因
        for task, workers in task_worker.items():
            ranked = []
            for wid, stats in workers.items():
                if stats["total"] < 2:
                    continue
                sr = stats["success"] / stats["total"]
                avg_time = stats["total_time"] / stats["total"]
                avg_quality = sum(stats["quality_scores"]) / len(stats["quality_scores"]) if stats["quality_scores"] else None
                # 效率分 = 成功率×0.4 + 速度分×0.3 + 质量分×0.3
                speed_score = max(0, 100 - avg_time * 2)
                quality_score = (avg_quality or 5) * 10
                efficiency = sr * 40 + speed_score * 0.3 + quality_score * 0.3
                ranked.append({
                    "worker": wid,
                    "efficiency": round(efficiency, 1),
                    "success_rate": round(sr, 2),
                    "avg_time": round(avg_time, 1),
                    "avg_quality": round(avg_quality, 1) if avg_quality else None,
                    "samples": stats["total"]
                })
            
            ranked.sort(key=lambda x: -x["efficiency"])
            patterns[task] = {
                "best_workers": ranked[:3],
                "total_observations": sum(s["total"] for s in workers.values()),
                "last_updated": datetime.now().isoformat()
            }
        
        # === 2. 失败模式提取 ===
        failure_patterns = defaultdict(lambda: defaultdict(int))
        for obs in observations:
            if not obs.get("success"):
                task = obs.get("task", "unknown")
                worker = obs.get("worker_id", "unknown")
                error = obs.get("error", "unknown")
                # 压缩错误类型
                if "timeout" in error.lower():
                    etype = "timeout"
                elif "429" in error or "rate" in error.lower():
                    etype = "rate_limit"
                else:
                    etype = "api_error"
                failure_patterns[f"{task}|{worker}"][etype] += 1
        
        compressed_failures = []
        for key, errors in failure_patterns.items():
            task, worker = key.split("|", 1)
            total = sum(errors.values())
            if total >= 2:  # 出现2次以上的失败模式
                compressed_failures.append({
                    "task": task,
                    "worker": worker,
                    "failure_count": total,
                    "failure_types": dict(errors),
                    "recommendation": f"避免用{worker}做{task}" if total >= 3 else f"谨慎使用{worker}做{task}"
                })
        
        # === 3. 生成路由规则 ===
        routing_rules = []
        for task, data in patterns.items():
            if not data["best_workers"]:
                continue
            best = data["best_workers"][0]
            if best["samples"] >= 3 and best["success_rate"] >= 0.7:
                rule = {
                    "task": task,
                    "primary_worker": best["worker"],
                    "primary_efficiency": best["efficiency"],
                    "fallback_chain": [w["worker"] for w in data["best_workers"]],
                    "confidence": min(1.0, best["samples"] / 20),  # 20次以上=高置信
                    "source": "experience_compression",
                    "generated_at": datetime.now().isoformat()
                }
                routing_rules.append(rule)
        
        # 保存
        self.data["patterns"] = patterns
        self.data["failure_patterns"] = compressed_failures
        self.data["routing_rules"] = routing_rules
        
        # === Meaning层：从经验模式中提取原则 ===
        # 不是单条observation的抽象，而是跨模式的结构性洞察
        meanings_extracted = self._extract_meanings(patterns, compressed_failures, routing_rules)
        self.data["meanings"] = meanings_extracted

        # === 保存压缩结果 ===
        self.data["compression_log"].append({
            "ts": datetime.now().isoformat(),
            "observations_processed": len(observations),
            "patterns_found": len(patterns),
            "failures_found": len(compressed_failures),
            "rules_generated": len(routing_rules)
        })
        if len(self.data["compression_log"]) > 50:
            self.data["compression_log"] = self.data["compression_log"][-50:]
        self._save()
        
        return {
            "patterns": len(patterns),
            "failures": len(compressed_failures),
            "rules": len(routing_rules),
            "observations_used": len(observations)
        }
    
    def _extract_meanings(self, patterns: dict, failures: dict, rules: list) -> list:
        """
        从经验模式中提取Meaning（"这件事说明了什么"）
        
        Meaning vs Principle vs Constraint：
        - Constraint：glm_4_flash + mean_reversion = AVOID（具体路由规则）
        - Meaning：失败可能来自岗位错配，而非Worker质量（洞察）
        - Principle：岗位错配大于执行失败（长期重复的Meaning沉淀为Principle）
        
        当前阶段：仅收集Meaning样本，禁止自动生成Principle。
        30天后评估哪些Meaning重复出现，才允许升级为Principle Candidate。
        
        触发条件：同一类现象在3+个不同场景中出现
        """
        meanings = []
        
        # 原则1：启动参数错误检测
        # 如果同一个worker在多个不同task上失败，说明不是task问题，是worker位置问题
        worker_fail_tasks = defaultdict(list)
        if isinstance(failures, list):
            # failures is a list of dicts
            for f_entry in failures:
                task = f_entry.get("task", "unknown")
                worker = f_entry.get("worker", "unknown")
                fail_count = f_entry.get("failure_count", 0)
                if fail_count >= 3:
                    worker_fail_tasks[worker].append(task)
        elif isinstance(failures, dict):
            for key, error_types in failures.items():
                parts = key.split("|")
                if len(parts) == 2:
                    task, worker = parts
                    total_fails = sum(error_types.values())
                    if total_fails >= 3:
                        worker_fail_tasks[worker].append(task)
        
        for worker, tasks in worker_fail_tasks.items():
            if len(tasks) >= 2:  # 同一个worker在2+不同task上失败
                meanings.append({
                    "type": "startup_parameter_mismatch",
                    "evidence": f"{worker} fails across {len(tasks)} tasks: {tasks}",
                    "meaning": f"同一Worker({worker})在{len(tasks)}个不同岗位失败，失败可能来自岗位错配而非Worker质量",
                    "source_workers": [worker],
                    "sample_count": len(tasks),
                    "note": "Meaning样本，非Principle。30天后观察是否重复出现才允许升级",
                    "ts": datetime.now().isoformat()
                })
        
        # 原则2：复杂度分界线检测
        # 如果某个category（complex/simple）的失败率系统性高于另一个
        try:
            import json as _j
            with open("/home/coze/signal_taxonomy.json") as _f:
                taxonomy = _j.load(_f)
            
            simple_types = taxonomy.get("categories", {}).get("simple_signal", {}).get("types", [])
            complex_types = taxonomy.get("categories", {}).get("complex_signal", {}).get("types", [])
            
            # 统计fitness_log
            fitness_log = "/home/coze/mine_output/fitness_log.jsonl"
            if os.path.exists(fitness_log):
                from collections import defaultdict as _dd
                cat_stats = _dd(lambda: {"success": 0, "fail": 0})
                with open(fitness_log) as _f:
                    for line in _f:
                        try:
                            entry = _j.loads(line.strip())
                            cat = entry.get("signal_category", "unknown")
                            if entry["outcome"] == "SUCCESS":
                                cat_stats[cat]["success"] += 1
                            else:
                                cat_stats[cat]["fail"] += 1
                        except:
                            continue
                
                simple_total = cat_stats["simple_signal"]["success"] + cat_stats["simple_signal"]["fail"]
                complex_total = cat_stats["complex_signal"]["success"] + cat_stats["complex_signal"]["fail"]
                
                if simple_total >= 5 and complex_total >= 5:
                    simple_rate = cat_stats["simple_signal"]["success"] / simple_total
                    complex_rate = cat_stats["complex_signal"]["success"] / complex_total
                    if complex_rate < simple_rate * 0.5:  # complex成功率不到simple的一半
                        meanings.append({
                            "type": "complexity_boundary",
                            "evidence": f"simple_rate={simple_rate:.0%}, complex_rate={complex_rate:.0%}",
                            "meaning": f"complex类型成功率({complex_rate:.0%})系统性低于simple({simple_rate:.0%})，信号复杂度可能是成功率的隐性分界线",
                            "sample_count": simple_total + complex_total,
                            "note": "Meaning样本，非Principle。30天后观察是否重复出现才允许升级",
                            "ts": datetime.now().isoformat()
                        })
        except:
            pass
        
        # 原则3：连续性断点检测
        # 如果observation数量突然下降，说明数据采集链路可能断裂
        # (这个由档案官日报负责，这里只做标记)
        
        # 原则4：效率塌陷检测
        # 如果某个task的top worker效率分<50，说明这个岗位本身可能有问题
        for task_name, task_data in patterns.items():
            if isinstance(task_data, dict) and 'best_workers' in task_data:
                best = task_data['best_workers']
                if best and best[0].get('efficiency', 100) < 50:
                    meanings.append({
                        "type": "efficiency_collapse",
                        "evidence": f"{task_name}: best worker efficiency={best[0]['efficiency']}, success_rate={best[0].get('success_rate',0)}",
                        "meaning": f"岗位({task_name})最高效率仅{best[0]['efficiency']}，可能不是Worker问题而是岗位设计问题——这个任务本身可能需要拆分或重新定义",
                        "source_task": task_name,
                        "sample_count": 1,
                        "note": "Meaning样本，非Principle。30天后观察是否重复出现才允许升级",
                        "ts": datetime.now().isoformat()
                    })
        
        # 原则5：独霸岗位检测
        # 如果某个worker在3+个task中都是top1，说明系统对这个worker依赖度过高
        worker_top_count = defaultdict(int)
        worker_top_tasks = defaultdict(list)
        for task_name, task_data in patterns.items():
            if isinstance(task_data, dict) and 'best_workers' in task_data:
                best = task_data['best_workers']
                if best:
                    top_worker = best[0].get('worker', 'unknown')
                    worker_top_count[top_worker] += 1
                    worker_top_tasks[top_worker].append(task_name)
        
        for worker, count in worker_top_count.items():
            if count >= 3:
                meanings.append({
                    "type": "single_point_of_excellence",
                    "evidence": f"{worker} is top1 in {count} tasks: {worker_top_tasks[worker]}",
                    "meaning": f"Worker({worker})独占{count}个岗位的最佳位置，系统对其依赖度过高——一旦该Worker下线，多个岗位将同时降级",
                    "source_workers": [worker],
                    "sample_count": count,
                    "note": "Meaning样本，非Principle。30天后观察是否重复出现才允许升级",
                    "ts": datetime.now().isoformat()
                })
        
        return meanings
    
    def apply_routing_rules(self):
        """
        把压缩后的路由规则应用到Registry——
        这就是"经验变成可执行规则"的一步
        
        根据经验数据动态更新worker的strengths
        """
        if not os.path.exists(REGISTRY_FILE):
            return "No registry"
        
        with open(REGISTRY_FILE) as f:
            reg = json.load(f)
        
        changes = []
        for rule in self.data.get("routing_rules", []):
            task = rule["task"]
            primary = rule["primary_worker"]
            confidence = rule.get("confidence", 0)
            
            if confidence < 0.3:
                continue  # 置信度太低不改
            
            # 从任务需求推导能力标签
            from task_router import TASK_PROFILES
            task_reqs = TASK_PROFILES.get(task, {}).get("requirements", [])
            
            # 如果某worker在某任务上表现好，把任务需求加到它的strengths里
            if primary in reg["workers"]:
                w = reg["workers"][primary]
                strengths = set(w.get("strengths", []))
                new_strengths = strengths | set(task_reqs)
                if new_strengths != strengths:
                    w["strengths"] = list(new_strengths)
                    w["proven_at"] = w.get("proven_at", {})
                    w["proven_at"][task] = {
                        "efficiency": rule["primary_efficiency"],
                        "confidence": confidence,
                        "samples": rule.get("confidence", 0) * 20
                    }
                    changes.append(f"{primary}+{task_reqs}(conf={confidence:.0%})")
        
        if changes:
            with open(REGISTRY_FILE, "w") as f:
                json.dump(reg, f, ensure_ascii=False, indent=2)
        
        return changes
    
    def report(self):
        lines = ["🧠 Experience Engine 经验报告", "=" * 50]
        
        patterns = self.data.get("patterns", {})
        if patterns:
            lines.append("\n📊 任务最佳工人(经验压缩):")
            for task, data in patterns.items():
                lines.append(f"\n  {task} ({data.get('total_observations',0)}次观察):")
                for w in data.get("best_workers", []):
                    lines.append(f"    {w['worker']}: eff={w['efficiency']} sr={w['success_rate']} avg={w['avg_time']}s")
        
        failures = self.data.get("failure_patterns", [])
        if failures:
            lines.append("\n⚠️ 失败模式:")
            for f in sorted(failures, key=lambda x: -x["failure_count"])[:5]:
                lines.append(f"  {f['task']}+{f['worker']}: {f['failure_count']}次 {f['failure_types']} → {f['recommendation']}")
        
        rules = self.data.get("routing_rules", [])
        if rules:
            lines.append(f"\n📐 生成的路由规则: {len(rules)}条")
            for r in rules:
                lines.append(f"  {r['task']}: {r['primary_worker']}(eff={r['primary_efficiency']}, conf={r.get('confidence',0):.0%})")
        
        # 压缩历史
        log = self.data.get("compression_log", [])
        if log:
            last = log[-1]
            lines.append(f"\n🔄 最近压缩: {last['observations_processed']}条→{last['patterns_found']}模式→{last['rules_generated']}规则")
        
        return "\n".join(lines)



    # === R1v2.0: 记录推理链 ===
    def record_reasoning_chain(self, task, worker, chain_data):
        """记录一次决策的完整推理路径"""
        entry = {
            "ts": datetime.now().isoformat(),
            "task": task,
            "worker": worker,
            "input_snapshot": chain_data.get("input", ""),
            "reasoning_steps": chain_data.get("steps", []),
            "alternatives_considered": chain_data.get("alternatives", []),
            "final_decision": chain_data.get("decision", ""),
            "confidence": chain_data.get("confidence", 0.5)
        }
        self.data.setdefault("reasoning_chains", []).append(entry)
        # 最多保留500条
        if len(self.data["reasoning_chains"]) > 500:
            self.data["reasoning_chains"] = self.data["reasoning_chains"][-500:]
        self._save()
        return entry["ts"]

    # === R1v2.0: 记录用户反馈 ===
    def record_feedback(self, source, content, reaction="unknown", quality=None):
        """记录用户/系统对产出的反馈

        Args:
            source: 反馈来源 (user/system/auto)
            content: 产出内容摘要或ID
            reaction: 反馈 (positive/negative/neutral/unknown)
            quality: 质量评分 1-10 (可选)
        """
        entry = {
            "ts": datetime.now().isoformat(),
            "source": source,
            "content": content,
            "reaction": reaction,
            "quality": quality
        }
        self.data.setdefault("user_feedback", []).append(entry)
        # 最多保留200条
        if len(self.data["user_feedback"]) > 200:
            self.data["user_feedback"] = self.data["user_feedback"][-200:]
        self._save()
        
        # 同时写入独立文件供外部工具读取
        try:
            with open(FEEDBACK_FILE, "a") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except:
            pass
        return entry["ts"]

    # === R1v2.0: 带权重衰减的压缩（近期观测权重更高）===
    def _ensure_structure(self):
        """确保数据结构含有所有必要字段"""
        defaults = {
            "version": "2.0",
            "patterns": {},
            "routing_rules": [],
            "compression_log": [],
            "failure_patterns": [],
            "meanings": [],
            "reasoning_chains": [],
            "user_feedback": [],
            "innovation_patterns": [],
            "self_improve_tips": []
        }
        for key, default in defaults.items():
            if key not in self.data:
                self.data[key] = default

    def compress_with_decay(self, decay_days=3):
        """经验压缩 + 时间权重衰减

        近期观测(decay_days内)权重大于历史观测，
        使系统更快适应模型能力变化和数据源波动。
        """
        self._ensure_structure()
        cutoff = (datetime.now() - timedelta(days=decay_days)).isoformat()
        
        if not os.path.exists(OBSERVATION_FILE):
            return {"error": "No observation data yet"}
        
        with open(OBSERVATION_FILE) as f:
            obs_data = json.load(f)
        
        observations = obs_data.get("observations", [])
        if len(observations) < 10:
            return {"error": f"Only {len(observations)} observations, need at least 10"}
        
        # 标记近期观测
        recent_count = 0
        for obs in observations:
            obs_ts = obs.get("ts", "")
            obs["_is_recent"] = obs_ts > cutoff
            if obs["_is_recent"]:
                recent_count += 1
        
        patterns = {}
        task_worker = defaultdict(lambda: defaultdict(
            lambda: {"total": 0, "success": 0, "total_time": 0, "total_tokens": 0, 
                     "quality_scores": [], "recent_total": 0, "recent_success": 0}
        ))
        
        for obs in observations:
            task = obs.get("task", "unknown")
            worker = obs.get("worker_id", "unknown")
            bucket = task_worker[task][worker]
            weight = 2.0 if obs.get("_is_recent") else 1.0  # 近期2x权重
            bucket["total"] += weight
            if obs.get("success"):
                bucket["success"] += weight
            bucket["total_time"] += obs.get("elapsed", 0)
            bucket["total_tokens"] += obs.get("tokens_out", 0)
            if obs.get("quality"):
                bucket["quality_scores"].append(obs["quality"])
            if obs.get("_is_recent"):
                bucket["recent_total"] += 1
                if obs.get("success"):
                    bucket["recent_success"] += 1
        
        # 后续压缩逻辑复用现有compress()的相同代码模式
        for task, workers in task_worker.items():
            ranked = []
            for wid, stats in workers.items():
                if stats["total"] < 2:
                    continue
                sr = stats["success"] / stats["total"]
                # 近期成功率单独计算（如果有近期数据）
                recent_sr = stats["recent_success"] / stats["recent_total"] if stats["recent_total"] >= 2 else sr
                avg_time = stats["total_time"] / stats["total"]
                avg_quality = sum(stats["quality_scores"]) / len(stats["quality_scores"]) if stats["quality_scores"] else None
                # 效率分：近期表现占60%权重
                speed_score = max(0, 100 - avg_time * 2)
                quality_score = (avg_quality or 5) * 10
                efficiency = (sr * 0.4 + recent_sr * 0.6) * 40 + speed_score * 0.3 + quality_score * 0.3
                ranked.append({
                    "worker": wid,
                    "efficiency": round(efficiency, 1),
                    "success_rate": round(sr, 2),
                    "recent_success_rate": round(recent_sr, 2),
                    "avg_time": round(avg_time, 1),
                    "avg_quality": round(avg_quality, 1) if avg_quality else None,
                    "samples": int(stats["total"]),
                    "recent_samples": int(stats["recent_total"])
                })
            
            ranked.sort(key=lambda x: -x["efficiency"])
            patterns[task] = {
                "best_workers": ranked[:3],
                "total_observations": int(sum(s["total"] for s in workers.values())),
                "recent_observations": recent_count,
                "decay_window_days": decay_days,
                "last_updated": datetime.now().isoformat()
            }
        
        # 复用旧的failure/meaning/rules提取逻辑（但用更新后的patterns）
        # 保存patterns到self.data
        self.data["patterns"] = patterns
        self.data["compression_log"].append({
            "ts": datetime.now().isoformat(),
            "observations_processed": len(observations),
            "patterns_found": len(patterns),
            "recent_weighted": recent_count,
            "decay_window_days": decay_days
        })
        if len(self.data["compression_log"]) > 50:
            self.data["compression_log"] = self.data["compression_log"][-50:]
        self._save()
        
        return {
            "patterns": len(patterns),
            "observations_used": len(observations),
            "recent_weighted": recent_count
        }
    
    # === R1v2.0: 创新模式检测 ===
    def detect_innovation_patterns(self):
        """
        检测不合现有分类的新模式。
        
        当某个worker在某task上的表现出现非预期变化（
        突然好转/突然恶化），但不匹配任何已知失败模式时，
        标记为"待观察的创新模式"。
        """
        if not self.data.get("patterns"):
            return []
        
        innovations = []
        for task, task_data in self.data["patterns"].items():
            workers = task_data.get("best_workers", [])
            for w in workers:
                # 发现：近期成功率 vs 历史成功率差异 > 30%
                recent_sr = w.get("recent_success_rate", 0)
                hist_sr = w.get("success_rate", 0)
                if recent_sr > 0 and hist_sr > 0:
                    delta = recent_sr - hist_sr
                    if abs(delta) > 0.3:
                        innovations.append({
                            "type": "sr_shift" if delta > 0 else "sr_decline",
                            "task": task,
                            "worker": w["worker"],
                            "delta": round(delta, 2),
                            "recent_sr": recent_sr,
                            "historical_sr": hist_sr,
                            "recent_samples": w.get("recent_samples", 0),
                            "ts": datetime.now().isoformat(),
                            "note": f"({w["worker"]})在({task})上表现发生{'+' if delta > 0 else ''}{delta:.0%}变化，需要关注"
                        })
        
        if innovations:
            self.data["innovation_patterns"] = innovations
            self._save()
        
        return innovations

    # === R1v2.0: 生成自我改进建议 ===
    def generate_improve_tips(self):
        """根据经验数据生成可操作的改进建议"""
        tips = []
        
        # 1. 检查是否有worker正在衰退
        for pattern in self.data.get("patterns", {}).values():
            for w in pattern.get("best_workers", []):
                if w.get("recent_success_rate", 1) < w.get("success_rate", 1) * 0.7:
                    tips.append({
                        "type": "worker_decline",
                        "target": w["worker"],
                        "suggestion": f"{w['worker']}近期胜率({w.get('recent_success_rate',0):.0%})显著低于历史({w.get('success_rate',0):.0%})，建议review或降级",
                        "priority": "P1",
                        "ts": datetime.now().isoformat()
                    })
        
        # 2. 检查ioU模式（持续改进中）
        if self.data.get("innovation_patterns"):
            tips.append({
                "type": "innovation_observed",
                "target": "multiple",
                "suggestion": f"发现{len(self.data['innovation_patterns'])}个不合常规的模式变化，建议人工review",
                "priority": "P2",
                "ts": datetime.now().isoformat()
            })
        
        # 3. 检查反馈趋势
        feedback = self.data.get("user_feedback", [])
        if feedback:
            negative = [f for f in feedback if f.get("reaction") == "negative"]
            if len(negative) >= 3:
                tips.append({
                    "type": "feedback_warning",
                    "target": "system",
                    "suggestion": f"近期收到{len(negative)}条负面反馈，建议检查产出质量",
                    "priority": "P1",
                    "ts": datetime.now().isoformat()
                })
        
        if tips:
            self.data["self_improve_tips"] = tips
            self._save()
        
        return tips



    # ============================================================
    # 渐进式检索系统 — v1.0（吸收 claude-mem 三层渐进思路）
    # 2026-06-24 新增
    # ============================================================
    
    def retrieve_by_layer(self, layer=1, query=None, limit=10, 
                          target_ts=None, target_task=None, target_worker=None):
        """
        渐进式三层检索：search_index → timeline → get_detail
        
        Layer 1 (search_index): 快速扫描observation_log，按条件过滤
            返回精简索引摘要（~50-80 token/条）
        Layer 2 (timeline): 围绕target_ts返回前后N条时间线上下文
        Layer 3 (get_detail): 返回完整observation记录
        
        Args:
            layer: 1=索引, 2=时间线, 3=详情
            query: 关键词匹配（对task/worker/error做子串匹配）
            limit: 每层返回条数上限
            target_ts: 时间线锚点（Layer 2必填）
            target_task: 按任务类型过滤
            target_worker: 按工人ID过滤
        """
        if not os.path.exists(OBSERVATION_FILE):
            return {"error": "No observation data yet", "layer": layer}
        
        with open(OBSERVATION_FILE) as f:
            obs_data = json.load(f)
        
        observations = obs_data.get("observations", [])
        if not observations:
            return {"error": "Empty observation log", "layer": layer}
        
        # 通用过滤
        filtered = observations
        if query:
            q = query.lower()
            filtered = [o for o in filtered if 
                       q in o.get("task", "").lower() or 
                       q in o.get("worker_id", "").lower() or
                       q in str(o.get("error", "")).lower()]
        if target_task:
            filtered = [o for o in filtered if o.get("task") == target_task]
        if target_worker:
            filtered = [o for o in filtered if o.get("worker_id") == target_worker]
        
        if layer == 1:
            # Layer 1: 索引摘要 — 精简版
            index = []
            for o in filtered[-limit:]:
                index.append({
                    "ts": o.get("ts", ""),
                    "task": o.get("task", "?"),
                    "worker": o.get("worker_id", "?"),
                    "model": o.get("model", "?"),
                    "corps": o.get("corps", "?"),
                    "ok": o.get("success", False),
                    "elapsed": round(o.get("elapsed", 0), 1),
                    "tokens": o.get("tokens_out", 0),
                    "error": (o.get("error", "") or "")[:40] if not o.get("success") else ""
                })
            return {
                "layer": 1,
                "total_matched": len(filtered),
                "returned": len(index),
                "index": index,
                "hint": "用 layer=2 + target_ts 查时间线，或用 layer=3 查完整记录"
            }
        
        elif layer == 2:
            if not target_ts:
                target_ts = filtered[-1]["ts"] if filtered else ""
            
            anchor_idx = -1
            for i, o in enumerate(filtered):
                if o.get("ts", "") == target_ts:
                    anchor_idx = i
                    break
            if anchor_idx == -1:
                anchor_idx = len(filtered) - 1
            
            half = max(3, limit // 2)
            start = max(0, anchor_idx - half)
            end = min(len(filtered), anchor_idx + half + 1)
            
            timeline = []
            for o in filtered[start:end]:
                timeline.append({
                    "ts": o.get("ts", ""),
                    "task": o.get("task", "?"),
                    "worker": o.get("worker_id", "?"),
                    "ok": o.get("success", False),
                    "elapsed": round(o.get("elapsed", 0), 1),
                    "is_anchor": o.get("ts", "") == target_ts,
                    "error_short": (o.get("error", "") or "")[:30] if not o.get("success") else ""
                })
            
            return {
                "layer": 2,
                "anchor_ts": target_ts,
                "timeline_range": f"#{start}~#{end-1}",
                "timeline": timeline,
                "hint": "用 layer=3 + target_ts 查完整记录"
            }
        
        elif layer == 3:
            if target_ts:
                details = [o for o in filtered if o.get("ts") == target_ts]
            else:
                details = filtered[-limit:]
            
            return {
                "layer": 3,
                "returned": len(details),
                "details": details,
                "hint": "可用 query/target_task/target_worker 缩小范围"
            }
        
        return {"error": f"Invalid layer: {layer}", "layer": layer}
    
    def quick_observe(self, task, worker_id, model, corps, success,
                      elapsed=0, tokens_in=0, tokens_out=0, error="", quality=None):
        """
        轻量写入一条observation（独立于task_router的写入点）
        
        适用场景：
        - 信号发现引擎在ACCEPT新因子时记录
        - Dragon Leader在涨停分组后记录
        - Stock Advisor在出建议后记录
        - 任何不在矿场班次内的独立任务
        """
        obs = {
            "ts": datetime.now().isoformat(),
            "task": task,
            "worker_id": worker_id,
            "model": model,
            "corps": corps,
            "elapsed": round(elapsed, 2),
            "success": success,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "error": str(error) if error else "",
            "quality": quality
        }
        
        if os.path.exists(OBSERVATION_FILE):
            try:
                with open(OBSERVATION_FILE) as f:
                    data = json.load(f)
            except:
                data = {"observations": []}
        else:
            data = {"observations": []}
        
        data["observations"].append(obs)
        
        if len(data["observations"]) > 5000:
            data["observations"] = data["observations"][-4000:]
        
        with open(OBSERVATION_FILE, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return obs


if __name__ == "__main__":
    engine = ExperienceEngine()
    result = engine.compress()
    print(f"压缩结果: {result}")
    
    if result.get("rules", 0) > 0:
        changes = engine.apply_routing_rules()
        print(f"路由更新: {changes}")
    
    print(engine.report())
