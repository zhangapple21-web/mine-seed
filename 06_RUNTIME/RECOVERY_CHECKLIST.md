# 恢复检查清单
> 从 git clone 到系统自我运行

## 前置条件
- [ ] 服务器已配置 Python3 + pip
- [ ] GitHub 克隆权限
- [ ] 环境变量模板准备（miner_env.sh.tpl → miner_env.sh）
- [ ] 各 API Key 可获取（参考 SECRET.md 或管理员）

## 恢复步骤

### Step 1: 克隆种子
```bash
git clone https://github.com/zhangapple21-web/mine-seed.git
cd mine-seed
```

### Step 2: 验证文明标识
```bash
cat 00_ROOT/ROOT_STATE.md
# 确认 Version、Axioms、Principles 与本机一致
```

### Step 3: 环境配置
```bash
cp 05_TOOLS/miner/miner_env.sh.tpl 05_TOOLS/miner/miner_env.sh
# 编辑 miner_env.sh，填入真实 API Key
bash 06_RUNTIME/SETUP.sh
```

### Step 4: 设置 Cron
```bash
crontab 06_RUNTIME/CRONTAB.md  # 参考配置手动设置
```

### Step 5: 首次运行验证
```bash
# 测试矿场
cd /home/coze && python3 05_TOOLS/miner/miner_24h.py --test

# 测试信号
python3 05_TOOLS/signals/signal_discovery.py --dry-run

# 验证约束
python3 -c "import json; f=open('03_DATA/CONSTRAINTS/routing_constraints.json'); print(f'约束 {len(json.load(f)[\"constraints\"])} 条')"
```

### Step 6: 灾难恢复演练（可选）
```bash
mkdir /tmp/recovery_test
cd /tmp/recovery_test
git clone https://github.com/zhangapple21-web/mine-seed.git
cd mine-seed
bash 06_RUNTIME/SETUP.sh
# 记录结果至 DISASTER_RECOVERY_REPORT.md
```

## 验收标准
- [ ] git clone 成功
- [ ] SETUP.sh 无错误
- [ ] 约束库完整
- [ ] miner_24h.py --test 通过
- [ ] signal_discovery.py --dry-run 通过
- [ ] 环境变量模板已配置
