"""
图片上传 API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid

from services.segment import remove_background
from services.removebg import remove_background_api
from services.openai_compatible import analyze_clothes_openai
from services.image_processor import compress_image
from storage.config_store import load_config
from domain.clothes import ClothesSemantics, ClothesCreate, ClothesItem, normalize_category_value
from storage.db import add_clothes, get_clothes_by_id, update_clothes, get_clothes_image_filename

router = APIRouter()

# 上传目录
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_CATEGORIES = {"top", "bottom", "shoes", "accessory", "uncategorized"}

# 图片压缩配置
IMAGE_MAX_SIZE = (1024, 1024)  # 最大边长
IMAGE_QUALITY = 85  # 质量


@router.post("/upload", response_model=ClothesItem)
async def upload_image(file: UploadFile = File(...)):
    """
    上传衣物图片（直接保存到未分类，不进行AI分析）

    流程：
    1. 接收图片并压缩保存
    2. 创建衣物记录（未分类）
    3. 返回基本信息
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")

    try:
        # 读取原始图片
        raw_bytes = await file.read()

        # 压缩图片
        compressed_bytes = compress_image(
            raw_bytes,
            max_size=IMAGE_MAX_SIZE,
            quality=IMAGE_QUALITY,
            output_format="PNG"
        )

        # 生成文件名并保存
        filename = f"{uuid.uuid4()}.png"
        filepath = UPLOAD_DIR / filename

        with open(filepath, "wb") as f:
            f.write(compressed_bytes)

        # 直接保存到未分类，不进行AI分析
        clothes_data = ClothesCreate(
            category="uncategorized",
            item="待分类",
            style_semantics=[],
            season_semantics=[],
            usage_semantics=[],
            color_semantics="unknown",
            description="请手动分类或使用AI分析",
            image_filename=filename
        )

        clothes_id = await add_clothes(clothes_data)
        clothes = await get_clothes_by_id(clothes_id)

        return clothes

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/upload/analyze/{clothes_id}", response_model=ClothesItem)
async def analyze_clothes(clothes_id: int):
    """
    AI分析衣物（需要先上传图片到未分类）
    """
    try:
        clothes = await get_clothes_by_id(clothes_id)
        if not clothes:
            raise HTTPException(status_code=404, detail="衣物不存在")

        # 直接从数据库获取图片文件名
        image_filename = await get_clothes_image_filename(clothes_id)
        if not image_filename:
            raise HTTPException(status_code=404, detail="图片文件名不存在")

        # 读取图片
        image_path = UPLOAD_DIR / image_filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="图片文件不存在")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # AI 分析
        semantics: ClothesSemantics = await analyze_clothes_openai(image_bytes)

        normalized_category = normalize_category_value(semantics.category)
        if normalized_category not in ALLOWED_CATEGORIES:
            normalized_category = "accessory"

        # 更新数据库
        update_data = ClothesCreate(
            category=normalized_category,
            item=semantics.item,
            style_semantics=semantics.style_semantics,
            season_semantics=semantics.season_semantics,
            usage_semantics=semantics.usage_semantics,
            color_semantics=semantics.color_semantics,
            description=semantics.description,
            image_filename=image_filename
        )
        await update_clothes(clothes_id, update_data)

        # 移动到对应分类（从 uncategorized 移除）
        # 返回更新后的数据
        clothes = await get_clothes_by_id(clothes_id)

        return clothes

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI分析失败: {str(e)}")
