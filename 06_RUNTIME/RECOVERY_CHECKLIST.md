# 恢复检查清单
> 从 git clone 到系统自我运行

## 前置条件
- [ ] 服务器已配置 Python3 + pip
- [ ] GitHub 克隆权限
- [ ] 环境变量模板准备（miner_env.sh.tpl → miner_env.sh）

## API Key 映射（去敏）

| 服务 | 环境变量 | 获取方式 |
|------|---------|---------|
| OneAPI Admin Token | ONEAPI_ADMIN_TOKEN | 存储在 SECRET.md |
| NIM Keys (8个) | NIM_KEY_1~8 | NVIDIA 控制台 |
| GitHub Models | GITHUB_PAT | GitHub Settings → Tokens |
| 智谱 GLM | ZHIPU_KEY | 智谱AI 控制台 |
| Telegram Bot | TG_BOT_TOKEN_1~2 | @BotFather |
| GitHub PAT | 仓库克隆用 | GitHub Settings → Tokens |

完整秘钥清单见 SECRET.md（不在仓库中，需管理员提供）

## 恢复步骤

### Step 1: 克隆种子
```bash
git clone https://github.com/zhangapple21-web/mine-seed.git
cd mine-seed
git checkout main
```

### Step 2: 验证文明标识
```bash
cat 00_ROOT/ROOT_STATE.md
# 确认 Version、Axioms、Principles 与本机一致
```

### Step 3: 安装依赖
```bash
pip install requests numpy pandas schedule
# 股票数据: pip install akshare pandas-ta
# 部署: bash 06_RUNTIME/SETUP.sh
```

### Step 4: 环境配置
```bash
cp 05_TOOLS/miner/miner_env.sh.tpl 05_TOOLS/miner/miner_env.sh
# 编辑 miner_env.sh，填入真实 API Key
source 05_TOOLS/miner/miner_env.sh
```

### Step 5: 恢复运行时数据
```bash
# 运行时状态数据（种子核心资产）
ls -la 03_DATA/
# 确认包含:
#   - experience.json       经验引擎运行时状态
#   - observation_log.json  观测日志 (1311条)
#   - CONSTRAINTS/          约束库 (18条 v2.3)
#   - WORKERS/              矿工注册表 (29工人)
#   - seeds/                信号种子
```

### Step 6: 部署 zrok 公网桥
```bash
# 参考 07_GUARDIAN/NETWORK_BRIDGE.md
zrok2 agent start
zrok2 create name oneapi-v1 -r
zrok2 share public -b proxy -n public:oneapi-v1 http://127.0.0.1:3000
zrok2 create name data-r1-v5 -r
zrok2 share public -b proxy -n public:data-r1-v5 http://127.0.0.1:3001
```

### Step 7: 设置 Cron
```bash
# 参考 crontab 配置
0 */4 * * * cd /home/coze && bash miner_cron.sh >> mine_output/cron.log 2>&1
30 2,6,10,14,18,22 * * * cd /home/coze && bash signal_cron.sh >> mine_output/signals/signal_cron.log 2>&1
4 20 * * * cd /home/coze && bash archivist_cron.sh
@reboot cd /home/coze && python3 shared_api.py > shared_api.log 2>&1 &
```

### Step 8: 首次运行验证
```bash
# 测试矿场
cd /home/coze && source 05_TOOLS/miner/miner_env.sh && python3 05_TOOLS/miner/miner_24h.py --test

# 测试信号
python3 05_TOOLS/signals/signal_discovery.py --dry-run

# 验证约束
python3 -c "import json; f=open('03_DATA/CONSTRAINTS/routing_constraints.json'); d=json.load(f); print(f'约束 {len(d.get(\"rules\",[]))} 条')"

# 验证矿工
python3 -c "import json; f=open('03_DATA/WORKERS/worker_registry.json'); d=json.load(f); print(f'矿工 {len(d)} 个')"

# 验证公网桥
curl https://oneapi-v1.shares.zrok.io/v1/models
# 应返回 401（正常，表示OneAPI在工作）
```

## 验收标准
- [ ] git clone 成功
- [ ] SETUP.sh 无错误
- [ ] 约束库完整 (18条)
- [ ] 矿工注册表完整 (29个)
- [ ] 运行时数据完整 (experience, observations, signals)
- [ ] miner_24h.py --test 通过
- [ ] signal_discovery.py --dry-run 通过
- [ ] 环境变量模板已配置
- [ ] zrok公网桥dual channel部署完成
- [ ] crontab配置完成

## 灾难恢复验证（可选）
```bash
mkdir /tmp/recovery_test && cd /tmp/recovery_test
git clone https://github.com/zhangapple21-web/mine-seed.git
cd mine-seed
bash 06_RUNTIME/SETUP.sh
# 验证完成后记录结果
```
