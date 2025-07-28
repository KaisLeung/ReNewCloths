import logging
import os
import io
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from PIL import Image
from utils.image_processing import ImageProcessor
from services.ai_service import AIStyleTransferService, ClothingTemplateService

logger = logging.getLogger(__name__)

# 全局服务实例
image_processor = ImageProcessor()
ai_service = AIStyleTransferService()
template_service = ClothingTemplateService()

# 用户状态管理
user_sessions: Dict[int, Dict[str, Any]] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/start命令"""
    user_id = update.effective_user.id
    user_sessions[user_id] = {'state': 'waiting_for_image'}
    
    welcome_text = """
🎭 欢迎使用AI换装Bot！

📸 请发送您的照片，我将为您提供虚拟换装服务。

🎨 支持的换装风格：
• 休闲装 (Casual)
• 正装 (Formal) 
• 运动装 (Sporty)
• 复古装 (Vintage)

💡 使用方法：
1. 发送您的照片
2. 选择换装风格
3. 等待AI生成结果

注意：为了最佳效果，请使用清晰的半身或全身照片。
    """
    
    await update.message.reply_text(welcome_text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理用户上传的照片"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    try:
        # 下载照片
        photo = update.message.photo[-1]  # 获取最高质量的照片
        file = await context.bot.get_file(photo.file_id)
        
        # 下载到内存
        photo_bytes = io.BytesIO()
        await file.download_to_memory(photo_bytes)
        photo_bytes.seek(0)
        
        # 转换为PIL图像
        user_image = Image.open(photo_bytes).convert('RGB')
        
        # 预处理图像
        user_image = image_processor.resize_image(user_image)
        user_image = image_processor.remove_background(user_image)
        
        # 保存到用户会话
        user_sessions[user_id]['original_image'] = user_image
        user_sessions[user_id]['state'] = 'image_received'
        
        # 创建风格选择键盘
        keyboard = []
        styles = template_service.get_available_styles()
        
        for i in range(0, len(styles), 2):
            row = []
            row.append(InlineKeyboardButton(
                f"🎽 {styles[i].title()}", 
                callback_data=f"style_{styles[i]}"
            ))
            if i + 1 < len(styles):
                row.append(InlineKeyboardButton(
                    f"👔 {styles[i+1].title()}", 
                    callback_data=f"style_{styles[i+1]}"
                ))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📸 照片接收成功！已完成背景处理。\n\n"
            "🎨 请选择您想要的换装风格：",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"处理照片时出错: {e}")
        await update.message.reply_text(
            "❌ 处理照片时出现错误，请重新发送照片。\n"
            "确保照片清晰且文件大小适中。"
        )

async def handle_style_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理风格选择回调"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in user_sessions or 'original_image' not in user_sessions[user_id]:
        await query.edit_message_text("❌ 请先发送照片！")
        return
    
    # 解析选择的风格
    style = query.data.replace('style_', '')
    user_sessions[user_id]['selected_style'] = style
    
    # 获取该风格的服装选项
    clothing_options = template_service.get_clothing_prompts(style)
    
    # 创建服装选择键盘
    keyboard = []
    for i, clothing in enumerate(clothing_options):
        keyboard.append([InlineKeyboardButton(
            f"👕 {clothing}", 
            callback_data=f"clothing_{i}_{style}"
        )])
    
    # 添加返回按钮
    keyboard.append([InlineKeyboardButton("🔙 返回风格选择", callback_data="back_to_styles")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎨 您选择了 {style.title()} 风格\n\n"
        f"👔 请选择具体的服装类型：",
        reply_markup=reply_markup
    )

async def handle_clothing_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理具体服装选择"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in user_sessions or 'original_image' not in user_sessions[user_id]:
        await query.edit_message_text("❌ 请先发送照片！")
        return
    
    # 解析选择
    parts = query.data.split('_', 2)
    clothing_index = int(parts[1])
    style = parts[2]
    
    clothing_options = template_service.get_clothing_prompts(style)
    selected_clothing = clothing_options[clothing_index]
    
    user_sessions[user_id]['selected_clothing'] = selected_clothing
    
    await query.edit_message_text("🔄 正在生成您的换装效果，请稍候...")
    
    # 开始AI处理
    try:
        original_image = user_sessions[user_id]['original_image']
        
        # 使用AI服务生成换装效果
        result_image = ai_service.generate_outfit_change(
            person_image=original_image,
            clothing_prompt=selected_clothing,
            style_prompt=f"{style} style"
        )
        
        if result_image:
            # 转换为字节流发送
            output_buffer = io.BytesIO()
            result_image.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=output_buffer,
                caption=f"✨ 换装完成！\n\n"
                       f"🎨 风格: {style.title()}\n"
                       f"👔 服装: {selected_clothing}\n\n"
                       f"💡 发送新照片继续体验！"
            )
            
            # 重置用户状态
            user_sessions[user_id] = {'state': 'waiting_for_image'}
            
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ 生成换装效果失败，请稍后再试。\n"
                     "可能是AI服务暂时不可用。"
            )
            
    except Exception as e:
        logger.error(f"AI处理失败: {e}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❌ 处理过程中出现错误，请重新尝试。"
        )

async def handle_back_to_styles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """返回风格选择"""
    query = update.callback_query
    await query.answer()
    
    # 重新显示风格选择
    keyboard = []
    styles = template_service.get_available_styles()
    
    for i in range(0, len(styles), 2):
        row = []
        row.append(InlineKeyboardButton(
            f"🎽 {styles[i].title()}", 
            callback_data=f"style_{styles[i]}"
        ))
        if i + 1 < len(styles):
            row.append(InlineKeyboardButton(
                f"👔 {styles[i+1].title()}", 
                callback_data=f"style_{styles[i+1]}"
            ))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎨 请选择您想要的换装风格：",
        reply_markup=reply_markup
    )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理帮助命令"""
    help_text = """
🤖 AI换装Bot使用指南

📋 功能说明：
• 上传照片进行虚拟换装
• 支持多种服装风格
• 自动背景处理
• 高质量AI生成

🎨 支持的风格：
• 休闲装 - 日常穿搭
• 正装 - 商务正式
• 运动装 - 健身运动  
• 复古装 - 复古时尚

📸 照片建议：
• 使用清晰的半身或全身照
• 光线充足，背景简单
• 人物姿态自然
• 文件大小不超过20MB

⚡ 命令列表：
/start - 开始使用
/help - 查看帮助
/status - 检查服务状态

💡 提示：处理时间约30-60秒，请耐心等待。
    """
    
    await update.message.reply_text(help_text)

async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """检查服务状态"""
    status_text = "🔍 正在检查服务状态...\n\n"
    
    # 检查AI服务
    ai_status = "✅ 正常" if ai_service.check_service_health() else "❌ 不可用"
    
    status_text += f"🤖 AI服务: {ai_status}\n"
    status_text += f"📊 活跃用户: {len(user_sessions)}\n"
    status_text += f"🎨 可用风格: {len(template_service.get_available_styles())}\n"
    
    await update.message.reply_text(status_text)

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理未知消息"""
    await update.message.reply_text(
        "🤔 抱歉，我不理解这个命令。\n\n"
        "📸 请发送照片开始换装，或使用 /help 查看帮助。"
    )