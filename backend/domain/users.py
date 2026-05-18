"""
用户数据模型
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^\w+$")
    email: EmailStr
    password: str = Field(..., min_length=6)
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str  # 支持用户名或邮箱
    password: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserProfileUpdate(BaseModel):
    """用户资料更新请求"""
    nickname: Optional[str] = None
    avatar_key: Optional[str] = None


class PasswordChange(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒


class TokenRefresh(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


class UserSettings(BaseModel):
    """用户设置响应"""
    id: int
    user_id: int
    theme: str = "light"
    language: str = "zh-CN"
    default_location: Optional[str] = None
    zodiac_sign: Optional[str] = None
    temperature_unit: str = "celsius"
    notification_enabled: bool = True


class UserSettingsUpdate(BaseModel):
    """用户设置更新请求"""
    theme: Optional[str] = None
    language: Optional[str] = None
    default_location: Optional[str] = None
    zodiac_sign: Optional[str] = None
    temperature_unit: Optional[str] = None
    notification_enabled: Optional[bool] = None