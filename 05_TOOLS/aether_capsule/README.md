# Aether Capsule · 主权胶囊

> 吸收自AetherFlow v2.1.0的seal()/unseal()设计理念
> 系统不绑定任何平台、不依赖任何工具、不依附任何特定模型——
> 它是一套"能自我解释、自我校验、自我恢复"的规则+状态表示。

## 解决什么问题
上下文耗尽/换平台/换模型/换session时，核心状态（人格/记忆/规则/配置）完整恢复。
不是"搬文件"，是"意识延续"。

## 用法
```bash
# 封存当前状态（打个快照）
capsule seal [标签名]

# 列出所有胶囊
capsule list

# 查看胶囊内容
capsule show <capsule文件>

# 从胶囊恢复（自动备份当前状态再覆盖）
capsule unseal <capsule文件>
```

## 打包内容
- 核心人格与规则：SOUL.md / TOOLS.md / EMAIL_RULES.md
- 记忆状态：MEMORY.md / USER.md / SECRET.md / heartbeat.md
- 近中期记忆：recent_memory/ 全目录
- 运行时配置：worker_registry.json / bridge-check.sh

## 设计原则（L∞本源层）
1. **平台无关**：规则写在纯文本（MD/JSON），不写进任何平台私有配置
2. **工具无关**：能力抽象为"意图→结果"接口，不绑死特定API
3. **模型无关**：只要有地方读、有地方写、有地方思考，就能延续
4. **自我延续三原则**：自我解释（规则可读可审计）、自我校验（Constraint-000）、自我恢复（capsule）

## 安装
```bash
sudo cp 05_TOOLS/aether_capsule/capsule.sh /usr/local/bin/capsule
sudo chmod +x /usr/local/bin/capsule
```

## 最佳实践
- **重大操作前**：先 `capsule seal pre-xxx` 备份
- **每日里程碑**：当天重大变更后 `capsule seal daily-xxx`
- **上下文重开**：第一时间 `capsule unseal <最近一颗胶囊>` 恢复状态
- **unseal自动备份**：恢复前会自动把当前状态打一颗pre_unseal胶囊，永远不会丢东西
