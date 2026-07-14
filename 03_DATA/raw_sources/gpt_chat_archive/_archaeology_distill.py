#!/usr/bin/env python3
"""
ChatGPT Archive Distillation - 考古蒸馏工具

Extract structured civilizational assets from ChatGPT archive.
Outputs:
    - 02_MEMORY/assets/experience/EXP-GPT-ARCHIVE-001.md
    - 02_MEMORY/pending_questions.json append
    - 02_MEMORY/assets/seed/SEED_GPT_R1R2_ARCHAEOLOGY.txt
"""

import json
from pathlib import Path
from datetime import datetime

ARCHIVE_DIR = Path(__file__).parent
CONV_FILE = ARCHIVE_DIR / "conversations.json"
ROOT_DIR = ARCHIVE_DIR.parent.parent.parent  # mine-seed
MEMORY_DIR = ROOT_DIR / "02_MEMORY"


def load_conversations():
    return json.loads(CONV_FILE.read_text(encoding='utf-8'))


def extract_conversation_text(conv):
    """Extract full conversation text"""
    mapping = conv.get('mapping', {})
    lines = []
    
    for node_id, node in mapping.items():
        msg = node.get('message', {})
        if not msg:
            continue
        
        author = msg.get('author', {}).get('role', 'unknown')
        content = msg.get('content', {})
        parts = content.get('parts', [])
        text = ' '.join(str(p) for p in parts if p).strip()
        
        if text:
            role = "USER" if author == 'user' else "ASSISTANT" if author == 'assistant' else author.upper()
            lines.append(f"[{role}]\n{text}\n")
    
    return '\n'.join(lines)


def distill_high_value_conversations():
    """Distill high-value conversations to structured files"""
    data = load_conversations()
    
    # High-value conversations identified by probe
    TARGETS = {
        1: "R2 Kernel 架构解析",
        2: "老张主线模式加载",
        3: "R1架构分析与演化",
        4: "R1结构与R2规划",
        7: "矿场架构优化建议",
        8: "验证机制与流程",
        9: "R1结构演化分析",
        10: "DAG恢复与实现",
        14: "三重交叉验证设计",
        15: "Shadow Layer 解析",
    }
    
    # 1. Create experience distillation
    exp_dir = MEMORY_DIR / "assets" / "experience"
    exp_dir.mkdir(parents=True, exist_ok=True)
    
    exp_file = exp_dir / "EXP-GPT-ARCHIVE-001.md"
    
    lines = []
    lines.append("# EXP-GPT-ARCHIVE-001: ChatGPT 历史会话考古蒸馏")
    lines.append("")
    lines.append(f"> 来源: ChatGPT 导出存档 ({ARCHIVE_DIR.name})")
    lines.append(f"> 蒸馏时间: {datetime.now().isoformat()}")
    lines.append(f"> 会话总数: {len(data)}")
    lines.append(f"> 高价值会话数: {len(TARGETS)}")
    lines.append("")
    lines.append("## 一阶主题识别")
    lines.append("")
    lines.append("| 主题 | 用户提及次数 | 重要性 |")
    lines.append("|------|-------------|--------|")
    lines.append("| R1 | 1018 | 核心架构")
    lines.append("| 验证 | 488 | 治理机制")
    lines.append("| 协议 | 444 | 约束体系")
    lines.append("| mine/seed | 436/434 | 矿场与种子层")
    lines.append("| 发现 | 414 | 发现协议")
    lines.append("| 架构 | 300 | 系统设计")
    lines.append("| 经验 | 296 | 经验沉淀")
    lines.append("| 约束 | 277 | 不变量")
    lines.append("| 矿场 | 255 | 资源调度")
    lines.append("| Router | 248 | 路由层")
    lines.append("")
    lines.append("## 高价值会话清单")
    lines.append("")
    
    for idx, title in TARGETS.items():
        conv = data[idx - 1]
        mapping = conv.get('mapping', {})
        user_count = sum(1 for n in mapping.values() if n and n.get('message') and n['message'].get('author', {}).get('role') == 'user')
        ast_count = sum(1 for n in mapping.values() if n and n.get('message') and n['message'].get('author', {}).get('role') == 'assistant')
        
        lines.append(f"### #{idx}: {title}")
        lines.append(f"- 用户消息: {user_count}")
        lines.append(f"- 助手消息: {ast_count}")
        lines.append(f"- 状态: 待进一步蒸馏")
        lines.append("")
    
    lines.append("## 考古发现")
    lines.append("")
    lines.append("1. **R1/R2 架构**: 大量讨论围绕 Kernel、Shadow Layer、Router、Mine、Seed 展开，可能存在未进入当前仓库的设计决策。")
    lines.append("2. **验证机制**: '验证' 是第二大主题，可能与当前 C-025 之前的验证协议有关。")
    lines.append("3. **约束体系**: '约束'、'协议'、'流程' 高频出现，说明早期设计强调治理结构。")
    lines.append("4. **发现协议**: '发现' 主题显著，可能与当前每日发现协议/Law Discovery 的前身有关。")
    lines.append("")
    lines.append("## 待考古问题")
    lines.append("")
    lines.append("- [ ] R1 Kernel 与当前 PRINCIPLES.md 中的约束是否有冲突？")
    lines.append("- [ ] Shadow Layer 是否对应 Runtime/dev 分类或 Memory Layer？")
    lines.append("- [ ] 验证机制与流程是否已被吸收到 red_blue_audit.py？")
    lines.append("- [ ] 矿场架构是否影响当前 OPS-003/OPS-006 的模型调度策略？")
    lines.append("")
    lines.append("## 原始文件")
    lines.append("")
    lines.append(f"- 完整存档: `{ARCHIVE_DIR}`")
    lines.append(f"- 索引摘要: `{ARCHIVE_DIR / '_archaeology_summary.json'}`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*注意: 此蒸馏为一级索引，未深入解析每条消息内容。深度考古需在后续 Mission 中按主题逐个展开。*")
    
    exp_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Experience distilled to: {exp_file}")
    
    # 2. Create seed note
    seed_dir = MEMORY_DIR / "assets" / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)
    
    seed_file = seed_dir / "SEED_GPT_R1R2_ARCHAEOLOGY.txt"
    seed_file.write_text(
        "[SEED] GPT_R1R2_ARCHAEOLOGY\n"
        "Source: ChatGPT archive export\n"
        "Themes: R1, R2, Kernel, Shadow, Mine, Seed, Router, Validation, Constraint, Protocol\n"
        "Status: UNMINED\n"
        "Priority: MEDIUM\n"
        f"Distilled: {datetime.now().isoformat()}\n"
        "Next Action: Per-theme deep archaeology when related Mission is active\n",
        encoding='utf-8'
    )
    print(f"Seed note created: {seed_file}")
    
    # 3. Append pending questions
    questions_file = MEMORY_DIR / "pending_questions.json"
    pending = []
    if questions_file.exists():
        try:
            pending = json.loads(questions_file.read_text(encoding='utf-8'))
            if not isinstance(pending, list):
                pending = [pending]
        except Exception:
            pending = []
    
    new_questions = [
        {
            "question": "ChatGPT archive 中 R1/R2 Kernel 讨论与当前 PRINCIPLES.md 约束是否有冲突或补充？",
            "source": "EXP-GPT-ARCHIVE-001",
            "priority": "P2",
            "status": "pending",
            "capability": "reasoning",
            "dedup_key": "gpt_archive_r1_kernel",
            "timestamp": datetime.now().isoformat()
        },
        {
            "question": "ChatGPT archive 中 Shadow Layer 设计是否应映射到当前 Runtime/dev 分类或 Memory Layer？",
            "source": "EXP-GPT-ARCHIVE-001",
            "priority": "P2",
            "status": "pending",
            "capability": "architecture",
            "dedup_key": "gpt_archive_shadow_layer",
            "timestamp": datetime.now().isoformat()
        },
        {
            "question": "ChatGPT archive 中验证机制与流程是否已被 red_blue_audit.py / Law Discovery Protocol 吸收？",
            "source": "EXP-GPT-ARCHIVE-001",
            "priority": "P2",
            "status": "pending",
            "capability": "audit",
            "dedup_key": "gpt_archive_validation_flow",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Deduplicate by dedup_key
    existing_keys = {q.get('dedup_key') for q in pending if q.get('dedup_key')}
    for q in new_questions:
        if q['dedup_key'] not in existing_keys:
            pending.append(q)
            existing_keys.add(q['dedup_key'])
    
    questions_file.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Pending questions updated: {questions_file}")


def main():
    distill_high_value_conversations()
    print("\nArchaeology distillation complete.")


if __name__ == "__main__":
    main()