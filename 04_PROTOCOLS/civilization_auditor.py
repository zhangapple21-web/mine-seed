"""---
id: PROTO-007
type: protocol
title: "Civilization Auditor — 文明审计器"
status: active
source: "R2 Development"
created: 2026-07-12
confidence: 0.88
lineage:
  - OPS-004
related: [PROTO-001, PROTO-002]
tags: [audit, civilization, graph]
archaeology:
  state: original
---
"""
#!/usr/bin/env python3
"""
AUD-001: Civilization Auditor — 文明审计器
============================================

三合一检测，避免 8 个 Scanner 各扫一遍：
  1. Duplicate Scanner  — 重复资产检测
  2. Zombie Scanner     — 死代码/死协议检测
  3. Missing Link Scanner — README→代码→协议→运行 链路缺失检测

输出:
  02_MEMORY/civilization_audit/audit_YYYYMMDD.json
  02_MEMORY/civilization_audit/audit_YYYYMMDD.md

集成:
  Heartbeat 每周跑一次（避免每天重复扫描浪费资源）
"""
import os, sys, json, hashlib, ast, re, argparse
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict

WORKSPACE = Path(__file__).parent.parent
AUDIT_DIR = WORKSPACE / "02_MEMORY" / "civilization_audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# 扫描范围（排除 .git, node_modules, __pycache__, .venv 等）
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
             ".pytest_cache", ".mypy_cache", "dist", "build", ".eggs"}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".log", ".tmp", ".swp", ".DS_Store"}

# C-017: 归档目录不参与僵尸检测（归档文件本就不应被引用）
ZOMBIE_SKIP_DIRS = SKIP_DIRS | {"superseded_archive"}
# C-014: R1 考古现场保留原貌，不参与僵尸检测
RAW_SOURCE_DIRS = {"raw_sources", "extracted"}

# C-014: 时间戳文件模式（属于时间序列数据，不视为僵尸）
TIME_SERIES_PATTERNS = [
    re.compile(r'_\d{8}T\d{6}'),      # situation_20260711T140531.json
    re.compile(r'_\d{8}_\d{4}\.'),    # thought_seed_20260630_0645.json
    re.compile(r'_\d{8}_\d{6}\.'),    # thought_seed_20260706_064757.json
    re.compile(r'exp_\w*_\d{8}T'),    # exp_provider_ollama_20260711T190940.json
    re.compile(r'loop_\d{8}T'),       # loop_20260710T155648.json
]

# C-013: 顶级目录（canonical path 检测用）
CANONICAL_TOP_DIRS = ["02_MEMORY", "03_DATA", "04_PROTOCOLS", "05_TOOLS", "06_RUNTIME",
                       "02_ARCHITECTURE", "02_modules", "02_LEARNING", "00_ROOT", "01_AGENTS"]

# C-015: 协议类型标记
PROTOCOL_TYPE_MARKER = re.compile(r'^#\s*TYPE:\s*(runtime|dev_tool)\s*$', re.MULTILINE)

# C-016: 约束追溯标记
IMPLEMENTS_MARKER = re.compile(r'#\s*Implements:\s*(.+)', re.IGNORECASE)
IMPLEMENTS_ID_EXTRACT = re.compile(r'C[-_]\d+', re.IGNORECASE)

# 代码文件扩展名
CODE_EXTENSIONS = {".py", ".js", ".ts", ".sh", ".bat"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".sh", ".tpl"}
DOC_EXTENSIONS = {".md", ".rst", ".txt"}


def _is_time_series_file(path: Path) -> bool:
    """C-014: 判断是否为时间序列文件（不应被审计为僵尸）"""
    name = path.name
    for pat in TIME_SERIES_PATTERNS:
        if pat.search(name):
            return True
    return False


def _is_in_raw_source(path: Path) -> bool:
    """C-014: 判断是否在 R1 考古现场目录中"""
    try:
        rel = path.relative_to(WORKSPACE)
        parts = rel.parts
        for part in parts:
            if part in RAW_SOURCE_DIRS:
                return True
        return False
    except ValueError:
        return False


def _get_protocol_type(path: Path) -> str:
    """C-015: 读取协议文件的 TYPE 标记，默认为 runtime"""
    try:
        # 只读前 20 行（标记应在文件头）
        with open(path, encoding="utf-8", errors="ignore") as f:
            for _ in range(20):
                line = f.readline()
                if not line:
                    break
                m = PROTOCOL_TYPE_MARKER.match(line.strip())
                if m:
                    return m.group(1)
    except Exception:
        pass
    return "runtime"  # 默认为运行时协议


# TYPE: runtime
# Implements: C-013 C-014 C-015 C-016 C-017 C-018
class CivilizationAuditor:
    """文明审计器 — 七合一检测"""

    def __init__(self):
        self.duplicates: List[Dict[str, Any]] = []
        self.zombies: List[Dict[str, Any]] = []
        self.missing_links: List[Dict[str, Any]] = []
        self.canonical_violations: List[Dict[str, Any]] = []
        self.retention_violations: List[Dict[str, Any]] = []
        self.memory_health: Dict[str, Any] = {}
        self.coverage: Dict[str, Any] = {}
        self.graph: Dict[str, Any] = {}
        self.stats: Dict[str, Any] = {}

    def _walk_files(self, root: Path, extensions: Set[str] = None,
                    skip_dirs: Set[str] = None) -> List[Path]:
        """遍历文件，支持扩展名过滤和自定义跳过目录"""
        sd = skip_dirs if skip_dirs is not None else SKIP_DIRS
        files = []
        for root_dir, dirs, filenames in os.walk(root):
            dirs[:] = [d for d in dirs if d not in sd]
            for fname in filenames:
                fpath = Path(root_dir) / fname
                if fpath.suffix in SKIP_EXTENSIONS:
                    continue
                if extensions and fpath.suffix not in extensions:
                    continue
                files.append(fpath)
        return files

    # ================================================================
    # 1. Duplicate Scanner — 重复资产检测
    # ================================================================
    def scan_duplicates(self) -> List[Dict[str, Any]]:
        """检测重复文件

        策略:
          a) 文件名相似度（heartbeat.py vs heartbeat_old.py vs heartbeat_v2.py）
          b) 内容 hash 相同（完全重复）
        """
        print("[AUDIT] Scanning duplicates...")

        # a) 按文件名聚类（检测 _old, _v2, _copy, _backup 变体）
        name_clusters = defaultdict(list)
        all_files = self._walk_files(WORKSPACE, CODE_EXTENSIONS | CONFIG_EXTENSIONS)

        for fpath in all_files:
            # 标准化文件名：去掉 _old, _v2, _copy, _backup, _tmp 后缀
            stem = fpath.stem
            base_stem = re.sub(r'[_-](old|v\d+|copy|backup|tmp|test|new|draft|wip)\d*$', '', stem, flags=re.IGNORECASE)
            # 也去掉 _2, _3 这样的数字后缀
            base_stem = re.sub(r'[_-]\d+$', '', base_stem)
            if base_stem != stem:
                name_clusters[base_stem].append(fpath)
            # 也收集原始文件
            if base_stem == stem:
                name_clusters[base_stem].append(fpath)

        # 找出有变体的集群
        duplicates = []
        for base_name, files in name_clusters.items():
            if len(files) < 2:
                continue
            # 计算每个文件的大小和修改时间
            file_infos = []
            for f in files:
                try:
                    stat = f.stat()
                    file_infos.append({
                        "path": str(f.relative_to(WORKSPACE)),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:10],
                    })
                except Exception:
                    pass

            # 按修改时间排序，最新的排前面
            file_infos.sort(key=lambda x: x["modified"], reverse=True)

            duplicates.append({
                "base_name": base_name,
                "files": file_infos,
                "count": len(file_infos),
                "recommendation": f"保留 {file_infos[0]['path']} (最新), 考虑归档其他 {len(file_infos)-1} 个",
            })

        # b) 内容 hash 相同的文件（完全重复）
        hash_map = defaultdict(list)
        for fpath in all_files:
            try:
                content = fpath.read_bytes()
                if len(content) < 50:  # 忽略太小的文件
                    continue
                h = hashlib.md5(content).hexdigest()
                hash_map[h].append(fpath)
            except Exception:
                pass

        for h, files in hash_map.items():
            if len(files) < 2:
                continue
            duplicates.append({
                "type": "identical_content",
                "hash": h,
                "files": [str(f.relative_to(WORKSPACE)) for f in files],
                "count": len(files),
                "recommendation": "内容完全相同，保留一个即可",
            })

        self.duplicates = duplicates
        print(f"  Found {len(duplicates)} duplicate clusters")
        return duplicates

    # ================================================================
    # 2. Zombie Scanner — 死代码检测
    # ================================================================
    def scan_zombies(self) -> List[Dict[str, Any]]:
        """检测死代码/死协议

        策略:
          a) .py 文件中的函数/类，检查是否被其他文件 import 或调用
          b) 文件名含 _old, _tmp, _test, _draft 的疑似废弃文件
          c) JSON/YAML 配置文件是否被代码引用

        C-014/C-017 排除规则:
          - superseded_archive/ 中的文件不视为僵尸（归档本就不应被引用）
          - raw_sources/extracted/ 中的文件不视为僵尸（R1 考古现场保留原貌）
          - 时间戳命名的文件不视为僵尸（属于时间序列数据，应走 retention）
        """
        print("[AUDIT] Scanning zombies...")

        zombies = []

        # a) 疑似废弃文件（文件名特征）
        zombie_patterns = re.compile(r'[_-](old|tmp|test|draft|wip|deprecated|unused|dead|copy|backup)\d*$', re.IGNORECASE)
        # C-017: 归档目录不参与僵尸检测
        all_code_files = self._walk_files(WORKSPACE, CODE_EXTENSIONS, skip_dirs=ZOMBIE_SKIP_DIRS)

        for fpath in all_code_files:
            # C-014: 跳过 R1 考古现场
            if _is_in_raw_source(fpath):
                continue
            if zombie_patterns.search(fpath.stem):
                try:
                    stat = fpath.stat()
                    zombies.append({
                        "type": "suspected_deprecated",
                        "path": str(fpath.relative_to(WORKSPACE)),
                        "reason": f"文件名包含废弃标记: {fpath.stem}",
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:10],
                    })
                except Exception:
                    pass

        # b) Python 文件中未被 import 的模块
        py_files = [f for f in all_code_files if f.suffix == ".py"
                    and not _is_in_raw_source(f)]
        all_imports = set()

        for fpath in py_files:
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                # 提取 import 语句
                for match in re.finditer(r'^\s*(?:from\s+(\S+)\s+import|import\s+(\S+))', content, re.MULTILINE):
                    module = match.group(1) or match.group(2)
                    # 只关心本地模块（不是标准库/第三方）
                    module_name = module.split(".")[0]
                    if not module_name.startswith("_"):
                        all_imports.add(module_name)
            except Exception:
                pass

        # 检查每个 .py 文件是否被其他文件 import
        for fpath in py_files:
            module_name = fpath.stem
            if module_name in ("__init__", "main", "setup", "conftest"):
                continue
            # 如果文件名是 _old 等变体，跳过（已在上面检测）
            if zombie_patterns.search(module_name):
                continue

            # 检查是否被 import
            if module_name not in all_imports:
                # 也检查是否作为脚本直接运行（有 if __name__ == "__main__"）
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    has_main = '__name__' in content and '__main__' in content
                    # 检查是否在 heartbeat 或其他入口中被 sys.path + import
                    is_entry = any(kw in module_name for kw in ["heartbeat", "awaken", "main", "run_"])
                except Exception:
                    has_main = False
                    is_entry = False

                if not has_main and not is_entry:
                    try:
                        stat = fpath.stat()
                        zombies.append({
                            "type": "unreferenced_module",
                            "path": str(fpath.relative_to(WORKSPACE)),
                            "reason": f"模块 {module_name} 未被任何文件 import",
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:10],
                        })
                    except Exception:
                        pass

        # c) 未被引用的 JSON 配置文件
        # C-017: 归档目录不参与；C-014: 时间序列文件走 retention 不走僵尸检测
        json_files = self._walk_files(WORKSPACE, {".json"}, skip_dirs=ZOMBIE_SKIP_DIRS)
        json_names = {}
        for f in json_files:
            if f.stem in ("package", "tsconfig", "launch", "settings"):
                continue
            # C-014: 跳过时间序列文件
            if _is_time_series_file(f):
                continue
            # C-014: 跳过 R1 考古现场
            if _is_in_raw_source(f):
                continue
            json_names[f.stem] = f

        if json_names:
            all_text = ""
            for fpath in py_files[:50]:  # 只读前 50 个 py 文件避免太慢
                try:
                    all_text += fpath.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    pass

            for stem, fpath in json_names.items():
                if stem not in all_text:
                    try:
                        stat = fpath.stat()
                        if stat.st_size > 100:  # 忽略空文件
                            zombies.append({
                                "type": "unreferenced_config",
                                "path": str(fpath.relative_to(WORKSPACE)),
                                "reason": f"配置 {stem}.json 未被代码引用",
                                "size": stat.st_size,
                            })
                    except Exception:
                        pass

        self.zombies = zombies
        print(f"  Found {len(zombies)} zombie files")
        return zombies

    # ================================================================
    # 3. Missing Link Scanner — 断链检测
    # ================================================================
    def scan_missing_links(self) -> List[Dict[str, Any]]:
        """检测 README→代码→协议→运行 链路缺失

        策略:
          a) README 中提到的功能，检查代码中是否有实现
          b) AGENTS.md 中声明的模块，检查是否真实存在
          c) Protocol 文件是否被 Heartbeat 调用
          d) constraints.json 中的约束是否在代码中被引用
        """
        print("[AUDIT] Scanning missing links...")

        missing_links = []

        # a) 检查 AGENTS.md 中声明的模块
        agents_md = WORKSPACE / "AGENTS.md"
        if agents_md.exists():
            content = agents_md.read_text(encoding="utf-8")
            # 提取模块名（通常是 `xxx.py` 或 backtick 包裹的文件名）
            mentioned_files = set(re.findall(r'`(\w+\.py)`', content))

            for fname in mentioned_files:
                # 检查文件是否存在
                found = False
                for root, dirs, files in os.walk(WORKSPACE):
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                    if fname in files:
                        found = True
                        break
                if not found:
                    missing_links.append({
                        "type": "declared_but_missing",
                        "source": "AGENTS.md",
                        "target": fname,
                        "reason": f"AGENTS.md 声明了 {fname}，但文件不存在",
                    })

        # b) 检查 Heartbeat 是否调用了所有 Protocol
        # C-015: 区分 runtime 协议（必须接线）和 dev_tool（不强制接线）
        heartbeat_path = WORKSPACE / "04_PROTOCOLS" / "heartbeat.py"
        protocol_dir = WORKSPACE / "04_PROTOCOLS"

        if heartbeat_path.exists() and protocol_dir.exists():
            heartbeat_content = heartbeat_path.read_text(encoding="utf-8")

            for proto_file in protocol_dir.glob("*.py"):
                if proto_file.name in ("heartbeat.py", "__init__.py"):
                    continue
                module_name = proto_file.stem
                # C-015: 读取协议类型标记
                proto_type = _get_protocol_type(proto_file)
                # dev_tool 不强制接线
                if proto_type == "dev_tool":
                    continue
                # 检查是否在 heartbeat 中被 import
                if module_name not in heartbeat_content:
                    # 也检查是否被其他 protocol import
                    referenced = False
                    for other in protocol_dir.glob("*.py"):
                        if other.name == proto_file.name:
                            continue
                        try:
                            other_content = other.read_text(encoding="utf-8")
                            if module_name in other_content:
                                referenced = True
                                break
                        except Exception:
                            pass

                    if not referenced:
                        missing_links.append({
                            "type": "protocol_not_wired",
                            "source": "04_PROTOCOLS",
                            "target": proto_file.name,
                            "reason": f"协议 {proto_file.name} 未被 Heartbeat 或其他协议调用",
                        })

        # c) 检查 constraints.json 中的约束是否在代码中被引用
        # C-016: 用 '# Implements: C-XXX' 注释标记替代字面匹配
        constraints_path = WORKSPACE / "constraints.json"
        if constraints_path.exists():
            constraints = json.loads(constraints_path.read_text(encoding="utf-8"))
            constraint_ids = [c.get("id", "") for c in constraints.get("constraints", [])]

            # C-016: 收集所有代码中的 Implements 标记
            implemented_ids = set()
            all_code = ""
            for fpath in self._walk_files(WORKSPACE, CODE_EXTENSIONS):
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    all_code += content
                    # 提取 # Implements: C-XXX 标记（支持一行多个）
                    for m in IMPLEMENTS_MARKER.finditer(content):
                        matched_str = m.group(1)
                        for cid_match in IMPLEMENTS_ID_EXTRACT.finditer(matched_str):
                            implemented_ids.add(cid_match.group(0).upper().replace("_", "-"))
                except Exception:
                    pass

            for cid in constraint_ids:
                if not cid:
                    continue
                cid_upper = cid.upper()
                # C-016: 优先看 Implements 标记，fallback 到字面匹配
                is_implemented = cid_upper in implemented_ids or cid in all_code
                if not is_implemented:
                    missing_links.append({
                        "type": "constraint_not_implemented",
                        "source": "constraints.json",
                        "target": cid,
                        "reason": f"约束 {cid} 未在代码中标注 '# Implements: {cid}'，也无字面引用",
                    })

        # d) 检查 README 中提到的功能关键词
        readme_files = list(WORKSPACE.glob("README*.md")) + list(WORKSPACE.glob("readme*.md"))
        feature_keywords = {
            "Telegram": ["telethon", "tg_push", "tg_pusher", "TelegramClient"],
            "GitHub": ["github", "git_api", "GITHUB_TOKEN"],
            "Provider": ["local_miner", "call_model", "provider"],
            "Heartbeat": ["heartbeat", "beat"],
            "Recovery": ["recovery", "Awaken", "EFP"],
        }

        for readme in readme_files:
            content = readme.read_text(encoding="utf-8", errors="ignore")
            for feature, keywords in feature_keywords.items():
                if feature.lower() in content.lower():
                    # 检查关键词是否在代码中出现
                    all_code = ""
                    for fpath in self._walk_files(WORKSPACE, CODE_EXTENSIONS)[:30]:
                        try:
                            all_code += fpath.read_text(encoding="utf-8", errors="ignore")
                        except Exception:
                            pass
                    if not any(kw in all_code for kw in keywords):
                        missing_links.append({
                            "type": "readme_feature_missing",
                            "source": readme.name,
                            "target": feature,
                            "reason": f"{readme.name} 提到 {feature}，但代码中未找到实现",
                        })

        self.missing_links = missing_links
        print(f"  Found {len(missing_links)} missing links")
        return missing_links

    # ================================================================
    # 4. Canonical Path Scanner — C-013 单一权威路径检测
    # ================================================================
    def scan_canonical_paths(self) -> List[Dict[str, Any]]:
        """C-013: 检测同一 base_name 出现在多个顶级目录

        每个 base_name 应该只有一个 canonical path。
        出现在多个顶级目录（02_MEMORY/03_DATA/04_PROTOCOLS/05_TOOLS/06_RUNTIME）视为违规。
        """
        print("[AUDIT] Scanning canonical paths (C-013)...")

        violations = []
        # 收集每个 base_name 在哪些顶级目录出现
        base_name_locations = defaultdict(set)

        all_files = self._walk_files(WORKSPACE, CODE_EXTENSIONS | CONFIG_EXTENSIONS)
        for fpath in all_files:
            try:
                rel = fpath.relative_to(WORKSPACE)
                parts = rel.parts
                if len(parts) < 2:
                    continue
                top_dir = parts[0]
                if top_dir not in CANONICAL_TOP_DIRS:
                    continue
                # 跳过例外（C-013: _SUPERSEDED_, extracted/, raw_sources/）
                rel_str = str(rel)
                if "_SUPERSEDED_" in rel_str or "extracted" in parts or "raw_sources" in parts:
                    continue
                # 用 stem 作为 base_name（去掉扩展名和 _SUPERSEDED 后缀）
                stem = fpath.stem
                # 去掉 __SUPERSEDED_日期 后缀
                stem = re.sub(r'__SUPERSEDED_\d+', '', stem)
                base_name_locations[stem].add(top_dir)
            except Exception:
                pass

        # 找出出现在多个顶级目录的 base_name
        for stem, top_dirs in base_name_locations.items():
            if len(top_dirs) < 2:
                continue
            # 找出这些文件的实际路径
            files_in_cluster = []
            for fpath in all_files:
                try:
                    rel = fpath.relative_to(WORKSPACE)
                    parts = rel.parts
                    if len(parts) < 2 or parts[0] not in CANONICAL_TOP_DIRS:
                        continue
                    if "_SUPERSEDED_" in str(rel) or "extracted" in parts or "raw_sources" in parts:
                        continue
                    if fpath.stem == stem or re.sub(r'__SUPERSEDED_\d+', '', fpath.stem) == stem:
                        stat = fpath.stat()
                        files_in_cluster.append({
                            "path": str(rel),
                            "top_dir": parts[0],
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:10],
                        })
                except Exception:
                    pass

            if len(files_in_cluster) >= 2:
                top_dirs_list = sorted(top_dirs)
                violations.append({
                    "base_name": stem,
                    "top_dirs": top_dirs_list,
                    "top_dir_count": len(top_dirs_list),
                    "files": files_in_cluster,
                    "recommendation": f"选择一个 canonical path（建议 {top_dirs_list[0]}），删除其他 {len(top_dirs_list)-1} 处副本",
                })

        print(f"  Found {len(violations)} canonical path violations")
        return violations

    # ================================================================
    # 5. Time-Series Retention Scanner — C-014 时间序列轮转检测
    # ================================================================
    def scan_time_series_retention(self, keep_n: int = 7) -> List[Dict[str, Any]]:
        """C-014: 检测时间戳文件是否超过 retention 阈值

        时间序列文件应保留 latest + 最近 N 份，超过视为违规。
        """
        print("[AUDIT] Scanning time-series retention (C-014)...")

        violations = []
        # 按基础模式分组
        series_groups = defaultdict(list)

        all_files = self._walk_files(WORKSPACE, {".json"})
        for fpath in all_files:
            if not _is_time_series_file(fpath):
                continue
            try:
                rel = fpath.relative_to(WORKSPACE)
                name = fpath.name
                # 提取基础模式（去掉时间戳部分）
                # situation_20260711T140531.json -> situation
                # thought_seed_20260630_0645.json -> thought_seed
                base = re.sub(r'_\d{8}T\d{6}.*', '', name)
                base = re.sub(r'_\d{8}_\d{4,6}.*', '', base)
                base = re.sub(r'\.\w+$', '', base)
                # exp_provider_ollama_20260711T190940.json -> exp_provider_ollama
                base = re.sub(r'_\d{8}T\d{6}.*', '', base)
                stat = fpath.stat()
                series_groups[base].append({
                    "path": str(rel),
                    "name": name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()[:19],
                })
            except Exception:
                pass

        for base, files in series_groups.items():
            if len(files) <= keep_n:
                continue
            # 按修改时间排序
            files.sort(key=lambda x: x["modified"], reverse=True)
            violations.append({
                "base_pattern": base,
                "total_files": len(files),
                "keep_latest_n": keep_n,
                "excess": len(files) - keep_n,
                "latest": files[0]["path"] if files else None,
                "oldest_to_clean": [f["path"] for f in files[keep_n:]],
                "recommendation": f"保留 latest + 最近 {keep_n} 份，清理 {len(files) - keep_n} 份超期文件",
            })

        print(f"  Found {len(violations)} time-series retention violations")
        return violations

    # ================================================================
    # 6. Memory Health Scanner — 记忆健康度检测
    # Implements: memory_health
    # ================================================================
    def scan_memory_health(self) -> Dict[str, Any]:
        """检测 memory_index_latest.json 的健康度

        分析维度:
          - 记忆类型分布
          - 概念引用统计（找出高价值概念 vs 无人引用的概念）
          - 死亡记忆（access_count = 0 的比例）
          - 重复记忆（相似标题或内容）
        """
        print("[AUDIT] Scanning memory health...")

        result = {
            "index_exists": False,
            "total_memories": 0,
            "type_distribution": {},
            "source_distribution": {},
            "category_distribution": {},
            "dead_memory_count": 0,
            "dead_memory_pct": 0.0,
            "concepts": [],
            "top_concepts": [],
            "orphan_concepts": [],
            "duplicate_titles": [],
            "health_score": 0,
        }

        # 查找最新的 memory_index
        idx_path = WORKSPACE / "02_MEMORY" / "memory_index_latest.json"
        if not idx_path.exists():
            # 找带日期的
            candidates = sorted(WORKSPACE.glob("02_MEMORY/memory_index_*.json"), reverse=True)
            if candidates:
                idx_path = candidates[0]

        if not idx_path.exists():
            print("  No memory index found")
            return result

        try:
            idx_data = json.loads(idx_path.read_text(encoding="utf-8"))
            entries = idx_data.get("entries", [])
            result["index_exists"] = True
            result["total_memories"] = len(entries)
            result["index_file"] = str(idx_path.relative_to(WORKSPACE))

            if not entries:
                return result

            # 类型 / 来源 / 分类分布
            type_dist = defaultdict(int)
            source_dist = defaultdict(int)
            cat_dist = defaultdict(int)
            dead_count = 0

            # 概念引用统计
            concept_refs = defaultdict(lambda: {
                "count": 0,
                "category": "未知",
                "relevance_sum": 0,
                "related_memories": [],
            })

            # 重复标题检测
            title_counts = defaultdict(list)

            for entry in entries:
                t = entry.get("type", "unknown")
                s = entry.get("source", "unknown")
                c = entry.get("category", "未知")
                type_dist[t] += 1
                source_dist[s] += 1
                cat_dist[c] += 1

                if entry.get("access_count", 0) == 0:
                    dead_count += 1

                # 概念统计
                for concept in entry.get("related_concepts", []):
                    name = concept.get("name", "")
                    if not name or len(name) <= 1:  # 过滤单字（as, in, id 等噪声）
                        continue
                    cat = concept.get("category", "待分类")
                    rel = concept.get("relevance", 0)
                    concept_refs[name]["count"] += 1
                    concept_refs[name]["category"] = cat
                    concept_refs[name]["relevance_sum"] += rel
                    if len(concept_refs[name]["related_memories"]) < 3:
                        concept_refs[name]["related_memories"].append(entry.get("title", "")[:60])

                # 标题去重（规范化后比较）
                title = entry.get("title", "")
                # 去掉日期/ID 等易变部分做近似匹配
                norm_title = re.sub(r'\d{4}[-_]?\d{2}[-_]?\d{2}', '', title)
                norm_title = re.sub(r'[a-f0-9]{6,}', '', norm_title)  # 去掉 hash
                norm_title = norm_title.strip()
                if len(norm_title) > 10:
                    title_counts[norm_title].append(entry.get("id", ""))

            result["type_distribution"] = dict(type_dist)
            result["source_distribution"] = dict(source_dist)
            result["category_distribution"] = dict(cat_dist)
            result["dead_memory_count"] = dead_count
            result["dead_memory_pct"] = round(dead_count / len(entries) * 100, 1)

            # 概念列表（按引用次数排序）
            concepts_list = []
            for name, data in concept_refs.items():
                concepts_list.append({
                    "concept": name,
                    "ref_count": data["count"],
                    "category": data["category"],
                    "avg_relevance": round(data["relevance_sum"] / data["count"], 1),
                })
            concepts_list.sort(key=lambda x: x["ref_count"], reverse=True)
            result["concepts"] = concepts_list

            # Top 20 高价值概念
            result["top_concepts"] = concepts_list[:20]

            # 孤儿概念（只被引用 1 次的概念）
            orphan_concepts = [c for c in concepts_list if c["ref_count"] == 1]
            result["orphan_concepts"] = orphan_concepts[:50]
            result["orphan_concept_count"] = len(orphan_concepts)

            # 重复标题
            dup_titles = []
            for norm_title, ids in title_counts.items():
                if len(ids) >= 2:
                    dup_titles.append({
                        "normalized_title": norm_title[:80],
                        "duplicate_count": len(ids),
                        "entry_ids": ids[:5],
                    })
            dup_titles.sort(key=lambda x: x["duplicate_count"], reverse=True)
            result["duplicate_titles"] = dup_titles[:30]
            result["duplicate_title_count"] = len(dup_titles)

            # 记忆健康分数（0-100）
            # 死亡记忆比例扣分：100% 死亡 = -50 分
            # 孤儿概念比例扣分：50% 孤儿 = -20 分
            # 重复记忆扣分：10% 重复 = -30 分
            score = 100
            score -= min(50, int(result["dead_memory_pct"] * 0.5))
            if len(concepts_list) > 0:
                orphan_pct = len(orphan_concepts) / len(concepts_list) * 100
                score -= min(20, int(orphan_pct * 0.2))
            dup_pct = len(dup_titles) / len(entries) * 100 if entries else 0
            score -= min(30, int(dup_pct * 3))
            result["health_score"] = max(0, score)

            print(f"  Memory Health: {result['health_score']}/100")
            print(f"  Total: {len(entries)} | Dead: {dead_count} ({result['dead_memory_pct']}%)")
            print(f"  Concepts: {len(concepts_list)} | Orphans: {len(orphan_concepts)}")
            print(f"  Duplicate titles: {len(dup_titles)}")

        except Exception as e:
            print(f"  Memory scan error: {e}")
            result["error"] = str(e)

        return result

    # ================================================================
    # 7. Civilization Coverage — 文明资产接管率
    # Implements: civilization_coverage
    # ================================================================
    def scan_coverage(self) -> Dict[str, Any]:
        """计算文明资产接管率（Civilization Coverage）

        从 7 个维度评估 R2 对历史资产的接管程度:
          1. Workspace Coverage — Workspace 中的文件被 R2 索引/引用的比例
          2. Memory Indexed — memory_index 中的记忆被 R2 主动引用的比例
          3. Session Recovery — Session 资产恢复率
          4. Protocol Coverage — 定义的协议中被 Heartbeat 接入的比例
          5. Constraint Implementation — 定义的约束中被代码实现的比例
          6. Experience Indexed — Experience 资产被索引的比例
          7. Provider Health — Provider 在线率（反映运行时资产健康度）

        核心指标: Civilization Coverage Score = 加权平均
        """
        print("[AUDIT] Scanning civilization coverage...")

        coverage = {}
        total_weight = 0
        weighted_score = 0

        # 1. Workspace Coverage: 估算 Workspace 中被 R2 认知系统引用的文件比例
        # 简化方法: 统计 04_PROTOCOLS + 06_RUNTIME 中引用的文件 vs 总文件
        all_files = self._walk_files(WORKSPACE, CODE_EXTENSIONS | CONFIG_EXTENSIONS | {".md"})
        # 排除归档/考古现场（本就不该被引用）
        active_files = [
            f for f in all_files
            if not _is_in_raw_source(f)
            and "superseded_archive" not in str(f.relative_to(WORKSPACE))
            and not _is_time_series_file(f)
        ]
        # 被引用的 = 在 runtime/protocol 代码中出现过的文件名
        referenced_stems = set()
        runtime_code = self._walk_files(
            WORKSPACE / "04_PROTOCOLS", CODE_EXTENSIONS
        ) + self._walk_files(
            WORKSPACE / "06_RUNTIME", CODE_EXTENSIONS
        )
        for fpath in runtime_code:
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                for af in active_files:
                    stem = af.stem
                    if len(stem) > 4 and stem in content:
                        referenced_stems.add(stem)
            except Exception:
                pass

        ws_coverage = round(len(referenced_stems) / len(active_files) * 100, 1) if active_files else 0
        coverage["workspace_coverage"] = {
            "score": ws_coverage,
            "weight": 15,
            "total_files": len(active_files),
            "referenced_files": len(referenced_stems),
        }

        # 2. Memory Indexed: 记忆健康度（复用 memory health 结果）
        mem_health = getattr(self, "memory_health", {})
        mem_score = mem_health.get("health_score", 0)
        mem_total = mem_health.get("total_memories", 0)
        coverage["memory_indexed"] = {
            "score": mem_score,
            "weight": 20,
            "total_memories": mem_total,
            "note": "基于记忆健康度（死亡记忆/孤儿概念/重复）",
        }

        # 3. Session Recovery: Session 资产恢复率
        # 检查找到的 session 文件数 vs 实际可用数
        session_files = list(WORKSPACE.rglob("*.session"))
        session_files += list(WORKSPACE.rglob("*.session-journal"))
        session_files += list(WORKSPACE.rglob("*.sqlite"))
        session_files += list(WORKSPACE.rglob("*.db"))
        session_files += list(Path.home().glob(".telegram*/*"))
        session_files += list(Path.home().glob("AppData/Roaming/Telegram Desktop/tdata/*"))

        # 简化：已知 Bot Session 活了算 50%，User Session 如果有 auth_key 再加 50%
        # 从 recovery_engine 的结果或 memory 中读取
        session_score = 50  # 已知 Bot 活了
        user_session_path = WORKSPACE / "06_RUNTIME" / "session" / "tg_collections.session"
        if user_session_path.exists():
            session_score += 25  # 有 User Session 文件（虽然可能 revoked）
        if len(session_files) > 3:
            session_score += 10  # 找到多个 session 资产
        session_score = min(100, session_score)
        coverage["session_recovery"] = {
            "score": session_score,
            "weight": 10,
            "session_files_found": len(session_files),
            "note": "Bot ALIVE + User Session 文件存在 (revoked)",
        }

        # 4. Protocol Coverage: 运行时协议被 Heartbeat 接入的比例
        proto_dir = WORKSPACE / "04_PROTOCOLS"
        proto_files = [f for f in proto_dir.glob("*.py") if f.name not in ("__init__.py",)]
        runtime_protos = []
        wired_protos = []
        heartbeat_path = proto_dir / "heartbeat.py"
        hb_content = heartbeat_path.read_text(encoding="utf-8") if heartbeat_path.exists() else ""

        for pf in proto_files:
            if pf.name == "heartbeat.py":
                continue
            ptype = _get_protocol_type(pf)
            if ptype == "runtime":
                runtime_protos.append(pf.name)
                stem = pf.stem
                if stem in hb_content:
                    wired_protos.append(pf.name)
                else:
                    # 检查是否被其他 runtime 协议间接引用
                    for other in proto_files:
                        if other.name == pf.name or other.name == "heartbeat.py":
                            continue
                        if _get_protocol_type(other) == "runtime":
                            try:
                                other_content = other.read_text(encoding="utf-8", errors="ignore")
                                if stem in other_content:
                                    wired_protos.append(pf.name)
                                    break
                            except Exception:
                                pass

        proto_score = round(len(wired_protos) / len(runtime_protos) * 100, 1) if runtime_protos else 0
        coverage["protocol_coverage"] = {
            "score": proto_score,
            "weight": 15,
            "total_runtime_protos": len(runtime_protos),
            "wired_protos": len(wired_protos),
            "runtime_protos": runtime_protos,
            "wired_list": wired_protos,
        }

        # 5. Constraint Implementation: 约束代码实现率
        constraints_path = WORKSPACE / "constraints.json"
        const_total = 0
        const_implemented = 0
        if constraints_path.exists():
            constraints = json.loads(constraints_path.read_text(encoding="utf-8"))
            constraint_ids = [c.get("id", "") for c in constraints.get("constraints", []) if c.get("id")]
            const_total = len(constraint_ids)
            # 收集 Implements 标记
            implemented_ids = set()
            all_code_files = self._walk_files(WORKSPACE, CODE_EXTENSIONS)
            for fpath in all_code_files:
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    for m in IMPLEMENTS_MARKER.finditer(content):
                        matched_str = m.group(1)
                        for cid_match in IMPLEMENTS_ID_EXTRACT.finditer(matched_str):
                            implemented_ids.add(cid_match.group(0).upper().replace("_", "-"))
                except Exception:
                    pass
            for cid in constraint_ids:
                if cid.upper() in implemented_ids or cid in hb_content:
                    const_implemented += 1

        const_score = round(const_implemented / const_total * 100, 1) if const_total else 0
        coverage["constraint_implementation"] = {
            "score": const_score,
            "weight": 15,
            "total_constraints": const_total,
            "implemented": const_implemented,
        }

        # 6. Experience Indexed: Experience 资产健康度
        # 检查 experience.json 和 experience 目录
        exp_dir = WORKSPACE / "02_MEMORY" / "experience"
        exp_files = list(exp_dir.glob("*.json")) if exp_dir.exists() else []
        exp_json = WORKSPACE / "02_MEMORY" / "experience.json"
        exp_count = len(exp_files)
        if exp_json.exists():
            exp_count += 1
        # 有经验目录且有文件 = 较高分
        exp_score = min(100, exp_count * 10) if exp_count > 0 else 0
        if exp_count >= 10:
            exp_score = 80
        if exp_count >= 30:
            exp_score = 90
        coverage["experience_indexed"] = {
            "score": exp_score,
            "weight": 10,
            "experience_files": exp_count,
            "experience_dir_exists": exp_dir.exists(),
        }

        # 7. Provider Health: Provider 健康度（反映运行时资产）
        # 简化估算：从 provider_health.json 或 provider_registry 读取
        provider_health_path = WORKSPACE / "02_MEMORY" / "provider_health.json"
        prov_score = 50  # 默认中间值
        prov_total = 0
        prov_alive = 0
        if provider_health_path.exists():
            try:
                ph = json.loads(provider_health_path.read_text(encoding="utf-8"))
                providers = ph.get("providers", {})
                prov_total = len(providers)
                for p, data in providers.items():
                    status = data.get("status", "unknown")
                    if status in ("healthy", "alive", "online"):
                        prov_alive += 1
                if prov_total > 0:
                    prov_score = round(prov_alive / prov_total * 100, 1)
            except Exception:
                pass
        coverage["provider_health"] = {
            "score": prov_score,
            "weight": 15,
            "total_providers": prov_total,
            "alive_providers": prov_alive,
        }

        # 计算加权总分
        for key, data in coverage.items():
            w = data.get("weight", 10)
            s = data.get("score", 0)
            weighted_score += s * w
            total_weight += w

        overall = round(weighted_score / total_weight, 1) if total_weight > 0 else 0
        coverage["_overall"] = {
            "score": overall,
            "total_weight": total_weight,
            "verdict": self._coverage_verdict(overall),
        }

        print(f"  Civilization Coverage: {overall}%")
        for key, data in coverage.items():
            if key == "_overall":
                continue
            print(f"    {key}: {data.get('score', 0)}% (weight {data.get('weight', 0)})")

        return coverage

    def _coverage_verdict(self, score: float) -> str:
        if score >= 90:
            return "高度接管 — 文明资产基本进入 R2 认知范围"
        elif score >= 70:
            return "中等接管 — 核心资产已接管，边缘资产待考古"
        elif score >= 50:
            return "部分接管 — 大量沉睡文明待唤醒"
        elif score >= 30:
            return "低接管率 — 系统仍在自我构建阶段"
        else:
            return "极低接管 — 文明资产基本处于沉睡状态"

    # ================================================================
    # 8. Civilization Graph Scanner — 文明图谱
    # 从分散的 Registry/Index/Question Center 等源中提取节点和边
    # ================================================================
    def scan_graph(self) -> Dict[str, Any]:
        """构建 Civilization Graph — 从分散的源中提取节点和边

        节点类型 (Node Types):
          - question      问题
          - hypothesis    假设
          - experiment    实验
          - decision      决策
          - capability    能力
          - provider      模型/服务提供者
          - constraint    约束
          - protocol      协议
          - experience    经验
          - concept       概念
          - memory        记忆
          - worker        工作者/模块
          - task          任务
          - rfc           RFC 提案
          - repository    代码仓库
          - artifact      产物/文件

        边类型 (Edge Types):
          - has_hypothesis   Question → Hypothesis
          - has_experiment   Hypothesis → Experiment
          - has_decision     Question → Decision
          - requires         Capability → Capability (子能力依赖)
          - provides         Provider → Capability
          - implements       Protocol → Constraint
          - related          Memory → Concept
          - references       Protocol → Protocol
          - generates        Worker/Task → Artifact
          - depends_on       Task/Worker → Capability
          - owned_by         Object → Worker
          - supersedes       Object → Object
          - caused_by        Object → Object
          - uses             Worker → Provider

        返回: {nodes: [...], edges: [...], stats: {...}}
        """
        print("[AUDIT] Building Civilization Graph...")

        nodes = {}  # id -> {id, type, label, properties}
        edges = []  # [{source, target, type, properties}]

        DIMENSION_WEIGHTS = {
            "reality": 0.25,
            "knowledge": 0.15,
            "memory": 0.20,
            "generation": 0.15,
            "execution": 0.15,
            "experience": 0.10,
        }

        NODE_COORDS = {
            "question":      {"reality": 0.6, "knowledge": 0.8, "memory": 0.7, "generation": 0.5, "execution": 0.3, "experience": 0.5},
            "hypothesis":    {"reality": 0.4, "knowledge": 0.7, "memory": 0.5, "generation": 0.8, "execution": 0.2, "experience": 0.3},
            "experiment":    {"reality": 0.8, "knowledge": 0.6, "memory": 0.4, "generation": 0.5, "execution": 0.9, "experience": 0.6},
            "decision":      {"reality": 0.5, "knowledge": 0.7, "memory": 0.6, "generation": 0.4, "execution": 0.8, "experience": 0.8},
            "capability":    {"reality": 0.5, "knowledge": 0.7, "memory": 0.4, "generation": 0.6, "execution": 0.8, "experience": 0.5},
            "provider":      {"reality": 0.3, "knowledge": 0.5, "memory": 0.2, "generation": 0.9, "execution": 0.7, "experience": 0.4},
            "constraint":    {"reality": 0.4, "knowledge": 0.9, "memory": 0.8, "generation": 0.2, "execution": 0.6, "experience": 0.9},
            "protocol":      {"reality": 0.6, "knowledge": 0.6, "memory": 0.5, "generation": 0.3, "execution": 0.9, "experience": 0.7},
            "concept":       {"reality": 0.3, "knowledge": 0.9, "memory": 0.9, "generation": 0.4, "execution": 0.2, "experience": 0.5},
            "memory":        {"reality": 0.2, "knowledge": 0.6, "memory": 1.0, "generation": 0.3, "execution": 0.1, "experience": 0.7},
            "experience":    {"reality": 0.4, "knowledge": 0.7, "memory": 0.8, "generation": 0.5, "execution": 0.3, "experience": 1.0},
            "worker":        {"reality": 0.7, "knowledge": 0.5, "memory": 0.4, "generation": 0.4, "execution": 0.9, "experience": 0.6},
            "task":          {"reality": 0.8, "knowledge": 0.5, "memory": 0.3, "generation": 0.3, "execution": 0.8, "experience": 0.5},
            "rfc":           {"reality": 0.3, "knowledge": 0.8, "memory": 0.5, "generation": 0.7, "execution": 0.2, "experience": 0.4},
            "repository":    {"reality": 0.5, "knowledge": 0.7, "memory": 0.8, "generation": 0.3, "execution": 0.6, "experience": 0.5},
            "artifact":      {"reality": 0.6, "knowledge": 0.5, "memory": 0.7, "generation": 0.4, "execution": 0.5, "experience": 0.6},
        }

        def _calc_civilization_score(coords):
            score = 0
            for dim, w in DIMENSION_WEIGHTS.items():
                score += coords.get(dim, 0) * w
            return round(score, 3)

        def add_node(nid, ntype, label, **props):
            coords = NODE_COORDS.get(ntype, {k: 0.5 for k in DIMENSION_WEIGHTS.keys()})
            if nid in nodes:
                nodes[nid]["properties"].update(props)
                return
            nodes[nid] = {
                "id": nid,
                "type": ntype,
                "label": label,
                "properties": props,
                "coords": coords,
                "civilization_score": _calc_civilization_score(coords),
            }

        def add_edge(src, tgt, etype, **props):
            if src not in nodes or tgt not in nodes:
                return
            edges.append({
                "source": src,
                "target": tgt,
                "type": etype,
                "properties": props,
            })

        # ---- 1. Question Center: Q → H → E → D ----
        qc_dir = WORKSPACE / "02_MEMORY" / "question_center"
        try:
            questions = []
            hypotheses = []
            experiments = []
            decisions = []

            # 先读数据
            q_file = qc_dir / "questions.json"
            if q_file.exists():
                questions = json.loads(q_file.read_text(encoding="utf-8"))
            h_file = qc_dir / "hypotheses.json"
            if h_file.exists():
                hypotheses = json.loads(h_file.read_text(encoding="utf-8"))
            e_file = qc_dir / "experiments.json"
            if e_file.exists():
                experiments = json.loads(e_file.read_text(encoding="utf-8"))
            d_file = qc_dir / "decisions.json"
            if d_file.exists():
                decisions = json.loads(d_file.read_text(encoding="utf-8"))

            # 第一遍：加所有节点
            for q in questions:
                qid = q.get("qid", "")
                if qid:
                    add_node(qid, "question", q.get("question", "")[:60],
                             status=q.get("status", "unknown"),
                             priority=q.get("priority", "P2"),
                             source=q.get("source", ""),
                             created_at=q.get("created_at", ""))
            for h in hypotheses:
                hid = h.get("hid", "")
                if hid:
                    add_node(hid, "hypothesis", h.get("hypothesis", "")[:60],
                             qid=h.get("qid", ""),
                             confidence=h.get("confidence", 0),
                             status=h.get("status", "proposed"))
            for e in experiments:
                eid = e.get("eid", "")
                if eid:
                    add_node(eid, "experiment", e.get("name", "")[:60],
                             hid=e.get("hid", ""),
                             status=e.get("status", "running"),
                             evidence_count=len(e.get("evidence_collected", [])))
            for d in decisions:
                did = d.get("did", "")
                if did:
                    add_node(did, "decision", d.get("decision", "")[:60],
                             qid=d.get("qid", ""),
                             outcome=d.get("outcome", ""))

            # 第二遍：加所有边
            for q in questions:
                qid = q.get("qid", "")
                if not qid:
                    continue
                for hid in q.get("hypotheses", []):
                    add_edge(qid, hid, "has_hypothesis")
                for did in q.get("decisions", []):
                    add_edge(qid, did, "has_decision")
            for h in hypotheses:
                hid = h.get("hid", "")
                if not hid:
                    continue
                for eid in h.get("experiments", []):
                    add_edge(hid, eid, "has_experiment")
            for e in experiments:
                eid = e.get("eid", "")
                hid = e.get("hid", "")
                if eid and hid:
                    add_edge(hid, eid, "has_experiment")
        except Exception as e:
            print(f"  Question Center graph error: {e}")

        # ---- 2. Capability Graph ----
        try:
            from local_miner import CAPABILITY_GRAPH, MODELS
            for cap, info in CAPABILITY_GRAPH.items():
                cap_id = f"CAP:{cap}"
                add_node(cap_id, "capability", cap,
                         desc=info.get("desc", ""),
                         requires=info.get("requires", []))
                # Capability → Capability (requires)
                for sub_cap in info.get("requires", []):
                    sub_id = f"CAP:{sub_cap}"
                    add_edge(cap_id, sub_id, "requires")

            # Provider / Model → Capability
            for model_name, info in MODELS.items():
                prov_id = f"PROV:{model_name}"
                add_node(prov_id, "provider", model_name,
                         provider=info.get("provider", ""),
                         priority=info.get("priority", 99))
                for cap in info.get("capabilities", []):
                    cap_id = f"CAP:{cap}"
                    add_edge(prov_id, cap_id, "provides")
        except Exception as e:
            print(f"  Capability graph error: {e}")

        # ---- 3. Constraints ----
        constraints_path = WORKSPACE / "constraints.json"
        try:
            if constraints_path.exists():
                constraints = json.loads(constraints_path.read_text(encoding="utf-8"))
                for c in constraints.get("constraints", []):
                    cid = c.get("id", "")
                    if not cid:
                        continue
                    add_node(cid, "constraint", c.get("name", ""),
                             severity=c.get("severity", ""),
                             source=c.get("source", ""),
                             file_ref=c.get("file_ref", ""))
        except Exception as e:
            print(f"  Constraint graph error: {e}")

        # ---- 4. Protocols (04_PROTOCOLS/*.py) ----
        proto_dir = WORKSPACE / "04_PROTOCOLS"
        try:
            for pf in proto_dir.glob("*.py"):
                if pf.name.startswith("__"):
                    continue
                stem = pf.stem
                proto_id = f"PROTO:{stem}"
                ptype = _get_protocol_type(pf)
                content = pf.read_text(encoding="utf-8", errors="ignore")
                # 先加节点（后面 add_edge 需要）
                add_node(proto_id, "protocol", stem, type=ptype)
                # 提取 Implements 标记
                implements = []
                for m in IMPLEMENTS_MARKER.finditer(content):
                    for cid_match in IMPLEMENTS_ID_EXTRACT.finditer(m.group(1)):
                        cid = cid_match.group(0).upper().replace("_", "-")
                        implements.append(cid)
                        add_edge(proto_id, cid, "implements")
                # 更新 implements 属性
                if implements:
                    nodes[proto_id]["properties"]["implements"] = implements
        except Exception as e:
            print(f"  Protocol graph error: {e}")

        # ---- 5. Memory Index (抽样 Top 概念) ----
        idx_path = WORKSPACE / "02_MEMORY" / "memory_index_latest.json"
        try:
            if idx_path.exists():
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                entries = idx.get("entries", [])
                # 只提取 Top 50 高引用概念，避免 2996 条记忆全塞进图
                concept_counts = defaultdict(int)
                concept_category = {}
                for entry in entries:
                    for concept in entry.get("related_concepts", []):
                        name = concept.get("name", "")
                        if len(name) <= 1:
                            continue
                        concept_counts[name] += concept.get("relevance", 0)
                        if name not in concept_category:
                            concept_category[name] = concept.get("category", "待分类")

                top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:50]
                for concept_name, rel_sum in top_concepts:
                    cid = f"CONCEPT:{concept_name}"
                    add_node(cid, "concept", concept_name,
                             relevance_sum=rel_sum,
                             category=concept_category.get(concept_name, "待分类"))

                # 用 memory_index 的总条目数做一个记忆组节点
                add_node("MEMORY_INDEX", "memory", f"Memory Index ({len(entries)} entries)",
                         total_entries=len(entries),
                         index_file=str(idx_path.relative_to(WORKSPACE)))
        except Exception as e:
            print(f"  Memory graph error: {e}")

        # ---- 6. Experience ----
        exp_json = WORKSPACE / "02_MEMORY" / "experience.json"
        exp_dir = WORKSPACE / "02_MEMORY" / "experience"
        try:
            exp_count = 0
            if exp_json.exists():
                exp_data = json.loads(exp_json.read_text(encoding="utf-8"))
                if isinstance(exp_data, list):
                    exp_count += len(exp_data)
                elif isinstance(exp_data, dict):
                    exp_count += len(exp_data.get("experiences", []))
            if exp_dir.exists():
                exp_count += len(list(exp_dir.glob("*.json")))

            add_node("EXP_POOL", "experience", f"Experience Pool ({exp_count} entries)",
                     count=exp_count,
                     dir_exists=exp_dir.exists())
        except Exception as e:
            print(f"  Experience graph error: {e}")

        # ---- 7. Workers (04_PROTOCOLS/*.py + 06_RUNTIME modules) ----
        try:
            WORKERS = [
                {"id": "WORKER:Heartbeat", "name": "Heartbeat", "capabilities": ["monitoring", "scheduling"],
                 "status": "running", "cost": "low", "priority": 1},
                {"id": "WORKER:AwarenessLoop", "name": "AwarenessLoop", "capabilities": ["observation", "pattern_detection"],
                 "status": "running", "cost": "medium", "priority": 2},
                {"id": "WORKER:QuestionEngine", "name": "QuestionEngine", "capabilities": ["question_generation", "abduction"],
                 "status": "running", "cost": "medium", "priority": 2},
                {"id": "WORKER:QuestionCenter", "name": "QuestionCenter", "capabilities": ["knowledge_management", "reasoning"],
                 "status": "running", "cost": "low", "priority": 2},
                {"id": "WORKER:MultiAgentDebate", "name": "MultiAgentDebate", "capabilities": ["debate", "decision_making"],
                 "status": "running", "cost": "high", "priority": 3},
                {"id": "WORKER:ExplorerV2", "name": "ExplorerV2", "capabilities": ["exploration", "discovery", "research"],
                 "status": "running", "cost": "high", "priority": 3},
                {"id": "WORKER:SelfEvolution", "name": "SelfEvolution", "capabilities": ["code_change", "adaptation"],
                 "status": "running", "cost": "high", "priority": 4},
                {"id": "WORKER:RoundTable", "name": "RoundTable", "capabilities": ["audit", "review"],
                 "status": "running", "cost": "medium", "priority": 4},
                {"id": "WORKER:ProviderHealth", "name": "ProviderHealth", "capabilities": ["health_check", "monitoring"],
                 "status": "running", "cost": "low", "priority": 2},
                {"id": "WORKER:EnvironmentSensor", "name": "EnvironmentSensor", "capabilities": ["observation", "sensing"],
                 "status": "running", "cost": "low", "priority": 1},
                {"id": "WORKER:LocalMiner", "name": "LocalMiner", "capabilities": ["code_analysis", "capability_graph"],
                 "status": "running", "cost": "medium", "priority": 2},
                {"id": "WORKER:CivilizationAuditor", "name": "CivilizationAuditor", "capabilities": ["audit", "graph_building"],
                 "status": "running", "cost": "medium", "priority": 3},
                {"id": "WORKER:StateGenerator", "name": "StateGenerator", "capabilities": ["state_reporting", "dashboard"],
                 "status": "running", "cost": "low", "priority": 2},
                {"id": "WORKER:TGPush", "name": "TGPush", "capabilities": ["notification", "messaging"],
                 "status": "running", "cost": "low", "priority": 2},
                {"id": "WORKER:RecoveryScanner", "name": "RecoveryScanner", "capabilities": ["recovery", "backup"],
                 "status": "running", "cost": "low", "priority": 2},
                {"id": "WORKER:Archivist", "name": "Archivist", "capabilities": ["memory_management", "preservation"],
                 "status": "running", "cost": "low", "priority": 2},
                {"id": "WORKER:ExperienceEngine", "name": "ExperienceEngine", "capabilities": ["experience_extraction", "learning"],
                 "status": "running", "cost": "medium", "priority": 3},
            ]

            for w in WORKERS:
                add_node(w["id"], "worker", w["name"],
                         capabilities=w["capabilities"],
                         status=w["status"],
                         cost=w["cost"],
                         priority=w["priority"])
                for cap in w["capabilities"]:
                    cap_id = f"CAP:{cap}"
                    add_edge(w["id"], cap_id, "depends_on")
        except Exception as e:
            print(f"  Worker graph error: {e}")

        # ---- 8. RFC ----
        rfc_dir = WORKSPACE / "RFC"
        try:
            if rfc_dir.exists():
                for rf in sorted(rfc_dir.glob("*.md")):
                    content = rf.read_text(encoding="utf-8", errors="ignore")
                    rfc_id_match = re.search(r'RFC[-_](\d+)', rf.name)
                    if rfc_id_match:
                        rid = f"RFC:{rfc_id_match.group(1)}"
                        title_match = re.search(r'#\s+(.+)', content)
                        title = title_match.group(1) if title_match else rf.stem
                        add_node(rid, "rfc", title[:60],
                                 filename=rf.name,
                                 path=str(rf.relative_to(WORKSPACE)))
        except Exception as e:
            print(f"  RFC graph error: {e}")

        # ---- 9. Tasks ----
        tasks_file = WORKSPACE / "02_MEMORY" / "tasks.md"
        try:
            if tasks_file.exists():
                content = tasks_file.read_text(encoding="utf-8")
                task_blocks = re.split(r'\n## ', content)
                for block in task_blocks:
                    tid_match = re.search(r'(TASK[-_]\d+)', block)
                    if tid_match:
                        tid = tid_match.group(1).upper()
                        title_match = re.search(r'^(.+?)(\n|\s|:)', block)
                        title = title_match.group(1).strip() if title_match else tid
                        status_match = re.search(r'Status:\s*(\w+)', block, re.IGNORECASE)
                        status = status_match.group(1) if status_match else "pending"
                        add_node(tid, "task", title[:60],
                                 status=status.lower())
        except Exception as e:
            print(f"  Task graph error: {e}")

        # ---- 10. Repository ----
        repos_path = WORKSPACE / "02_MEMORY" / "repos.json"
        try:
            if repos_path.exists():
                repos = json.loads(repos_path.read_text(encoding="utf-8"))
                for repo in repos.get("repos", []):
                    repo_id = f"REPO:{repo.get('name', '').replace('/', '_')}"
                    add_node(repo_id, "repository", repo.get("name", "")[:60],
                             url=repo.get("url", ""),
                             branch=repo.get("branch", ""),
                             last_sync=repo.get("last_sync", ""))
        except Exception as e:
            print(f"  Repository graph error: {e}")

        # ---- 统计 ----
        type_counts = defaultdict(int)
        edge_type_counts = defaultdict(int)
        for n in nodes.values():
            type_counts[n["type"]] += 1
        for e in edges:
            edge_type_counts[e["type"]] += 1

        # 计算图密度
        n = len(nodes)
        m = len(edges)
        max_edges = n * (n - 1) if n > 1 else 1
        density = round(m / max_edges * 100, 3) if n > 1 else 0

        # 找最连接的节点（PageRank 太复杂，用 degree）
        degree = defaultdict(int)
        for e in edges:
            degree[e["source"]] += 1
            degree[e["target"]] += 1
        top_connected = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:10]

        # 计算六维坐标统计和平均文明分数
        dim_stats = {}
        all_scores = []
        for n in nodes.values():
            coords = n.get("coords", {})
            score = n.get("civilization_score", 0)
            all_scores.append(score)
            for dim, val in coords.items():
                if dim not in dim_stats:
                    dim_stats[dim] = []
                dim_stats[dim].append(val)

        avg_scores = {}
        for dim, vals in dim_stats.items():
            avg_scores[dim] = round(sum(vals) / len(vals), 3)

        avg_civilization_score = round(sum(all_scores) / len(all_scores), 3) if all_scores else 0
        top_score_nodes = sorted(
            [(nid, n.get("civilization_score", 0)) for nid, n in nodes.items()],
            key=lambda x: x[1], reverse=True
        )[:10]

        graph = {
            "nodes": list(nodes.values()),
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "density_pct": density,
                "node_types": dict(type_counts),
                "edge_types": dict(edge_type_counts),
                "top_connected": [
                    {"id": nid, "degree": deg, "type": nodes.get(nid, {}).get("type", "?")}
                    for nid, deg in top_connected
                ],
                "dimension_weights": DIMENSION_WEIGHTS,
                "avg_dimension_scores": avg_scores,
                "avg_civilization_score": avg_civilization_score,
                "top_score_nodes": [
                    {"id": nid, "score": score, "type": nodes.get(nid, {}).get("type", "?"), "label": nodes.get(nid, {}).get("label", "")}
                    for nid, score in top_score_nodes
                ],
            },
        }

        print(f"  Graph: {len(nodes)} nodes, {len(edges)} edges, {density}% density")
        for ntype, cnt in type_counts.items():
            print(f"    {ntype}: {cnt}")
        print(f"  Top connected nodes:")
        for nid, deg in top_connected[:5]:
            ninfo = nodes.get(nid, {})
            print(f"    {nid} ({ninfo.get('type', '?')}): degree={deg}")

        return graph

    # ================================================================
    # 生成报告
    # ================================================================
    def generate_report(self) -> Dict[str, Any]:
        """生成文明健康报告"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")

        # 统计
        total_files = len(self._walk_files(WORKSPACE))

        # 重复文件统计
        dup_files_count = sum(d.get("count", 0) for d in self.duplicates)

        # 僵尸文件统计
        zombie_by_type = defaultdict(int)
        for z in self.zombies:
            zombie_by_type[z.get("type", "unknown")] += 1

        # 断链统计
        link_by_type = defaultdict(int)
        for m in self.missing_links:
            link_by_type[m.get("type", "unknown")] += 1

        # C-013: canonical path 违规统计
        canonical_violations = getattr(self, "canonical_violations", [])

        # C-014: 时间序列 retention 违规统计
        retention_violations = getattr(self, "retention_violations", [])

        # Memory Health
        memory_health = getattr(self, "memory_health", {})

        # Civilization Coverage
        coverage = getattr(self, "coverage", {})

        # Civilization Graph
        graph = getattr(self, "graph", {})

        # DNA Compliance
        dna_compliance = self._scan_dna_compliance()

        # 健康分数（0-100）
        # 重复越多扣分，僵尸越多扣分，断链越多扣分，canonical 违规扣分，retention 违规扣分
        health_score = 100
        health_score -= min(20, len(self.duplicates) * 2)              # 重复最多扣20
        health_score -= min(20, len(self.zombies) * 2)                 # 僵尸最多扣20
        health_score -= min(15, len(self.missing_links) * 5)           # 断链最多扣15
        health_score -= min(15, len(canonical_violations) * 2)         # C-013 最多扣15
        health_score -= min(10, len(retention_violations) * 3)         # C-014 最多扣10
        # 记忆健康也影响文明健康
        mem_health_score = memory_health.get("health_score", 100)
        health_score -= min(20, int((100 - mem_health_score) * 0.2))   # 记忆健康最多影响20分
        health_score = max(0, health_score)

        report = {
            "timestamp": now.isoformat(),
            "date": date_str,
            "stats": {
                "total_files": total_files,
                "duplicate_clusters": len(self.duplicates),
                "duplicate_files": dup_files_count,
                "zombie_files": len(self.zombies),
                "zombie_by_type": dict(zombie_by_type),
                "missing_links": len(self.missing_links),
                "link_by_type": dict(link_by_type),
                "canonical_violations": len(canonical_violations),
                "retention_violations": len(retention_violations),
                "memory_health": memory_health.get("health_score", 0),
                "civilization_coverage": coverage.get("_overall", {}).get("score", 0),
                "health_score": health_score,
            },
            "duplicates": self.duplicates[:50],  # 限制输出
            "zombies": self.zombies[:100],
            "missing_links": self.missing_links[:50],
            "canonical_violations": canonical_violations[:30],
            "retention_violations": retention_violations[:30],
            "memory_health": memory_health,
            "coverage": coverage,
            "graph": graph,
            "dna_compliance": dna_compliance,
        }

        # 保存 JSON
        json_path = AUDIT_DIR / f"audit_{date_str}.json"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

        # 保存独立的 civilization_graph.json（供其他模块读取）
        if graph:
            graph_path = WORKSPACE / "02_MEMORY" / "civilization_graph.json"
            graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
            print(f"  [AUDIT] Civilization Graph saved to {graph_path}")

        # 生成 Markdown
        self._generate_markdown(report, date_str)

        return report

    def _scan_dna_compliance(self) -> Dict[str, Any]:
        """扫描 DNA 合规性（Civilization Entry DNA）"""
        try:
            sys.path.insert(0, str(WORKSPACE / "04_PROTOCOLS"))
            from civilization_entry_dna import scan_dna_compliance
            result = scan_dna_compliance(str(WORKSPACE / "02_MEMORY"))
            result["protocols"] = scan_dna_compliance(str(WORKSPACE / "04_PROTOCOLS"))
            return result
        except Exception as e:
            return {"error": str(e)}

    def _generate_markdown(self, report: Dict[str, Any], date_str: str):
        """生成 Markdown 报告"""
        s = report["stats"]
        health = s["health_score"]
        health_emoji = "🟢" if health >= 80 else "🟡" if health >= 50 else "🔴"

        lines = [
            f"# 文明健康报告 {date_str}",
            "",
            f"## 总览",
            "",
            f"{health_emoji} **健康分数: {health}/100**",
            "",
            f"- 文件总数: {s['total_files']}",
            f"- 重复集群: {s['duplicate_clusters']} (含 {s['duplicate_files']} 个文件)",
            f"- 僵尸文件: {s['zombie_files']}",
            f"- 断链: {s['missing_links']}",
            f"- 记忆健康: {s.get('memory_health', 0)}/100",
            f"- 文明接管率: {s.get('civilization_coverage', 0)}%",
            "",
        ]

        # Civilization Coverage
        cov = report.get("coverage", {})
        overall = cov.get("_overall", {})
        if overall:
            lines.append("## 文明接管率")
            lines.append("")
            cov_score = overall.get("score", 0)
            cov_emoji = "🟢" if cov_score >= 80 else "🟡" if cov_score >= 50 else "🔴"
            lines.append(f"{cov_emoji} **{cov_score}%** — {overall.get('verdict', '')}")
            lines.append("")
            lines.append("| 维度 | 分数 | 权重 | 详情 |")
            lines.append("|------|------|------|------|")
            dim_names = {
                "workspace_coverage": "Workspace Coverage",
                "memory_indexed": "Memory Indexed",
                "session_recovery": "Session Recovery",
                "protocol_coverage": "Protocol Coverage",
                "constraint_implementation": "Constraint Implementation",
                "experience_indexed": "Experience Indexed",
                "provider_health": "Provider Health",
            }
            for key, data in cov.items():
                if key == "_overall":
                    continue
                name = dim_names.get(key, key)
                score = data.get("score", 0)
                weight = data.get("weight", 0)
                # 取第一个存在的数字字段作为详情
                detail = ""
                for f in ["total_files", "total_memories", "total_constraints",
                           "total_providers", "total_runtime_protos",
                           "session_files_found", "experience_files"]:
                    if f in data and data[f]:
                        detail = str(data[f])
                        break
                lines.append(f"| {name} | {score}% | {weight} | {detail} |")
            lines.append("")

        # Memory Health
        mh = report.get("memory_health", {})
        if mh.get("index_exists"):
            lines.append("## 记忆健康度")
            lines.append("")
            mh_score = mh.get("health_score", 0)
            mh_emoji = "🟢" if mh_score >= 80 else "🟡" if mh_score >= 50 else "🔴"
            lines.append(f"{mh_emoji} **记忆健康: {mh_score}/100**")
            lines.append("")
            lines.append(f"- 记忆总数: {mh.get('total_memories', 0)}")
            lines.append(f"- 死亡记忆 (access=0): {mh.get('dead_memory_count', 0)} ({mh.get('dead_memory_pct', 0)}%)")
            lines.append(f"- 概念总数: {len(mh.get('concepts', []))}")
            lines.append(f"- 孤儿概念 (只引用1次): {mh.get('orphan_concept_count', 0)}")
            lines.append(f"- 重复标题: {mh.get('duplicate_title_count', 0)}")
            lines.append("")

            # 类型分布
            type_dist = mh.get("type_distribution", {})
            if type_dist:
                lines.append("### 记忆类型分布")
                lines.append("")
                for t, cnt in sorted(type_dist.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"- {t}: {cnt}")
                lines.append("")

            # Top 10 高引用概念
            top_concepts = mh.get("top_concepts", [])
            if top_concepts:
                lines.append("### Top 10 高价值概念")
                lines.append("")
                lines.append("| 概念 | 引用数 | 分类 | 平均关联度 |")
                lines.append("|------|--------|------|-----------|")
                for c in top_concepts[:10]:
                    lines.append(f"| {c['concept']} | {c['ref_count']} | {c.get('category', '?')} | {c.get('avg_relevance', 0)} |")
                lines.append("")

        # Civilization Graph
        graph = report.get("graph", {})
        graph_stats = graph.get("stats", {})
        if graph_stats and graph_stats.get("total_nodes", 0) > 0:
            lines.append("## 文明图谱 (Civilization Graph)")
            lines.append("")
            n_nodes = graph_stats.get("total_nodes", 0)
            n_edges = graph_stats.get("total_edges", 0)
            density = graph_stats.get("density_pct", 0)
            lines.append(f"**{n_nodes}** 节点 · **{n_edges}** 边 · 密度 **{density}%**")
            lines.append("")

            # 节点类型分布
            node_types = graph_stats.get("node_types", {})
            if node_types:
                lines.append("### 节点类型")
                lines.append("")
                lines.append("| 类型 | 数量 |")
                lines.append("|------|------|")
                for ntype, cnt in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"| {ntype} | {cnt} |")
                lines.append("")

            # 边类型分布
            edge_types = graph_stats.get("edge_types", {})
            if edge_types:
                lines.append("### 关系类型")
                lines.append("")
                lines.append("| 关系 | 数量 |")
                lines.append("|------|------|")
                for etype, cnt in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"| {etype} | {cnt} |")
                lines.append("")

            # Top 连接节点
            top_conn = graph_stats.get("top_connected", [])
            if top_conn:
                lines.append("### Top 10 核心节点")
                lines.append("")
                lines.append("| 节点 | 类型 | 连接度 |")
                lines.append("|------|------|--------|")
                for n in top_conn[:10]:
                    lines.append(f"| {n['id']} | {n['type']} | {n['degree']} |")
                lines.append("")

        # DNA Compliance
        dna = report.get("dna_compliance", {})
        if dna and not dna.get("error"):
            lines.append("## DNA 合规 (Civilization Entry DNA)")
            lines.append("")
            mem_total = dna.get("total", 0)
            mem_has = dna.get("has_dna", 0)
            mem_pct = (mem_has / mem_total * 100) if mem_total > 0 else 0
            lines.append(f"- 02_MEMORY: {mem_has}/{mem_total} ({mem_pct:.0f}%)")
            proto = dna.get("protocols", {})
            if proto:
                p_total = proto.get("total", 0)
                p_has = proto.get("has_dna", 0)
                p_pct = (p_has / p_total * 100) if p_total > 0 else 0
                lines.append(f"- 04_PROTOCOLS: {p_has}/{p_total} ({p_pct:.0f}%)")
            by_type = dna.get("by_type", {})
            if by_type:
                lines.append("")
                lines.append("### 已标记类型分布")
                lines.append("")
                for t, cnt in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"- {t}: {cnt}")
            lines.append("")

        # 重复文件
        if report["duplicates"]:
            lines.append("## 重复资产")
            lines.append("")
            lines.append("| 基础名 | 变体数 | 最新文件 | 建议 |")
            lines.append("|--------|--------|----------|------|")
            for d in report["duplicates"][:20]:
                if d.get("type") == "identical_content":
                    lines.append(f"| (内容相同) | {d['count']} | {d['files'][0]} | 内容完全重复 |")
                else:
                    files = d.get("files", [])
                    latest = files[0]["path"] if files else "?"
                    lines.append(f"| {d['base_name']} | {d['count']} | {latest} | {d.get('recommendation', '')} |")
            lines.append("")

        # 僵尸文件
        if report["zombies"]:
            lines.append("## 僵尸文件")
            lines.append("")
            zbt = s.get("zombie_by_type", {})
            type_names = {
                "suspected_deprecated": "疑似废弃（文件名含 _old/_tmp 等）",
                "unreferenced_module": "未被引用的模块",
                "unreferenced_config": "未被引用的配置",
            }
            for t, count in zbt.items():
                lines.append(f"- {type_names.get(t, t)}: {count} 个")
            lines.append("")
            lines.append("| 文件 | 类型 | 原因 |")
            lines.append("|------|------|------|")
            for z in report["zombies"][:30]:
                lines.append(f"| {z['path']} | {z.get('type', '?')} | {z.get('reason', '')} |")
            lines.append("")

        # 断链
        if report["missing_links"]:
            lines.append("## 断链检测")
            lines.append("")
            lbt = s.get("link_by_type", {})
            type_names = {
                "declared_but_missing": "声明了但文件不存在",
                "protocol_not_wired": "协议未接入 Heartbeat",
                "constraint_not_implemented": "约束未在代码中实现",
                "readme_feature_missing": "README 提到但代码无实现",
            }
            for t, count in lbt.items():
                lines.append(f"- {type_names.get(t, t)}: {count} 个")
            lines.append("")
            lines.append("| 目标 | 类型 | 原因 |")
            lines.append("|------|------|------|")
            for m in report["missing_links"][:20]:
                lines.append(f"| {m.get('target', '?')} | {m.get('type', '?')} | {m.get('reason', '')} |")
            lines.append("")

        # 建议
        lines.append("## 建议行动")
        lines.append("")
        if s["duplicate_clusters"] > 0:
            lines.append(f"1. 清理 {s['duplicate_files']} 个重复文件（保留最新版本）")
        if s["zombie_files"] > 0:
            lines.append(f"2. 清理或归档 {s['zombie_files']} 个僵尸文件")
        if s["missing_links"] > 0:
            lines.append(f"3. 修复 {s['missing_links']} 个断链（或更新文档）")
        if health >= 80:
            lines.append("4. 文明健康度良好，继续保持")
        lines.append("")

        md_path = AUDIT_DIR / f"audit_{date_str}.md"
        md_path.write_text("\n".join(lines), encoding="utf-8")

    # ================================================================
    # 运行全部检测
    # ================================================================
    def run_all(self) -> Dict[str, Any]:
        """运行全部七项检测"""
        print("=" * 60)
        print("AUD-001: Civilization Auditor")
        print("=" * 60)

        self.scan_duplicates()
        self.scan_zombies()
        self.scan_missing_links()
        # C-013: canonical path 检测
        self.canonical_violations = self.scan_canonical_paths()
        # C-014: 时间序列 retention 检测
        self.retention_violations = self.scan_time_series_retention()
        # Memory Health: 记忆健康度
        self.memory_health = self.scan_memory_health()
        # Civilization Coverage: 文明资产接管率
        self.coverage = self.scan_coverage()
        # Civilization Graph: 文明图谱
        self.graph = self.scan_graph()

        report = self.generate_report()

        print(f"\n{'='*60}")
        print(f"审计完成: 健康分数 {report['stats']['health_score']}/100")
        print(f"  重复: {report['stats']['duplicate_clusters']} 集群")
        print(f"  僵尸: {report['stats']['zombie_files']} 个")
        print(f"  断链: {report['stats']['missing_links']} 个")
        print(f"  C-013 canonical 违规: {report['stats']['canonical_violations']} 个")
        print(f"  C-014 retention 违规: {report['stats']['retention_violations']} 个")
        cov = report.get("coverage", {}).get("_overall", {})
        graph_stats = report.get("graph", {}).get("stats", {})
        print(f"  文明接管率: {cov.get('score', 0)}% — {cov.get('verdict', '')}")
        print(f"  文明图谱: {graph_stats.get('total_nodes', 0)} nodes, {graph_stats.get('total_edges', 0)} edges")
        print(f"{'='*60}")

        return report


def main():
    parser = argparse.ArgumentParser(description="AUD-001 Civilization Auditor")
    parser.add_argument("--duplicates", action="store_true", help="只扫描重复")
    parser.add_argument("--zombies", action="store_true", help="只扫描僵尸")
    parser.add_argument("--links", action="store_true", help="只扫描断链")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    auditor = CivilizationAuditor()

    if args.duplicates:
        auditor.scan_duplicates()
        print(json.dumps(auditor.duplicates, ensure_ascii=False, indent=2, default=str))
    elif args.zombies:
        auditor.scan_zombies()
        print(json.dumps(auditor.zombies, ensure_ascii=False, indent=2, default=str))
    elif args.links:
        auditor.scan_missing_links()
        print(json.dumps(auditor.missing_links, ensure_ascii=False, indent=2, default=str))
    else:
        report = auditor.run_all()
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
