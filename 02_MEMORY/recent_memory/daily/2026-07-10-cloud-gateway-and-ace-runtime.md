# 2026-07-10 — 云端 ACE Gateway 部署 + ACE Runtime 修复

## 今日成果

### 1. OneAPI Gateway 部署（云端/TRAE 沙箱）
- **背景**：疯子原生产环境在 Coze 容器 (`140.143.238.57`)，使用官方 `songquanpeng/one-api` v0.6.10
- **问题**：one-api 二进制在 TRAE 沙箱中卡在 `initializing token encoders`（tiktoken 下载阻塞）
- **解决方案**：用 Python FastAPI 实现等价网关 `ace_gateway.py`，核心功能对齐
  - OpenAI 兼容 `/v1/chat/completions` + `/v1/models`
  - 多渠道路由 + NIM 16 key 轮询
  - API Token 鉴权（对齐疯子的 miner-v2 / miner-token）
  - 管理接口 `/api/channel/` `/api/token/`

### 2. 渠道连通性验证
| 渠道 | 模型 | 状态 |
|------|------|------|
| Zhipu-GLM (#2) | glm-4-flash | ✅ 可用 |
| Zhipu-GLM (#2) | glm-4-air | ❌ 429 余额不足 |
| GitHub Models (#57) | gpt-4o-mini | ✅ 可用（换用 2026-07-02 新 PAT） |
| NVIDIA NIM (#59-66) | deepseek-v4-flash | ✅ 可用 |
| NVIDIA NIM (#59-66) | mistral-medium-3.5 | ✅ 可用 |
| NVIDIA NIM (#59-66) | llama-3.3-70b | ⚠️ 超时（NIM 端负载高） |
| OpenRouter (#7) | llama-3.3-70b:free | ✅ 可用（换用 Key #4） |

### 3. ACE Runtime 修复
- **问题**：`scheduler.py` 和 `task_roles.py` 接口不兼容
  - scheduler 传 `(identity, memory, event_bus, task_queue)`，调用 `node.process(task)`
  - task_roles 期望 `(task_pool, lexicon, ...)`，无 `process()` 方法
- **解决方案**：创建 `nodes/__init__.py` 适配层
  - `_BaseNodeAdapter` 桥接 scheduler 接口到 task_roles 接口
  - 每个节点（Observer/Researcher/Validator/Archivist）重写 `process(task_dict)`
  - TaskPool 使用独立目录避免与 TaskQueue 冲突
- **结果**：`ace.py test` 9/9 测试全部通过

### 4. 密钥管理
- 网关从 `coze-assets/02_miner_config/miner_env.sh` 自动加载 16 个 NIM Key + GLM Key + GitHub PAT
- GitHub PAT 更新为 SECRET.md 中 2026-07-02 的新 token（矿场下苦力专用）
- OpenRouter 更新为 Key #4（SECRET.md 中 2026-06-20 的 key）

## 关键文件
| 文件 | 位置 | 作用 |
|------|------|------|
| `ace_gateway.py` | `/workspace/one-api-data/` | OpenAI 兼容路由网关 |
| `nodes/__init__.py` | `ace_core/nodes/` | scheduler ↔ task_roles 适配层 |
| `nodes/observer.py` | `ace_core/nodes/` | 观察者节点适配器 |
| `nodes/researcher.py` | `ace_core/nodes/` | 研究员节点适配器 |
| `nodes/validator.py` | `ace_core/nodes/` | 验证者节点适配器 |
| `nodes/archivist.py` | `ace_core/nodes/` | 档案官节点适配器 |

## 双轨定位
- **Windows 本地**（另一个 agent）：观测站 + 备份点
- **云端 TRAE**（本 agent）：执行节点 — Gateway + ACE Runtime
- lab_01 (Coze 容器) zrok 隧道仍 502，需在容器内修复

## 下一步
- [ ] 把 `ace_gateway.py` 和 `nodes/` 适配层提交到 mine-seed
- [ ] 加载疯子/小疯子身份到 ACE Runtime
- [ ] 接入 LLM Router 到 ACE Gateway（让 ACE 可以调用模型）
- [ ] 监控 NIM key 消耗和渠道健康状态
