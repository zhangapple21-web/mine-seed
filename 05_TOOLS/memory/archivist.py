#!/usr/bin/env python3
"""
档案官 (Archivist) - 矿场每日知识报告生成器
Daily Knowledge Report Generator for Mine Operations
"""

import json
import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 配置路径
BASE_DIR = Path(os.environ.get("BASE_DIR", "/home/coze"))
MINE_OUTPUT = BASE_DIR / os.environ.get("MINE_OUTPUT_DIR", "mine_output")
OBSERVATION_LOG = MINE_OUTPUT / "observation_log.json"
EXPERIENCE_FILE = MINE_OUTPUT / "experience.json"
SUMMARY_FILE = MINE_OUTPUT / "summary.json"
SIGNALS_DIR = MINE_OUTPUT / "signals"
KNOWLEDGE_DIR = MINE_OUTPUT / "knowledge"

class Archivist:
    """档案官 - 矿场知识报告生成器"""
    
    def __init__(self):
        self.today = date.today()
        self.report_date = self.today.strftime("%Y-%m-%d")
        self.json_output = KNOWLEDGE_DIR / f"daily_report_{self.today.strftime('%Y%m%d')}.json"
        self.md_output = KNOWLEDGE_DIR / f"daily_report_{self.today.strftime('%Y%m%d')}.md"
        
        # 数据容器
        self.observations = []
        self.experience = {}
        self.summary = {}
        self.signals = []
        
    def log(self, msg: str):
        """日志输出"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [Archivist] {msg}")
    
    def load_data(self) -> bool:
        """加载所有数据源"""
        self.log("开始加载数据源...")
        
        try:
            # 1. 加载观察日志
            if OBSERVATION_LOG.exists():
                with open(OBSERVATION_LOG, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.observations = data.get('observations', [])
                self.log(f"加载观察日志: {len(self.observations)} 条记录")
            else:
                self.log(f"警告: 观察日志不存在 {OBSERVATION_LOG}")
                self.observations = []
            
            # 2. 加载经验数据
            if EXPERIENCE_FILE.exists():
                with open(EXPERIENCE_FILE, 'r', encoding='utf-8') as f:
                    self.experience = json.load(f)
                self.log("加载经验数据成功")
            else:
                self.log(f"警告: 经验文件不存在 {EXPERIENCE_FILE}")
                self.experience = {}
            
            # 3. 加载summary
            if SUMMARY_FILE.exists():
                with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
                    self.summary = json.load(f)
                self.log("加载summary成功")
            else:
                self.log(f"警告: summary不存在 {SUMMARY_FILE}")
                self.summary = {}
            
            # 4. 加载信号
            self._load_signals()
            
            return True
            
        except Exception as e:
            self.log(f"加载数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_signals(self):
        """加载信号文件"""
        self.signals = []
        if not SIGNALS_DIR.exists():
            self.log(f"警告: 信号目录不存在 {SIGNALS_DIR}")
            return
        
        # 查找今天的信号文件
        today_prefix = self.today.strftime("%Y%m%d")
        
        for signal_file in SIGNALS_DIR.glob("signal_*.json"):
            try:
                with open(signal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 检查是否是今天的信号
                if data.get('timestamp', '').startswith(today_prefix):
                    self.signals.append(data)
                elif signal_file.stat().st_mtime > (datetime.now().timestamp() - 86400):
                    # 也包含最近24小时内修改的
                    self.signals.append(data)
                    
            except Exception as e:
                self.log(f"加载信号文件失败 {signal_file}: {e}")
        
        self.log(f"加载信号文件: {len(self.signals)} 个")
    
    def analyze_observations(self) -> Dict[str, Any]:
        """分析观察日志 - 今日发现层"""
        result = {
            "total_observations": len(self.observations),
            "success_count": 0,
            "failure_count": 0,
            "success_rate": 0.0,
            "active_workers": set(),
            "corps_stats": defaultdict(lambda: {"total": 0, "success": 0}),
            "task_stats": defaultdict(lambda: {"total": 0, "success": 0, "avg_time": []}),
            "avg_response_time": 0,
        }
        
        if not self.observations:
            return result
        
        response_times = []
        
        for obs in self.observations:
            worker = obs.get('worker_id', 'unknown')
            corps = obs.get('corps', 'Unknown')
            task = obs.get('task', 'unknown')
            success = obs.get('success', False)
            elapsed = obs.get('elapsed', 0)
            
            result["active_workers"].add(worker)
            result["corps_stats"][corps]["total"] += 1
            result["task_stats"][task]["total"] += 1
            
            if success:
                result["success_count"] += 1
                result["corps_stats"][corps]["success"] += 1
                result["task_stats"][task]["success"] += 1
                if elapsed > 0:
                    result["task_stats"][task]["avg_time"].append(elapsed)
            else:
                result["failure_count"] += 1
        
        # 计算成功率
        total = result["success_count"] + result["failure_count"]
        if total > 0:
            result["success_rate"] = round(result["success_count"] / total * 100, 1)
        
        # 计算平均响应时间
        for task in result["task_stats"]:
            times = result["task_stats"][task]["avg_time"]
            if times:
                result["task_stats"][task]["avg_response_time"] = round(sum(times) / len(times), 1)
            del result["task_stats"][task]["avg_time"]  # 清理临时数据
        
        result["active_workers"] = list(result["active_workers"])
        
        # 计算军团利用率
        corps_utilization = {}
        for corps, stats in result["corps_stats"].items():
            corps_utilization[corps] = stats["success"] / max(stats["total"], 1) * 100
        
        result["corps_utilization"] = dict(corps_utilization)
        
        # 计算矿场健康度
        result["mine_health"] = result["success_rate"]
        
        return result
    
    def analyze_experience(self) -> Dict[str, Any]:
        """分析经验数据 - 今日经验层"""
        result = {
            "patterns": {},
            "routing_rules": [],
            "failure_patterns": [],
            "compression_log": [],
        }
        
        # Patterns分析
        patterns = self.experience.get("patterns", {})
        for task, pattern in patterns.items():
            best_workers = pattern.get("best_workers", [])
            top_worker = best_workers[0] if best_workers else {}
            
            result["patterns"][task] = {
                "best_worker": top_worker.get("worker", "N/A"),
                "best_efficiency": top_worker.get("efficiency", 0),
                "total_observations": pattern.get("total_observations", 0),
                "all_workers": [
                    {
                        "worker": w.get("worker"),
                        "efficiency": w.get("efficiency"),
                        "success_rate": w.get("success_rate"),
                        "avg_time": w.get("avg_time")
                    }
                    for w in best_workers
                ]
            }
        
        # 路由规则
        result["routing_rules"] = self.experience.get("routing_rules", [])
        
        # 失败模式
        result["failure_patterns"] = self.experience.get("failure_patterns", [])
        
        # 压缩日志
        result["compression_log"] = self.experience.get("compression_log", [])
        
        # 工人效率排名
        all_workers = []
        for task, pattern in patterns.items():
            for worker in pattern.get("best_workers", []):
                all_workers.append({
                    "task": task,
                    "worker": worker.get("worker"),
                    "efficiency": worker.get("efficiency", 0),
                    "success_rate": worker.get("success_rate", 0),
                    "avg_time": worker.get("avg_time", 0),
                    "samples": worker.get("samples", 0)
                })
        
        # 按效率排序
        result["worker_efficiency_ranking"] = sorted(
            all_workers, 
            key=lambda x: x.get("efficiency", 0), 
            reverse=True
        )[:10]  # TOP10
        
        return result
    
    def analyze_signals(self) -> Dict[str, Any]:
        """分析信号 - 信号产出"""
        result = {
            "total_signals": len(self.signals),
            "accepted": [],
            "iterating": [],
            "rejected": [],
            "signal_names": [],
        }
        
        for sig in self.signals:
            status = sig.get("status", "UNKNOWN").upper()
            signal_name = sig.get("signal_name", sig.get("selected_signal", "N/A"))
            metrics = sig.get("metrics", {})
            
            sig_info = {
                "name": signal_name,
                "timestamp": sig.get("timestamp", "N/A"),
                "ic": metrics.get("mean_ic", 0),
                "p_value": metrics.get("p_value", 1),
                "iteration": sig.get("iteration", 1),
                "status": sig.get("status", "UNKNOWN")
            }
            
            result["signal_names"].append(signal_name)
            
            if "ACCEPTED" in status:
                result["accepted"].append(sig_info)
            elif "ITERATING" in status or "ITERATION" in status:
                result["iterating"].append(sig_info)
            else:
                result["rejected"].append(sig_info)
        
        return result
    
    def generate_decisions(self, obs_analysis: Dict, exp_analysis: Dict, sig_analysis: Dict) -> List[Dict]:
        """生成决策建议"""
        decisions = []
        
        # 1. 效率>70%的任务→保持当前分配
        for task, pattern in exp_analysis.get("patterns", {}).items():
            if pattern["best_efficiency"] > 70:
                decisions.append({
                    "type": "KEEP",
                    "priority": "LOW",
                    "task": task,
                    "message": f"任务 {task} 效率 {pattern['best_efficiency']}% > 70%，建议保持当前工人分配",
                    "action": "维持现状"
                })
        
        # 2. 效率<50%的任务→考虑换工人
        for task, pattern in exp_analysis.get("patterns", {}).items():
            if pattern["best_efficiency"] < 50:
                decisions.append({
                    "type": "CHANGE",
                    "priority": "HIGH",
                    "task": task,
                    "message": f"任务 {task} 效率 {pattern['best_efficiency']}% < 50%，建议评估并更换工人",
                    "action": "评估替换方案"
                })
        
        # 3. 失败模式→避免特定组合
        for failure in exp_analysis.get("failure_patterns", []):
            task = failure.get("task", "unknown")
            worker = failure.get("worker", "unknown")
            count = failure.get("failure_count", 0)
            rec = failure.get("recommendation", "")
            
            decisions.append({
                "type": "AVOID",
                "priority": "HIGH",
                "task": task,
                "worker": worker,
                "message": f"发现 {count} 次失败: {rec}",
                "action": "避免该组合"
            })
        
        # 4. 新ACCEPTED信号→建议纳入因子库
        for sig in sig_analysis.get("accepted", []):
            decisions.append({
                "type": "ADD_FACTOR",
                "priority": "MEDIUM",
                "signal": sig["name"],
                "message": f"信号 {sig['name']} 已ACCEPTED (IC={sig['ic']:.4f})，建议纳入因子库",
                "action": "加入因子库"
            })
        
        # 5. 军团利用率<10%→考虑分配更多任务
        corps_utils = obs_analysis.get("corps_utilization", {})
        for corps, util in corps_utils.items():
            if util < 10 and obs_analysis.get("corps_stats", {}).get(corps, {}).get("total", 0) > 0:
                decisions.append({
                    "type": "INCREASE_LOAD",
                    "priority": "MEDIUM",
                    "corps": corps,
                    "message": f"军团 {corps} 利用率 {util:.1f}% < 10%，建议分配更多任务",
                    "action": "增加任务分配"
                })
        
        # 6. 健康度<80%→排查失败任务
        health = obs_analysis.get("mine_health", 100)
        if health < 80:
            decisions.append({
                "type": "INVESTIGATE",
                "priority": "HIGH",
                "message": f"矿场健康度 {health}% < 80%，建议排查失败任务原因",
                "action": "排查失败"
            })
        
        # 7. 健康度≥95%→运行稳定
        if health >= 95:
            decisions.append({
                "type": "STABLE",
                "priority": "INFO",
                "message": f"矿场健康度 {health}% ≥ 95%，运行稳定",
                "action": "无需干预"
            })
        
        return decisions
    
    def generate_report(self) -> Dict[str, Any]:
        """生成完整报告"""
        self.log("开始生成报告...")
        
        # 分析各层数据
        obs_analysis = self.analyze_observations()
        exp_analysis = self.analyze_experience()
        sig_analysis = self.analyze_signals()
        
        # 生成决策
        decisions = self.generate_decisions(obs_analysis, exp_analysis, sig_analysis)
        
        # 组装报告
        report = {
            "report_date": self.report_date,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            
            # 今日发现 (Observation层)
            "observation": {
                "mine_health": obs_analysis.get("mine_health", 0),
                "success_failure": f"{obs_analysis['success_count']}/{obs_analysis['failure_count']}",
                "success_count": obs_analysis["success_count"],
                "failure_count": obs_analysis["failure_count"],
                "total_observations": obs_analysis["total_observations"],
                "active_workers": obs_analysis["active_workers"],
                "corps_utilization": obs_analysis.get("corps_utilization", {}),
                "task_stats": dict(obs_analysis["task_stats"]),
            },
            
            # 今日经验 (Experience层)
            "experience": {
                "patterns": exp_analysis["patterns"],
                "worker_efficiency_top5": exp_analysis["worker_efficiency_ranking"][:5],
                "failure_patterns": exp_analysis["failure_patterns"],
                "routing_rules_count": len(exp_analysis["routing_rules"]),
                "compression_runs": len(exp_analysis["compression_log"]),
            },
            
            # 信号产出
            "signals": {
                "total": sig_analysis["total_signals"],
                "accepted": sig_analysis["accepted"],
                "iterating": sig_analysis["iterating"],
                "rejected": sig_analysis["rejected"],
            },
            
            # 今日决策 (Knowledge层)
            "decisions": decisions,
            
            # 摘要
            "summary": {
                "high_priority_actions": [d for d in decisions if d.get("priority") == "HIGH"],
                "medium_priority_actions": [d for d in decisions if d.get("priority") == "MEDIUM"],
                "low_priority_actions": [d for d in decisions if d.get("priority") == "LOW"],
                "info_actions": [d for d in decisions if d.get("priority") == "INFO"],
            }
        }
        
        return report
    
    def report_to_markdown(self, report: Dict) -> str:
        """生成Markdown格式报告"""
        md = []
        md.append(f"# 📋 Daily Knowledge Report — {report['report_date']}")
        md.append("")
        
        # 今日发现
        md.append("## 🔍 今日发现")
        obs = report["observation"]
        md.append(f"- **矿场健康度**: {obs['mine_health']}%")
        md.append(f"- **成功/失败**: {obs['success_failure']}")
        md.append(f"- **活跃工人**: {len(obs['active_workers'])} ({', '.join(obs['active_workers'][:5])})")
        md.append(f"- **ACCEPTED信号**: {len(report['signals']['accepted'])}")
        
        corps_utils = obs.get('corps_utilization', {})
        corps_str = " ".join([f"{corps}={util:.0f}%" for corps, util in corps_utils.items()])
        md.append(f"- **军团利用**: {corps_str}")
        md.append("")
        
        # 任务详情
        if obs.get('task_stats'):
            md.append("### 任务统计")
            md.append("| 任务 | 成功 | 总数 | 成功率 | 平均耗时(s) |")
            md.append("|------|------|------|--------|------------|")
            for task, stats in obs['task_stats'].items():
                total = stats['total']
                success = stats['success']
                rate = success / max(total, 1) * 100
                avg_time = stats.get('avg_response_time', 0)
                md.append(f"| {task} | {success} | {total} | {rate:.0f}% | {avg_time:.1f} |")
            md.append("")
        
        # 信号详情
        if report['signals']['accepted']:
            md.append("### ✅ ACCEPTED 信号详情")
            for sig in report['signals']['accepted']:
                md.append(f"- **{sig['name']}** (IC={sig['ic']:.4f}, p={sig['p_value']:.3f}, iter={sig['iteration']})")
            md.append("")
        
        # 今日经验
        md.append("## 🧠 今日经验")
        
        # 什么管用
        md.append("### ✅ 什么管用")
        for task, pattern in report['experience']['patterns'].items():
            if pattern['best_efficiency'] >= 60:
                md.append(f"- **{task}**: {pattern['best_worker']} (效率 {pattern['best_efficiency']}%)")
        md.append("")
        
        # 什么失败
        md.append("### ❌ 什么失败")
        failures = report['experience']['failure_patterns']
        if failures:
            for f in failures:
                md.append(f"- **{f['task']}** + {f['worker']}: {f['failure_count']}次失败 → {f['recommendation']}")
        else:
            md.append("- 今日无明显失败模式")
        md.append("")
        
        # 工人效率TOP5
        md.append("### 🏆 工人效率 TOP5")
        md.append("| 排名 | 工人 | 任务 | 效率 | 成功率 | 平均耗时 |")
        md.append("|------|------|------|------|--------|---------|")
        for i, w in enumerate(report['experience']['worker_efficiency_top5'][:5], 1):
            md.append(f"| {i} | {w['worker']} | {w['task']} | {w['efficiency']}% | {w['success_rate']*100:.0f}% | {w['avg_time']:.1f}s |")
        md.append("")
        
        # 今日决策
        md.append("## 🎯 今日决策")
        
        # 高优先级
        high = report['summary']['high_priority_actions']
        if high:
            md.append("### 🔴 高优先级")
            for d in high:
                md.append(f"- **{d['message']}** → {d['action']}")
            md.append("")
        
        # 中优先级
        medium = report['summary']['medium_priority_actions']
        if medium:
            md.append("### 🟡 中优先级")
            for d in medium:
                md.append(f"- **{d['message']}** → {d['action']}")
            md.append("")
        
        # 低优先级
        low = report['summary']['low_priority_actions']
        if low:
            md.append("### 🟢 低优先级")
            for d in low:
                md.append(f"- {d['message']}")
            md.append("")
        
        # 信息
        info = report['summary']['info_actions']
        if info:
            md.append("### ℹ️ 信息")
            for d in info:
                md.append(f"- {d['message']}")
            md.append("")
        
        # === 交接班摘要（连续性压缩器）===
        # 不是流水账，是"明天的我来上班，需要知道什么"
        md.append("")
        md.append("## 🔄 交接班摘要")
        md.append("> 今天的100件事，压缩成明天的3件")
        md.append("")
        
        # 1. 最重要的事（高优先级决策 + 新约束）
        critical = report['summary'].get('high_priority_actions', [])
        if critical:
            md.append("**明天必须知道的：**")
            for d in critical[:3]:  # 最多3条
                md.append(f"  1. {d['message']} → {d['action']}")
            md.append("")
        
        # 2. 新增约束/毒组合（从experience同步）
        try:
            import json as _j
            with open(os.environ.get("ROUTING_CONSTRAINTS_FILE", "/home/coze/routing_constraints.json")) as _f:
                rc = _j.load(_f)
            recent = [r for r in rc.get('rules', []) 
                     if r.get('review_status') == 'ACTIVE' and '2026-06-18' in str(r.get('confirmed_ts', '')) or '2026-06-19' in str(r.get('confirmed_ts', ''))]
            if recent:
                md.append("**新增约束：**")
                for r in recent[:3]:
                    action = r.get('action', '?')
                    task = r.get('task', '?')
                    worker = r.get('worker', '?')
                    md.append(f"  - {action}: {worker} + {task}")
                md.append("")
        except:
            pass
        
        # 3. 健康趋势（对比昨天）
        obs = report.get('observation', {})
        health = obs.get('mine_health', 0)
        if health > 0:
            status = "🟢 正常" if health >= 80 else ("🟡 关注" if health >= 60 else "🔴 异常")
            md.append(f"**矿场状态：** {status} ({health}%)")
        
        md.append("")
        md.append("---")
        md.append(f"*报告生成时间: {report['generated_at']}*")
        
        return "\n".join(md)
    
    def save_reports(self, report: Dict, md_content: str) -> bool:
        """保存报告"""
        try:
            # 确保目录存在
            KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
            
            # 保存JSON
            with open(self.json_output, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.log(f"JSON报告已保存: {self.json_output}")
            
            # 保存Markdown
            with open(self.md_output, 'w', encoding='utf-8') as f:
                f.write(md_content)
            self.log(f"Markdown报告已保存: {self.md_output}")
            
            return True
            
        except Exception as e:
            self.log(f"保存报告失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """执行主流程"""
        self.log("档案官启动...")
        
        # 加载数据
        if not self.load_data():
            self.log("数据加载失败，退出")
            return False
        
        # 生成报告
        report = self.generate_report()
        md_content = self.report_to_markdown(report)
        
        # 保存报告
        if not self.save_reports(report, md_content):
            self.log("报告保存失败，退出")
            return False
        
        # 打印摘要
        self.log("=" * 50)
        self.log("📊 报告摘要")
        self.log(f"  日期: {report['report_date']}")
        self.log(f"  矿场健康度: {report['observation']['mine_health']}%")
        self.log(f"  成功/失败: {report['observation']['success_failure']}")
        self.log(f"  ACCEPTED信号: {len(report['signals']['accepted'])}")
        self.log(f"  高优先级决策: {len(report['summary']['high_priority_actions'])}")
        self.log("=" * 50)
        self.log("✅ 档案官任务完成")
        
        return True


def main():
    """主入口"""
    archivist = Archivist()
    success = archivist.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
