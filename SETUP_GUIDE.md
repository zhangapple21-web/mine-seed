# 疯子Agent 换设备复原指南

## 一、前置条件
1. 安装 Coze Agent on Cloud 或配置好云电脑
2. 安装 git
3. 确保可以访问 GitHub

## 二、克隆本仓库
```bash
git clone https://github.com/zhangapple21-web/coze-assets.git
cd coze-assets
```

## 三、恢复顺序

### 1. 恢复秘钥配置
- 将 01_credentials/SECRET.md 中的API Key写入对应位置
- 矿场环境变量参照 02_miner_config/miner_env.sh 配置

### 2. 恢复矿场配置
```bash
# 复制矿场核心配置文件到对应目录
cp 02_miner_config/miner_env.sh /home/coze/miner_env.sh
cp 02_miner_config/routing_constraints.json /home/coze/routing_constraints.json
cp 02_miner_config/worker_registry.json /home/coze/worker_registry.json
cp 02_miner_config/signal_registry.json /home/coze/mine_output/signals/signal_registry.json
```

### 3. 恢复Agent人设
- 03_agent_profile/ 下的 SOUL.md / TOOLS.md / USER.md / EMAIL_RULES.md
- 写入Agent工作目录 ./ 基础设定/ 下

### 4. 恢复zrok公网桥
```bash
# 复制systemd服务
cp 04_zrok/zrok-*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable zrok-mine-v6 zrok-data-r1-v6
systemctl start zrok-mine-v6 zrok-data-r1-v6
```

## 四、验证
```bash
# 检查矿场能否启动
source /home/coze/miner_env.sh
python3 -c "print('矿场环境就绪')"

# 检查OneAPI
curl -s http://localhost:3000/api/status

# 检查zrok公网
curl -s https://mine-v6.shares.zrok.io/api/status
```