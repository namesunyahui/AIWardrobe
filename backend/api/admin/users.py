"""
管理员 - 用户管理 API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from sqlalchemy import select, func
from api.admin.deps import require_admin, get_admin_permissions
from services.auth import CurrentUser, get_current_user
from storage.db import (
    get_user_by_id,
    deactivate_user,
    activate_user,
    delete_user,
    add_admin,
    get_admin_by_user_id,
)
from storage.database import get_session_maker
from storage.models_mysql import User, Clothes
from services.minio import get_minio_service
from domain.users import UserResponse
from domain.constants import ROLE_ADMIN, ROLE_SUPERADMIN, ROLE_USER

router = APIRouter()


@router.get("/image/{image_key:path}")
async def get_admin_image(
    image_key: str,
):
    """
    管理员图片代理 - 解决跨域问题，返回302重定向
    """
    from services.minio import MINIO_ENDPOINT, MINIO_BUCKET
    from fastapi.responses import RedirectResponse

    # 验证 image_key 格式
    if ".." in image_key or image_key.startswith("/"):
        raise HTTPException(status_code=400, detail="无效的图片路径")

    # 直接重定向到 MinIO URL
    minio_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{image_key}"
    return RedirectResponse(url=minio_url, status_code=302)


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: CurrentUser = Depends(require_admin())
):
    """获取用户列表（管理员）"""
    async_session_maker = get_session_maker()

    conditions = [User.is_deleted == False]
    if search:
        search_pattern = f"%{search}%"
        conditions.append((User.username.like(search_pattern)) | (User.email.like(search_pattern)))

    async with async_session_maker() as session:
        stmt = select(func.count(User.id)).where(*conditions)
        total = await session.scalar(stmt) or 0

        # 使用子查询一次性获取所有用户的衣物数量
        offset = (page - 1) * limit
        clothes_count_subquery = (
            select(func.count(Clothes.id))
            .where(Clothes.user_id == User.id)
            .correlate(User)
            .scalar_subquery()
            .label('clothes_count')
        )
        stmt = (
            select(User, clothes_count_subquery)
            .where(*conditions)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        rows = result.all()

    items = []
    for row in rows:
        user = row[0]
        clothes_count = row[1] or 0
        items.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "clothes_count": clothes_count
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin())
):
    """获取用户详情（管理员）"""
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(func.count(Clothes.id)).where(Clothes.user_id == user_id)
        clothes_count = await session.scalar(stmt) or 0

        stmt = (
            select(Clothes)
            .where(Clothes.user_id == user_id)
            .order_by(Clothes.created_at.desc())
            .limit(20)
        )
        result = await session.execute(stmt)
        clothes = result.scalars().all()

    minio_service = get_minio_service()
    # 返回后端代理的图片 URL，解决跨域问题
    clothes_list = []
    for c in clothes:
        image_key = c.image_key or c.image_filename
        # 使用后端代理接口
        image_url = f"/api/admin/image/{image_key}"
        clothes_list.append({"id": c.id, "category": c.category, "item": c.item, "image_url": image_url})

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "nickname": user["nickname"],
        "role": user["role"],
        "is_active": user["is_active"],
        "created_at": user["created_at"],
        "clothes_count": clothes_count,
        "clothes": clothes_list
    }


@router.post("/users/{user_id}/disable")
async def disable_user(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin())
):
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="不能禁用自己")

    success = await deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"message": "用户已禁用"}


@router.post("/users/{user_id}/enable")
async def enable_user(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin())
):
    """启用用户"""
    success = await activate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"message": "用户已启用"}


@router.delete("/users/{user_id}")
async def delete_user_account(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin())
):
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    success = await delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"message": "用户已删除"}


@router.post("/users/{user_id}/promote")
async def promote_to_admin(
    user_id: int,
    permissions: str = "[]",
    current_user: CurrentUser = Depends(require_admin())
):
    if current_user.role != ROLE_SUPERADMIN:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")

    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    existing = await get_admin_by_user_id(user_id)
    if existing:
        raise HTTPException(status_code=400, detail="该用户已经是管理员")

    await add_admin(user_id, permissions, current_user.user_id)

    from sqlalchemy import update
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(role=ROLE_ADMIN)
        )
        await session.commit()

    return {"message": "已提升为管理员"}


@router.post("/users/{user_id}/demote")
async def demote_from_admin(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin())
):
    if current_user.role != ROLE_SUPERADMIN:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")

    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    from sqlalchemy import update, delete
    from storage.models_mysql import Admin
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        await session.execute(delete(Admin).where(Admin.user_id == user_id))
        await session.execute(
            update(User).where(User.id == user_id).values(role=ROLE_USER)
        )
        await session.commit()

    return {"message": "已降级为普通用户"}