"""
图片上传 API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import uuid

from services.openai_compatible import analyze_clothes_openai
from services.image_processor import compress_image
from services.minio import upload_to_minio, get_minio_service
from storage.config_store import load_config
from domain.clothes import ClothesSemantics, ClothesCreate, ClothesItem, normalize_category_value
from storage.db import add_clothes, get_clothes_by_id, update_clothes, get_clothes_image_filename
from services.auth import CurrentUser, get_current_user
from domain.constants import CLOTHES_CATEGORIES, IMAGE_MAX_SIZE, IMAGE_QUALITY, IMAGE_ALLOWED_TYPES, IMAGE_MAX_FILE_SIZE

router = APIRouter()

# 图片压缩配置（从 constants 导入）
# IMAGE_MAX_SIZE, IMAGE_QUALITY, IMAGE_ALLOWED_TYPES, IMAGE_MAX_FILE_SIZE


@router.post("/upload", response_model=ClothesItem)
async def upload_image(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user)
):
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

        # 上传到 MinIO
        image_key = await upload_to_minio(
            user_id=current_user.user_id,
            image_data=compressed_bytes,
            category="clothes"
        )

        # 直接保存到未分类，不进行AI分析
        clothes_data = ClothesCreate(
            category="uncategorized",
            item="待分类",
            style_semantics=[],
            season_semantics=[],
            usage_semantics=[],
            color_semantics="unknown",
            description="请手动分类或使用AI分析",
            image_filename=image_key
        )

        clothes_id = await add_clothes(clothes_data, user_id=current_user.user_id)
        clothes = await get_clothes_by_id(clothes_id, user_id=current_user.user_id)

        return clothes

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/upload/analyze/{clothes_id}", response_model=ClothesItem)
async def analyze_clothes(
    clothes_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    AI分析衣物（需要先上传图片到未分类）
    """
    try:
        clothes = await get_clothes_by_id(clothes_id, user_id=current_user.user_id)
        if not clothes:
            raise HTTPException(status_code=404, detail="衣物不存在")

        # 直接从数据库获取图片的 image_key (MinIO object key)
        image_key = await get_clothes_image_filename(clothes_id, user_id=current_user.user_id)
        if not image_key:
            raise HTTPException(status_code=404, detail="图片不存在")

        # 从 MinIO 获取图片数据
        minio_service = get_minio_service()
        try:
            response = minio_service.client.get_object(minio_service.bucket, image_key)
            image_bytes = response.read()
            response.close()
            response.release_conn()
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"读取图片失败: {str(e)}")

        # AI 分析
        semantics: ClothesSemantics = await analyze_clothes_openai(image_bytes)

        normalized_category = normalize_category_value(semantics.category)
        if normalized_category not in CLOTHES_CATEGORIES:
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
            image_filename=image_key
        )
        await update_clothes(clothes_id, update_data, user_id=current_user.user_id)

        # 返回更新后的数据
        clothes = await get_clothes_by_id(clothes_id, user_id=current_user.user_id)

        return clothes

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI分析失败: {str(e)}")
