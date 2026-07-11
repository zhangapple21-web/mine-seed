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

# 代码文件扩展名
CODE_EXTENSIONS = {".py", ".js", ".ts", ".sh", ".bat"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".sh", ".tpl"}
DOC_EXTENSIONS = {".md", ".rst", ".txt"}


class CivilizationAuditor:
    """文明审计器 — 三合一检测"""

    def __init__(self):
        self.duplicates: List[Dict[str, Any]] = []
        self.zombies: List[Dict[str, Any]] = []
        self.missing_links: List[Dict[str, Any]] = []
        self.stats: Dict[str, Any] = {}

    def _walk_files(self, root: Path, extensions: Set[str] = None) -> List[Path]:
        """遍历文件，支持扩展名过滤"""
        files = []
        for root_dir, dirs, filenames in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
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
        """
        print("[AUDIT] Scanning zombies...")

        zombies = []

        # a) 疑似废弃文件（文件名特征）
        zombie_patterns = re.compile(r'[_-](old|tmp|test|draft|wip|deprecated|unused|dead|copy|backup)\d*$', re.IGNORECASE)
        all_code_files = self._walk_files(WORKSPACE, CODE_EXTENSIONS)

        for fpath in all_code_files:
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
        py_files = [f for f in all_code_files if f.suffix == ".py"]
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
        json_files = self._walk_files(WORKSPACE, {".json"})
        json_names = {f.stem: f for f in json_files if f.stem not in ("package", "tsconfig", "launch", "settings")}

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
        heartbeat_path = WORKSPACE / "04_PROTOCOLS" / "heartbeat.py"
        protocol_dir = WORKSPACE / "04_PROTOCOLS"

        if heartbeat_path.exists() and protocol_dir.exists():
            heartbeat_content = heartbeat_path.read_text(encoding="utf-8")

            for proto_file in protocol_dir.glob("*.py"):
                if proto_file.name in ("heartbeat.py", "__init__.py"):
                    continue
                module_name = proto_file.stem
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
        constraints_path = WORKSPACE / "constraints.json"
        if constraints_path.exists():
            constraints = json.loads(constraints_path.read_text(encoding="utf-8"))
            constraint_ids = [c.get("id", "") for c in constraints.get("constraints", [])]

            # 收集所有代码文本
            all_code = ""
            for fpath in self._walk_files(WORKSPACE, CODE_EXTENSIONS):
                try:
                    all_code += fpath.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    pass

            for cid in constraint_ids:
                if cid and cid not in all_code:
                    missing_links.append({
                        "type": "constraint_not_implemented",
                        "source": "constraints.json",
                        "target": cid,
                        "reason": f"约束 {cid} 在代码中未被引用",
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

        # 健康分数（0-100）
        # 重复越多扣分，僵尸越多扣分，断链越多扣分
        health_score = 100
        health_score -= min(30, len(self.duplicates) * 3)  # 重复最多扣30
        health_score -= min(30, len(self.zombies) * 2)     # 僵尸最多扣30
        health_score -= min(40, len(self.missing_links) * 5)  # 断链最多扣40
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
                "health_score": health_score,
            },
            "duplicates": self.duplicates[:50],  # 限制输出
            "zombies": self.zombies[:100],
            "missing_links": self.missing_links[:50],
        }

        # 保存 JSON
        json_path = AUDIT_DIR / f"audit_{date_str}.json"
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

        # 生成 Markdown
        self._generate_markdown(report, date_str)

        return report

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
            "",
        ]

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
        """运行全部三项检测"""
        print("=" * 60)
        print("AUD-001: Civilization Auditor")
        print("=" * 60)

        self.scan_duplicates()
        self.scan_zombies()
        self.scan_missing_links()

        report = self.generate_report()

        print(f"\n{'='*60}")
        print(f"审计完成: 健康分数 {report['stats']['health_score']}/100")
        print(f"  重复: {report['stats']['duplicate_clusters']} 集群")
        print(f"  僵尸: {report['stats']['zombie_files']} 个")
        print(f"  断链: {report['stats']['missing_links']} 个")
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
