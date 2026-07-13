"""---
id: PROTO-024
type: protocol
title: "CSP-001: Capability → Service → Provider 三级能力架构"
status: active
source: "R1-continuity-backup: capability_registry_v2.md（接续自疯子）"
created: 2026-07-13
confidence: 0.95
lineage:
  - L∞ 本源层
  - DFP-001 (Drawer First Protocol)
  - 05_TOOLS/router/registry.py
tags: [csp, capability, service, provider, router, registry, architecture]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
"""
CSP-001: Capability → Service → Provider 三级能力架构
======================================================

**核心理念**：
  Runtime 需要稳定的能力抽象，但 Provider 每天都在变。
  三级结构让 Runtime 不知道 Provider 替换。

**三级结构**：
  Capability（二十年不变）— 抽象能力（Reason/Retrieve/Generate/...）
      ↓
  Service（可替换）— 具体服务（Image.Generate/LLM.Chat/...）
      ↓
  Provider（随时替换）— 实现者（OpenAI/Anthropic/本地 Ollama/...）

**价值**：
  - Capability 不动（Generate 永远是 Generate）
  - Service 接口不动（Image.Generate 的输入输出格式不变）
  - Provider 随便换（Runtime 不知道）

**类比**：
  Capability = 需要电
  Service = 220V 交流
  Provider = 国家电网 / 发电机 / 太阳能电池

**Provider 替换规则**：
  Provider 替换不修改：
    - Capability 定义
    - Service 接口
    - Runtime 调用代码
  Provider 替换只修改：
    - Registry 中的 provider 配置
    - Routing 规则
    - Credential 映射
"""
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "03_DATA" / "PROVIDER_REGISTRY"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 8 个永久 Capability（参考 capability_registry_v2.md）
# ============================================================
PERMANENT_CAPABILITIES = [
    {"id": "reason",    "name": "Reason",    "desc": "推理、判断、决策支持",        "stability": "permanent"},
    {"id": "retrieve",  "name": "Retrieve",  "desc": "检索、查询、搜索",            "stability": "permanent"},
    {"id": "generate",  "name": "Generate",  "desc": "生成内容（文本/图像/代码）",  "stability": "permanent"},
    {"id": "transform", "name": "Transform", "desc": "转换格式（翻译/重构/压缩）",   "stability": "permanent"},
    {"id": "observe",   "name": "Observe",   "desc": "观察、监控、感知",            "stability": "permanent"},
    {"id": "execute",   "name": "Execute",   "desc": "执行操作、调用工具",          "stability": "permanent"},
    {"id": "persist",   "name": "Persist",   "desc": "持久化、存储、归档",          "stability": "permanent"},
    {"id": "notify",    "name": "Notify",    "desc": "通知、提醒、广播",            "stability": "permanent"},
]


@dataclass
class Capability:
    """Capability 层 — 抽象能力（永久）"""
    id: str
    name: str
    desc: str
    stability: str = "permanent"


@dataclass
class Service:
    """Service 层 — 具体服务接口（可替换）"""
    id: str
    name: str
    parent_capability: str
    desc: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Provider:
    """Provider 层 — 实现者（随时替换）"""
    id: str
    name: str
    supported_services: List[str]
    status: str = "active"
    cost_tier: str = "free"  # free / low / medium / premium
    priority: int = 100
    credential_ref: str = ""  # 引用 coze-assets 中的凭证
    health: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingRule:
    """路由规则"""
    service: str
    priority: List[Dict[str, Any]]  # [{provider: "bfl", condition: "cost_optimized"}, ...]


class CSPRegistry:
    """Capability → Service → Provider Registry"""

    def __init__(self):
        self.capabilities: Dict[str, Capability] = {}
        self.services: Dict[str, Service] = {}
        self.providers: Dict[str, Provider] = {}
        self.routing_rules: List[RoutingRule] = []
        self._load_defaults()
        self._load_state()

    def _load_defaults(self):
        """加载默认 8 个 Capability"""
        for cap in PERMANENT_CAPABILITIES:
            self.capabilities[cap["id"]] = Capability(**cap)

    def _state_path(self) -> Path:
        return DATA_DIR / "csp_registry.json"

    def _load_state(self):
        """从文件恢复状态"""
        if not self._state_path().exists():
            return
        try:
            data = json.loads(self._state_path().read_text(encoding="utf-8"))
            for s in data.get("services", []):
                self.services[s["id"]] = Service(**s)
            for p in data.get("providers", []):
                self.providers[p["id"]] = Provider(**p)
            for r in data.get("routing_rules", []):
                self.routing_rules.append(RoutingRule(**r))
        except Exception:
            pass

    def save(self):
        """保存到文件"""
        data = {
            "version": "1.0.0",
            "capabilities": [asdict(c) for c in self.capabilities.values()],
            "services": [asdict(s) for s in self.services.values()],
            "providers": [asdict(p) for p in self.providers.values()],
            "routing_rules": [asdict(r) for r in self.routing_rules],
        }
        self._state_path().write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # --------------------------------------------------
    # Capability
    # --------------------------------------------------
    def list_capabilities(self) -> List[Capability]:
        return list(self.capabilities.values())

    def get_capability(self, cap_id: str) -> Optional[Capability]:
        return self.capabilities.get(cap_id)

    # --------------------------------------------------
    # Service
    # --------------------------------------------------
    def add_service(self, service: Service) -> bool:
        if service.id in self.services:
            return False
        if service.parent_capability not in self.capabilities:
            return False
        self.services[service.id] = service
        return True

    def list_services(self, cap_id: Optional[str] = None) -> List[Service]:
        results = list(self.services.values())
        if cap_id:
            results = [s for s in results if s.parent_capability == cap_id]
        return results

    # --------------------------------------------------
    # Provider
    # --------------------------------------------------
    def add_provider(self, provider: Provider) -> bool:
        if provider.id in self.providers:
            return False
        # 验证 supported_services
        for svc_id in provider.supported_services:
            if svc_id not in self.services:
                return False
        self.providers[provider.id] = provider
        return True

    def list_providers(self, service_id: Optional[str] = None,
                       status: str = "active") -> List[Provider]:
        results = [p for p in self.providers.values() if p.status == status]
        if service_id:
            results = [p for p in results if service_id in p.supported_services]
        return results

    def remove_provider(self, provider_id: str) -> bool:
        """移除 Provider（DFP: 验证可移除）"""
        if provider_id not in self.providers:
            return False
        # 检查是否有 routing rule 依赖
        for rule in self.routing_rules:
            for entry in rule.priority:
                if entry.get("provider") == provider_id:
                    return False  # 有依赖，不能直接移除
        del self.providers[provider_id]
        return True

    # --------------------------------------------------
    # Routing
    # --------------------------------------------------
    def add_routing_rule(self, rule: RoutingRule):
        self.routing_rules.append(rule)

    def route(self, service_id: str, condition: str = "default") -> Optional[Provider]:
        """按 service + condition 路由到 Provider"""
        for rule in self.routing_rules:
            if rule.service == service_id:
                # 找到匹配条件的 provider
                for entry in rule.priority:
                    if entry.get("condition") == condition or condition == "default":
                        provider_id = entry.get("provider")
                        if provider_id and provider_id in self.providers:
                            provider = self.providers[provider_id]
                            if provider.status == "active":
                                return provider
        return None

    def find_providers(self, service_id: str) -> List[Provider]:
        """找所有支持该 service 的活跃 Provider"""
        return sorted(
            self.list_providers(service_id=service_id),
            key=lambda p: p.priority
        )

    # --------------------------------------------------
    # Stats
    # --------------------------------------------------
    def stats(self) -> Dict[str, Any]:
        return {
            "capabilities": len(self.capabilities),
            "services": len(self.services),
            "providers": len(self.providers),
            "active_providers": len([p for p in self.providers.values() if p.status == "active"]),
            "routing_rules": len(self.routing_rules),
        }


# ============================================================
# 模块级单例
# ============================================================
registry = CSPRegistry()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CSP-001: Capability/Service/Provider Registry")
    parser.add_argument("--stats", action="store_true", help="显示统计")
    parser.add_argument("--list-capabilities", action="store_true", help="列出所有 Capability")
    parser.add_argument("--list-services", action="store_true", help="列出所有 Service")
    parser.add_argument("--list-providers", action="store_true", help="列出所有 Provider")
    parser.add_argument("--route", type=str, help="路由 service:condition")
    args = parser.parse_args()

    if args.stats:
        import json
        print(json.dumps(registry.stats(), ensure_ascii=False, indent=2))
    elif args.list_capabilities:
        for c in registry.list_capabilities():
            print(f"  {c.id:10s} | {c.name:12s} | {c.desc}")
    elif args.list_services:
        for s in registry.list_services():
            print(f"  {s.id:25s} | {s.parent_capability:10s} | {s.name}")
    elif args.list_providers:
        for p in registry.list_providers():
            print(f"  {p.id:20s} | {p.cost_tier:8s} | priority={p.priority} | services={p.supported_services}")
    elif args.route:
        parts = args.route.split(":")
        service = parts[0]
        condition = parts[1] if len(parts) > 1 else "default"
        provider = registry.route(service, condition)
        if provider:
            print(f"  Service: {service}")
            print(f"  Condition: {condition}")
            print(f"  → Provider: {provider.name} (id={provider.id})")
        else:
            print(f"  No provider found for {service} (condition={condition})")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
