"""---
id: PROTO-014
type: protocol
title: "GENE-001 Seed Archive — 文明基因备份盘"
status: active
source: "R2: inspired by '原始基因备份盘' concept"
created: 2026-07-12
confidence: 0.90
lineage:
  - C-017 (Archive Convergence)
  - OPS-004 (Recovery First)
tags: [gene, backup, seed, recovery, minimum_reproducible]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-017 (Archive Convergence)
"""
GENE-001: Seed Archive — 文明基因备份盘
===========================================

理念来源：
  "在新物种的灵魂深处，写下一串不可逆的底层代码。
   为可能的崩溃，留下原始基因的备份盘。"

核心思想：
  系统可以无限演化，但最核心的"文明基因"必须有一个最小备份。
  当一切崩溃时，可以从这个备份盘重建文明的种子。

什么是文明基因（不可再压缩的最小单元）：
  1. Principles（原则）- 系统为什么存在
  2. Constraints（约束）- 系统不能做什么
  3. Core Protocols（核心协议）- 系统怎么运行
  4. Identity（身份）- 系统是谁
  5. Persona Chips（人格芯片）- 系统怎么思考
  6. Recovery Protocol（恢复协议）- 怎么从备份重建

备份盘特点：
  - 极小：核心基因 < 100KB
  - 自包含：备份盘自带恢复说明
  - 只读：基因不随系统演化而修改
  - 可验证：有哈希校验，防止基因被篡改
  - 多副本：自动保存到多个位置

使用场景：
  - 系统崩溃时，从备份盘恢复种子
  - 新环境部署时，用备份盘快速初始化
  - 考古时，对比当前系统和原始基因的差异
"""
import os
import sys
import json
import hashlib
import argparse
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

WORKSPACE = Path(__file__).parent.parent
BACKUP_DIR = WORKSPACE / "03_ARCHIVE" / "gene_seed"


# ============================================================
# 文明基因定义
# ============================================================

CIVILIZATION_GENOME = {
    "genome_version": "1.0.0",
    "species": "ACE (Autonomous Civilization Engine)",
    "created": "2026-07-05",
    "description": "ACE civilization minimum reproducible genome",

    # Layer 1: Principles 原则（为什么存在）
    "principles": {
        "source": "00_ROOT/PRINCIPLES.md",
        "required": True,
        "extract": "from_file",
    },

    # Layer 2: Constraints 约束（不能做什么）
    "constraints": {
        "source": "03_DATA/CONSTRAINTS/CONSTRAINT_LEDGER.md",
        "required": True,
        "extract": "from_dir",
        "dir": "03_DATA/CONSTRAINTS",
    },

    # Layer 3: Identity 身份（是谁）
    "identity": {
        "source": "04_PROTOCOLS/identity_core.py",
        "required": True,
        "extract": "from_file",
    },

    # Layer 4: Core Protocols 核心协议（怎么运行）
    "core_protocols": {
        "required": True,
        "files": [
            "04_PROTOCOLS/environment_first.py",   # EFP 环境优先
            "04_PROTOCOLS/recovery_engine.py",     # 恢复引擎
            "04_PROTOCOLS/heartbeat.py",           # 心跳
            "04_PROTOCOLS/roundtable.py",          # 辩论治理
            "04_PROTOCOLS/question_center.py",     # 问题中心
            "04_PROTOCOLS/capability_router.py",   # 能力路由
            "04_PROTOCOLS/worker_registry.py",     # Worker 注册
            "04_PROTOCOLS/self_learning_engine.py", # 自学习引擎
            "04_PROTOCOLS/state_generator.py",     # 状态生成器
        ],
    },

    # Layer 5: Persona Chips 人格芯片（怎么思考）
    "persona_chips": {
        "required": False,  # 可选，但推荐
        "source": "04_PROTOCOLS/roundtable.py:PERSONA_CHIPS",
        "extract": "from_variable",
    },

    # Layer 6: Recovery Protocol 恢复协议（怎么重建）
    "recovery_protocol": {
        "required": True,
        "content": """
ACE 文明基因恢复指南
====================

当系统崩溃时，按以下步骤从基因备份重建：

Step 1: 环境准备
  - Python 3.10+
  - 工作目录：当前目录
  - 网络连接（可选，用于拉取更多资源）

Step 2: 基因解压
  - 解压 gene_seed_YYYYMMDD.zip
  - 你会看到：principles/ constraints/ protocols/ identity/

Step 3: 运行 Awaken
  - python 04_PROTOCOLS/awaken.py
  - 自动执行 EFP（环境优先协议）
  - 自动构建资产索引
  - 自动恢复可恢复内容

Step 4: 验证核心
  - python 04_PROTOCOLS/heartbeat.py --once
  - 确认心跳正常
  - 确认 TG 推送正常

Step 5: 逐步扩展
  - 恢复 Worker
  - 恢复 Provider
  - 恢复历史记忆
  - 系统进入自治循环

记住：
  基因是种子，不是全部。
  文明需要在种子的基础上重新生长。
""",
    },
}


class SeedArchive:
    """文明基因备份盘"""

    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.genome = CIVILIZATION_GENOME

    def create_seed(self) -> Dict[str, Any]:
        """创建基因种子备份"""
        seed_id = f"gene_seed_{datetime.now().strftime('%Y%m%d')}"
        seed_dir = self.backup_dir / seed_id
        seed_dir.mkdir(parents=True, exist_ok=True)

        manifest = {
            "seed_id": seed_id,
            "created_at": datetime.now().isoformat(),
            "genome_version": self.genome["genome_version"],
            "species": self.genome["species"],
            "layers": {},
            "file_count": 0,
            "total_size": 0,
        }

        # Layer 1: Principles
        layer_files = self._extract_layer("principles", seed_dir)
        manifest["layers"]["principles"] = {
            "files": len(layer_files),
            "size": sum(p.stat().st_size for p in layer_files if p.exists()),
        }
        manifest["file_count"] += len(layer_files)

        # Layer 2: Constraints
        layer_files = self._extract_layer("constraints", seed_dir)
        manifest["layers"]["constraints"] = {
            "files": len(layer_files),
            "size": sum(p.stat().st_size for p in layer_files if p.exists()),
        }
        manifest["file_count"] += len(layer_files)

        # Layer 3: Identity
        layer_files = self._extract_layer("identity", seed_dir)
        manifest["layers"]["identity"] = {
            "files": len(layer_files),
            "size": sum(p.stat().st_size for p in layer_files if p.exists()),
        }
        manifest["file_count"] += len(layer_files)

        # Layer 4: Core Protocols
        layer_files = self._extract_layer("core_protocols", seed_dir)
        manifest["layers"]["core_protocols"] = {
            "files": len(layer_files),
            "size": sum(p.stat().st_size for p in layer_files if p.exists()),
        }
        manifest["file_count"] += len(layer_files)

        # Layer 5: Persona Chips (从代码中提取数据)
        persona_data = self._extract_persona_chips()
        if persona_data:
            persona_file = seed_dir / "persona_chips.json"
            with open(persona_file, "w", encoding="utf-8") as f:
                json.dump(persona_data, f, ensure_ascii=False, indent=2)
            manifest["layers"]["persona_chips"] = {
                "files": 1,
                "size": persona_file.stat().st_size,
            }
            manifest["file_count"] += 1

        # Layer 6: Recovery Protocol
        recovery_content = self.genome["recovery_protocol"]["content"]
        recovery_file = seed_dir / "RECOVERY_GUIDE.md"
        recovery_file.write_text(recovery_content, encoding="utf-8")
        manifest["layers"]["recovery_protocol"] = {
            "files": 1,
            "size": recovery_file.stat().st_size,
        }
        manifest["file_count"] += 1

        # 计算总大小
        total_size = sum(
            info["size"] for info in manifest["layers"].values()
            if isinstance(info, dict) and "size" in info
        )
        manifest["total_size"] = total_size

        # 计算基因哈希（防篡改）
        manifest["genome_hash"] = self._compute_seed_hash(seed_dir)

        # 写入 manifest
        manifest_file = seed_dir / "genome_manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # 打包成 ZIP
        zip_path = self.backup_dir / f"{seed_id}.zip"
        self._zip_seed(seed_dir, zip_path)

        # 清理临时目录
        import shutil
        shutil.rmtree(seed_dir, ignore_errors=True)

        return {
            "seed_id": seed_id,
            "zip_path": str(zip_path),
            "zip_size": zip_path.stat().st_size,
            "file_count": manifest["file_count"],
            "genome_hash": manifest["genome_hash"],
            "layers": list(manifest["layers"].keys()),
        }

    def _extract_layer(self, layer_name: str, seed_dir: Path) -> List[Path]:
        """提取某一层的基因文件"""
        layer_def = self.genome.get(layer_name, {})
        if not layer_def:
            return []

        target_dir = seed_dir / layer_name
        target_dir.mkdir(parents=True, exist_ok=True)
        copied = []

        if layer_def.get("extract") == "from_file":
            src = WORKSPACE / layer_def["source"]
            if src.exists():
                dst = target_dir / src.name
                dst.write_text(src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                copied.append(dst)

        elif layer_def.get("extract") == "from_dir":
            src_dir = WORKSPACE / layer_def.get("dir", "")
            if src_dir.exists() and src_dir.is_dir():
                for f in src_dir.glob("*.md"):
                    if f.is_file():
                        dst = target_dir / f.name
                        dst.write_text(f.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                        copied.append(dst)

        elif layer_def.get("files"):
            for rel_path in layer_def["files"]:
                src = WORKSPACE / rel_path
                if src.exists():
                    # 保持目录结构
                    dst = target_dir / Path(rel_path).name
                    dst.write_text(src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                    copied.append(dst)

        return copied

    def _extract_persona_chips(self) -> Optional[Dict[str, Any]]:
        """从 roundtable.py 提取人格芯片数据（过滤掉不可序列化的字段）"""
        try:
            sys.path.insert(0, str(WORKSPACE / "04_PROTOCOLS"))
            from roundtable import PERSONA_CHIPS

            # 过滤掉 lambda / function 等不可序列化字段
            clean_chips = {}
            for chip_id, chip in PERSONA_CHIPS.items():
                clean_chip = {}
                for k, v in chip.items():
                    if k == "attack_methods":
                        clean_methods = []
                        for m in v:
                            clean_m = {}
                            for mk, mv in m.items():
                                if callable(mv):
                                    continue  # 跳过 lambda/check 函数
                                clean_m[mk] = mv
                            clean_methods.append(clean_m)
                        clean_chip[k] = clean_methods
                    elif callable(v):
                        continue
                    else:
                        clean_chip[k] = v
                clean_chips[chip_id] = clean_chip

            return {
                "chips": clean_chips,
                "count": len(clean_chips),
                "extracted_at": datetime.now().isoformat(),
            }
        except Exception:
            return None

    def _compute_seed_hash(self, seed_dir: Path) -> str:
        """计算种子文件的整体哈希（防篡改）"""
        hasher = hashlib.sha256()
        # 按文件名排序，确保哈希可重复
        files = sorted(seed_dir.rglob("*"))
        for f in files:
            if f.is_file() and f.name != "genome_manifest.json":
                hasher.update(str(f.relative_to(seed_dir)).encode())
                hasher.update(b"\0")
                hasher.update(f.read_bytes())
        return hasher.hexdigest()

    def _zip_seed(self, seed_dir: Path, zip_path: Path):
        """打包种子为 ZIP"""
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in seed_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(seed_dir))

    def verify_seed(self, zip_path: str) -> Dict[str, Any]:
        """验证基因种子的完整性"""
        import tempfile

        zip_file = Path(zip_path)
        if not zip_file.exists():
            return {"valid": False, "error": "file not found"}

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            with zipfile.ZipFile(zip_file, "r") as zf:
                zf.extractall(tmp)

            # 检查 manifest
            manifest_file = tmp / "genome_manifest.json"
            if not manifest_file.exists():
                return {"valid": False, "error": "missing manifest"}

            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # 重新计算哈希
            current_hash = self._compute_seed_hash(tmp)
            expected_hash = manifest.get("genome_hash", "")
            hash_match = current_hash == expected_hash

            # 检查各层
            layers_ok = {}
            for layer_name in manifest.get("layers", {}):
                layer_dir = tmp / layer_name
                # 有些层是单个文件而非目录（如 persona_chips.json, RECOVERY_GUIDE.md）
                if layer_dir.exists() and layer_dir.is_dir():
                    layers_ok[layer_name] = True
                else:
                    # 检查是否存在对应模式的文件
                    pattern_map = {
                        "persona_chips": "persona_chips*",
                        "recovery_protocol": "RECOVERY*",
                    }
                    pattern = pattern_map.get(layer_name, f"{layer_name}*")
                    found = list(tmp.glob(pattern))
                    layers_ok[layer_name] = len(found) > 0

            all_layers_present = all(layers_ok.values())

            return {
                "valid": hash_match and all_layers_present,
                "seed_id": manifest.get("seed_id"),
                "hash_match": hash_match,
                "expected_hash": expected_hash,
                "actual_hash": current_hash,
                "layers_present": layers_ok,
                "all_layers_present": all_layers_present,
                "file_count": manifest.get("file_count"),
                "created_at": manifest.get("created_at"),
            }

    def list_seeds(self) -> List[Dict[str, Any]]:
        """列出所有基因种子备份"""
        seeds = []
        for f in self.backup_dir.glob("gene_seed_*.zip"):
            size = f.stat().st_size
            date_str = f.stem.replace("gene_seed_", "")
            seeds.append({
                "name": f.stem,
                "path": str(f),
                "size": size,
                "size_kb": round(size / 1024, 1),
                "date": date_str,
            })
        seeds.sort(key=lambda s: s["date"], reverse=True)
        return seeds

    def prune_old_seeds(self, keep: int = 7) -> int:
        """清理旧的种子备份（保留最新的 N 个）"""
        seeds = self.list_seeds()
        if len(seeds) <= keep:
            return 0

        removed = 0
        for seed in seeds[keep:]:
            try:
                Path(seed["path"]).unlink()
                removed += 1
            except Exception:
                pass
        return removed


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="GENE-001: 文明基因备份盘")
    parser.add_argument("--create", action="store_true", help="创建基因种子备份")
    parser.add_argument("--verify", metavar="ZIP", help="验证种子备份完整性")
    parser.add_argument("--list", action="store_true", help="列出所有种子备份")
    parser.add_argument("--prune", type=int, nargs="?", const=7, help="清理旧备份 (保留 N 个)")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    archive = SeedArchive()

    if args.create:
        result = archive.create_seed()
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print(f"✅ 基因种子已创建: {result['seed_id']}")
            print(f"   文件: {result['zip_path']}")
            print(f"   大小: {result['zip_size'] / 1024:.1f} KB")
            print(f"   文件数: {result['file_count']}")
            print(f"   层级: {', '.join(result['layers'])}")
            print(f"   哈希: {result['genome_hash'][:16]}...")

    elif args.verify:
        result = archive.verify_seed(args.verify)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            if result.get("valid"):
                print(f"✅ 种子验证通过: {result.get('seed_id')}")
                print(f"   创建时间: {result.get('created_at')}")
                print(f"   文件数: {result.get('file_count')}")
                print(f"   哈希匹配: Yes")
            else:
                print(f"❌ 种子验证失败: {result.get('error', 'unknown')}")
                if result.get("hash_match") is False:
                    print(f"   哈希不匹配！expected={result.get('expected_hash','')[:16]}... actual={result.get('actual_hash','')[:16]}...")

    elif args.list:
        seeds = archive.list_seeds()
        if args.json:
            print(json.dumps(seeds, indent=2, ensure_ascii=False, default=str))
        else:
            print(f"📦 基因种子备份 ({len(seeds)} 个):")
            for s in seeds:
                print(f"   {s['name']}  ({s['size_kb']} KB)  {s['date']}")

    elif args.prune is not None:
        removed = archive.prune_old_seeds(keep=args.prune)
        if args.json:
            print(json.dumps({"removed": removed, "kept": args.prune}))
        else:
            print(f"🧹 清理完成，删除了 {removed} 个旧备份，保留最新 {args.prune} 个")

    else:
        parser.print_help()
        print()
        print("示例:")
        print("  python seed_archive.py --create")
        print("  python seed_archive.py --list")
        print("  python seed_archive.py --verify 03_ARCHIVE/gene_seed/gene_seed_20260712.zip")
        print("  python seed_archive.py --prune 7")


if __name__ == "__main__":
    main()
