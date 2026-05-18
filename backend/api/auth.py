"""
认证 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta

router = APIRouter()

from services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_hash,
    CurrentUser,
    get_current_user,
)
from storage.db import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    update_user_password,
    update_user_profile,
    deactivate_user,
    activate_user,
    delete_user,
    add_refresh_token,
    is_token_revoked,
)
from domain.users import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfileUpdate,
    PasswordChange,
    TokenResponse,
    TokenRefresh,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已注册
    existing_email = await get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建用户
    password_hash = get_password_hash(user_data.password)
    user_id = await create_user(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        nickname=user_data.nickname
    )

    # 获取创建的用户信息
    user = await get_user_by_id(user_id)
    return UserResponse(**user)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """用户登录"""
    # 支持用户名或邮箱登录
    user = await get_user_by_username(credentials.username)
    if not user:
        # 尝试邮箱登录
        user = await get_user_by_email(credentials.username)

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 验证密码
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 检查账户是否启用
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    # 生成 Token
    token_data = {"sub": str(user["id"]), "username": user["username"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # 存储 refresh token 到黑名单（用于后续退出或刷新）
    refresh_expires = datetime.utcnow() + timedelta(days=7)
    token_hash = get_token_hash(refresh_token)
    await add_refresh_token(user["id"], token_hash, refresh_expires.isoformat())

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefresh):
    """刷新 Access Token"""
    # 解码 refresh token
    payload = decode_token(request.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="无效的 Refresh Token")

    # 检查 token 是否在黑名单
    token_hash = get_token_hash(request.refresh_token)
    if await is_token_revoked(token_hash):
        raise HTTPException(status_code=401, detail="Token 已失效")

    # 获取用户信息
    user_id = payload.get("sub")
    user = await get_user_by_id(int(user_id))

    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")

    # 生成新的 Access Token
    token_data = {"sub": str(user["id"]), "username": user["username"]}
    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # 保持原来的 refresh token
        expires_in=3600
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """获取当前用户信息"""
    user = await get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse(**user)


@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    current_user: CurrentUser = Depends(get_current_user)
):
    """修改密码"""
    user = await get_user_by_id(current_user.user_id)

    # 验证旧密码
    if not verify_password(password_data.old_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="当前密码错误")

    # 更新密码
    new_hash = get_password_hash(password_data.new_password)
    await update_user_password(current_user.user_id, new_hash)

    return {"message": "密码修改成功"}


@router.put("/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新个人资料"""
    await update_user_profile(
        current_user.user_id,
        nickname=profile_data.nickname,
        avatar_key=profile_data.avatar_key
    )

    user = await get_user_by_id(current_user.user_id)
    return UserResponse(**user)


@router.post("/logout")
async def logout(
    current_user: CurrentUser = Depends(get_current_user)
):
    """退出登录"""
    # 可以选择将当前 token 加入黑名单
    # 这里暂时不实现，因为 JWT 是无状态的
    return {"message": "退出成功"}


@router.delete("/account")
async def delete_account(
    password: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """注销账户"""
    user = await get_user_by_id(current_user.user_id)

    # 验证密码
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="密码错误")

    # 软删除用户
    await delete_user(current_user.user_id)

    return {"message": "账户已注销"}