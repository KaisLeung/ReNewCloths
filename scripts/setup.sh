#!/bin/bash

echo "🚀 设置AI换装Bot项目..."

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查NVIDIA Docker (如果使用GPU)
if command -v nvidia-smi &> /dev/null; then
    echo "✅ 检测到NVIDIA GPU"
    if ! docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi &> /dev/null; then
        echo "❌ NVIDIA Docker支持未正确配置"
        echo "请安装nvidia-docker2: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
        exit 1
    fi
    echo "✅ NVIDIA Docker配置正确"
else
    echo "⚠️  未检测到NVIDIA GPU，将使用CPU模式"
fi

# 创建必要目录
echo "📁 创建目录结构..."
mkdir -p uploads outputs temp models logs

# 复制环境变量文件
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 已创建.env文件，请编辑并填入您的配置"
    echo "⚠️  请确保设置TELEGRAM_BOT_TOKEN"
fi

# 设置权限
chmod +x scripts/*.sh

echo "✅ 项目设置完成！"
echo ""
echo "📋 下一步："
echo "1. 编辑 .env 文件，设置 TELEGRAM_BOT_TOKEN"
echo "2. 运行: docker-compose up -d"
echo "3. 查看日志: docker-compose logs -f"
echo ""
echo "🔗 获取Telegram Bot Token:"
echo "   https://t.me/BotFather"