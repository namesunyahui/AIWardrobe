"""
SQLite 数据库模型定义
使用 aiosqlite 进行异步操作
"""

# ========== 用户模块 ==========

# 用户表
USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nickname TEXT,
    avatar_key TEXT,
    role TEXT DEFAULT 'user',  -- user / admin / superadmin
    is_active INTEGER DEFAULT 1,
    is_deleted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

USERS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
"""

# 用户设置表
USER_SETTINGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    theme TEXT DEFAULT 'light',
    language TEXT DEFAULT 'zh-CN',
    default_location TEXT,
    zodiac_sign TEXT,
    temperature_unit TEXT DEFAULT 'celsius',
    notification_enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

USER_SETTINGS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
"""

# Token 黑名单表
REFRESH_TOKENS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL,
    token_type TEXT DEFAULT 'refresh',
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

REFRESH_TOKENS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);
"""

# 管理员表
ADMINS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    permissions TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);
"""

ADMINS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_admins_user_id ON admins(user_id);
"""

# 管理员操作日志表
ADMIN_LOGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

ADMIN_LOGS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin ON admin_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_created ON admin_logs(created_at);
"""

# ========== 衣物模块 ==========

# 衣物表（已修改，添加 user_id 和 image_key）
CLOTHES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS clothes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    category TEXT NOT NULL,  -- top, bottom, shoes, accessory
    item TEXT NOT NULL,
    style_semantics TEXT,  -- JSON array
    season_semantics TEXT,  -- JSON array
    usage_semantics TEXT,  -- JSON array
    color_semantics TEXT,
    description TEXT,
    image_key TEXT NOT NULL,  -- MinIO key，兼容旧字段 image_filename
    image_filename TEXT,  -- 兼容旧版本
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

# 创建索引用于快速查询
CLOTHES_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_clothes_user_id ON clothes(user_id);
CREATE INDEX IF NOT EXISTS idx_clothes_category ON clothes(category);
CREATE INDEX IF NOT EXISTS idx_clothes_category_user ON clothes(category, user_id);
CREATE INDEX IF NOT EXISTS idx_clothes_created_at ON clothes(created_at);
"""

# ========== 推荐模块 ==========

# 推荐历史表
RECOMMENDATION_RECORDS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS recommendation_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    record_date TEXT NOT NULL,
    weather_location TEXT,
    weather_data TEXT,
    horoscope_data TEXT,
    recommendation_text TEXT,
    outfit_summary TEXT,
    selection_reasons TEXT,
    suggested_top_id INTEGER,
    suggested_bottom_id INTEGER,
    suggested_shoes_id INTEGER,
    suggested_accessory_ids TEXT,
    purchase_suggestions TEXT,
    goal_raw TEXT,
    goal_normalized TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

RECOMMENDATION_RECORDS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_recommendation_user_id ON recommendation_records(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_date ON recommendation_records(user_id, record_date);
"""

# 收藏表
FAVORITE_RECOMMENDATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS favorite_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommendation_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recommendation_id) REFERENCES recommendation_records(id) ON DELETE CASCADE,
    UNIQUE(user_id, recommendation_id)
);
"""

FAVORITE_RECOMMENDATIONS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_favorite_user_id ON favorite_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_favorite_recommendation_id ON favorite_recommendations(recommendation_id);
"""

# ========== 星座运势模块 ==========

# 星座运势缓存表（已修改，添加 user_id）
HOROSCOPE_RECORDS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS horoscope_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    record_date TEXT NOT NULL,  -- YYYY-MM-DD
    zodiac_sign TEXT NOT NULL,
    zodiac_name TEXT NOT NULL,
    source_provider TEXT NOT NULL,  -- aztro / fallback / ai
    source_payload TEXT NOT NULL,  -- JSON
    llm_status TEXT NOT NULL DEFAULT 'pending',  -- pending / done / failed / skipped
    llm_reasoning TEXT,
    llm_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, record_date, zodiac_sign)
);
"""

HOROSCOPE_RECORDS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_horoscope_user_date ON horoscope_records(user_id, record_date, zodiac_sign);
"""
