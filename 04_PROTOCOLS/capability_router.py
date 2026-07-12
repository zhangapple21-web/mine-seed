"""Capability Router — 能力路由引擎

根据 Civilization Graph 实现：
  Question → Capability → Worker

核心逻辑：
  1. 读取 civilization_graph.json
  2. 根据问题/任务提取所需能力
  3. 在 Worker Registry 中查找匹配的 Worker
  4. 返回最佳路由路径

路由策略：
  - 精确匹配：Worker 的 capabilities 包含所有所需能力
  - 能力覆盖度：匹配越多能力的 Worker 优先级越高
  - 成本优先：低成本 Worker 优先
  - 状态过滤：只考虑 running 状态的 Worker
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

WORKSPACE = Path(__file__).parent.parent
GRAPH_PATH = WORKSPACE / "02_MEMORY" / "civilization_graph.json"

CAPABILITY_KEYWORDS = {
    "research": ["研究", "探索", "调查", "分析", "搜索", "发现", "考古"],
    "reasoning": ["推理", "逻辑", "判断", "辩论", "决策", "思考"],
    "coding": ["代码", "编写", "修改", "实现", "编程", "开发"],
    "debate": ["辩论", "讨论", "争议", "决策", "评估"],
    "summarize": ["总结", "概括", "报告", "摘要", "提炼"],
    "monitoring": ["监控", "检测", "健康", "状态", "心跳"],
    "observation": ["观察", "感知", "扫描", "检测", "环境"],
    "planning": ["规划", "计划", "设计", "方案"],
    "execution": ["执行", "运行", "实施"],
    "memory_management": ["记忆", "存储", "归档", "保存"],
    "audit": ["审计", "审查", "检查", "验证"],
    "notification": ["通知", "推送", "消息", "提醒"],
    "recovery": ["恢复", "备份", "修复", "抢救"],
    "exploration": ["探索", "发现", "未知", "新领域"],
    "discovery": ["发现", "识别", "探测"],
    "abduction": ["假设", "推测", "猜想"],
    "knowledge_management": ["知识", "管理", "组织", "检索"],
    "adaptation": ["适应", "演化", "进化", "调整"],
    "review": ["审查", "评估", "检查"],
    "health_check": ["健康", "检查", "状态"],
    "sensing": ["感知", "检测"],
    "code_analysis": ["代码", "分析", "挖掘"],
    "capability_graph": ["能力", "图谱", "关系"],
    "graph_building": ["图谱", "构建", "图"],
    "state_reporting": ["状态", "报告", "展示"],
    "dashboard": ["仪表", "面板", "展示"],
    "messaging": ["消息", "通信", "发送"],
    "experience_extraction": ["经验", "提取", "学习"],
    "learning": ["学习", "经验", "沉淀"],
    "preservation": ["保存", "保护", "留存"],
    "scheduling": ["调度", "定时", "计划"],
    "question_generation": ["问题", "生成", "提问"],
}


class CapabilityRouter:
    def __init__(self):
        self.graph = {}
        self.workers = {}
        self.capabilities = {}
        self._load_graph()

    def _load_graph(self):
        if GRAPH_PATH.exists():
            try:
                self.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
                self._index_workers()
                self._index_capabilities()
            except Exception as e:
                print(f"CapabilityRouter: failed to load graph: {e}")

    def _index_workers(self):
        self.workers = {}
        for node in self.graph.get("nodes", []):
            if node.get("type") == "worker":
                self.workers[node["id"]] = node

    def _index_capabilities(self):
        self.capabilities = {}
        for node in self.graph.get("nodes", []):
            if node.get("type") == "capability":
                self.capabilities[node["id"]] = node

    def extract_capabilities(self, text: str) -> List[str]:
        """从文本中提取所需能力"""
        required = []
        text_lower = text.lower()
        for cap, keywords in CAPABILITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower or kw.lower() in text_lower:
                    required.append(cap)
                    break
        return list(set(required))

    def find_workers(self, capabilities: List[str]) -> List[Dict[str, Any]]:
        """根据所需能力查找匹配的 Worker"""
        results = []
        cap_ids = [f"CAP:{c}" for c in capabilities]

        for wid, worker in self.workers.items():
            props = worker.get("properties", {})
            if props.get("status") != "running":
                continue

            worker_caps = props.get("capabilities", [])
            worker_cap_ids = [f"CAP:{c}" for c in worker_caps]

            matched = [c for c in cap_ids if c in worker_cap_ids]
            coverage = len(matched) / len(cap_ids) if cap_ids else 0

            if coverage == 0:
                continue

            results.append({
                "worker_id": wid,
                "worker_name": worker.get("label", ""),
                "matched_capabilities": [c.replace("CAP:", "") for c in matched],
                "coverage": coverage,
                "cost": props.get("cost", "high"),
                "priority": props.get("priority", 99),
                "status": props.get("status", "unknown"),
            })

        results.sort(key=lambda x: (
            -x["coverage"],
            x["priority"],
            {"low": 0, "medium": 1, "high": 2}[x["cost"]],
        ))

        return results

    def route(self, question: str, qid: str = "") -> Dict[str, Any]:
        """完整路由：Question → Capability → Worker"""
        required_caps = self.extract_capabilities(question)
        workers = self.find_workers(required_caps)

        best = workers[0] if workers else None

        return {
            "qid": qid,
            "question": question[:80],
            "required_capabilities": required_caps,
            "matched_workers": workers[:5],
            "best_worker": best,
            "routing_strategy": "coverage_priority",
        }

    def get_worker_info(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """获取 Worker 详细信息"""
        return self.workers.get(worker_id)

    def get_capability_info(self, cap_id: str) -> Optional[Dict[str, Any]]:
        """获取能力详细信息"""
        if not cap_id.startswith("CAP:"):
            cap_id = f"CAP:{cap_id}"
        return self.capabilities.get(cap_id)

    def list_all_workers(self) -> List[Dict[str, Any]]:
        """列出所有注册的 Worker"""
        result = []
        for wid, worker in self.workers.items():
            props = worker.get("properties", {})
            result.append({
                "id": wid,
                "name": worker.get("label", ""),
                "capabilities": props.get("capabilities", []),
                "status": props.get("status", "unknown"),
                "cost": props.get("cost", "medium"),
                "priority": props.get("priority", 5),
            })
        return sorted(result, key=lambda x: x["priority"])

    def list_all_capabilities(self) -> List[Dict[str, Any]]:
        """列出所有能力"""
        result = []
        for cid, cap in self.capabilities.items():
            result.append({
                "id": cid,
                "name": cap.get("label", ""),
                "desc": cap.get("properties", {}).get("desc", ""),
                "requires": cap.get("properties", {}).get("requires", []),
            })
        return sorted(result, key=lambda x: x["name"])


if __name__ == "__main__":
    router = CapabilityRouter()

    print("=== Registered Workers ===")
    for w in router.list_all_workers():
        caps = ", ".join(w["capabilities"])
        print(f"  {w['name']:20s} status={w['status']:6s} cost={w['cost']:6s} priority={w['priority']}")
        print(f"      capabilities: {caps}")

    print()
    print("=== Route Tests ===")

    test_cases = [
        "为什么 Provider 失败？需要调查原因",
        "需要探索新的代码架构",
        "检查系统健康状态",
        "生成今天的文明报告",
        "自动修改代码实现新功能",
    ]

    for tc in test_cases:
        route = router.route(tc)
        best = route["best_worker"]
        caps = ", ".join(route["required_capabilities"])
        if best:
            print(f"Q: {tc[:30]}...")
            print(f"   需要能力: {caps}")
            print(f"   最佳 Worker: {best['worker_name']} (coverage={best['coverage']:.0%})")
        else:
            print(f"Q: {tc[:30]}...")
            print(f"   需要能力: {caps}")
            print(f"   无匹配 Worker")
        print()