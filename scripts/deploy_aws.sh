#!/bin/bash

echo "☁️  部署到AWS..."

# 检查AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI未安装，请先安装并配置"
    exit 1
fi

# 配置变量
INSTANCE_TYPE="g4dn.xlarge"  # GPU实例类型
AMI_ID="ami-0c02fb55956c7d316"  # Amazon Linux 2 with GPU support
KEY_NAME="ai-outfit-bot-key"
SECURITY_GROUP="ai-outfit-bot-sg"
REGION="us-east-1"

echo "🔧 配置AWS资源..."

# 创建密钥对 (如果不存在)
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION &> /dev/null; then
    echo "🔑 创建密钥对..."
    aws ec2 create-key-pair --key-name $KEY_NAME --region $REGION --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
fi

# 创建安全组 (如果不存在)
if ! aws ec2 describe-security-groups --group-names $SECURITY_GROUP --region $REGION &> /dev/null; then
    echo "🔒 创建安全组..."
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP \
        --description "AI Outfit Bot Security Group" \
        --region $REGION \
        --query 'GroupId' --output text)
    
    # 添加入站规则
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 7860 \
        --cidr 0.0.0.0/0 \
        --region $REGION
fi

# 创建用户数据脚本
cat > user-data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y docker git

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 安装NVIDIA Docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | tee /etc/yum.repos.d/nvidia-docker.repo
yum install -y nvidia-docker2
systemctl restart docker

# 启动Docker
systemctl start docker
systemctl enable docker

# 克隆项目
cd /home/ec2-user
git clone https://github.com/your-username/ai-outfit-bot.git
cd ai-outfit-bot

# 设置权限
chown -R ec2-user:ec2-user /home/ec2-user/ai-outfit-bot
EOF

echo "🚀 启动EC2实例..."

# 启动实例
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-groups $SECURITY_GROUP \
    --user-data file://user-data.sh \
    --region $REGION \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "📋 实例ID: $INSTANCE_ID"

# 等待实例运行
echo "⏳ 等待实例启动..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# 获取公网IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ 部署完成！"
echo ""
echo "📋 连接信息:"
echo "  实例ID: $INSTANCE_ID"
echo "  公网IP: $PUBLIC_IP"
echo "  SSH连接: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo "  GPU服务: http://$PUBLIC_IP:7860"
echo ""
echo "🔧 下一步:"
echo "1. SSH连接到服务器"
echo "2. 编辑.env文件设置TELEGRAM_BOT_TOKEN"
echo "3. 运行: docker-compose up -d"

# 清理临时文件
rm -f user-data.sh