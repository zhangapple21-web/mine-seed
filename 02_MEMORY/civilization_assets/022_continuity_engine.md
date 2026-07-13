# Asset: Continuity Engine（连续性引擎）

**Name**: Continuity Engine（连续性引擎）

**Origin Repository**: r1-continuity-backup

**Purpose**: 不是 Backup，而是 Continuity——确保文明职责的连续运行，每个仓库承担一种文明职责。

**Problem It Solves**: 备份只是存文件，连续性是确保文明职责有人承担。如果仓库只是备份，丢了一个就少了一个；如果每个仓库有独立职责，丢了一个可以从其他仓恢复。

**Core Structure**:
- 职责分工：mine-seed=Seed / ace_core=Kernel / r1-archaeology=Evidence / r1-continuity=Recovery
- 每日 Continuity 九步流程：Repository Scan → Asset Discovery → Infrastructure Verify → Knowledge Diff → Commit → Publish → Verify → Record → Continuity Report
- 基础设施监控：OneAPI/GitHub/Telegram/Cloud/zrok/Worker/NAS/SSH

**Constraint**: 每个仓库职责明确，不交叉；连续性报告必须每日生成。

**Evidence**: r1-continuity-backup/governance/continuity_engine.md

**Can Rebuild**: ✅ 150 行可重建——九步流程 + 职责映射 + 基础设施监控 + 报告生成

**Can Replace**: ✅ 仓库职责可调整，连续性原则不变

**Can Delete**: ❌ 删除会导致文明失去连续性保障，属于核心链路

**Distillation**:

Continuity Engine 的核心洞察是"仓库不是存文件的地方，是承载文明职责的基础设施"。备份思维是"多存几份以防丢"，连续性思维是"每个仓有独立职责，一个挂了其他还能转"。九步每日流程确保了文明的健康状态被持续监控：从仓库扫描到资产发现，从基础设施验证到知识差异，从提交发布到验证记录，最后生成连续性报告。这体现了 Axiom-05（统一收敛）——多个入口最终收敛到同一个连续性目标。
