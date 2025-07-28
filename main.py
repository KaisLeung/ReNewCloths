import logging
import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters
)
from config import Config
from bot.handlers import (
    start, 
    handle_photo, 
    handle_style_selection,
    handle_clothing_selection,
    handle_back_to_styles,
    handle_help,
    handle_status,
    handle_unknown
)

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

def setup_directories():
    """创建必要的目录"""
    directories = [Config.UPLOAD_DIR, Config.OUTPUT_DIR, Config.TEMP_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    logger.info("目录设置完成")

def main():
    """主函数"""
    # 检查配置
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("未设置TELEGRAM_BOT_TOKEN环境变量")
        return
    
    # 设置目录
    setup_directories()
    
    # 创建应用
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # 添加处理器
    
    # 命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("status", handle_status))
    
    # 照片处理器
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # 回调查询处理器
    application.add_handler(CallbackQueryHandler(
        handle_style_selection, 
        pattern=r"^style_"
    ))
    application.add_handler(CallbackQueryHandler(
        handle_clothing_selection, 
        pattern=r"^clothing_"
    ))
    application.add_handler(CallbackQueryHandler(
        handle_back_to_styles, 
        pattern="^back_to_styles$"
    ))
    
    # 未知消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))
    
    logger.info("🤖 AI换装Bot启动中...")
    logger.info(f"🔗 Bot Token: {Config.TELEGRAM_BOT_TOKEN[:20]}...")
    logger.info(f"🖥️  GPU服务器: {Config.GPU_SERVER_URL}")
    
    # 启动Bot
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()