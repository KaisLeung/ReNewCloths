import cv2
import numpy as np
from PIL import Image
import io
import base64
from rembg import remove
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.max_size = (1024, 1024)
    
    def resize_image(self, image: Image.Image, max_size: Tuple[int, int] = None) -> Image.Image:
        """调整图像大小，保持宽高比"""
        if max_size is None:
            max_size = self.max_size
            
        # 计算新的尺寸
        width, height = image.size
        max_width, max_height = max_size
        
        # 计算缩放比例
        scale = min(max_width / width, max_height / height)
        
        if scale < 1:
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """使用rembg移除背景"""
        try:
            # 转换为字节
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # 移除背景
            output = remove(img_byte_arr)
            
            # 转换回PIL Image
            result = Image.open(io.BytesIO(output))
            return result.convert('RGBA')
        except Exception as e:
            logger.error(f"背景移除失败: {e}")
            return image.convert('RGBA')
    
    def extract_person_mask(self, image: Image.Image) -> Image.Image:
        """提取人物遮罩"""
        # 转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 使用Canny边缘检测
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # 形态学操作
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # 转换回PIL格式
        mask_pil = Image.fromarray(mask).convert('L')
        return mask_pil
    
    def segment_clothing(self, image: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """分割服装区域"""
        # 这里简化实现，实际可以使用更复杂的分割模型
        # 上半身区域 (简单的基于位置的分割)
        width, height = image.size
        
        # 上半身遮罩 (大概在图像的上半部分)
        upper_mask = Image.new('L', (width, height), 0)
        upper_region = Image.new('L', (width, height//2), 255)
        upper_mask.paste(upper_region, (0, height//4))
        
        # 下半身遮罩
        lower_mask = Image.new('L', (width, height), 0)
        lower_region = Image.new('L', (width, height//2), 255)
        lower_mask.paste(lower_region, (0, height//2))
        
        return upper_mask, lower_mask
    
    def apply_clothing_template(self, person_image: Image.Image, 
                              clothing_template: Image.Image,
                              mask: Image.Image) -> Image.Image:
        """将服装模板应用到人物图像上"""
        # 调整模板尺寸
        clothing_resized = clothing_template.resize(person_image.size, Image.Resampling.LANCZOS)
        
        # 创建合成图像
        result = person_image.copy()
        result.paste(clothing_resized, (0, 0), mask)
        
        return result
    
    def enhance_image(self, image: Image.Image) -> Image.Image:
        """图像增强处理"""
        # 转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 应用CLAHE (对比度限制自适应直方图均衡化)
        lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # 转换回PIL格式
        return Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
    
    def image_to_base64(self, image: Image.Image) -> str:
        """将PIL图像转换为base64字符串"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def base64_to_image(self, base64_str: str) -> Image.Image:
        """将base64字符串转换为PIL图像"""
        img_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(img_data))
        return image