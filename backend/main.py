"""
AI 智能衣柜 - FastAPI 后端入口
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from api.upload import router as upload_router
from api.wardrobe import router as wardrobe_router
from api.config import router as config_router
from api.weather import router as weather_router
from api.recommendation import router as recommendation_router
from api.recommendation_extra import router as recommendation_extra_router
from api.horoscope import router as horoscope_router
from api.auth import router as auth_router
from api.images import router as images_router
from api.settings import router as settings_router
from api.avatar import router as avatar_router
from api.admin.users import router as admin_users_router
from api.admin.stats import router as admin_stats_router
from storage.db import init_db, migrate_to_multiuser, get_user_by_username, create_user, add_admin, get_admin_by_user_id
from services.auth import get_password_hash

# 上传目录
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    print("[OK] Database initialized")

    # 迁移到多用户版本
    await migrate_to_multiuser()
    print("[OK] Database migrated to multi-user")

    # 初始化默认管理员
    await init_default_admin()
    print("[OK] Default admin initialized")

    yield
    # 关闭时的清理工作（如需要）
    print("[Bye] Application shutdown")


async def init_default_admin():
    """初始化默认管理员账户"""
    username = os.getenv("INIT_ADMIN_USER", "syh")
    password = os.getenv("INIT_ADMIN_PASS", "qwer1234")

    # 检查用户是否已存在
    existing_user = await get_user_by_username(username)
    if existing_user:
        # 检��是否已是管理员
        admin = await get_admin_by_user_id(existing_user["id"])
        if not admin:
            # 提升为管理员
            await add_admin(existing_user["id"], '["all"]')
            print(f"[OK] User '{username}' promoted to admin")
        return

    # 创建默认管理员用户
    email = f"{username}@admin.local"
    password_hash = get_password_hash(password)
    user_id = await create_user(
        username=username,
        email=email,
        password_hash=password_hash,
        nickname="管理员"
    )

    # 添加管理员权限
    await add_admin(user_id, '["all"]')
    print(f"[OK] Default admin created: {username} / {password}")


app = FastAPI(
    title="AI 智能衣柜",
    description="个人 AI 智能衣柜系统 - 上传照片、语义识别、智能穿搭",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置 - 从环境变量读取允许的域名
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件 - 用于访问上传的图片
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(images_router, prefix="/api/images", tags=["图片"])
app.include_router(upload_router, prefix="/api", tags=["上传"])
app.include_router(wardrobe_router, prefix="/api", tags=["衣柜"])
app.include_router(settings_router, prefix="/api", tags=["用户设置"])
app.include_router(avatar_router, prefix="/api", tags=["头像"])
app.include_router(config_router, prefix="/api", tags=["配置"])
app.include_router(weather_router, prefix="/api", tags=["天气"])
app.include_router(recommendation_router, prefix="/api", tags=["AI推荐"])
app.include_router(recommendation_extra_router, prefix="/api", tags=["推荐历史"])
app.include_router(horoscope_router, prefix="/api", tags=["星座运势"])
app.include_router(admin_users_router, prefix="/api/admin", tags=["管理员-用户"])
app.include_router(admin_stats_router, prefix="/api/admin", tags=["管理员-统计"])


@app.get("/api")
async def api_info():
    """API 信息"""
    return {
        "message": "👕 AI 智能衣柜 API",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /api/upload",
            "wardrobe": "GET /api/wardrobe",
            "wardrobe_by_category": "GET /api/wardrobe/{category}",
            "clothes_detail": "GET /api/clothes/{id}",
            "delete_clothes": "DELETE /api/clothes/{id}",
            "weather": "GET /api/weather",
            "weather_suggestion": "GET /api/weather/suggestion",
            "ai_recommendation": "GET /api/recommendation",
            "daily_horoscope": "GET /api/horoscope/daily"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# --------------------------------------------------------------------------
# 前端静态资源服务 (用于 Docker/生产环境)
# --------------------------------------------------------------------------
static_dir = Path(__file__).parent / "static"

if static_dir.exists():
    # 1. 优先挂载静态资源 (assets, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    # 2. 处理 favicon.ico 等根目录文件
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse(static_dir / "favicon.ico")

    # 3. 根路径返回 index.html
    @app.get("/")
    async def serve_root():
        return FileResponse(static_dir / "index.html")

    # 4. SPA 路由 - 所有未匹配的路径都返回 index.html
    # 注意：这必须放在所有 API 路由定义之后
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        # 如果请求的是 API 或 uploads (且未被上面的路由捕获)，则说明是 404
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
             return {"error": "Not Found", "detail": f"Path {full_path} not found"}
        
        # 尝试直接返回文件 (e.g. manifest.json, robots.txt)
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
            
        # 默认返回 index.html 让前端路由处理
        return FileResponse(static_dir / "index.html")
else:
    # 纯后端模式下的根路径提示
    @app.get("/")
    async def root():
        return {
            "message": "Backend is running. Frontend static files not found.",
            "api_info": "/api",
            "docs": "/docs"
        }
