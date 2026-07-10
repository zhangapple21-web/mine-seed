#!/usr/bin/env python3
"""
constraint_injector.py — 给miner_24h.py注入constraint过滤逻辑
最小侵入：只在match_task_to_worker()返回前加一个约束检查
2026-06-20 疯子
"""
import ast, sys, os

TARGET = '/home/coze/miner_24h.py'
BACKUP = '/home/coze/miner_24h.py.bak.pre_constraint_inject_20260620'
CONSTRAINT_FILE = '/home/coze/routing_constraints.json'

# 约束检查代码（注入到match_task_to_worker函数末尾，return之前）
CONSTRAINT_CODE = '''
    # ---- Constraint过滤 (2026-06-20 注入) ----
    try:
        import json as _json
        _cf = '/home/coze/routing_constraints.json'
        if os.path.exists(_cf):
            _cd = _json.load(open(_cf))
            _avoids = _cd.get('avoids', [])
            _prefers = _cd.get('prefers', [])
            # 检查AVOID
            for _a in _avoids:
                if _a.get('task') == task_type and _a.get('worker') == best_worker:
                    print(f"⛔ AVOID: {task_type}→{best_worker} (constraint={_a.get('id','?')})")
                    # 尝试fallback到次优
                    if _a.get('worker') == best_worker:
                        best_worker = None
                        # 重新选次优worker
                        for _wid, _wp in WORKER_PROFILES.items():
                            if _wid == _a.get('worker'):
                                continue
                            if _wp["current_load"] >= _wp["max_load"]:
                                continue
                            _is_avoided = False
                            for _a2 in _avoids:
                                if _a2.get('task') == task_type and _a2.get('worker') == _wid:
                                    _is_avoided = True
                                    break
                            if _is_avoided:
                                continue
                            if best_worker is None:
                                best_worker = _wid
                                break
                    break
            # 检查PREFER
            for _p in _prefers:
                if _p.get('task') == task_type:
                    _pw = _p.get('worker')
                    if _pw in WORKER_PROFILES and WORKER_PROFILES[_pw]["current_load"] < WORKER_PROFILES[_pw]["max_load"]:
                        best_worker = _pw
                        break
    except Exception as _e:
        print(f"⚠️ constraint check error: {_e}")
    # ---- Constraint过滤结束 ----
'''

lines = open(TARGET).readlines()

# 找到match_task_to_worker中 "return best_worker" 的位置
# 这是在函数末尾，我们要在return前插入constraint检查
new_lines = []
injected = False

for i, line in enumerate(lines):
    # 找到函数内第一个 return best_worker
    if not injected and 'return best_worker' in line and 'match_task_to_worker' not in line:
        # 获取缩进
        indent = ' ' * (len(line) - len(line.lstrip()))
        # 插入constraint代码（调整缩进为函数内缩进+4）
        for cl in CONSTRAINT_CODE.strip().split('\n'):
            if cl.strip():
                new_lines.append(indent + cl.lstrip() + '\n')
            else:
                new_lines.append('\n')
        injected = True
    new_lines.append(line)

if not injected:
    print("ERROR: 未找到 'return best_worker' 注入点")
    sys.exit(1)

# 验证语法
try:
    ast.parse(''.join(new_lines))
except SyntaxError as e:
    print(f"SYNTAX ERROR after injection: {e}")
    sys.exit(1)

# 备份
import shutil
if not os.path.exists(BACKUP):
    shutil.copy2(TARGET, BACKUP)
    print(f"Backup: {BACKUP}")

# 写入
open(TARGET, 'w').writelines(new_lines)
print(f"✅ Constraint injection complete. Injected before 'return best_worker'")

# 同时创建avoids/prefers格式的routing_constraints.json（如果不存在或格式不对）
# 这个文件会被miner_24h.py读取
import json
rc_path = CONSTRAINT_FILE
rc_backup = CONSTRAINT_FILE + '.bak.pre_inject_20260620'
if os.path.exists(rc_path):
    try:
        existing = json.load(open(rc_path))
        if 'avoids' in existing and 'prefers' in existing:
            print(f"routing_constraints.json already has avoids/prefers format, skipping rewrite")
        else:
            # 备份旧文件
            if not os.path.exists(rc_backup):
                shutil.copy2(rc_path, rc_backup)
            print(f"Old routing_constraints.json backed up to {rc_backup}")
            print(f"WARNING: Old format doesn't have avoids/prefers. Manual migration needed.")
    except:
        print(f"WARNING: routing_constraints.json parse error, will need manual fix")
