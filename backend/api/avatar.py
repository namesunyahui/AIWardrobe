"""
头像 API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from services.minio import upload_to_minio, get_minio_service
from services.auth import CurrentUser, get_current_user
from storage.db import update_user_profile, get_user_by_id
import uuid

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user)
):
    """上传用户头像"""
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、WebP、GIF 格式图片")

    try:
        # 读取图片
        image_data = await file.read()

        # 检查文件大小
        if len(image_data) > MAX_AVATAR_SIZE:
            raise HTTPException(status_code=400, detail="图片大小不能超过 2MB")

        # 压缩并上传到 MinIO
        from services.image_processor import compress_image
        compressed = compress_image(
            image_data,
            max_size=(512, 512),
            quality=85,
            output_format="PNG"
        )

        # 上传头像到 MinIO (category=avatar)
        image_key = await upload_to_minio(
            user_id=current_user.user_id,
            image_data=compressed,
            category="avatar"
        )

        # 更新用户头像记录
        await update_user_profile(current_user.user_id, avatar_key=image_key)

        # 获取预签名 URL
        service = get_minio_service()
        avatar_url = service.get_presigned_url(image_key)

        return {"avatar_url": avatar_url, "image_key": image_key}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传头像失败: {str(e)}")


@router.get("/avatar")
async def get_avatar(current_user: CurrentUser = Depends(get_current_user)):
    """获取当前用户头像 URL"""
    user = await get_user_by_id(current_user.user_id)
    if not user or not user.get("avatar_key"):
        return {"avatar_url": None, "image_key": None}

    service = get_minio_service()
    avatar_url = service.get_presigned_url(user["avatar_key"])

    return {"avatar_url": avatar_url, "image_key": user["avatar_key"]}


@router.delete("/avatar")
async def delete_avatar(current_user: CurrentUser = Depends(get_current_user)):
    """删除用户头像"""
    user = await get_user_by_id(current_user.user_id)
    if not user or not user.get("avatar_key"):
        raise HTTPException(status_code=404, detail="头像不存在")

    # 删除 MinIO 中的头像文件
    from services.minio import delete_from_minio
    await delete_from_minio(user["avatar_key"])

    # 清空用户头像记录
    await update_user_profile(current_user.user_id, avatar_key=None)

    return {"message": "头像已删除"}