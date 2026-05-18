"""常量定义"""

# ========== 用户角色 ==========
ROLE_USER = "user"
ROLE_ADMIN = "admin"
ROLE_SUPERADMIN = "superadmin"

ROLES = [ROLE_USER, ROLE_ADMIN, ROLE_SUPERADMIN]
ADMIN_ROLES = [ROLE_ADMIN, ROLE_SUPERADMIN]

# ========== 衣物分类 ==========
CATEGORY_TOP = "top"
CATEGORY_BOTTOM = "bottom"
CATEGORY_SHOES = "shoes"
CATEGORY_ACCESSORY = "accessory"
CATEGORY_UNCATEGORIZED = "uncategorized"

CLOTHES_CATEGORIES = [
    CATEGORY_TOP,
    CATEGORY_BOTTOM,
    CATEGORY_SHOES,
    CATEGORY_ACCESSORY,
    CATEGORY_UNCATEGORIZED,
]

# ========== 图片上传配置 ==========
IMAGE_MAX_SIZE = (1024, 1024)  # 最大边长
IMAGE_QUALITY = 85  # 质量
IMAGE_ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
IMAGE_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ========== JWT 配置 ==========
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1小时
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7天

# ========== 缓存配置 ==========
CACHE_TTL_SECONDS = 600  # 10分钟缓存
WEATHER_CACHE_TTL = 600  # 天气缓存

# ========== API 重试配置 ==========
MAX_RETRIES = 3
INITIAL_DELAY = 1.0  # 秒

# ========== 分页配置 ==========
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_HISTORY_LIMIT = 10

# ========== 工具函数 ==========
def normalize_api_base(api_base: str) -> str:
    """规范化 API Base URL，确保以 /v1 结尾"""
    if not api_base:
        return api_base
    base = api_base.rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    return base