#!/usr/bin/env python3
"""
智能路由器 v1 - 从"调用AI"到"管理AI劳动力"的质变
功能：
1. 按速度/质量/成本动态选模型
2. 自动淘汰差模型、自动升级好模型
3. 持久化模型评分到JSON
"""
import json, time, os, threading
from datetime import datetime, timedelta

PERF_FILE = "/home/coze/mine_output/model_performance.json"

# 模型评分维度: speed(0-100), quality(0-100), reliability(0-100), cost_efficiency(0-100)
# cost_efficiency: 免费模型=100, 付费=按价格倒扣
DEFAULT_PROFILES = {
    # Ultra级
    "nvidia/nemotron-3-ultra-550b-a55b": {"speed": 30, "quality": 95, "reliability": 70, "cost": 100, "tier": "ultra"},
    "qwen/qwen3.5-397b-a17b": {"speed": 40, "quality": 90, "reliability": 80, "cost": 100, "tier": "ultra"},
    "qwen/qwen3.5-122b-a10b": {"speed": 50, "quality": 85, "reliability": 85, "cost": 100, "tier": "heavy"},
    
    # Heavy级
    "meta/llama-3.3-70b-instruct": {"speed": 70, "quality": 80, "reliability": 95, "cost": 100, "tier": "heavy"},
    "openai/gpt-oss-120b": {"speed": 60, "quality": 82, "reliability": 80, "cost": 100, "tier": "heavy"},
    "nvidia/nemotron-3-super-120b-a12b": {"speed": 55, "quality": 83, "reliability": 75, "cost": 100, "tier": "heavy"},
    "mistralai/mistral-large-3-675b-instruct-2512": {"speed": 45, "quality": 88, "reliability": 80, "cost": 100, "tier": "heavy"},
    "zai/glm-5.1": {"speed": 65, "quality": 80, "reliability": 85, "cost": 100, "tier": "heavy"},
    "gpt-4o": {"speed": 75, "quality": 88, "reliability": 90, "cost": 80, "tier": "heavy"},
    
    # Reason级
    "nvidia/llama-3.3-nemotron-super-49b-v1.5": {"speed": 50, "quality": 85, "reliability": 80, "cost": 100, "tier": "reason"},
    "bytedance/seed-oss-36b-instruct": {"speed": 55, "quality": 80, "reliability": 80, "cost": 100, "tier": "reason"},
    
    # Fast级
    "deepseek-ai/deepseek-v4-flash": {"speed": 80, "quality": 75, "reliability": 85, "cost": 100, "tier": "fast"},
    "openai/gpt-oss-20b": {"speed": 85, "quality": 72, "reliability": 85, "cost": 100, "tier": "fast"},
    "stepfun-ai/step-3.7-flash": {"speed": 85, "quality": 70, "reliability": 85, "cost": 100, "tier": "fast"},
    "google/gemma-4-31b-it": {"speed": 80, "quality": 72, "reliability": 80, "cost": 100, "tier": "fast"},
    "qwen/qwen3-next-80b-a3b-instruct": {"speed": 75, "quality": 75, "reliability": 85, "cost": 100, "tier": "fast"},
    "moonshotai/kimi-k2.6": {"speed": 70, "quality": 78, "reliability": 80, "cost": 100, "tier": "fast"},
    "minimaxai/minimax-m2.7": {"speed": 72, "quality": 74, "reliability": 80, "cost": 100, "tier": "fast"},
    "meta/llama-4-maverick-17b-128e-instruct": {"speed": 78, "quality": 70, "reliability": 80, "cost": 100, "tier": "fast"},
    "gpt-4o-mini": {"speed": 90, "quality": 72, "reliability": 95, "cost": 80, "tier": "fast"},
    "glm-4-flash": {"speed": 88, "quality": 68, "reliability": 90, "cost": 100, "tier": "fast"},
    
    # 已淘汰
    "deepseek-ai/deepseek-v4-pro": {"speed": 15, "quality": 90, "reliability": 40, "cost": 100, "tier": "dead"},
    "DeepSeek-R1": {"speed": 20, "quality": 88, "reliability": 50, "cost": 80, "tier": "dead"},
}

class ModelRouter:
    def __init__(self):
        self.perf = self._load()
        self.lock = threading.Lock()
    
    def _load(self):
        if os.path.exists(PERF_FILE):
            try:
                with open(PERF_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {"models": DEFAULT_PROFILES, "history": [], "retired": []}
    
    def _save(self):
        with open(PERF_FILE, "w") as f:
            json.dump(self.perf, f, ensure_ascii=False, indent=2)
    
    def score(self, model, weights=None):
        """计算模型综合分，默认: speed*0.3 + quality*0.35 + reliability*0.25 + cost*0.1"""
        w = weights or {"speed": 0.3, "quality": 0.35, "reliability": 0.25, "cost": 0.1}
        p = self.perf["models"].get(model)
        if not p or p.get("tier") == "dead":
            return 0
        return sum(p.get(k, 0) * v for k, v in w.items())
    
    def select(self, tier="fast", strategy="balanced", count=3):
        """
        选择最优模型
        strategy: balanced(综合) / speed(最快) / quality(最好) / cost(最省)
        """
        weight_map = {
            "balanced": {"speed": 0.3, "quality": 0.35, "reliability": 0.25, "cost": 0.1},
            "speed":    {"speed": 0.6, "quality": 0.15, "reliability": 0.15, "cost": 0.1},
            "quality":  {"speed": 0.1, "quality": 0.6,  "reliability": 0.2,  "cost": 0.1},
            "cost":     {"speed": 0.1, "quality": 0.2,  "reliability": 0.1,  "cost": 0.6},
        }
        weights = weight_map.get(strategy, weight_map["balanced"])
        
        candidates = []
        for model, profile in self.perf["models"].items():
            if profile.get("tier") == "dead":
                continue
            if tier == "any" or profile.get("tier") == tier:
                s = self.score(model, weights)
                if s > 0:
                    candidates.append((model, s, profile))
        
        candidates.sort(key=lambda x: -x[1])
        return candidates[:count]
    
    def record(self, model, task_type, elapsed, success, tokens_out=0, error_msg=""):
        """记录一次调用的表现"""
        with self.lock:
            entry = {
                "time": datetime.now().isoformat(),
                "model": model,
                "task": task_type,
                "elapsed": round(elapsed, 1),
                "success": success,
                "tokens_out": tokens_out,
                "error": error_msg[:100] if error_msg else ""
            }
            self.perf["history"].append(entry)
            
            # 只保留最近500条
            if len(self.perf["history"]) > 500:
                self.perf["history"] = self.perf["history"][-500:]
            
            # 动态调整评分
            profile = self.perf["models"].get(model)
            if profile and profile.get("tier") != "dead":
                self._update_score(model, profile, entry)
            
            self._save()
    
    def _update_score(self, model, profile, entry):
        """基于实际调用调整评分"""
        # 速度调整：如果实际耗时远超预期，降速
        tier_avg_speed = {"ultra": 35, "heavy": 65, "reason": 50, "fast": 80}
        avg = tier_avg_speed.get(profile.get("tier", "fast"), 70)
        
        # 简单的指数移动平均
        if entry["success"]:
            actual_speed = max(0, 100 - entry["elapsed"])  # elapsed越小speed越高
            profile["speed"] = round(profile["speed"] * 0.8 + actual_speed * 0.2)
            profile["reliability"] = min(100, profile["reliability"] + 0.5)
        else:
            profile["reliability"] = max(0, profile["reliability"] - 2)
            if "timeout" in entry.get("error", "").lower():
                profile["speed"] = max(0, profile["speed"] - 3)
    
    def auto_retire(self, threshold=40):
        """自动淘汰：综合分低于阈值的模型"""
        retired_now = []
        for model, profile in list(self.perf["models"].items()):
            if profile.get("tier") == "dead":
                continue
            s = self.score(model)
            if s < threshold:
                profile["tier"] = "dead"
                self.perf["retired"].append({
                    "model": model,
                    "score": round(s, 1),
                    "retired_at": datetime.now().isoformat(),
                    "reason": f"综合分{s:.0f}低于阈值{threshold}"
                })
                retired_now.append(model)
        if retired_now:
            self._save()
        return retired_now
    
    def auto_promote(self):
        """自动升级：同tier里表现突出的模型提升tier"""
        promoted = []
        tier_order = {"fast": 0, "reason": 1, "heavy": 2, "ultra": 3}
        tier_names = {0: "fast", 1: "reason", 2: "heavy", 3: "ultra"}
        
        for model, profile in self.perf["models"].items():
            if profile.get("tier") == "dead":
                continue
            current_tier = profile.get("tier", "fast")
            current_rank = tier_order.get(current_tier, 0)
            s = self.score(model)
            
            # 如果综合分>85，且当前tier不是最高，考虑升级
            if s > 85 and current_rank < 3:
                # 看看在上一级tier里排第几
                next_tier = tier_names.get(current_rank + 1, "ultra")
                competitors = [m for m, p in self.perf["models"].items() 
                              if p.get("tier") == next_tier and p.get("tier") != "dead"]
                if competitors:
                    competitor_scores = [self.score(m) for m in competitors]
                    avg_score = sum(competitor_scores) / len(competitor_scores) if competitor_scores else 0
                    if s > avg_score * 0.9:  # 接近上一级平均水平就升级
                        profile["tier"] = next_tier
                        promoted.append(f"{model} → {next_tier}(分{s:.0f})")
        
        if promoted:
            self._save()
        return promoted
    
    def report(self):
        """输出当前模型军团状态报告"""
        lines = ["=" * 50, "🏭 模型军团状态报告", "=" * 50]
        
        for tier in ["ultra", "heavy", "reason", "fast", "dead"]:
            models = [(m, p) for m, p in self.perf["models"].items() if p.get("tier") == tier]
            if not models:
                continue
            emoji = {"ultra": "👑", "heavy": "💪", "reason": "🧠", "fast": "⚡", "dead": "💀"}
            lines.append(f"\n{emoji.get(tier, '?')} {tier.upper()}级:")
            for model, profile in sorted(models, key=lambda x: -self.score(x[0])):
                s = self.score(model)
                lines.append(f"  {s:5.1f} | {model}")
                lines.append(f"        spd={profile['speed']} qual={profile['quality']} rel={profile['reliability']} cost={profile['cost']}")
        
        # Recent history stats
        recent = self.perf["history"][-50:] if self.perf["history"] else []
        if recent:
            success_rate = sum(1 for h in recent if h["success"]) / len(recent) * 100
            avg_time = sum(h["elapsed"] for h in recent if h["success"]) / max(1, sum(1 for h in recent if h["success"]))
            lines.append(f"\n📊 最近{len(recent)}次: 成功率{success_rate:.0f}% | 平均耗时{avg_time:.1f}s")
        
        return "\n".join(lines)

if __name__ == "__main__":
    router = ModelRouter()
    print(router.report())
    print("\n--- 快速级Top3 (速度优先) ---")
    for m, s, p in router.select("fast", "speed"):
        print(f"  {s:.1f} {m}")
    print("\n--- 重活级Top3 (质量优先) ---")
    for m, s, p in router.select("heavy", "quality"):
        print(f"  {s:.1f} {m}")
