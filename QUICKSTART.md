# 🚀 AI换装Bot 快速启动指南

## 📋 准备工作

### 1. 获取Telegram Bot Token
1. 在Telegram中搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新Bot
3. 按提示设置Bot名称和用户名  
4. 保存获得的Token

### 2. 环境要求
- Docker 和 Docker Compose (推荐)
- 或者 Python 3.11+ (本地运行)
- NVIDIA GPU (可选，用于真实AI推理)

## 🐳 Docker部署 (推荐)

### 第一步：项目设置
```bash
# 克隆项目
git clone <your-repo-url>
cd ai-outfit-bot

# 运行设置脚本
./scripts/setup.sh
```

### 第二步：配置Token
编辑 `.env` 文件，添加您的Token：
```env
TELEGRAM_BOT_TOKEN=your_actual_token_here
```

### 第三步：启动服务
```bash
# 一键启动
./scripts/start.sh

# 或手动启动
docker-compose up -d
```

### 第四步：查看状态
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 💻 本地测试运行

如果您没有GPU或Docker环境，可以使用本地测试模式：

```bash
# 设置环境
./scripts/setup.sh

# 配置.env文件
nano .env  # 添加TELEGRAM_BOT_TOKEN

# 本地测试运行
./scripts/test_local.sh
```

本地测试模式会使用模拟AI服务，不会生成真实的换装效果，但可以测试Bot的基本交互功能。

## ☁️ 云端部署

### AWS自动部署
```bash
# 配置AWS CLI
aws configure

# 自动部署到AWS
./scripts/deploy_aws.sh
```

### 手动云端部署
1. 创建GPU实例 (g4dn.xlarge或更高)
2. 安装Docker和NVIDIA Docker
3. 克隆项目并按上述步骤配置

## 🎮 使用Bot

### 基本命令
- `/start` - 开始使用
- `/help` - 查看帮助
- `/status` - 检查服务状态

### 换装流程
1. 发送您的照片
2. 选择换装风格 (休闲/正装/运动/复古)
3. 选择具体服装类型
4. 等待AI生成结果

## 🔧 常见问题

### Bot无响应
```bash
# 检查Token是否正确
cat .env | grep TELEGRAM_BOT_TOKEN

# 重启服务
docker-compose restart
```

### GPU服务启动失败
```bash
# 检查GPU
nvidia-smi

# 检查NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi
```

### 依赖安装失败
```bash
# 更新Docker
sudo apt update && sudo apt install docker.io docker-compose

# 或使用本地Python环境
pip3 install -r requirements.txt
```

## 📊 服务状态检查

### Docker环境
```bash
# 服务状态
docker-compose ps

# 资源使用
docker stats

# 详细日志
docker-compose logs telegram-bot
docker-compose logs gpu-server
```

### 本地环境
```bash
# 运行测试
python3 test_local.py

# 检查进程
ps aux | grep python
```

## 🛑 停止服务

```bash
# Docker
docker-compose down

# 本地
# 按 Ctrl+C 停止
```

## 📞 获取帮助

如果遇到问题：
1. 查看日志文件
2. 检查网络连接
3. 确认配置文件
4. 提交Issue到项目仓库

---

🎉 现在您可以开始使用AI换装Bot了！发送照片给Bot开始体验虚拟换装服务。