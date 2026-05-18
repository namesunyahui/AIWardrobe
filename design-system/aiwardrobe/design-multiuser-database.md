# AIWardrobe 多用户数据库设计（完整版）

## 1. 数据库概览

### 1.1 现有表（需修改）

| 表名 | 修改内容 |
|------|----------|
| `clothes` | 添加 `user_id` 字段，添加索引 |
| `horoscope_records` | 添加 `user_id` 字段，修改唯一约束 |

### 1.2 新增表

| 表名 | 用途 |
|------|------|
| `users` | 用户账户信息 |
| `user_settings` | 用户偏好设置 |
| `recommendation_records` | 推荐历史记录 |
| `favorite_recommendations` | 推荐收藏 |
| `refresh_tokens` | Refresh Token 黑名单 |
| `user_avatar` | 用户头像（可选，也可直接存 MinIO key） |

---

## 2. 用户模块表

### 2.1 users - 用户表

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nickname TEXT,
    avatar_key TEXT,                    -- MinIO 头像 key，如 "1/avatars/xxx.png"
    is_active INTEGER DEFAULT 1,        -- 1=启用, 0=禁用
    is_deleted INTEGER DEFAULT 0,       -- 软删除标记
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| username | TEXT | 登录用户名，唯一 |
| email | TEXT | 邮箱，唯一 |
| password_hash | TEXT | bcrypt 加密后的密码 |
| nickname | TEXT | 昵称，可为空 |
| avatar_key | TEXT | MinIO 头像路径 |
| is_active | INTEGER | 账户是否启用 |
| is_deleted | INTEGER | 软删除标记（0=正常, 1=已删除） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 2.2 user_settings - 用户设置表

```sql
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    theme TEXT DEFAULT 'light',                 -- light / dark / system
    language TEXT DEFAULT 'zh-CN',             -- zh-CN / en-US / ja-JP
    default_location TEXT,                     -- 默认城市
    zodiac_sign TEXT,                           -- 星座
    temperature_unit TEXT DEFAULT 'celsius',   -- celsius / fahrenheit
    notification_enabled INTEGER DEFAULT 1,    -- 是否开启通知
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
```

**预设选项：**
- `theme`: `light`, `dark`, `system`
- `language`: `zh-CN`, `en-US`, `ja-JP`
- `temperature_unit`: `celsius`, `fahrenheit`
- `zodiac_sign`: `aries`, `taurus`, `gemini`, `cancer`, `leo`, `virgo`, `libra`, `scorpio`, `sagittarius`, `capricorn`, `aquarius`, `pisces`

---

### 2.3 refresh_tokens - Token 黑名单表

```sql
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL,              -- Token 的 hash 值
    token_type TEXT DEFAULT 'refresh',     -- refresh / access
    expires_at TIMESTAMP NOT NULL,         -- 过期时间
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

**说明：** 用于退出登录时撤销 Token，或记录已过期的 Token

---

## 3. 衣物模块表

### 3.1 clothes - 衣物表（修改）

```sql
-- 修改后的 clothes 表
CREATE TABLE IF NOT EXISTS clothes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,                -- top, bottom, shoes, accessory, uncategorized
    item TEXT NOT NULL,
    style_semantics TEXT,                  -- JSON array: ["casual", "street"]
    season_semantics TEXT,                 -- JSON array: ["spring", "summer"]
    usage_semantics TEXT,                  -- JSON array: ["daily", "work"]
    color_semantics TEXT,
    description TEXT,
    image_key TEXT NOT NULL,               -- MinIO 对象 key，如 "1/clothes/uuid.png"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, id)                    -- 同一用户下的 ID 唯一
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_clothes_user_id ON clothes(user_id);
CREATE INDEX IF NOT EXISTS idx_clothes_category_user ON clothes(category, user_id);
CREATE INDEX IF NOT EXISTS idx_clothes_created_at ON clothes(created_at);
```

**字段变化：**
| 旧字段 | 新字段 | 说明 |
|--------|--------|------|
| `image_filename` | `image_key` | 存储 MinIO key 而非本地文件名 |
| - | `user_id` | 新增：所属用户 ID |
| - | `updated_at` | 新增：更新时间 |

---

## 4. 推荐模块表

### 4.1 recommendation_records - 推荐历史表

```sql
CREATE TABLE IF NOT EXISTS recommendation_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    record_date TEXT NOT NULL,             -- YYYY-MM-DD
    weather_location TEXT,                 -- 请求时的城市
    weather_data TEXT,                     -- 天气数据 JSON
    horoscope_data TEXT,                   -- 星座运势 JSON
    recommendation_text TEXT,              -- AI 推荐文本
    outfit_summary TEXT,                   -- 穿搭总结
    selection_reasons TEXT,                -- 选择理由 JSON
    suggested_top_id INTEGER,              -- 推荐的衣物 ID
    suggested_bottom_id INTEGER,
    suggested_shoes_id INTEGER,
    suggested_accessory_ids TEXT,          -- JSON array
    purchase_suggestions TEXT,             -- JSON array: 购买建议
    goal_raw TEXT,                         -- 用户输入的目标
    goal_normalized TEXT,                  -- 归一化后的目标
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, id)                    -- 同一用户下的 ID 唯一
);

CREATE INDEX IF NOT EXISTS idx_recommendation_user_id ON recommendation_records(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_date ON recommendation_records(user_id, record_date);
```

---

### 4.2 favorite_recommendations - 收藏表

```sql
CREATE TABLE IF NOT EXISTS favorite_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommendation_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recommendation_id) REFERENCES recommendation_records(id) ON DELETE CASCADE,
    UNIQUE(user_id, recommendation_id)    -- 同一用户不能重复收藏
);

CREATE INDEX IF NOT EXISTS idx_favorite_user_id ON favorite_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_favorite_recommendation_id ON favorite_recommendations(recommendation_id);
```

---

## 5. 星座运势模块表

### 5.1 horoscope_records - 星座运势表（修改）

```sql
-- 修改后的 horoscope_records 表
CREATE TABLE IF NOT EXISTS horoscope_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    record_date TEXT NOT NULL,             -- YYYY-MM-DD
    zodiac_sign TEXT NOT NULL,             -- aries, taurus, etc.
    zodiac_name TEXT NOT NULL,             -- 白羊座, 金牛座, etc.
    source_provider TEXT NOT NULL,         -- aztro / fallback / ai
    source_payload TEXT NOT NULL,          -- 原始数据 JSON
    llm_status TEXT DEFAULT 'pending',     -- pending / done / failed / skipped
    llm_reasoning TEXT,                    -- LLM 推理结果
    llm_error TEXT,                        -- 错误信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, record_date, zodiac_sign)  -- 每个用户的每天每星座唯一
);

CREATE INDEX IF NOT EXISTS idx_horoscope_user_date ON horoscope_records(user_id, record_date, zodiac_sign);
```

**字段变化：**
| 变化 | 说明 |
|------|------|
| 新增 `user_id` | 每个用户独立缓存自己的运势 |
| 修改唯一约束 | 改为 `(user_id, record_date, zodiac_sign)` |

---

## 6. 完整表关系图

```
┌─────────────────┐       ┌──────────────────────┐
│     users       │       │    user_settings     │
├─────────────────┤       ├──────────────────────┤
│ id (PK)         │◄──────│ user_id (FK)         │
│ username        │       │ theme                │
│ email           │       │ language             │
│ password_hash   │       │ default_location     │
│ nickname        │       │ zodiac_sign          │
│ avatar_key      │       │ temperature_unit     │
│ is_active       │       └──────────────────────┘
│ is_deleted      │
└────────┬────────┘
         │
         │ (1:N)
         ├──────────────────────────┐
         │                          │
         ▼                          ▼
┌─────────────────┐       ┌──────────────────────────┐
│     clothes     │       │  recommendation_records  │
├─────────────────┤       ├──────────────────────────┤
│ id (PK)         │       │ id (PK)                  │
│ user_id (FK)    │       │ user_id (FK)             │
│ category        │       │ record_date              │
│ item            │       │ weather_data             │
│ style_semantics │       │ recommendation_text      │
│ season_semantics│       │ suggested_top_id (FK)    │
│ usage_semantics │       │ suggested_bottom_id (FK) │
│ color_semantics │       │ suggested_shoes_id (FK)  │
│ description     │       │ goal_raw                 │
│ image_key       │       │ created_at               │
│ created_at      │       └────────────┬─────────────┘
└─────────────────┘                    │
                                       │ (1:N)
                                       ▼
                        ┌──────────────────────────┐
                        │ favorite_recommendations │
                        ├──────────────────────────┤
                        │ id (PK)                  │
                        │ user_id (FK)             │
                        │ recommendation_id (FK)   │
                        │ created_at               │
                        └──────────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│  horoscope_records  │       │  refresh_tokens     │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ user_id (FK)        │       │ user_id (FK)        │
│ record_date         │       │ token_hash          │
│ zodiac_sign         │       │ expires_at          │
│ zodiac_name         │       │ revoked_at          │
│ source_provider     │       └──��──────────────────┘
│ source_payload      │
│ llm_status          │
│ llm_reasoning       │
│ created_at          │
└─────────────────────┘
```

---

## 7. 数据库迁移脚本

### 7.1 V1 -> V2 迁移（添加用户系统）

```sql
-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nickname TEXT,
    avatar_key TEXT,
    is_active INTEGER DEFAULT 1,
    is_deleted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建默认用户（用于迁移现有数据）
INSERT INTO users (username, email, password_hash, nickname)
VALUES ('default_user', 'default@aiwardrobe.local', 'LEGACY', '默认用户');

-- 3. 获取默认用户 ID（假设为 1）
-- 将现有衣物关联到默认用户
ALTER TABLE clothes ADD COLUMN user_id INTEGER DEFAULT 1;
UPDATE clothes SET user_id = 1 WHERE user_id IS NULL;

-- 4. 添加外键约束
-- 注意：SQLite 外键需要在每次连接时启用 PRAGMA foreign_keys = ON;
-- 这里通过触发器实现级联删除（SQLite 不直接支持 ADD CONSTRAINT）

-- 5. 创建索引
CREATE INDEX IF NOT EXISTS idx_clothes_user_id ON clothes(user_id);
CREATE INDEX IF NOT EXISTS idx_clothes_category_user ON clothes(category, user_id);

-- 6. 创建用户设置表
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

-- 为现有用户创建设置
INSERT INTO user_settings (user_id) SELECT id FROM users;

-- 7. 创建 Token 黑名单表
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL,
    token_type TEXT DEFAULT 'refresh',
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 8. 修改星座运势表
ALTER TABLE horoscope_records ADD COLUMN user_id INTEGER DEFAULT 1;
UPDATE horoscope_records SET user_id = 1 WHERE user_id IS NULL;

-- 删除旧的唯一约束，创建新的
DROP INDEX IF EXISTS idx_horoscope_date_sign;
CREATE UNIQUE INDEX IF NOT EXISTS idx_horoscope_user_date 
ON horoscope_records(user_id, record_date, zodiac_sign);

-- 9. 创建推荐历史表
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

CREATE INDEX IF NOT EXISTS idx_recommendation_user_id ON recommendation_records(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_date ON recommendation_records(user_id, record_date);

-- 10. 创建收藏表
CREATE TABLE IF NOT EXISTS favorite_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommendation_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recommendation_id) REFERENCES recommendation_records(id) ON DELETE CASCADE,
    UNIQUE(user_id, recommendation_id)
);

CREATE INDEX IF NOT EXISTS idx_favorite_user_id ON favorite_recommendations(user_id);
```

---

## 8. 数据模型（Python）

### 8.1 用户模型

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^\w+$")
    email: EmailStr
    password: str = Field(..., min_length=6)
    nickname: Optional[str] = None

class UserLogin(BaseModel):
    username: str  # 支持用户名或邮箱
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_key: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)
```

### 8.2 用户设置模型

```python
from typing import Literal
from pydantic import BaseModel

class UserSettings(BaseModel):
    user_id: int
    theme: Literal["light", "dark", "system"] = "light"
    language: Literal["zh-CN", "en-US", "ja-JP"] = "zh-CN"
    default_location: Optional[str] = None
    zodiac_sign: Optional[str] = None
    temperature_unit: Literal["celsius", "fahrenheit"] = "celsius"
    notification_enabled: bool = True
```

### 8.3 Token 模型

```python
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒

class TokenRefresh(BaseModel):
    refresh_token: str
```

---

## 9. SQL 执行顺序

```sql
-- 初始化顺序（init_db 中执行）
1. CREATE TABLE users;
2. CREATE TABLE user_settings;
3. CREATE TABLE refresh_tokens;
4. CREATE TABLE clothes (已有，添加字段);
5. CREATE TABLE recommendation_records;
6. CREATE TABLE favorite_recommendations;
7. CREATE TABLE horoscope_records (已有，添加字段);
8. CREATE INDEX ... (所有索引);
```

---

## 10. 注意事项

1. **软删除 vs 硬删除**
   - 用户使用 `is_deleted` 软删除
   - 衣物、推荐历史使用 `ON DELETE CASCADE` 硬删除

2. **SQLite 外键**
   - SQLite 默认不启用外键约束
   - 必须在连接时执行 `PRAGMA foreign_keys = ON`

3. **JSON 字段**
   - SQLite 原生不支持 JSON 类型
   - 使用 `TEXT` 存储 JSON 字符串，应用层解析

4. **密码存储**
   - 使用 bcrypt，salt 轮数 12
   - 不要存储明文密码

5. **Token 存储**
   - 只存储 token 的 hash 值，不存储原始 token
   - 定期清理过期 token（可使用 cron job）

---

*文档版本: 1.1*
*更新日期: 2026-05-13*