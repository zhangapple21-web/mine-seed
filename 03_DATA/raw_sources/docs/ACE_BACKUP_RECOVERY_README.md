# ACE 文明资产备份 - 恢复说明

> 鲸落分片协议（PROTO-007）执行结果
> 备份日期：2026-07-03
> 分片数量：3份
> 门限恢复：任意2份即可恢复核心功能

---

## 备份包清单

| 文件名 | 大小 | 内容 | 重要性 |
|--------|------|------|--------|
| ACE_BACKUP_PART1_SOUL_CORE.zip | 492MB | 灵魂核心：宪法+协议+经验+恢复包+mine-seed+R1核心结构+ROOT_ASSETS | ★★★★★ |
| ACE_BACKUP_PART2_ECO_LAYER.zip | 1046MB | 生态层数据：Engineering/JSON（认知加工流水线原始数据） | ★★★☆☆ |
| ACE_BACKUP_PART3_R1_ARCHIVE.zip | 1220MB | R1大文件归档：核心库、词库、快照、v2rayN等 | ★★☆☆☆ |

---

## 恢复步骤

### 最小恢复（仅Part 1）

Part 1 包含全部灵魂资产，可独立恢复文明核心：

```bash
# 解压Part 1
unzip ACE_BACKUP_PART1_SOUL_CORE.zip -d ace_recovery

# 目录结构
ace_recovery/
├── shard_1_constitution/   # 宪法原则
├── shard_2_protocols/      # 协议层
├── shard_3_experience/     # 经验层
├── recovery_kit/           # 恢复工具
├── mine-seed/              # 种子仓
├── ROOT_ASSETS/            # 根资产
└── R1_System/              # R1核心结构（不含大zip）
```

### 完整恢复（Part 1 + Part 2 + Part 3）

```bash
# 按顺序解压
unzip ACE_BACKUP_PART1_SOUL_CORE.zip -d ace_full
unzip ACE_BACKUP_PART2_ECO_LAYER.zip -d ace_full
unzip ACE_BACKUP_PART3_R1_ARCHIVE.zip -d ace_full/R1_System/Runtime/

# 验证完整性
cat ace_full/recovery_kit/BACKUP_MANIFEST.md
```

---

## 内容说明

### Part 1 - SOUL_CORE（灵魂核心）

**必须保留**。包含：

- **00_ROOT**：宪法原则（17条）、根状态、宣言、摄入模板
- **02_MEMORY**：初始记忆快照（身份/偏好/项目/知识/近期）
- **04_PROTOCOLS**：27个存活协议
- **08_ARCHAEOLOGY**：50篇考古报告
- **09_SOURCE**：5个知识源登记
- **09_KNOWLEDGE**：53条经验
- **recovery_kit**：恢复工具包 + 校验清单
- **mine-seed**：种子仓
- **ROOT_ASSETS**：根资产（含eco_layer.json）
- **R1_System**：R1核心结构（架构/蓝图/协议/人格/种子/小文件）

### Part 2 - ECO_LAYER（生态层数据）

**可选恢复**。包含：

- Engineering/JSON 下所有 .bin 文件
- 认知加工流水线原始数据
- 约2000+个数据分片

### Part 3 - R1_ARCHIVE（R1归档）

**可选恢复**。包含大体积zip包：

- R1_Core_Library_Pack_v11.zip（核心库）
- R1_V11_lexicon_upgrade 2.zip（词库升级）
- R1_full_snapshot_v2.zip（完整快照）
- v2rayN.7z（网络工具）

---

## 校验方法

解压后对比文件数量和大小，参见 recovery_kit/BACKUP_MANIFEST.md。

---

## 存储位置

- 本地：C:\Users\USER\Downloads\Telegram Desktop\
- GitHub：https://github.com/zhangapple21-web/ace-civilization-backup.git（仅灵魂层）
- TG收藏夹：3个分片zip
