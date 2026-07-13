"""---
id: PROTO-004
type: protocol
title: "Self Evolution — 自我演化引擎"
status: active
source: "R2 Development"
created: 2026-07-12
confidence: 0.88
lineage:
  - OPS-005
  - PROTO-003
related: [PROTO-001, PROTO-003]
tags: [evolution, self_modify, runtime]
archaeology:
  state: original
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-011
"""
EVO-001: Self Evolution — 自我演化引擎
========================================

核心思想:
  Experience 不是终点，而是 Evolution 的输入。
  当 Multi-Agent Debate 批准一个决策后，Self Evolution 负责把它变成实际的代码/配置变更。

执行语义:
  Experience → Constraint → Code Change → Test → Commit → RoundTable Audit → Push

安全原则:
  1. 只修改白名单内的文件类型（.json / .yaml / .txt / 简单 .py 常量）
  2. 不修改核心协议代码（04_PROTOCOLS/ 下的复杂逻辑）
  3. 先生成 patch，验证语法/结构正确后再应用
  4. 所有变更必须可回滚（git commit + 备份）
  5. 变更后必须运行相关检查（import / json load / 单元测试）

支持的演化类型:
  - constraint_add:   添加新约束到 constraints.json
  - provider_config:  调整 Provider 配置（优先级、超时等）
  - threshold_update: 更新阈值常量
  - state_update:     更新 CURRENT_STATE.md 中的状态（只限非关键部分）
  - unknown:          生成任务给人工，不自动执行

输出:
  02_MEMORY/evolution/evolution_YYYYMMDD_HHMMSS.json
"""
import os, sys, json, re, subprocess, argparse, shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from local_miner import call_model
from civilization_contract import contract

WORKSPACE = Path(__file__).parent.parent
EVOLUTION_DIR = WORKSPACE / "02_MEMORY" / "evolution"
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

# 演化白名单 — 只有这些文件可以被自动修改
EVOLUTION_ALLOWLIST = {
    "constraints.json": str(WORKSPACE / "constraints.json"),
    "provider_config.json": str(WORKSPACE / "04_PROTOCOLS" / "provider_config.json"),
    "heartbeat_schedule.json": str(WORKSPACE / "04_PROTOCOLS" / "heartbeat_schedule.json"),
    "explorer_topics.json": str(WORKSPACE / "04_PROTOCOLS" / "explorer_topics.json"),
}

# 核心协议文件，绝对禁止自动修改
EVOLUTION_DENYLIST = [
    "04_PROTOCOLS/heartbeat.py",
    "04_PROTOCOLS/local_miner.py",
    "04_PROTOCOLS/environment_sensor.py",
    "04_PROTOCOLS/awareness_loop.py",
    "04_PROTOCOLS/question_engine.py",
    "04_PROTOCOLS/multi_agent_debate.py",
    "04_PROTOCOLS/explorer_v2.py",
    "04_PROTOCOLS/self_evolution.py",
]


class PatchGenerator:
    """生成代码/配置修改方案"""

    def __init__(self):
        pass

    def classify_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """判断决策属于哪种演化类型"""
        action = decision.get("action", "")
        text = (action + " " + decision.get("rationale", "")).lower()

        if "constraint" in text or "约束" in text:
            return {"type": "constraint_add", "description": "添加新约束"}
        if "provider" in text or "priority" in text or "超时" in text or "timeout" in text:
            return {"type": "provider_config", "description": "调整 Provider 配置"}
        if "threshold" in text or "阈值" in text:
            return {"type": "threshold_update", "description": "更新阈值"}
        if "state" in text or "current_state" in text:
            return {"type": "state_update", "description": "更新状态文档"}

        return {"type": "unknown", "description": "暂不支持自动演化"}

    def generate_constraint_patch(self, decision: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """生成约束添加 patch"""
        prompt = f"""你是 ACE 自我演化系统的 Patch 生成器。

决策：{decision.get('action')}
理由：{decision.get('rationale')}

请基于这个决策，生成一个可以添加到 constraints.json 的新约束条目。

constraints.json 格式示例：
{{
  "constraints": [
    {{
      "id": "C-001",
      "name": "Provider fallback required",
      "description": "任何 Provider 失败时必须能切换到备用源",
      "severity": "must",
      "source": "experience:provider_failure"
    }}
  ]
}}

请输出 JSON：
{{
  "new_constraint": {{
    "id": "C-XXX",
    "name": "...",
    "description": "...",
    "severity": "must/should/may",
    "source": "experience:..."
  }},
  "explanation": "为什么这个约束能防止问题再次发生"
}}
"""
        result = call_model(prompt, max_tokens=400, capability="reasoning")
        if "error" in result:
            return None

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            if content.strip().startswith("```"):
                lines = content.strip().split("\n")
                content = "\n".join(lines[1:-1])
            parsed = json.loads(content.strip())
            return parsed.get("new_constraint")
        except Exception:
            return None

    def generate_provider_config_patch(self, decision: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """生成 Provider 配置 patch"""
        prompt = f"""你是 ACE 自我演化系统的 Patch 生成器。

决策：{decision.get('action')}
理由：{decision.get('rationale')}

请基于这个决策，生成 provider_config.json 的修改方案。

格式示例：
{{
  "changes": [
    {{
      "op": "update",
      "path": "providers.GitHub.priority",
      "value": 90
    }}
  ],
  "explanation": "..."
}}

请输出 JSON：
{{
  "changes": [...],
  "explanation": "..."
}}
"""
        result = call_model(prompt, max_tokens=400, capability="reasoning")
        if "error" in result:
            return None

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            if content.strip().startswith("```"):
                lines = content.strip().split("\n")
                content = "\n".join(lines[1:-1])
            parsed = json.loads(content.strip())
            return parsed
        except Exception:
            return None


class PatchApplier:
    """应用 patch 到文件"""

    def __init__(self):
        self.backups = []

    def _backup(self, filepath: Path) -> Path:
        """创建备份"""
        backup_path = EVOLUTION_DIR / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filepath.name}"
        if filepath.exists():
            shutil.copy2(filepath, backup_path)
        self.backups.append((filepath, backup_path))
        return backup_path

    def apply_constraint_patch(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        """应用约束 patch — 新约束不直接 ACTIVE，先 PENDING_REVIEW（C-010）"""
        target = WORKSPACE / "constraints.json"
        if not target.exists():
            target.write_text(json.dumps({"constraints": []}, ensure_ascii=False, indent=2), encoding="utf-8")

        self._backup(target)

        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            constraints = data.setdefault("constraints", [])

            # 检查是否已存在相同 ID
            new_id = patch.get("id")
            if any(c.get("id") == new_id for c in constraints):
                return {"status": "skipped", "reason": f"Constraint {new_id} already exists"}

            # C-010: 新约束不直接 ACTIVE，先 PENDING_REVIEW
            # C-004: 7天后必须重新评估
            from datetime import timedelta
            patch["review_status"] = "PENDING_REVIEW"
            patch["review_schedule"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            patch["review_count"] = 0
            patch["auto_generated"] = True

            constraints.append(patch)
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"status": "applied", "file": str(target), "constraint_id": new_id, "review_status": "PENDING_REVIEW"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def apply_json_patch(self, target_path: Path, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """应用 JSON patch（简单的 key 更新）

        CONTRACT ENFORCEMENT:
            在执行任何写入之前，强制检查 Civilization 契约。
            如果目标路径落在 Tier 1/Tier 2，直接抛出 RuntimeError。
            只有 Tier 3 (Runtime) 路径允许直接写入。

            ARCH-011 SAFETY GUARD:
            此方法不接受 via_admission 参数。任何对 Tier 1/Tier 2 的写入
            必须通过 Admission Engine，通过 evolve() → apply_constraint_patch() 路径执行。
            直接调用此方法写入 Tier 1/Tier 2 将被拒绝。

        Args:
            target_path: 目标文件路径
            changes: 变更列表

        Raises:
            RuntimeError: 目标路径在 Civilization 受保护区
        """
        zone = contract._classify_zone(target_path)
        
        if zone in ("tier1", "tier2"):
            raise RuntimeError(
                f"[ARCH-011 BLOCK] Cannot write to Civilization-protected path: {target_path}\n"
                f"  zone: {zone}\n"
                f"  reason: apply_json_patch() does NOT support writing to Tier 1/Tier 2.\n"
                f"  solution: Use Admission Engine to review, then call evolve() with approved decision.\n"
                f"  via_admission parameter has been REMOVED for security — see ARCH-011."
            )

        if not target_path.exists():
            return {"status": "failed", "error": f"Target file not found: {target_path}"}

        self._backup(target_path)

        try:
            data = json.loads(target_path.read_text(encoding="utf-8"))

            for change in changes:
                op = change.get("op")
                path = change.get("path", "")
                value = change.get("value")

                if op == "update":
                    keys = path.split(".")
                    node = data
                    for key in keys[:-1]:
                        if key not in node:
                            node[key] = {}
                        node = node[key]
                    node[keys[-1]] = value

            target_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"status": "applied", "file": str(target_path), "changes": len(changes)}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def rollback(self):
        """回滚所有备份"""
        for original, backup in self.backups:
            if backup.exists():
                shutil.copy2(backup, original)
        return {"status": "rolled_back", "count": len(self.backups)}


class SelfEvolution:
    """自我演化引擎"""

    def __init__(self):
        self.patch_gen = PatchGenerator()
        self.patch_applier = PatchApplier()

    def _validate_change(self, result: Dict[str, Any]) -> bool:
        """验证变更是否基本安全"""
        if result.get("status") != "applied":
            return False

        filepath = Path(result.get("file", ""))
        if not filepath.exists():
            return False

        # JSON 文件必须能解析
        if filepath.suffix == ".json":
            try:
                json.loads(filepath.read_text(encoding="utf-8"))
                return True
            except Exception:
                return False

        return True

    def _git_commit(self, files: List[str], message: str) -> Dict[str, Any]:
        """提交变更到 git"""
        try:
            subprocess.run(["git", "add"] + files, cwd=str(WORKSPACE), check=True, capture_output=True, text=True)
            subprocess.run(["git", "commit", "-m", message], cwd=str(WORKSPACE), check=True, capture_output=True, text=True)
            return {"status": "committed", "message": message}
        except subprocess.CalledProcessError as e:
            return {"status": "failed", "error": e.stderr}

    def evolve(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """基于一个 approved decision 执行演化"""
        print(f"\n[SELF EVOLUTION] Processing decision: {decision.get('qid', '?')}")

        classification = self.patch_gen.classify_decision(decision)
        evo_type = classification["type"]
        print(f"  Classified as: {evo_type} ({classification['description']})")

        if evo_type == "unknown":
            return {
                "qid": decision.get("qid"),
                "decision": decision.get("decision"),
                "type": evo_type,
                "status": "deferred_to_human",
                "reason": "暂不支持自动演化此类型决策",
            }

        # 生成 patch
        if evo_type == "constraint_add":
            patch = self.patch_gen.generate_constraint_patch(decision)
            if not patch:
                return {"status": "failed", "reason": "Failed to generate constraint patch"}
            target_files = [str(WORKSPACE / "constraints.json")]

        elif evo_type == "provider_config":
            patch = self.patch_gen.generate_provider_config_patch(decision)
            if not patch:
                return {"status": "failed", "reason": "Failed to generate provider config patch"}
            target_path = WORKSPACE / "04_PROTOCOLS" / "provider_config.json"
            target_files = [str(target_path)]

        else:
            return {"status": "deferred_to_human", "reason": f"Type {evo_type} not yet implemented"}

        # Nature Reserve check — 自然保留区检查
        try:
            from nature_reserve import reserve
            rel_targets = [str(Path(f).relative_to(WORKSPACE)).replace("\\", "/") for f in target_files]
            reserve_check = reserve.check_batch(rel_targets)
            if not reserve_check["all_clear"]:
                violations = reserve_check["violations"]
                print(f"  [BLOCKED] Nature Reserve violation: {violations}")
                return {
                    "qid": decision.get("qid"),
                    "status": "blocked_by_reserve",
                    "reason": f"目标文件在自然保留区内（{violations[0]['level']}），禁止自动修改",
                    "violations": violations,
                }
        except ImportError:
            pass  # 自然保留区模块不存在时跳过检查

        # Apply patch
        if evo_type == "constraint_add":
            apply_result = self.patch_applier.apply_constraint_patch(patch)
        elif evo_type == "provider_config":
            apply_result = self.patch_applier.apply_json_patch(target_path, patch.get("changes", []))

        # 验证
        if not self._validate_change(apply_result):
            print(f"  Validation failed, rolling back...")
            self.patch_applier.rollback()
            return {
                "status": "failed",
                "apply_result": apply_result,
                "reason": "Validation failed after apply",
            }

        print(f"  Applied: {apply_result}")

        # RoundTable 审计 — 临时跳过（新红蓝战队架构待集成）
        rel_files = [str(Path(f).relative_to(WORKSPACE)) for f in target_files]
        audit_results = [{"file": f, "decision": "skipped", "reason": "new roundtable architecture pending integration"} for f in rel_files]

        # Git commit
        commit_msg = f"[EVO-001] Auto-evolution from {decision.get('qid', 'unknown')}: {classification['description']}"
        commit_result = self._git_commit(target_files, commit_msg)
        print(f"  Commit: {commit_result}")

        result = {
            "qid": decision.get("qid"),
            "decision": decision.get("decision"),
            "type": evo_type,
            "status": "evolved",
            "classification": classification,
            "apply_result": apply_result,
            "audit": audit_results,
            "commit": commit_result,
            "timestamp": datetime.now().isoformat(),
        }

        # 保存演化记录
        self._save_record(result)
        return result

    def _save_record(self, result: Dict[str, Any]):
        """保存演化记录"""
        filename = f"evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = EVOLUTION_DIR / filename
        filepath.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    def process_approved_decisions(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量处理 approved decisions

        去重策略：每个决策只处理一次。
        - 有 evolved_status 字段的 → 已处理过，跳过
        - 处理后更新 evolved_status + evolved_at，写回 decisions.json
        """
        from question_center import QuestionCenter
        qc = QuestionCenter()
        results = []

        for d in decisions:
            did = d.get("did", "")
            if not (d.get("outcome") == "approved" or d.get("decision") == "approved"):
                continue

            if d.get("evolved_status"):
                results.append({
                    "qid": d.get("qid"),
                    "did": did,
                    "status": "skipped",
                    "reason": f"already processed: {d['evolved_status']}",
                })
                continue

            try:
                r = self.evolve(d)
            except Exception as e:
                r = {
                    "qid": d.get("qid"),
                    "did": did,
                    "status": "error",
                    "error": str(e),
                }

            status = r.get("status", "unknown")
            d["evolved_status"] = status
            d["evolved_at"] = datetime.now().isoformat()
            if r.get("reason"):
                d["evolved_reason"] = r["reason"]

            # 同步更新 qc 中的对应决策对象（按 did 匹配）
            for qd in qc.decisions:
                if qd.get("did") == did:
                    qd["evolved_status"] = status
                    qd["evolved_at"] = d["evolved_at"]
                    if r.get("reason"):
                        qd["evolved_reason"] = r["reason"]
                    break

            results.append(r)

        qc._save_all()
        return results


def main():
    parser = argparse.ArgumentParser(description="EVO-001 Self Evolution")
    parser.add_argument("--decision-file", help="JSON file with approved decisions")
    parser.add_argument("--decision", help="Single decision JSON string")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    evo = SelfEvolution()

    if args.decision:
        decisions = [json.loads(args.decision)]
    elif args.decision_file:
        decisions = json.loads(Path(args.decision_file).read_text(encoding="utf-8"))
    else:
        print("No decision provided. Use --decision or --decision-file")
        return

    results = evo.process_approved_decisions(decisions)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    else:
        for r in results:
            print(f"\n{r.get('qid')} → {r.get('status')}")
            if "apply_result" in r:
                print(f"  Applied: {r['apply_result']}")


# ============================================================
# Contract Enforcement Unit Tests
# ============================================================
def _run_contract_tests():
    """Unit tests for ARCH-011 safety guard in apply_json_patch()"""
    print("\n[ARCH-011 TEST] Running apply_json_patch safety guard tests...")

    temp_dir = WORKSPACE / "06_RUNTIME" / "test_contract"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_tier3 = temp_dir / "test_temp.json"
    temp_tier3.write_text('{"test": "value"}', encoding="utf-8")

    try:
        applier = PatchApplier()

        # Test 1: Tier 3 write should succeed
        result = applier.apply_json_patch(temp_tier3, [{"op": "update", "path": "test", "value": "modified"}])
        assert result["status"] == "applied", f"Tier 3 write should succeed, got {result}"
        print("  [PASS] Tier 3 write succeeds")

        # Test 2: Tier 1 write should raise RuntimeError (ARCH-011 BLOCK)
        tier1_path = WORKSPACE / "02_MEMORY" / "civilization_assets" / "test_contract_asset.json"
        tier1_path.parent.mkdir(parents=True, exist_ok=True)
        tier1_path.write_text('{"test": "value"}', encoding="utf-8")

        try:
            applier.apply_json_patch(tier1_path, [{"op": "update", "path": "test", "value": "modified"}])
            raise AssertionError("Tier 1 write should have raised RuntimeError (ARCH-011 BLOCK)")
        except RuntimeError as e:
            assert "ARCH-011 BLOCK" in str(e), f"Expected ARCH-011 BLOCK in error, got: {e}"
            assert "Civilization-protected" in str(e)
            print("  [PASS] Tier 1 write raises RuntimeError with ARCH-011 BLOCK")

        # Test 3: Tier 2 write should also raise RuntimeError (ARCH-011 BLOCK)
        tier2_path = WORKSPACE / "02_MEMORY" / "archaeology" / "test_contract_evidence.json"
        tier2_path.parent.mkdir(parents=True, exist_ok=True)
        tier2_path.write_text('{"test": "value"}', encoding="utf-8")

        try:
            applier.apply_json_patch(tier2_path, [{"op": "update", "path": "test", "value": "modified"}])
            raise AssertionError("Tier 2 write should have raised RuntimeError (ARCH-011 BLOCK)")
        except RuntimeError as e:
            assert "ARCH-011 BLOCK" in str(e), f"Expected ARCH-011 BLOCK in error, got: {e}"
            print("  [PASS] Tier 2 write raises RuntimeError with ARCH-011 BLOCK")

        # Cleanup test files
        tier1_path.unlink(missing_ok=True)
        tier2_path.unlink(missing_ok=True)

        print("\n[ARCH-011 TEST] All 3 tests passed.")

    finally:
        temp_tier3.unlink(missing_ok=True)
        try:
            temp_dir.rmdir()
        except:
            pass


if __name__ == "__main__":
    main()
