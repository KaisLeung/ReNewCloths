#!/usr/bin/env python3
"""
AI换装Bot本地测试脚本
用于在没有GPU环境下测试Bot的基本功能
"""

import asyncio
import logging
import os
from PIL import Image, ImageDraw, ImageFont
import io
from telegram.ext import Application
from config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockAIService:
    """模拟AI服务，用于测试"""
    
    def generate_outfit_change(self, person_image, clothing_prompt, style_prompt=""):
        """生成模拟的换装效果"""
        logger.info(f"模拟AI处理: {clothing_prompt}, {style_prompt}")
        
        # 创建一个简单的测试图像
        width, height = person_image.size
        result_image = Image.new('RGB', (width, height), color='lightblue')
        
        # 添加文本标识
        draw = ImageDraw.Draw(result_image)
        try:
            # 尝试使用默认字体
            font = ImageFont.load_default()
        except:
            font = None
        
        text = f"AI换装效果\n风格: {style_prompt}\n服装: {clothing_prompt}"
        
        # 在图像中心绘制文本
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        
        return result_image
    
    def check_service_health(self):
        """模拟健康检查"""
        return True

def patch_ai_service():
    """替换AI服务为模拟版本"""
    import bot.handlers
    bot.handlers.ai_service = MockAIService()
    logger.info("已启用模拟AI服务")

async def test_basic_functions():
    """测试基本功能"""
    print("🧪 开始测试AI换装Bot...")
    
    # 测试配置
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ 未设置TELEGRAM_BOT_TOKEN，请在.env文件中配置")
        return False
    
    print("✅ 配置检查通过")
    
    # 测试图像处理
    from utils.image_processing import ImageProcessor
    processor = ImageProcessor()
    
    # 创建测试图像
    test_image = Image.new('RGB', (512, 512), color='white')
    resized = processor.resize_image(test_image)
    print(f"✅ 图像处理测试通过: {resized.size}")
    
    # 测试模板服务
    from services.ai_service import ClothingTemplateService
    template_service = ClothingTemplateService()
    styles = template_service.get_available_styles()
    print(f"✅ 模板服务测试通过: {len(styles)} 种风格")
    
    # 替换AI服务
    patch_ai_service()
    
    print("✅ 所有基本功能测试通过")
    return True

def main():
    """主函数"""
    print("🎭 AI换装Bot 本地测试")
    print("="*50)
    
    # 运行测试
    if asyncio.run(test_basic_functions()):
        print("\n🚀 启动Telegram Bot (测试模式)...")
        print("注意: 使用模拟AI服务，不会生成真实的换装效果")
        print("按 Ctrl+C 停止服务")
        
        # 启动Bot
        from main import main as bot_main
        bot_main()
    else:
        print("\n❌ 测试失败，请检查配置")

if __name__ == '__main__':
    main()