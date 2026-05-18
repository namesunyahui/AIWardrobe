"""
用户设置 API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from services.auth import CurrentUser, get_current_user
from storage.db import get_user_settings, update_user_settings
from domain.users import UserSettings, UserSettingsUpdate

router = APIRouter()


@router.get("", response_model=UserSettings)
async def get_settings(current_user: CurrentUser = Depends(get_current_user)):
    """获取当前用户设置"""
    settings = await get_user_settings(current_user.user_id)
    if not settings:
        raise HTTPException(status_code=404, detail="用户设置不存在")
    return settings


@router.put("", response_model=UserSettings)
async def update_settings(
    settings_data: UserSettingsUpdate,
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新用户设置"""
    # 过滤掉 None 值
    update_data = {k: v for k, v in settings_data.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="没有要更新的内容")

    success = await update_user_settings(current_user.user_id, **update_data)
    if not success:
        raise HTTPException(status_code=500, detail="更新设置失败")

    # 返回更新后的设置
    updated_settings = await get_user_settings(current_user.user_id)
    return updated_settings