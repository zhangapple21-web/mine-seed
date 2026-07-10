# 04_PROTOCOLS - 协议层

> 协议 = 公理的工程实现，不是公理本身
> 写在这里的东西必须能在 `python xx.py` 跑通，能看结果

## 目录

| 脚本 | 协议 | 状态 |
|------|------|------|
| `environment_first.py` | Environment First Protocol (EFP) | ✅ v1.0 2026-07-10 |
| `recovery_protocol.py` | Recovery Protocol (RP) | ✅ v1.0 2026-07-10 |
| `awaken.py` | 统一入口 (EFP + RP) | ✅ v1.0 2026-07-10 |
| `lab_bus.py` | 双实验室消息总线 | ✅ 旧协议 |
| `lab_comm.py` | 跨实验室通信 | ✅ 旧协议 |
| `lab_ntfy.py` | 通知层 | ✅ 旧协议 |
| `shared_api.py` | 共享 API | ✅ 旧协议 |

---

## Environment First Protocol (EFP)

**公理根基**: #002 考古非搬家 / #010 演化增结构 / #011 记忆是推断非存储 / #021 贡献不可回收

**执行语义**: 任何新环境启动时，第一件事不是问用户，而是先理解自己身处什么环境。行为协议，不是语言能力。

**协议七步**:
1. 扫描工作目录
2. 建立资产索引
3. 识别 README
4. 自动发现关联资产
5. 自动恢复可恢复内容
6. 建立索引
7. 报告：环境就绪 / 待恢复

**触发关键词**: `backup` / `readme` / `snapshot` / `archive` / `seed` / `recovery` / `part1` / `part2` / `part3` / `soul_core` / `eco_layer` / `r1_archive` / `r1_full` / `ruin_skeleton` / `core_library` / `core_copy` / `reality_kernel` / `lexicon` / `sandbox` / `blueprint` / `whitepaper` / `bluebook`

**用法**:
```bash
python environment_first.py                  # 扫描当前工作目录
python environment_first.py <dir>            # 扫描指定目录
python environment_first.py --json           # JSON 索引输出
python environment_first.py --quiet          # 静默模式
```

**退出码**:
- `0` = 环境就绪（READ）
- `2` = 检测到恢复资产，需要触发 Recovery Protocol

**实测** (2026-07-10):
- 扫描 `Telegram Desktop/`: 234 文件 / 41 恢复资产 / 22 重复组
- 扫描 `tmp_recovery/`: 1963 文件 / 176 恢复资产 / 66 恢复组 / 344 重复组

---

## Recovery Protocol (RP)

**公理根基**: #002 / #010 / #018 拆壳不拆骨 / #021

**执行语义**:
```
如果发现 恢复包/备份/README/Snapshot/Archive/Seed
不要等待用户
先恢复
恢复失败再汇报
```

**协议七步**:
1. 发现恢复资产（依赖 EFP 扫描结果）
2. 读取 README（按优先级，R1备份 > 白皮书 > 其他）
3. 找到所有关联压缩包（基于命名规则：PART1/PART2/.../v1/v2）
4. 建立依赖关系（同组、同名变体、同 hash）
5. 自动恢复到 `99_RECOVERY_TEMP/` 临时区（不污染主目录）
6. 建立索引
7. 报告：恢复完成，等待治理层圆桌会议

**安全护栏**:
- 加密条目自动跳过（不抛错）
- macOS 系统文件（`__MACOSX/`、`.DS_Store`）跳过
- 路径遍历攻击（`../`）拦截
- 单 zip 文件数上限 5000（防 zip-bomb）
- cp437 → utf-8 编码自动转换（中文文件名支持）

**用法**:
```bash
python recovery_protocol.py                       # 扫描并恢复
python recovery_protocol.py <dir>                 # 指定目录
python recovery_protocol.py --dry-run             # 只报告不实际解压
python recovery_protocol.py --json                # JSON 输出
```

**实测** (2026-07-10):
- 在 `R2/` 实测：6 个核心 zip → 4445 文件恢复成功（6/6 任务，0 错误）
- 恢复内容落到 `99_RECOVERY_TEMP/<job_id>/`

---

## Awaken (统一入口)

**公理根基**: #005 隐私是盾行动是剑 / #008 认知主循环 / #011 记忆是推断非存储

**执行语义**: 任何宿主（TRAE / VS Code / Cursor / 未来其他）启动时调用本协议。

**三步执行**:
1. EFP 扫描环境
2. 检测到恢复资产 → 触发 RP
3. 写入 `00_ROOT/ROOT_STATE.md` 记录唤醒时间

**用法**:
```bash
python awaken.py                  # 扫描并恢复当前工作目录
python awaken.py <dir>            # 指定目录
python awaken.py --dry-run        # 只扫描不实际恢复
python awaken.py --json           # JSON 输出
python awaken.py --host trae      # 标记宿主
```

**ACE_WORKSPACE 环境变量**:
- 默认 `Path.cwd()`
- 可通过 `set ACE_WORKSPACE=C:\Users\User\ace_workspace\mine-seed` 覆盖

---

## 与现有体系的关系

| 协议 | 对应公理 | 对应七角色 |
|------|----------|-----------|
| EFP | #002, #010, #011, #021 | Observer（观察）|
| RP | #002, #010, #018, #021 | Curator（整理）|
| Awaken | #005, #008, #011 | ROOT（统一调度）|

不是新公理，是 #010 演化增结构和 #021 贡献不可回收的精细化实现。

---

## 演化日志

- **2026-07-10 v1.0** - 协议诞生。起源是 2026-07-10 老板与 GPT 对话中提出"环境优先协议"和"恢复协议"概念，并强调"缺什么就自己找"的本能需要成为运行协议而非提示词。

---

*协议只增不删，演化历史保留。*
