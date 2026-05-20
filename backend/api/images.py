"""
图片访问 API
"""
from fastapi import APIRouter, HTTPException, Depends
from services.minio import get_minio_service, get_minio_url
from services.auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/proxy/{image_key:path}")
async def get_image_proxy(image_key: str):
    """
    公开图片代理 - 解决跨域问题，返回302重定向
    """
    from services.minio import MINIO_ENDPOINT, MINIO_BUCKET
    from fastapi.responses import RedirectResponse

    # 验证 image_key 格式
    if ".." in image_key or image_key.startswith("/"):
        raise HTTPException(status_code=400, detail="无效的图片路径")

    # 直接重定向到 MinIO URL
    minio_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{image_key}"
    return RedirectResponse(url=minio_url, status_code=302)


@router.get("/{image_key}")
async def get_image(image_key: str, current_user: CurrentUser = Depends(get_current_user)):
    """
    获取图片访问 URL

    Args:
        image_key: MinIO 对象 key，如 "1/clothes/xxx.png"

    Returns:
        预签名访问 URL
    """
    # 验证 image_key 格式（防止路径遍历攻击）
    if ".." in image_key or image_key.startswith("/"):
        raise HTTPException(status_code=400, detail="无效的图片路径")

    # 验证用户权限（只能访问自己的图片）
    # image_key 格式: {user_id}/...
    parts = image_key.split("/")
    if parts and parts[0] != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="无权限访问此图片")

    try:
        service = get_minio_service()
        url = await service.get_presigned_url(image_key)
        return {"image_url": url, "image_key": image_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片失败: {str(e)}")


@router.delete("/{image_key}")
async def delete_image(image_key: str, current_user: CurrentUser = Depends(get_current_user)):
    """
    删除图片

    Args:
        image_key: MinIO 对象 key
    """
    # 验证权限
    parts = image_key.split("/")
    if parts and parts[0] != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="无权限删除此图片")

    try:
        service = get_minio_service()
        await service.delete_image(image_key)
        return {"message": "删除成功", "image_key": image_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除图片失败: {str(e)}")