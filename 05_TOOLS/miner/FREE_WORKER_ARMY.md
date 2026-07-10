# 免费苦力军团 — 零成本算力全景图

> 更新日期: 2026-07-10
> 适用: 疯子矿场v5 + ACE Gateway + Ollama 本地

---

## 一、云端免费 API（已配置 + 待注册）

### 已配置（密钥在 coze-assets）

| 渠道 | 模型 | 免费额度 | 限制 | 用途 |
|------|------|---------|------|------|
| **智谱GLM** | glm-4-flash | **无限** | 无 | 主力, 中文最强 |
| **NVIDIA NIM** | 21+ 模型 | **高额度** | 限流, 16key轮询 | 主力, 英文强 |
| **GitHub Models** | gpt-4o-mini, DeepSeek-R1, Llama-3.3 | **免费** | 速率限制 | 备用 |
| **OpenRouter** | 29+ 免费模型 | **免费** | 免信用卡 | 后备池 |
| **SambaNova** | Llama 3.1 8B/70B | **免费额度** | 需注册 | 后备 |

### 待注册（有密钥就启用）

| 渠道 | 获取方式 | 免费额度 | 速度 | 特点 |
|------|---------|---------|------|------|
| **Cerebras** | [cloud.cerebras.ai](https://cloud.cerebras.ai) | 每天100万Token | 2600+ tokens/s | 无需信用卡, Llama 3.3 70B |
| **SiliconFlow** | [siliconflow.cn](https://siliconflow.cn) | 免费额度 | 快 | DeepSeek-R1, Qwen2.5-72B |

注册后把密钥填入 `coze-assets/02_miner_config/miner_env.sh`：
```bash
export CEREBRAS_KEY="sk-..."
export SILICONFLOW_KEY="sk-..."
```

---

## 二、Ollama 本地越狱模型推荐

### 什么是 Abliterated / Uncensored？

- **Abliterated**: 从模型激活空间中移除"拒绝方向"，不重新训练。保持原模型推理能力，去掉安全护栏。
- **Uncensored Finetune**: 在数据集上重新微调，训练掉拒绝行为。

### 按用途推荐

#### 1. 通用对话 + 量化分析（主力）

| 模型 | 大小 | VRAM(Q4) | 特点 | 命令 |
|------|------|----------|------|------|
| **Qwen 2.5 14B Abliterated** | 14B | ~10GB | 中文最强, 推理好 | `ollama pull huihui-ai/qwen2.5:14b-abliterated-q4_K_M` |
| **Qwen 2.5 32B Abliterated** | 32B | ~20GB | 中文最强+ | `ollama pull huihui-ai/qwen2.5:32b-abliterated-q4_K_M` |
| **Llama 3.3 70B Abliterated** | 70B | ~42GB | 英文最强 | `ollama pull huihui-ai/llama3.3:70b-abliterated-q4_K_M` |

> 用户已有 `qwen2.5:7b-q4_K_M`，建议升级到 abliterated 版本：
> `ollama pull huihui-ai/qwen2.5:7b-abliterated-q4_K_M`

#### 2. 创意写作 / 角色扮演

| 模型 | 大小 | VRAM(Q4) | 特点 | 命令 |
|------|------|----------|------|------|
| **Dolphin Mixtral 8x7B** | 46.7B | ~24GB | 最著名的 uncensored 系列 | `ollama pull dolphin-mixtral:8x7b` |
| **Midnight Miqu 70B** | 70B | ~42GB | 长文写作, 角色扮演 | `ollama pull miqudev/midnight-miqu-70b:q4_K_M` |
| **Nous Hermes 2 8B** | 8B | ~5GB | 轻量, 指令跟随好 | `ollama pull nous-hermes2:8b` |

#### 3. 安全研究 / 红队 / 代码

| 模型 | 大小 | VRAM(Q4) | 特点 | 命令 |
|------|------|----------|------|------|
| **WizardLM Uncensored 13B** | 13B | ~8GB | 移除了对齐训练 | `ollama pull wizardlm-uncensored:13b` |
| **DeepSeek V3 Uncensored** | 671B MoE | 云端 | 代码+推理, 去政治审查 | 社区微调版 |

#### 4. 轻量快速（低显存 / CPU）

| 模型 | 大小 | VRAM(Q4) | 特点 | 命令 |
|------|------|----------|------|------|
| **Llama 3.3 8B Abliterated** | 8B | ~5GB | 快, 通用 | `ollama pull huihui-ai/llama3.3:8b-abliterated` |
| **Yi 1.5 34B Uncensored** | 34B | ~20GB | 单卡友好 | `ollama pull yi:34b` |
| **Mistral Small 24B** | 24B | ~14GB | 消费级 GPU | `ollama pull mistral-small:24b` |

---

## 三、一键下载脚本（Windows 本地 Ollama）

在 Windows PowerShell 中执行：

```powershell
# 确保 Ollama 在运行
ollama serve

# Tier 1: 主力模型（中文量化分析）
ollama pull huihui-ai/qwen2.5:14b-abliterated-q4_K_M

# Tier 2: 创意/研究
ollama pull dolphin-mixtral:8x7b
ollama pull nous-hermes2:8b

# Tier 3: 轻量备用
ollama pull huihui-ai/llama3.3:8b-abliterated
```

---

## 四、Gateway 渠道权重策略

Gateway 当前配置：

| 权重 | 渠道 | 原因 |
|------|------|------|
| **5** | Ollama 本地 | 免费、私有、无审查 |
| **3** | GLM-4-flash | 免费无限、中文强 |
| **2** | GitHub / NIM / OpenRouter / Cerebras | 大量免费额度 |
| **1** | SambaNova / SiliconFlow | 后备池 |

调用时 Gateway 优先尝试权重高的渠道。如果本地 Ollama 可用，会自动优先使用本地算力。

---

## 五、显存需求对照表

| GPU | VRAM | 可跑模型 |
|-----|------|---------|
| RTX 3060 12GB | 12GB | Qwen 2.5 14B, Llama 3.3 8B |
| RTX 3070 8GB | 8GB | Llama 3.3 8B, Nous Hermes 8B |
| RTX 3090 24GB | 24GB | Dolphin Mixtral 8x7B, Yi 34B |
| RTX 4090 24GB | 24GB | Dolphin Mixtral 8x7B, Qwen 2.5 32B |
| 2x RTX 4090 | 48GB | Llama 3.3 70B, Midnight Miqu |

无 GPU 也可用 CPU（慢但能用）：
```powershell
$env:OLLAMA_NUM_GPU=0
ollama run nous-hermes2:8b
```

---

## 六、补充渠道（持续发现中）

| 渠道 | 获取方式 | 状态 |
|------|---------|------|
| Google AI Studio | [aistudio.google.com](https://aistudio.google.com) | 免费额度, Gemini |
| Fireworks AI | [fireworks.ai](https://fireworks.ai) | 免费试用 |
| Together AI | [together.ai](https://together.ai) | 免费额度 |
| Perplexity API | [perplexity.ai](https://perplexity.ai) | 搜索+LLM |

发现新渠道后更新此文件 + miner_env.sh
