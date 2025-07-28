import requests
import io
import base64
from PIL import Image
from typing import Optional, Dict, Any
import logging
from config import Config

logger = logging.getLogger(__name__)

class AIStyleTransferService:
    def __init__(self):
        self.gpu_server_url = Config.GPU_SERVER_URL
        self.model_name = Config.STABLE_DIFFUSION_MODEL
        
    def generate_outfit_change(self, 
                             person_image: Image.Image,
                             clothing_prompt: str,
                             style_prompt: str = "",
                             negative_prompt: str = "blurry, low quality, distorted") -> Optional[Image.Image]:
        """使用AI生成换装效果"""
        try:
            # 准备请求数据
            img_base64 = self._image_to_base64(person_image)
            
            payload = {
                "init_images": [img_base64],
                "prompt": f"{clothing_prompt}, {style_prompt}, high quality, detailed, realistic",
                "negative_prompt": negative_prompt,
                "steps": 30,
                "cfg_scale": 7.5,
                "width": 512,
                "height": 768,
                "denoising_strength": 0.7,
                "sampler_name": "DPM++ 2M Karras"
            }
            
            # 发送到GPU服务器
            response = requests.post(
                f"{self.gpu_server_url}/sdapi/v1/img2img",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'images' in result and result['images']:
                    # 解码第一张图像
                    img_data = base64.b64decode(result['images'][0])
                    return Image.open(io.BytesIO(img_data))
            else:
                logger.error(f"AI服务请求失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"AI换装生成失败: {e}")
            
        return None
    
    def generate_with_controlnet(self,
                               person_image: Image.Image,
                               pose_image: Image.Image,
                               clothing_prompt: str) -> Optional[Image.Image]:
        """使用ControlNet进行精确的换装生成"""
        try:
            person_b64 = self._image_to_base64(person_image)
            pose_b64 = self._image_to_base64(pose_image)
            
            payload = {
                "init_images": [person_b64],
                "prompt": f"{clothing_prompt}, high quality, detailed, fashion photography",
                "negative_prompt": "blurry, low quality, distorted, deformed",
                "steps": 25,
                "cfg_scale": 7.0,
                "width": 512,
                "height": 768,
                "denoising_strength": 0.6,
                "controlnet_args": [
                    {
                        "input_image": pose_b64,
                        "module": "openpose",
                        "model": "control_v11p_sd15_openpose",
                        "weight": 1.0,
                        "guidance_start": 0.0,
                        "guidance_end": 1.0
                    }
                ]
            }
            
            response = requests.post(
                f"{self.gpu_server_url}/controlnet/img2img",
                json=payload,
                timeout=150
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'images' in result and result['images']:
                    img_data = base64.b64decode(result['images'][0])
                    return Image.open(io.BytesIO(img_data))
                    
        except Exception as e:
            logger.error(f"ControlNet生成失败: {e}")
            
        return None
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """将PIL图像转换为base64字符串"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    def check_service_health(self) -> bool:
        """检查AI服务是否可用"""
        try:
            response = requests.get(f"{self.gpu_server_url}/sdapi/v1/progress", timeout=10)
            return response.status_code == 200
        except:
            return False

class ClothingTemplateService:
    """服装模板服务"""
    def __init__(self):
        self.templates = {
            'casual': [
                'casual t-shirt and jeans',
                'hoodie and sweatpants',
                'polo shirt and chinos'
            ],
            'formal': [
                'business suit and tie',
                'formal dress',
                'blazer and dress pants'
            ],
            'sporty': [
                'athletic wear and sneakers',
                'gym clothes',
                'running outfit'
            ],
            'vintage': [
                'retro 80s style clothing',
                'vintage 90s outfit',
                'classic vintage dress'
            ]
        }
    
    def get_clothing_prompts(self, style: str) -> list:
        """获取指定风格的服装提示词"""
        return self.templates.get(style, self.templates['casual'])
    
    def get_available_styles(self) -> list:
        """获取所有可用的风格"""
        return list(self.templates.keys())