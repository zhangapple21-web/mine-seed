"""
Ecology Observer (v1)

目标：
- 观察城市运作痕迹（daily 记录 + git 变更）
- 识别长期重复出现但无法被现有角色覆盖的生态位
- 生成候选清单与“居民诞生申请”草案（半自动见证：提交 PR 由治理层合并）

重要限制：
- 本脚本不会创建新居民，只会输出提名材料
- 不会读取或写入任何密钥（.secrets 为忽略目录）
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DAILY_DIR = os.path.join(REPO_ROOT, "02_MEMORY", "recent_memory", "daily")
ECO_DIR = os.path.join(REPO_ROOT, "02_MEMORY", "recent_memory", "ecology")
NOM_DIR = os.path.join(ECO_DIR, "nominations")
TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "ecology_taxonomy.json")


def _run_git(args: List[str]) -> str:
    git = shutil.which("git") or shutil.which("git.exe")
    if not git:
        # 常见安装位置兜底（Windows）
        candidates = [
            r"C:\Program Files\Git\cmd\git.exe",
            r"C:\Program Files\Git\bin\git.exe",
            r"C:\Program Files (x86)\Git\cmd\git.exe",
            r"C:\Program Files (x86)\Git\bin\git.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                git = c
                break
    if not git:
        raise RuntimeError("git executable not found in PATH (or common locations)")

    out = subprocess.check_output([git, *args], cwd=REPO_ROOT, stderr=subprocess.STDOUT)
    return out.decode("utf-8", errors="ignore")


def _safe_mkdir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def _read_text(path: str, max_bytes: int = 500_000) -> str:
    with open(path, "rb") as f:
        data = f.read(max_bytes)
    return data.decode("utf-8", errors="ignore")


def _load_taxonomy() -> dict:
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _date_days_ago(days: int) -> str:
    return (dt.datetime.now() - dt.timedelta(days=days)).strftime("%Y-%m-%d")


def _list_daily_files(days: int) -> List[str]:
    if not os.path.isdir(DAILY_DIR):
        return []
    files = [os.path.join(DAILY_DIR, f) for f in os.listdir(DAILY_DIR) if f.endswith(".md")]
    files.sort(reverse=True)
    # 粗略：只取最近 N 个文件（文件命名不完全统一，但足够用于观测）
    return files[: max(0, days)]


def _git_changed_paths_since(days: int) -> List[str]:
    """
    收集最近 N 天内 git commit 涉及的文件路径（用于观察“持续发生的工作流”）。
    """
    since = f"--since={days}.days"
    raw = _run_git(["log", since, "--name-only", "--pretty=format:"])
    paths = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # 忽略本地敏感目录
        if line.startswith(".secrets/") or "/.secrets/" in line:
            continue
        paths.append(line.replace("\\", "/"))
    return paths


def _group_paths(paths: List[str]) -> Dict[str, int]:
    """
    将路径归类为“工作流前缀”：
    - 05_TOOLS/<tool>
    - 03_DATA/<domain>
    - 03_RESEARCH/<domain>
    - 04_PROTOCOLS
    - docs/<area>
    其余归为 top-level。
    """
    counts: Dict[str, int] = {}
    for p in paths:
        parts = p.split("/")
        if not parts:
            continue
        prefix = parts[0]
        if prefix in {"05_TOOLS", "03_DATA", "03_RESEARCH", "docs"} and len(parts) >= 2:
            key = f"{prefix}/{parts[1]}"
        else:
            key = prefix
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def _count_signal(text: str, signals: List[str]) -> int:
    t = text.lower()
    total = 0
    for s in signals:
        if not s:
            continue
        total += len(re.findall(re.escape(s.lower()), t))
    return total


@dataclass
class Candidate:
    slug: str
    name: str
    occurrences_30d: int
    evidence_paths: List[str]
    stable_input: str
    stable_output_paths: List[str]
    memory_deposit_paths: List[str]
    protocol_hint: str
    covered_by_existing_roles: List[str]
    ecological_need: bool
    replaceable_by_existing_roles: bool
    status: str  # NOT_YET / ELIGIBLE / REJECTED


def _evaluate_candidate(
    *,
    slug: str,
    name: str,
    occurrences: int,
    evidence_paths: List[str],
    stable_input_hint: str,
    stable_output_paths: List[str],
    memory_deposit_paths: List[str],
    covered_by_existing_roles: List[str],
) -> Candidate:
    """
    以“可自动验证的证据”为主，给出保守判断：
    - 没有稳定输出/记忆沉积 => NOT_YET
    - 有输出 + 记忆沉积 + 高出现频次 => 可进入 ELIGIBLE（仍需治理层见证）
    """
    # 条件 3/4/5 的“自动证据”仅做最小验证：路径存在即可
    stable_output_ok = all(os.path.exists(os.path.join(REPO_ROOT, p)) for p in stable_output_paths) if stable_output_paths else False
    memory_ok = any(os.path.exists(os.path.join(REPO_ROOT, p)) for p in memory_deposit_paths) if memory_deposit_paths else False

    # 生态必要性：高频 + 输出 + 记忆
    ecological_need = bool(occurrences >= 10 and stable_output_ok and memory_ok)

    # 可替代性：如果明确被现有角色覆盖，则倾向可替代；否则默认不可替代未知 -> False
    replaceable = bool(covered_by_existing_roles)

    # 状态：仅当“生态必要性”且“不可被现有角色覆盖”时，才进入 ELIGIBLE
    # 若已被现有角色覆盖 => REJECTED（已有覆盖，无需新增居民）
    # 其他情况暂标记 NOT_YET（持续观察，等待证据累积）
    if ecological_need and not replaceable:
        status = "ELIGIBLE"
    elif replaceable:
        status = "REJECTED"
    else:
        status = "NOT_YET"

    return Candidate(
        slug=slug,
        name=name,
        occurrences_30d=occurrences,
        evidence_paths=evidence_paths[:20],
        stable_input=stable_input_hint or "unknown",
        stable_output_paths=stable_output_paths,
        memory_deposit_paths=memory_deposit_paths,
        protocol_hint="(needs protocol or reuse existing)",
        covered_by_existing_roles=covered_by_existing_roles,
        ecological_need=ecological_need,
        replaceable_by_existing_roles=replaceable,
        status=status,
    )


def build_candidates(days: int) -> List[Candidate]:
    tax = _load_taxonomy()
    min_occ = int(tax.get("min_occurrences_for_candidate", 5))
    known = tax.get("known_streams", [])

    daily_files = _list_daily_files(days)
    daily_text = "\n".join(_read_text(p) for p in daily_files)

    changed_paths = _git_changed_paths_since(days)
    grouped = _group_paths(changed_paths)

    candidates: List[Candidate] = []
    for s in known:
        slug = s.get("slug", "").strip()
        name = s.get("name", slug)
        signals = s.get("signals", [])

        occ_daily = _count_signal(daily_text, signals)
        occ_git = 0
        # git 侧按“前缀命中”粗算
        for k, v in grouped.items():
            if any(sig in k for sig in signals):
                occ_git += v

        occurrences = occ_daily + occ_git
        if occurrences < min_occ:
            continue

        evidence = []
        # 证据路径：取 top 的几个 prefix
        for k, v in list(grouped.items())[:30]:
            if any(sig in k for sig in signals):
                evidence.append(f"{k} (changes={v})")

        candidates.append(
            _evaluate_candidate(
                slug=slug,
                name=name,
                occurrences=occurrences,
                evidence_paths=evidence,
                stable_input_hint=s.get("stable_input_hint", ""),
                stable_output_paths=s.get("stable_output_paths", []),
                memory_deposit_paths=s.get("memory_deposit_paths", []),
                covered_by_existing_roles=s.get("covered_by_existing_roles", []),
            )
        )

    # 额外：从 git 前缀里自动提名“未知工作流”（不创建居民，只记录观察）
    for k, v in list(grouped.items())[:10]:
        if v < max(8, min_occ):
            continue
        # 跳过已知
        if any(k.startswith(sig) for s in known for sig in s.get("signals", [])):
            continue
        slug = re.sub(r"[^a-z0-9]+", "_", k.lower()).strip("_")
        candidates.append(
            Candidate(
                slug=f"unknown_{slug}",
                name=f"未知工作流：{k}",
                occurrences_30d=v,
                evidence_paths=[f"{k} (changes={v})"],
                stable_input="repo activity",
                stable_output_paths=[],
                memory_deposit_paths=[],
                protocol_hint="unknown",
                covered_by_existing_roles=[],
                ecological_need=False,
                replaceable_by_existing_roles=False,
                status="NOT_YET",
            )
        )

    # 按 status 与出现次数排序
    def key(c: Candidate) -> Tuple[int, int]:
        s = 0 if c.status == "ELIGIBLE" else 1
        return (s, -c.occurrences_30d)

    candidates.sort(key=key)
    return candidates


def render_resident_nominations(cands: List[Candidate], days: int) -> str:
    lines = []
    lines.append("# resident_nominations")
    lines.append("")
    lines.append(f"- window_days: {days}")
    lines.append(f"- generated_at: {dt.datetime.now().isoformat()}")
    lines.append("")
    lines.append("## 候选清单")
    lines.append("")
    if not cands:
        lines.append("> 今日无新增发现，但现有证据未改变结论。")
        lines.append("")
        return "\n".join(lines)

    for c in cands:
        lines.append(f"### {c.name} (`{c.slug}`)")
        lines.append(f"- status: `{c.status}`")
        lines.append(f"- occurrences_30d: `{c.occurrences_30d}`")
        lines.append(f"- ecological_need: `{str(c.ecological_need).lower()}`")
        lines.append(f"- replaceable_by_existing_roles: `{str(c.replaceable_by_existing_roles).lower()}`")
        if c.covered_by_existing_roles:
            lines.append(f"- covered_by_existing_roles: {', '.join(c.covered_by_existing_roles)}")
        lines.append(f"- stable_input: {c.stable_input}")
        if c.stable_output_paths:
            lines.append(f"- stable_output_paths: {', '.join(c.stable_output_paths)}")
        if c.memory_deposit_paths:
            lines.append(f"- memory_deposit_paths: {', '.join(c.memory_deposit_paths)}")
        if c.evidence_paths:
            lines.append("- evidence:")
            for e in c.evidence_paths[:10]:
                lines.append(f"  - {e}")
        lines.append("")
    return "\n".join(lines)


def render_daily_log(cands: List[Candidate], days: int) -> str:
    lines = []
    lines.append(f"## {dt.datetime.now().strftime('%Y-%m-%d')} 生态观察员")
    lines.append(f"- window_days: {days}")
    eligible = [c for c in cands if c.status == "ELIGIBLE"]
    lines.append(f"- eligible_count: {len(eligible)}")
    if eligible:
        lines.append("- eligible:")
        for c in eligible:
            lines.append(f"  - {c.slug}: {c.name} (occ={c.occurrences_30d})")
    else:
        lines.append("> 今日无新增发现，但现有证据未改变结论。")
    lines.append("")
    return "\n".join(lines)


def write_outputs(cands: List[Candidate], days: int) -> None:
    _safe_mkdir(ECO_DIR)
    _safe_mkdir(NOM_DIR)

    # resident_nominations.md (overwrite)
    rn_path = os.path.join(ECO_DIR, "resident_nominations.md")
    with open(rn_path, "w", encoding="utf-8") as f:
        f.write(render_resident_nominations(cands, days))

    # ecology_observer_daily.md (append, 确保换行分隔)
    daily_path = os.path.join(ECO_DIR, "ecology_observer_daily.md")
    with open(daily_path, "a", encoding="utf-8") as f:
        # 前置 \n 保证即使文件末尾无换行也能正确分隔
        f.write("\n" + render_daily_log(cands, days))

    # per-candidate nomination stub (ensure exists, only for ELIGIBLE)
    for c in cands:
        if c.status != "ELIGIBLE":
            continue
        stub_path = os.path.join(NOM_DIR, f"AUM-RESIDENT-{c.slug}.md")
        # 读取已有stub，只刷新 machine-generated JSON block
        existing_content = None
        if os.path.exists(stub_path):
            with open(stub_path, 'r', encoding='utf-8') as ef:
                existing_content = ef.read()
        eco_json = json.dumps(
            {
                "ecological_need": c.ecological_need,
                "replaceable_by_existing_roles": c.replaceable_by_existing_roles,
            },
            indent=2,
            ensure_ascii=False,
        )
        # 构建stub内容
        stub_lines = [
            f"# {c.name}",
            "",
            "## 申请单（草案）",
            "",
            "- 生态位长期存在：",
            "- 无法被现有角色覆盖：",
            "- 稳定输入：",
            "- 稳定输出：",
            "- 独立记忆沉积：",
            "- 独立协议：",
            "",
            "<!-- MACHINE_GENERATED_BLOCK_START -->",
            "### 生态必要性审查",
            "",
            "```json",
            eco_json,
            "```",
            "<!-- MACHINE_GENERATED_BLOCK_END -->",
            "",
            "### 证据",
            "",
            f"- occurrences_30d: `{c.occurrences_30d}`",
            f"- status: `{c.status}`",
            "",
            "### 结论（治理层见证）",
            "",
            "- result: PENDING",
            "",
        ]
        stub_content = "\n".join(stub_lines)

        # 如果已有stub存在，只替换machine-generated block；否则创建新文件
        if existing_content is not None:
            import re as _re
            new_stub = _re.sub(
                r'<!-- MACHINE_GENERATED_BLOCK_START -->.*?<!-- MACHINE_GENERATED_BLOCK_END -->',
                '<!-- MACHINE_GENERATED_BLOCK_START -->\n### 生态必要性审查\n\n```json\n' + eco_json + '\n```\n<!-- MACHINE_GENERATED_BLOCK_END -->',
                existing_content,
                flags=_re.DOTALL
            )
            with open(stub_path, "w", encoding="utf-8") as f:
                f.write(new_stub)
        else:
            with open(stub_path, "w", encoding="utf-8") as f:
                f.write(stub_content)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--write", action="store_true", help="写入 ecology 产物文件（默认只打印摘要）")
    args = ap.parse_args()

    cands = build_candidates(days=args.days)

    # stdout 摘要（不含敏感信息）
    print("ecology_observer:")
    print(f"- window_days: {args.days}")
    print(f"- candidates: {len(cands)}")
    for c in cands[:10]:
        print(f"  - {c.slug} status={c.status} occ={c.occurrences_30d} replaceable={c.replaceable_by_existing_roles}")

    if args.write:
        write_outputs(cands, days=args.days)
        print(f"- wrote: {os.path.relpath(ECO_DIR, REPO_ROOT)}")


if __name__ == "__main__":
    main()
