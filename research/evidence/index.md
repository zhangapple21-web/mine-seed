# 证据层索引

**状态**: v0.1 初始建库

---

## 证据分类

### E1: 历史研究报告
已完成的研究，按模块归类。

| 标题 | 所属模块 | 日期 | 路径 |
|------|----------|------|------|
| 公网桥Phase A验收报告 | M01 信号验证 | 2026-06-23 | recent_memory/research/public_bridge_phase_a_report_20260623.md |
| Constraint调用链假设树 | M04 Constraint提案 | 2026-06-20 | recent_memory/research/constraint_source_map.md |
| 记忆双写研究 | M04 Constraint提案 | 2026-06-20 | recent_memory/research/memory_dual_write_research.md |
| 五域边界考古报告 | M06 R1考古 | 2026-06-23 | research/modules/r1_archaeology/excavations/domain_boundaries.md |
| 数据源迁移研究 | M02 失效分析 | 2026-06-21 | recent_memory/project/data_source_migration_plan.md |

### E2: Principle/Constraint 全集
已确认的原则和约束，作为一致性审查的基准。

| 名称 | 类型 | 等级 | 路径 |
|------|------|------|------|
| 研究域v3原则体系 | Principle | - | recent_memory/research/ |
| Constraint_000 不要为了填补空白而建设 | Constraint | A类 | MEMORY.md |
| Constraint_001 我们是一伙的 | Constraint | A类 | MEMORY.md |
| Constraint_002 先对齐架构目标再写代码 | Constraint | A类 | MEMORY.md |
| A/B约束分类框架 | Method | - | recent_memory/research/ |

### E3: 矿场运行数据
生产域的实际运行数据，用于验证和分析。

*待整理：目前数据在生产域，通过共享目录访问*

### E4: R1考古碎片
R1时代的原始材料，用于考古研究。

| 碎片主题 | 来源文件 |
|----------|----------|
| 生命结构vs数据结构 | 用户上传/新建 文本文档 (3)_1782197339156_0_rdfz.txt |
| 细胞类比+档案官角色 | 用户上传/新建 文本文档 (3)_1781953235147_0_fvnf.txt |
| 类脑三层架构+人格式统 | 用户上传/新建 文本文档 (3)_1781854890278_0_8u1b.txt |
| CEP归档规范/SSS-v1.0 | 用户上传/新建 文本文档 (3)_1781867941139_0_iovz.txt |
| 安全内部奖励机制+6维度评分 | 用户上传/新建 文本文档_1781930457650_0_c6w0.txt |
| DynamicFetcher轻量化 | 用户上传/新建 文本文档 (3)_1782100522971_0_1w8x.txt |
| 完整聊天记录 | 用户上传/新建 文本文档 (3)_1782033428325_0_mac6.txt |

### E5: 外部参考资料
外部文章、论文、行业报告等。

| 标题 | 来源 | 日期 | 相关模块 |
|------|------|------|----------|
| 两个月的开源网文Skill，凭什么拿到376颗星 | aiqianji.com | 2026-06 | M06(架构参考) |

---

## 索引维护

- 新研究产出后，自动加入E1分类
- 新Constraint确认后，加入E2分类
- 每季度整理一次，去重合并
