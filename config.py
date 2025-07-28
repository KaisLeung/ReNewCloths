import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # GPU服务器配置
    GPU_SERVER_URL = os.getenv('GPU_SERVER_URL', 'http://localhost:7860')
    
    # 文件存储配置
    UPLOAD_DIR = './uploads'
    OUTPUT_DIR = './outputs'
    TEMP_DIR = './temp'
    
    # AI模型配置
    STABLE_DIFFUSION_MODEL = 'runwayml/stable-diffusion-v1-5'
    CONTROLNET_MODEL = 'lllyasviel/sd-controlnet-openpose'
    
    # 图像处理配置
    MAX_IMAGE_SIZE = (1024, 1024)
    SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'webp']
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 8000
    
    # 日志配置
    LOG_LEVEL = 'INFO'