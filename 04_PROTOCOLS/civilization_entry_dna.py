"""---
id: PROTO-009
type: protocol
title: "Civilization Entry DNA — 知识单位基因规范"
status: active
source: "R2 Development"
created: 2026-07-12
confidence: 0.90
lineage:
  - CHIP-LINEAGE-001
related: [KERNEL-DNA-V1, INV-MANIFEST-001]
tags: [dna, identity, entry, spec]
archaeology:
  state: original
---
"""
"""
Civilization Entry DNA — 文明知识单位的基因规范

核心理念：
  Every Knowledge has Identity.
  不是模板，是 DNA — 每个知识单位出生时就必须带着的基因。

四维结构：
  Identity    → 我是谁
  Evidence    → 证据在哪
  Relationship → 跟谁有关
  Archaeology  → 考古状态

Entry Type Hierarchy (文明生长顺序):
  axiom → principle → constraint → protocol → experience → artifact
  这是一个闭环：principle 产生 protocol，protocol 运行后产出 experience，
  experience 沉淀后变成 constraint，constraint 固化后升回 principle。

使用方式：
  在 .md / .py / .json 文件头部嵌入 YAML front-matter：

  ---
  id: INV-L0-001
  type: axiom
  title: Continuity Principle
  status: active
  source: R1 Deep Archaeology
  created: 2026-07-12
  lineage: [PRINCIPLES.md, TG-Saved-001]
  related: [INV-L0-002, PROTO-004]
  tags: [continuity, kernel, invariant]
  confidence: 0.92
  evidence: [E-001, E-003, E-036]
  archaeology:
    state: recovered
    sources: 5
  ---
"""

import re
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ============================================================
# Entry Type Hierarchy — 文明生长顺序
# ============================================================

ENTRY_TYPES = {
    "axiom": {
        "level": 0,
        "desc": "不证自明的公理，文明的起点",
        "grows_into": "principle",
    },
    "principle": {
        "level": 1,
        "desc": "从公理推导出的原则",
        "grows_into": "constraint",
    },
    "constraint": {
        "level": 2,
        "desc": "原则固化为可执行的约束",
        "grows_into": "protocol",
    },
    "protocol": {
        "level": 3,
        "desc": "约束实现为具体协议/代码",
        "grows_into": "experience",
    },
    "experience": {
        "level": 4,
        "desc": "协议运行后产出的经验",
        "grows_into": "artifact",
    },
    "artifact": {
        "level": 5,
        "desc": "经验沉淀为可交付的产出物",
        "grows_into": "axiom",  # 闭环：artifact 可以反哺新的 axiom
    },
    # 特殊类型（不在主生长链上）
    "question": {"level": -1, "desc": "待回答的问题", "grows_into": "hypothesis"},
    "hypothesis": {"level": -1, "desc": "待验证的假设", "grows_into": "axiom"},
    "config": {"level": -1, "desc": "配置文件", "grows_into": None},
    "report": {"level": -1, "desc": "报告/文档", "grows_into": None},
    "unknown": {"level": -1, "desc": "未知类型", "grows_into": None},
}

# 文明生长闭环
GROWTH_CYCLE = ["axiom", "principle", "constraint", "protocol", "experience", "artifact"]

# Archaeology states
ARCHAELOGY_STATES = {
    "original": "R2 原生产出，非考古恢复",
    "recovered": "从 R1 废墟中恢复的实体文件",
    "inferred": "基于证据推测，无实体文件",
    "evolved": "从 R1 恢复后在 R2 中演化的版本",
    "dead": "已废弃，不再使用",
    "unknown": "状态未知",
}

# ============================================================
# DNA 规范定义
# ============================================================

# 核心字段（必须有）
REQUIRED_FIELDS = ["id", "type", "title", "status"]

# 推荐字段（有更好，没有也行）
RECOMMENDED_FIELDS = ["source", "created", "lineage", "related", "tags", "confidence", "evidence", "archaeology"]

# DNA 四维映射
DNA_DIMENSIONS = {
    "Identity": ["id", "type", "title", "status"],
    "Evidence": ["source", "created", "confidence", "evidence"],
    "Relationship": ["lineage", "related", "tags"],
    "Archaeology": ["archaeology"],
}

# ============================================================
# YAML front-matter 解析器
# ============================================================

# 匹配 --- ... --- 之间的 YAML front-matter（.md 文件）
FRONT_MATTER_RE = re.compile(
    r'^---\s*\n(.*?)\n---\s*\n',
    re.DOTALL
)

# 匹配 Python docstring 中的 YAML front-matter（.py 文件）
# 格式: """---\n...\n---\n"""
PY_DOCSTRING_RE = re.compile(
    r'^"""\s*---\s*\n(.*?)\n---\s*\n\s*"""',
    re.DOTALL
)


def parse_dna(filepath: str) -> Optional[Dict[str, any]]:
    """从文件中解析 DNA front-matter。

    支持两种格式：
    - .md 文件: 裸 YAML front-matter (--- ... ---)
    - .py 文件: docstring 包裹的 YAML (triple-quote + --- ... --- + triple-quote)

    Returns:
        DNA dict if found, None otherwise.
    """
    path = Path(filepath)
    if not path.exists():
        return None

    content = path.read_text(encoding='utf-8', errors='ignore')

    # 尝试裸 YAML front-matter
    match = FRONT_MATTER_RE.match(content)
    if match:
        yaml_text = match.group(1)
        dna = _parse_simple_yaml(yaml_text)
        if dna:
            return dna

    # 尝试 Python docstring 中的 YAML
    match = PY_DOCSTRING_RE.match(content)
    if match:
        yaml_text = match.group(1)
        dna = _parse_simple_yaml(yaml_text)
        if dna:
            return dna

    return None


def _parse_simple_yaml(text: str) -> Dict[str, any]:
    """极简 YAML 解析器，只支持 key: value 和 key: [list] 格式。

    不依赖 PyYAML，避免外部依赖。
    """
    result = {}
    current_key = None
    current_list = None
    nested_dict = None  # for nested key-value blocks like archaeology:

    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Detect indentation level
        indent = len(line) - len(line.lstrip())

        # List item under a key (  - item)
        if stripped.startswith('- ') and current_key:
            if current_list is None:
                current_list = []
            val = stripped[2:].strip()
            # Remove quotes if present
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            current_list.append(val)
            continue

        # Nested key-value under current_key (e.g., "  state: recovered" under "archaeology:")
        if nested_dict is not None and indent > 0 and ':' in stripped and not stripped.startswith('- '):
            idx = stripped.index(':')
            nkey = stripped[:idx].strip()
            nval = stripped[idx + 1:].strip()
            if nval.startswith('"') and nval.endswith('"'):
                nval = nval[1:-1]
            elif nval.startswith("'") and nval.endswith("'"):
                nval = nval[1:-1]
            try:
                if '.' in nval:
                    nval = float(nval)
                else:
                    nval = int(nval)
            except ValueError:
                pass
            nested_dict[nkey] = nval
            continue

        # End of nested block — save it
        if nested_dict is not None:
            result[current_key] = nested_dict
            nested_dict = None
            current_key = None

        # Save previous list
        if current_list is not None and current_key:
            result[current_key] = current_list
            current_list = None
            current_key = None

        # key: value
        if ':' in stripped:
            idx = stripped.index(':')
            key = stripped[:idx].strip()
            val = stripped[idx + 1:].strip()

            if val == '':
                # Multi-line value (list or nested dict)
                current_key = key
                current_list = None
                nested_dict = {}  # ready for either list or dict items
            elif val.startswith('[') and val.endswith(']'):
                # Inline list: [a, b, c]
                items = [x.strip().strip('"\'') for x in val[1:-1].split(',') if x.strip()]
                result[key] = items
                current_key = None
                nested_dict = None
            else:
                # Scalar value
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.startswith("'") and val.endswith("'"):
                    val = val[1:-1]
                # Try to parse as number
                try:
                    if '.' in val:
                        result[key] = float(val)
                    else:
                        result[key] = int(val)
                except ValueError:
                    result[key] = val
                current_key = None
                nested_dict = None

    # Save last list or nested dict
    if current_list is not None and current_key:
        result[current_key] = current_list
    elif nested_dict is not None and current_key:
        result[current_key] = nested_dict

    return result


def validate_dna(dna: Dict[str, any]) -> Tuple[bool, List[str]]:
    """验证 DNA 是否符合规范。

    Returns:
        (is_valid, issues)
    """
    issues = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in dna:
            issues.append(f"Missing required field: {field}")

    # Check type is valid
    if 'type' in dna:
        if dna['type'] not in ENTRY_TYPES:
            issues.append(f"Unknown type: {dna['type']}. Valid: {list(ENTRY_TYPES.keys())}")

    # Check archaeology state if present
    if 'archaeology' in dna and isinstance(dna['archaeology'], dict):
        state = dna['archaeology'].get('state', '')
        if state and state not in ARCHAELOGY_STATES:
            issues.append(f"Unknown archaeology state: {state}. Valid: {list(ARCHAELOGY_STATES.keys())}")

    # Check confidence range
    if 'confidence' in dna:
        try:
            conf = float(dna['confidence'])
            if conf < 0 or conf > 1:
                issues.append(f"Confidence out of range [0,1]: {conf}")
        except (ValueError, TypeError):
            issues.append(f"Confidence not a number: {dna['confidence']}")

    return (len(issues) == 0, issues)


def generate_dna(
    entry_id: str,
    entry_type: str,
    title: str,
    status: str = "active",
    source: str = "",
    lineage: List[str] = None,
    related: List[str] = None,
    tags: List[str] = None,
    confidence: float = 0.0,
    evidence: List[str] = None,
    archaeology_state: str = "original",
    archaeology_sources: int = 0,
) -> str:
    """生成 DNA YAML front-matter 字符串。

    Returns:
        YAML string to prepend to file content.
    """
    lines = ["---"]

    # Identity
    lines.append(f"id: {entry_id}")
    lines.append(f"type: {entry_type}")
    lines.append(f"title: \"{title}\"")
    lines.append(f"status: {status}")

    # Evidence
    if source:
        lines.append(f"source: \"{source}\"")
    lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
    if confidence > 0:
        lines.append(f"confidence: {confidence:.2f}")
    if evidence:
        lines.append(f"evidence: [{', '.join(evidence)}]")

    # Relationship
    if lineage:
        lines.append("lineage:")
        for item in lineage:
            lines.append(f"  - {item}")
    if related:
        lines.append(f"related: [{', '.join(related)}]")
    if tags:
        lines.append(f"tags: [{', '.join(tags)}]")

    # Archaeology
    lines.append("archaeology:")
    lines.append(f"  state: {archaeology_state}")
    if archaeology_sources > 0:
        lines.append(f"  sources: {archaeology_sources}")

    lines.append("---")
    lines.append("")  # blank line after front-matter

    return '\n'.join(lines)


def scan_dna_compliance(directory: str) -> Dict[str, any]:
    """扫描目录下所有知识文件的 DNA 合规性。

    Returns:
        {
            "total": N,
            "has_dna": N,
            "missing_dna": [file paths],
            "invalid_dna": [{path, issues}],
            "by_type": {type: count},
            "by_state": {state: count},
        }
    """
    root = Path(directory)
    extensions = {'.md', '.py', '.json', '.yaml', '.yml'}

    result = {
        "total": 0,
        "has_dna": 0,
        "missing_dna": [],
        "invalid_dna": [],
        "by_type": {},
        "by_state": {},
    }

    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        if path.suffix not in extensions:
            continue
        # Skip node_modules, __pycache__, .git
        if any(part in str(path) for part in ['node_modules', '__pycache__', '.git', 'superseded_archive']):
            continue

        result["total"] += 1
        dna = parse_dna(str(path))

        if dna is None:
            result["missing_dna"].append(str(path))
            continue

        result["has_dna"] += 1
        is_valid, issues = validate_dna(dna)
        if not is_valid:
            result["invalid_dna"].append({"path": str(path), "issues": issues})

        # Count by type
        etype = dna.get('type', 'unknown')
        result["by_type"][etype] = result["by_type"].get(etype, 0) + 1

        # Count by archaeology state
        arch = dna.get('archaeology', {})
        if isinstance(arch, dict):
            state = arch.get('state', 'unknown')
        else:
            state = 'unknown'
        result["by_state"][state] = result["by_state"].get(state, 0) + 1

    return result


def print_compliance_report(directory: str):
    """打印 DNA 合规报告。"""
    report = scan_dna_compliance(directory)

    print("=" * 60)
    print("Civilization Entry DNA — Compliance Report")
    print("=" * 60)
    print()
    print(f"Directory: {directory}")
    print(f"Total knowledge files: {report['total']}")
    print(f"Has DNA: {report['has_dna']} ({report['has_dna'] / max(1, report['total']) * 100:.0f}%)")
    print(f"Missing DNA: {len(report['missing_dna'])}")
    print(f"Invalid DNA: {len(report['invalid_dna'])}")
    print()

    if report["by_type"]:
        print("By Type:")
        for t, count in sorted(report["by_type"].items(), key=lambda x: -x[1]):
            print(f"  {t}: {count}")
        print()

    if report["by_state"]:
        print("By Archaeology State:")
        for s, count in sorted(report["by_state"].items(), key=lambda x: -x[1]):
            print(f"  {s}: {count}")
        print()

    if report["missing_dna"][:10]:
        print("Files missing DNA (first 10):")
        for p in report["missing_dna"][:10]:
            print(f"  {p}")
        if len(report["missing_dna"]) > 10:
            print(f"  ... and {len(report['missing_dna']) - 10} more")
        print()

    if report["invalid_dna"][:5]:
        print("Files with invalid DNA (first 5):")
        for item in report["invalid_dna"][:5]:
            print(f"  {item['path']}")
            for issue in item["issues"]:
                print(f"    → {issue}")
        print()

    # Growth cycle coverage
    print("Growth Cycle Coverage:")
    for t in GROWTH_CYCLE:
        count = report["by_type"].get(t, 0)
        marker = "✓" if count > 0 else "✗"
        print(f"  {marker} {t}: {count}")

    return report


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Civilization Entry DNA")
    parser.add_argument("--scan", type=str, help="Scan directory for DNA compliance")
    parser.add_argument("--generate", action="store_true", help="Generate sample DNA")
    args = parser.parse_args()

    if args.scan:
        print_compliance_report(args.scan)
    elif args.generate:
        sample = generate_dna(
            entry_id="EXP-021",
            entry_type="experience",
            title="Recovery Scanner L7 Telegram Layer",
            status="active",
            source="R2 Development",
            lineage=["TG-ARCH-002", "REC-001"],
            related=["PROTO-004", "INV-L0-001"],
            tags=["recovery", "telegram", "scanner"],
            confidence=0.92,
            evidence=["E-036", "E-038"],
            archaeology_state="original",
            archaeology_sources=1,
        )
        print(sample)
    else:
        parser.print_help()
