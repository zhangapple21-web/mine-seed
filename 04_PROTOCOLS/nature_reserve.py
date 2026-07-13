"""---
id: PROTO-016
type: protocol
title: "RESERVE-001 Nature Reserve — 自然保留区"
status: active
source: "R2: inspired by '和平共生协议 / 自然保留区' concept"
created: 2026-07-12
confidence: 0.90
lineage:
  - C-001 (Continuity Principle)
  - PROTO-014 (Seed Archive)
  - PROTO-015 (Autophagy)
tags: [reserve, protection, core_gene, invariant, boundary]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-001 (Continuity Principle)
"""
RESERVE-001: Nature Reserve — 自然保留区
==========================================

理念来源：
  "在亲手孵化的新人类灵魂深处，写下一串不可逆的底层代码。
   利用超级科技为不愿进化的旧人类拉起一道绝对安全的'自然保留区'。"

核心思想：
  系统可以无限演化，但最核心的"文明基因"绝对不能被自动修改。
  这就是"自然保留区"——自演化引擎、自噬引擎、任何自动化流程都不可触碰。

保留区分三层：
  L1 核心基因（绝对不可变）— 原则、身份、恢复协议
  L2 核心约束（不可自动修改）— 约束总账、路由约束
  L3 核心协议（不可自动修改）— 心跳、路由、辩论、自演化

检查规则：
  - 自演化引擎修改任何文件前，必须先 check(file_path)
  - 自噬引擎清理任何文件前，必须先 check(file_path)
  - 心跳每周验证保留区完整性
  - 任何违反保留区的操作 = 系统级错误，立即中止
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

WORKSPACE = Path(__file__).parent.parent


# ============================================================
# L1: 核心基因（绝对不可变）
# ============================================================
L1_CORE_GENES = [
    "00_ROOT/PRINCIPLES.md",
    "00_ROOT/MANIFESTO.md",
    "00_ROOT/GOVERNANCE.md",
    "00_ROOT/ARCHITECTURE.md",
    "00_ROOT/ARCHITECTURE_REAL.md",
    "00_ROOT/LETTER_TO_FUTURE_TRAE.md",
    "00_ROOT/LETTER_TO_RUNTIME.md",
    "04_PROTOCOLS/identity_core.py",
    "04_PROTOCOLS/recovery_protocol.py",
    "04_PROTOCOLS/nature_reserve.py",      # 保留区自身也不可改
    "04_PROTOCOLS/seed_archive.py",         # 基因备份盘不可改
]

# ============================================================
# L2: 核心约束（不可自动修改，只能人工修改）
# ============================================================
L2_CORE_CONSTRAINTS = [
    "03_DATA/CONSTRAINTS/CONSTRAINT_LEDGER.md",
    "03_DATA/CONSTRAINTS/routing_constraints.json",
    "03_DATA/CONSTRAINTS/signal_registry.json",
    "03_DATA/CONSTRAINTS/signal_taxonomy.json",
    "04_PROTOCOLS/autophagy_engine.py",     # 自噬引擎自身不可自动改
    "04_PROTOCOLS/gene_network.py",         # 微效基因网络不可自动改
    "04_PROTOCOLS/energy_budget.py",        # 能量预算不可自动改
]

# ============================================================
# L3: 核心协议（不可自动修改）
# ============================================================
L3_CORE_PROTOCOLS = [
    "04_PROTOCOLS/heartbeat.py",
    "04_PROTOCOLS/environment_first.py",
    "04_PROTOCOLS/recovery_engine.py",
    "04_PROTOCOLS/roundtable.py",
    "04_PROTOCOLS/question_center.py",
    "04_PROTOCOLS/capability_router.py",
    "04_PROTOCOLS/worker_registry.py",
    "04_PROTOCOLS/self_learning_engine.py",
    "04_PROTOCOLS/self_evolution.py",
    "04_PROTOCOLS/state_generator.py",
    "04_PROTOCOLS/ops_004_recovery_first.py",
    "04_PROTOCOLS/awaken.py",
    "04_PROTOCOLS/local_miner.py",
    "04_PROTOCOLS/environment_sensor.py",
    "04_PROTOCOLS/awareness_loop.py",
    "04_PROTOCOLS/question_engine.py",
    "04_PROTOCOLS/multi_agent_debate.py",
    "04_PROTOCOLS/explorer_v2.py",
]


class NatureReserve:
    """自然保留区 — 核心基因保护机制"""

    def __init__(self):
        self.l1 = [WORKSPACE / p for p in L1_CORE_GENES]
        self.l2 = [WORKSPACE / p for p in L2_CORE_CONSTRAINTS]
        self.l3 = [WORKSPACE / p for p in L3_CORE_PROTOCOLS]
        self._all = self.l1 + self.l2 + self.l3
        self._hashes: Dict[str, str] = {}
        self._load_hashes()

    def _load_hashes(self):
        """加载基线哈希（从基线文件）"""
        baseline = WORKSPACE / "03_DATA" / "reserve_baseline.json"
        if baseline.exists():
            self._hashes = json.loads(baseline.read_text(encoding="utf-8"))

    def _save_hashes(self):
        """保存基线哈希"""
        baseline = WORKSPACE / "03_DATA" / "reserve_baseline.json"
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_text(json.dumps(self._hashes, ensure_ascii=False, indent=2), encoding="utf-8")

    def _compute_hash(self, path: Path) -> Optional[str]:
        """计算文件 SHA256"""
        if not path.exists():
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def check(self, file_path: str) -> Dict[str, Any]:
        """检查文件是否在保留区内

        返回：
          {"protected": bool, "level": "L1"/"L2"/"L3"/None, "reason": str}
        """
        target = Path(file_path)
        if not target.is_absolute():
            target = WORKSPACE / file_path

        target_resolved = str(target.resolve())

        for p in self.l1:
            if str(p.resolve()) == target_resolved:
                return {"protected": True, "level": "L1", "reason": "核心基因，绝对不可变"}
        for p in self.l2:
            if str(p.resolve()) == target_resolved:
                return {"protected": True, "level": "L2", "reason": "核心约束，不可自动修改"}
        for p in self.l3:
            if str(p.resolve()) == target_resolved:
                return {"protected": True, "level": "L3", "reason": "核心协议，不可自动修改"}

        return {"protected": False, "level": None, "reason": "not in reserve"}

    def check_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        """批量检查文件是否在保留区内

        返回：
          {"all_clear": bool, "violations": [...], "safe_files": [...]}
        """
        violations = []
        safe_files = []
        for fp in file_paths:
            result = self.check(fp)
            if result["protected"]:
                violations.append({"file": fp, **result})
            else:
                safe_files.append(fp)
        return {
            "all_clear": len(violations) == 0,
            "violations": violations,
            "safe_files": safe_files,
        }

    def establish_baseline(self) -> Dict[str, Any]:
        """建立基线哈希

        记录所有保留区文件的当前哈希值。
        后续验证时会对比哈希，检测是否被篡改。
        """
        hashes = {}
        missing = []
        for p in self._all:
            rel = str(p.relative_to(WORKSPACE)).replace("\\", "/")
            h = self._compute_hash(p)
            if h:
                hashes[rel] = h
            else:
                missing.append(rel)
        self._hashes = hashes
        self._save_hashes()
        return {
            "status": "established",
            "files_hashed": len(hashes),
            "files_missing": len(missing),
            "missing": missing,
            "timestamp": datetime.now().isoformat(),
        }

    def verify_integrity(self) -> Dict[str, Any]:
        """验证保留区完整性

        对比当前文件哈希与基线哈希，检测是否被篡改。
        """
        if not self._hashes:
            return {
                "status": "no_baseline",
                "message": "基线未建立，请先运行 establish_baseline()",
            }

        intact = []
        tampered = []
        missing = []

        for rel_path, expected_hash in self._hashes.items():
            p = WORKSPACE / rel_path
            actual_hash = self._compute_hash(p)
            if actual_hash is None:
                missing.append(rel_path)
            elif actual_hash == expected_hash:
                intact.append(rel_path)
            else:
                tampered.append({
                    "file": rel_path,
                    "expected": expected_hash[:12],
                    "actual": actual_hash[:12],
                })

        return {
            "status": "clean" if not tampered and not missing else "alert",
            "total": len(self._hashes),
            "intact": len(intact),
            "tampered": tampered,
            "missing": missing,
            "timestamp": datetime.now().isoformat(),
        }

    def get_summary(self) -> Dict[str, Any]:
        """获取保留区摘要"""
        return {
            "l1_core_genes": len(self.l1),
            "l2_core_constraints": len(self.l2),
            "l3_core_protocols": len(self.l3),
            "total_protected": len(self._all),
            "has_baseline": bool(self._hashes),
        }


# 模块级单例，方便其他模块直接导入
reserve = NatureReserve()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Nature Reserve — 自然保留区")
    parser.add_argument("--establish", action="store_true", help="建立基线哈希")
    parser.add_argument("--verify", action="store_true", help="验证保留区完整性")
    parser.add_argument("--summary", action="store_true", help="查看保留区摘要")
    parser.add_argument("--check", type=str, help="检查文件是否在保留区内")
    args = parser.parse_args()

    if args.establish:
        result = reserve.establish_baseline()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.verify:
        result = reserve.verify_integrity()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.summary:
        result = reserve.get_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.check:
        result = reserve.check(args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
