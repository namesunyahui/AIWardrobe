"""
管理员权限中间件
"""
from fastapi import HTTPException, Depends
from services.auth import CurrentUser, get_current_user
from domain.constants import ROLE_ADMIN, ROLE_SUPERADMIN, ADMIN_ROLES


def require_admin():
    """要求是管理员（admin 或 superadmin）"""
    async def checker(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in ADMIN_ROLES:
            raise HTTPException(status_code=403, detail="需要管理员权限")
        return current_user
    return checker


def require_superadmin():
    """要求是超级管理员"""
    async def checker(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role != ROLE_SUPERADMIN:
            raise HTTPException(status_code=403, detail="需要超级管理员权限")
        return current_user
    return checker


def check_permission(permissions: list, required: str) -> bool:
    """检查权限"""
    if "*" in permissions:
        return True
    return required in permissions


async def get_admin_permissions(user_id: int) -> list:
    """获取用户的管理员权限"""
    from storage.db import get_admin_by_user_id

    admin = await get_admin_by_user_id(user_id)
    if not admin:
        return []

    import json
    return json.loads(admin["permissions"] or "[]")


def require_permission(permission: str):
    """要求特定权限"""
    async def checker(current_user: CurrentUser = Depends(get_current_user)):
        # superadmin 拥有所有权限
        if current_user.role == ROLE_SUPERADMIN:
            return current_user

        # admin 角色拥有所有基本权限
        if current_user.role == ROLE_ADMIN:
            return current_user

        raise HTTPException(status_code=403, detail="权限不足")
    return checker