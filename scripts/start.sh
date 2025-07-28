#!/bin/bash

echo "🚀 启动AI换装Bot..."

# 检查.env文件
if [ ! -f .env ]; then
    echo "❌ .env文件不存在，请先运行 ./scripts/setup.sh"
    exit 1
fi

# 检查TELEGRAM_BOT_TOKEN
if ! grep -q "TELEGRAM_BOT_TOKEN=.*[^[:space:]]" .env; then
    echo "❌ 请在.env文件中设置TELEGRAM_BOT_TOKEN"
    exit 1
fi

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示日志
echo "📝 显示最新日志..."
docker-compose logs --tail=20

echo "✅ 启动完成！"
echo ""
echo "📋 有用的命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"