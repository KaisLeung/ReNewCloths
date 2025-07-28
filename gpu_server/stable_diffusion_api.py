import torch
import io
import base64
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionControlNetImg2ImgPipeline
from controlnet_aux import OpenposeDetector
from diffusers import ControlNetModel
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI换装GPU服务", version="1.0.0")

# 全局变量存储模型
pipe = None
controlnet_pipe = None
openpose = None

class Img2ImgRequest(BaseModel):
    init_images: List[str]
    prompt: str
    negative_prompt: str = "blurry, low quality, distorted"
    steps: int = 30
    cfg_scale: float = 7.5
    width: int = 512
    height: int = 768
    denoising_strength: float = 0.7
    sampler_name: str = "DPM++ 2M Karras"

class ControlNetRequest(BaseModel):
    init_images: List[str]
    prompt: str
    negative_prompt: str = "blurry, low quality, distorted"
    steps: int = 25
    cfg_scale: float = 7.0
    width: int = 512
    height: int = 768
    denoising_strength: float = 0.6
    controlnet_args: List[dict]

class ProgressResponse(BaseModel):
    progress: float
    eta_relative: float

def load_models():
    """加载AI模型"""
    global pipe, controlnet_pipe, openpose
    
    try:
        logger.info("正在加载Stable Diffusion模型...")
        
        # 基础Stable Diffusion模型
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            safety_checker=None,
            requires_safety_checker=False
        )
        pipe = pipe.to("cuda")
        pipe.enable_memory_efficient_attention()
        
        logger.info("Stable Diffusion模型加载完成")
        
        # ControlNet模型
        logger.info("正在加载ControlNet模型...")
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-openpose",
            torch_dtype=torch.float16
        )
        
        controlnet_pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=torch.float16,
            safety_checker=None,
            requires_safety_checker=False
        )
        controlnet_pipe = controlnet_pipe.to("cuda")
        controlnet_pipe.enable_memory_efficient_attention()
        
        # OpenPose检测器
        openpose = OpenposeDetector.from_pretrained('lllyasviel/Annotators')
        
        logger.info("所有模型加载完成")
        
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        raise

def base64_to_image(base64_str: str) -> Image.Image:
    """将base64转换为PIL图像"""
    img_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(img_data))
    return image.convert('RGB')

def image_to_base64(image: Image.Image) -> str:
    """将PIL图像转换为base64"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

@app.on_event("startup")
async def startup_event():
    """服务启动时加载模型"""
    if torch.cuda.is_available():
        logger.info(f"检测到GPU: {torch.cuda.get_device_name()}")
        load_models()
    else:
        logger.warning("未检测到GPU，某些功能可能无法使用")

@app.get("/")
async def root():
    return {"message": "AI换装GPU服务运行中", "status": "healthy"}

@app.get("/sdapi/v1/progress")
async def get_progress():
    """获取处理进度 (兼容Automatic1111 API)"""
    return ProgressResponse(progress=0.0, eta_relative=0.0)

@app.post("/sdapi/v1/img2img")
async def img2img(request: Img2ImgRequest):
    """图像到图像转换API"""
    global pipe
    
    if pipe is None:
        raise HTTPException(status_code=503, detail="模型未加载")
    
    try:
        # 解码输入图像
        if not request.init_images:
            raise HTTPException(status_code=400, detail="需要提供初始图像")
        
        init_image = base64_to_image(request.init_images[0])
        init_image = init_image.resize((request.width, request.height))
        
        logger.info(f"开始处理图像: {request.prompt}")
        
        # 生成图像
        with torch.autocast("cuda"):
            result = pipe(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                image=init_image,
                strength=request.denoising_strength,
                num_inference_steps=request.steps,
                guidance_scale=request.cfg_scale,
                width=request.width,
                height=request.height
            )
        
        # 转换结果
        output_images = []
        for img in result.images:
            output_images.append(image_to_base64(img))
        
        logger.info("图像处理完成")
        
        return {
            "images": output_images,
            "parameters": request.dict()
        }
        
    except Exception as e:
        logger.error(f"图像处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/controlnet/img2img")
async def controlnet_img2img(request: ControlNetRequest):
    """ControlNet图像处理API"""
    global controlnet_pipe, openpose
    
    if controlnet_pipe is None or openpose is None:
        raise HTTPException(status_code=503, detail="ControlNet模型未加载")
    
    try:
        # 解码输入图像
        if not request.init_images:
            raise HTTPException(status_code=400, detail="需要提供初始图像")
        
        init_image = base64_to_image(request.init_images[0])
        init_image = init_image.resize((request.width, request.height))
        
        # 生成OpenPose
        pose_image = openpose(init_image)
        
        logger.info(f"开始ControlNet处理: {request.prompt}")
        
        # 生成图像
        with torch.autocast("cuda"):
            result = controlnet_pipe(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                image=init_image,
                control_image=pose_image,
                strength=request.denoising_strength,
                num_inference_steps=request.steps,
                guidance_scale=request.cfg_scale,
                width=request.width,
                height=request.height,
                controlnet_conditioning_scale=1.0
            )
        
        # 转换结果
        output_images = []
        for img in result.images:
            output_images.append(image_to_base64(img))
        
        logger.info("ControlNet处理完成")
        
        return {
            "images": output_images,
            "parameters": request.dict()
        }
        
    except Exception as e:
        logger.error(f"ControlNet处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    gpu_available = torch.cuda.is_available()
    models_loaded = pipe is not None and controlnet_pipe is not None
    
    return {
        "status": "healthy" if gpu_available and models_loaded else "degraded",
        "gpu_available": gpu_available,
        "models_loaded": models_loaded,
        "device": str(torch.cuda.get_device_name()) if gpu_available else "CPU"
    }

if __name__ == "__main__":
    uvicorn.run(
        "stable_diffusion_api:app",
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )