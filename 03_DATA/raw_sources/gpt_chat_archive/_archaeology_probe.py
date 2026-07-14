#!/usr/bin/env python3
"""
ChatGPT Archive Archaeology Probe
Scan high-value conversations and extract first-order signals.
"""

import json
from pathlib import Path
from collections import Counter

ARCHIVE_DIR = Path(__file__).parent
CONV_FILE = ARCHIVE_DIR / "conversations.json"


def load_conversations():
    return json.loads(CONV_FILE.read_text(encoding='utf-8'))


def extract_messages(conv):
    """Extract user and assistant messages"""
    mapping = conv.get('mapping', {})
    messages = []
    
    for node_id, node in mapping.items():
        msg = node.get('message', {})
        if not msg:
            continue
        
        author = msg.get('author', {}).get('role', 'unknown')
        content = msg.get('content', {})
        parts = content.get('parts', [])
        text = ' '.join(str(p) for p in parts if p).strip()
        
        if text:
            messages.append({
                'role': author,
                'text': text,
                'node_id': node_id
            })
    
    return messages


def probe_conversations():
    data = load_conversations()
    
    # High-value targets based on title
    TARGETS = [0, 1, 2, 3, 6, 7, 8, 9, 13, 14]
    
    summary = []
    all_user_text = []
    all_assistant_text = []
    
    for idx in TARGETS:
        if idx >= len(data):
            continue
        
        c = data[idx]
        title = c.get('title', 'Untitled')
        messages = extract_messages(c)
        
        user_msgs = [m for m in messages if m['role'] == 'user']
        assistant_msgs = [m for m in messages if m['role'] == 'assistant']
        
        all_user_text.extend([m['text'] for m in user_msgs])
        all_assistant_text.extend([m['text'] for m in assistant_msgs])
        
        # Extract key terms
        combined_text = ' '.join(m['text'] for m in messages).lower()
        keywords = []
        for kw in ['r1', 'r2', 'kernel', 'shadow', '矿场', '验证', '架构', '约束', '协议', '流程', 'dag', 'router', 'mine', 'seed', 'adr', 'mcp', 'red team', 'blue team']:
            if kw in combined_text:
                keywords.append(kw)
        
        summary.append({
            'idx': idx + 1,
            'title': title,
            'total_msgs': len(messages),
            'user_msgs': len(user_msgs),
            'assistant_msgs': len(assistant_msgs),
            'keywords': keywords
        })
    
    # Print summary
    print("=" * 80)
    print("ChatGPT Archive Archaeology Probe")
    print("=" * 80)
    
    for item in summary:
        print(f"\n#{item['idx']:2d}: {item['title']}")
        print(f"     messages: total={item['total_msgs']:4d} | user={item['user_msgs']:4d} | assistant={item['assistant_msgs']:4d}")
        print(f"     keywords: {', '.join(item['keywords'])}")
    
    # Top terms
    print("\n" + "=" * 80)
    print("Top User-Driven Themes")
    print("=" * 80)
    
    user_text = ' '.join(all_user_text).lower()
    terms = []
    for term in ['r1', 'r2', 'kernel', 'shadow', '矿场', '验证', '架构', '约束', '协议', '流程', 'dag', 'router', 'mine', 'seed', 'adr', 'mcp', 'red team', 'blue team', '经验', '发现', '政策', '规律', '学习']:
        count = user_text.count(term)
        if count > 0:
            terms.append((term, count))
    
    terms.sort(key=lambda x: x[1], reverse=True)
    for term, count in terms[:15]:
        print(f"  {term:15s}: {count:3d}")
    
    # Save summary
    output_file = ARCHIVE_DIR / "_archaeology_summary.json"
    output_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nSummary saved to: {output_file}")


if __name__ == "__main__":
    probe_conversations()