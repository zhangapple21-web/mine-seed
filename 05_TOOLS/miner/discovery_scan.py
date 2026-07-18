#!/usr/bin/env python3
"""
Discovery Scanner — 每日发现协议首次运行

扫描方向（云端可执行）：
1. mine-seed 仓库未开采部分
2. claw-soul 仓库未开采部分

扫描方向（需本地环境）：
3. TG 收藏夹增量
4. 本地文件系统

Stop Condition：
- 只记录不实现
- 不超出已知边界继续挖掘
- 产出清单，不执行任何操作

用法：
  python3 discovery_scan.py
"""

import os
import json
from datetime import datetime
from pathlib import Path

MINE_SEED = Path(os.environ.get("MINE_SEED", "/workspace/fengzi-repos/mine-seed"))
CLAW_SOUL = Path(os.environ.get("CLAW_SOUL", "/workspace/fengzi-repos/claw-soul"))
OUTPUT_DIR = MINE_SEED / "02_MEMORY" / "discovery_queue"


def scan_repo(repo_path: Path, repo_name: str, known_patterns: list) -> dict:
    """扫描仓库，找出未被已知模式覆盖的文件/目录"""
    findings = {
        "repo": repo_name,
        "path": str(repo_path),
        "unindexed_dirs": [],
        "unindexed_files": [],
        "orphan_files": [],  # 没有在任何索引中引用的文件
    }

    if not repo_path.exists():
        findings["error"] = "路径不存在"
        return findings

    # 收集所有文件
    all_files = []
    all_dirs = []
    for root, dirs, files in os.walk(repo_path):
        # 跳过 .git
        dirs[:] = [d for d in dirs if d != '.git']
        rel_root = Path(root).relative_to(repo_path)
        for d in dirs:
            all_dirs.append(str(rel_root / d))
        for f in files:
            all_files.append(str(rel_root / f))

    # 检查哪些不在已知模式中
    for d in all_dirs:
        if not any(p in d for p in known_patterns):
            if d not in findings["unindexed_dirs"]:
                findings["unindexed_dirs"].append(d)

    for f in all_files:
        if not any(p in f for p in known_patterns):
            if f not in findings["unindexed_files"]:
                findings["unindexed_files"].append(f)

    return findings


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")

    # 已知模式（已在文明索引中覆盖的）
    mine_seed_known = [
        "00_ROOT",
        "01_AGENTS",
        "01_IDENTITY",
        "02_LEARNING",
        "02_MEMORY",
        "02_modules",
        "03_DATA",
        "04_CONSTRAINT",
        "04_PROTOCOLS",
        "05_TOOLS",
        "06_RUNTIME",
        "07_GUARDIAN",
        "V6_RFC",
        "WORKERS",
        "cloud",
        "daily",
        "docs",
        "dashboard",
        "advisor",
        "aether_capsule",
        "candidate_theories",
        "cases",
        "charters",
        "constraint_proposal",
        "daily_archaeology",
        "decisions",
        "binary_sense_reports",
        "ARCHITECTURE.md",
        "README.md",
        "LOCAL_SETUP_CHECKLIST.md",
        "CIVILIZATION.md",
        "AGENTS.md",
        "CURRENT_STATE.md",
        "NEW_COMPUTER_RESURRECTION.md",
        "constraints.json",
        "CIVILIZATION",
    ]

    claw_soul_known = [
        "01_IDENTITY",
        "02_MEMORY",
        "03_RULES",
        "04_CREDENTIALS",
        "05_PROJECTS",
        "06_SCRIPTS",
        "07_OPERATIONS",
        "lab_02",
        "README.md",
    ]

    # 扫描 mine-seed
    mine_findings = scan_repo(MINE_SEED, "mine-seed", mine_seed_known)

    # 扫描 claw-soul
    claw_findings = scan_repo(CLAW_SOUL, "claw-soul", claw_soul_known)

    # 生成清单
    report = {
        "scan_date": datetime.now().isoformat(),
        "mission_id": "AUM-MISSION-DAILY-001",
        "stop_condition": "只记录不实现，不超出已知边界",
        "findings": [mine_findings, claw_findings],
        "next_actions": [],
    }

    # 提取关键发现
    for finding in [mine_findings, claw_findings]:
        repo = finding["repo"]
        for d in finding["unindexed_dirs"][:10]:  # 最多10个
            report["next_actions"].append({
                "type": "investigate_dir",
                "repo": repo,
                "path": d,
                "reason": "未被文明索引覆盖",
            })
        for f in finding["unindexed_files"][:10]:
            report["next_actions"].append({
                "type": "investigate_file",
                "repo": repo,
                "path": f,
                "reason": "未被文明索引覆盖",
            })

    # 保存
    json_file = OUTPUT_DIR / f"discovery_{today}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Markdown 摘要
    md_lines = [
        f"# Discovery Report — {datetime.now().strftime('%Y-%m-%d')}",
        "",
        f"> Mission: AUM-MISSION-DAILY-001",
        f"> Stop Condition: 只记录不实现，不超出已知边界",
        "",
        "---",
        "",
        "## 扫描范围",
        "",
        "- ✅ mine-seed 仓库（云端）",
        "- ✅ claw-soul 仓库（云端）",
        "- ⏳ TG 收藏夹（需本地环境）",
        "- ⏳ 本地文件系统（需本地环境）",
        "",
        "---",
        "",
        "## 关键发现",
        "",
    ]

    for finding in [mine_findings, claw_findings]:
        repo = finding["repo"]
        dirs = finding.get("unindexed_dirs", [])
        files = finding.get("unindexed_files", [])
        md_lines.extend([
            f"### {repo}",
            "",
            f"- 未索引目录: {len(dirs)}",
            f"- 未索引文件: {len(files)}",
            "",
        ])
        if dirs:
            md_lines.append("**未索引目录（前10）**:")
            for d in dirs[:10]:
                md_lines.append(f"- `{d}`")
            md_lines.append("")
        if files:
            md_lines.append("**未索引文件（前10）**:")
            for f in files[:10]:
                md_lines.append(f"- `{f}`")
            md_lines.append("")

    md_lines.extend([
        "---",
        "",
        "## 下一步（待 Governor/本地 CODE 处理）",
        "",
    ])

    for action in report["next_actions"][:15]:
        md_lines.append(f"- [{action['type']}] `{action['repo']}/{action['path']}` — {action['reason']}")

    md_lines.extend([
        "",
        "---",
        "",
        "*本报告由 Discovery Scanner 自动生成。只记录，不执行。*",
    ])

    md_file = OUTPUT_DIR / f"discovery_{today}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))

    print(f"Discovery 完成:")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")
    print(f"  未索引项: mine-seed={len(mine_findings['unindexed_dirs'])+len(mine_findings['unindexed_files'])}, claw-soul={len(claw_findings['unindexed_dirs'])+len(claw_findings['unindexed_files'])}")


if __name__ == "__main__":
    main()
