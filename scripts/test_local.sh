#!/bin/bash

echo "🧪 AI换装Bot 本地测试"
echo "========================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

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

# 安装依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt --user

# 创建必要目录
mkdir -p uploads outputs temp

# 运行测试
echo "🚀 启动本地测试..."
python3 test_local.py