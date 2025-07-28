# 🎭 AI换装Bot

一个基于Telegram的AI虚拟换装机器人，使用Stable Diffusion技术为用户提供智能换装服务。

## ✨ 功能特性

- 🤖 **Telegram Bot集成** - 通过Telegram直接使用
- 🎨 **多种服装风格** - 休闲、正装、运动、复古等风格
- 🖼️ **智能背景处理** - 自动抠图和背景移除
- 🚀 **GPU加速推理** - 支持CUDA加速的AI模型
- 🐳 **Docker部署** - 容器化部署，支持一键启动
- ☁️ **云端支持** - 支持AWS等云平台部署

## 🏗️ 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │───▶│   Bot Service   │───▶│   GPU Server    │
│                 │    │                 │    │                 │
│ • 用户交互      │    │ • 图像预处理    │    │ • AI推理       │
│ • 照片接收      │    │ • 背景移除      │    │ • Stable Diffusion │
│ • 结果展示      │    │ • 风格管理      │    │ • ControlNet    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- NVIDIA GPU (推荐，可选)
- NVIDIA Docker (如使用GPU)
- Telegram Bot Token

### 1. 获取Bot Token

1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新的Bot
3. 按提示设置Bot名称和用户名
4. 保存获得的Token

### 2. 克隆项目

```bash
git clone https://github.com/your-username/ai-outfit-bot.git
cd ai-outfit-bot
```

### 3. 配置环境

```bash
# 运行设置脚本
chmod +x scripts/setup.sh
./scripts/setup.sh

# 编辑环境变量
cp .env.example .env
nano .env  # 设置TELEGRAM_BOT_TOKEN
```

### 4. 启动服务

```bash
# 使用启动脚本
chmod +x scripts/start.sh
./scripts/start.sh

# 或者手动启动
docker-compose up -d
```

### 5. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f telegram-bot
docker-compose logs -f gpu-server
```

## 📁 项目结构

```
ai-outfit-bot/
├── bot/                    # Telegram Bot代码
│   ├── handlers.py        # 消息处理器
│   └── __init__.py
├── services/              # 业务服务
│   ├── ai_service.py      # AI推理服务
│   └── __init__.py
├── utils/                 # 工具模块
│   ├── image_processing.py # 图像处理
│   └── __init__.py
├── gpu_server/            # GPU服务器
│   ├── stable_diffusion_api.py # SD API服务
│   └── requirements.txt
├── docker/                # Docker配置
│   ├── Dockerfile.bot     # Bot服务Docker文件
│   └── Dockerfile.gpu     # GPU服务Docker文件
├── scripts/               # 部署脚本
│   ├── setup.sh          # 项目设置
│   ├── start.sh          # 启动脚本
│   └── deploy_aws.sh     # AWS部署
├── docker-compose.yml     # Docker Compose配置
├── requirements.txt       # Python依赖
├── config.py             # 配置文件
├── main.py               # 主程序
└── README.md             # 项目说明
```

## 🎮 使用指南

### Bot命令

- `/start` - 开始使用Bot
- `/help` - 查看帮助信息
- `/status` - 检查服务状态

### 换装流程

1. **发送照片** - 上传您的半身或全身照片
2. **选择风格** - 从休闲、正装、运动、复古中选择
3. **选择服装** - 选择具体的服装类型
4. **等待生成** - AI处理约30-60秒
5. **获取结果** - 接收换装后的照片

### 照片建议

- ✅ 使用清晰的半身或全身照
- ✅ 光线充足，背景简单
- ✅ 人物姿态自然
- ✅ 文件大小不超过20MB
- ❌ 避免模糊或过暗的照片

## ☁️ 云端部署

### AWS部署

```bash
# 配置AWS CLI
aws configure

# 运行部署脚本
chmod +x scripts/deploy_aws.sh
./scripts/deploy_aws.sh
```

部署脚本会自动：
- 创建EC2 GPU实例 (g4dn.xlarge)
- 配置安全组和密钥对
- 安装Docker和NVIDIA Docker
- 设置项目环境

### 手动云端配置

1. **创建GPU实例**
   ```bash
   # AWS
   aws ec2 run-instances --instance-type g4dn.xlarge --image-id ami-xxx
   
   # GCP
   gcloud compute instances create ai-outfit-bot --machine-type n1-standard-4 --accelerator type=nvidia-tesla-t4,count=1
   ```

2. **安装依赖**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose nvidia-docker2
   
   # CentOS/RHEL
   sudo yum install docker docker-compose nvidia-docker2
   ```

3. **配置NVIDIA Docker**
   ```bash
   sudo systemctl restart docker
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | sudo tee /etc/yum.repos.d/nvidia-docker.repo
   sudo yum install nvidia-docker2
   sudo systemctl restart docker
   ```

## 🔧 高级配置

### 自定义AI模型

在 `config.py` 中修改模型配置：

```python
# Stable Diffusion模型
STABLE_DIFFUSION_MODEL = 'runwayml/stable-diffusion-v1-5'

# ControlNet模型  
CONTROLNET_MODEL = 'lllyasviel/sd-controlnet-openpose'
```

### 添加新的服装风格

在 `services/ai_service.py` 中的 `ClothingTemplateService` 添加：

```python
self.templates = {
    'new_style': [
        'new clothing prompt 1',
        'new clothing prompt 2',
    ]
}
```

### 性能优化

1. **GPU内存优化**
   ```python
   pipe.enable_memory_efficient_attention()
   pipe.enable_xformers_memory_efficient_attention()
   ```

2. **模型量化**
   ```python
   pipe = pipe.to(torch.float16)  # 半精度
   ```

3. **批处理优化**
   ```python
   # 在ai_service.py中调整batch_size
   ```

## 📊 监控和日志

### 查看服务状态

```bash
# Docker服务状态
docker-compose ps

# 系统资源使用
docker stats

# GPU使用情况
nvidia-smi
```

### 日志管理

```bash
# 实时日志
docker-compose logs -f

# 保存日志到文件
docker-compose logs > logs/app.log

# 限制日志大小
docker-compose logs --tail=100
```

## 🐛 故障排除

### 常见问题

1. **Bot无响应**
   ```bash
   # 检查Token配置
   cat .env | grep TELEGRAM_BOT_TOKEN
   
   # 重启Bot服务
   docker-compose restart telegram-bot
   ```

2. **GPU服务失败**
   ```bash
   # 检查GPU可用性
   nvidia-smi
   
   # 检查CUDA版本
   docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi
   ```

3. **内存不足**
   ```bash
   # 释放GPU内存
   docker-compose restart gpu-server
   
   # 调整模型精度
   # 在config.py中设置torch.float16
   ```

4. **网络连接问题**
   ```bash
   # 检查服务间通信
   docker-compose exec telegram-bot curl http://gpu-server:7860/health
   ```

### 调试模式

启用详细日志：

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 重启服务
docker-compose restart
```

## 🛡️ 安全考虑

- 🔐 妥善保管Bot Token
- 🚫 不要在公开仓库中提交.env文件
- 🔒 限制GPU服务器的网络访问
- 👤 考虑用户权限和频率限制

## 📈 性能指标

- **处理时间**: 30-60秒/张图片
- **GPU内存**: 约6-8GB (高质量模式)
- **并发处理**: 取决于GPU内存大小
- **图片质量**: 512x768或1024x1024

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📝 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- 📧 邮件: your-email@example.com
- 🐛 问题报告: [GitHub Issues](https://github.com/your-username/ai-outfit-bot/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/your-username/ai-outfit-bot/discussions)

## 🎉 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Stable Diffusion](https://github.com/CompVis/stable-diffusion)
- [ControlNet](https://github.com/lllyasviel/ControlNet)
- [Diffusers](https://github.com/huggingface/diffusers)

---

<div align="center">
  Made with ❤️ by AI Outfit Bot Team
</div>
