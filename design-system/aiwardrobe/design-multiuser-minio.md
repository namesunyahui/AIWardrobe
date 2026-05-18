# AIWardrobe 多用户 + MinIO 存储设计方案

## 1. 需求概述

### 1.1 当前状态
- 单用户应用，所有数据共享
- 图片存储在本地文件系统 `backend/uploads/`
- SQLite 数据库存储元数据

### 1.2 目标
- 支持多用户注册登录
- 用户数据隔离（只能看到自己的衣物）
- 图片存储迁移到 MinIO 对象存储

---

## 2. 系统架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  Login  │  │Register │  │ Wardrobe│  │   AI    │       │
│  └────┬────┘  └────┬────��  └────┬────┘  └────┬────┘       │
└───────┼────────────┼────────────┼────────────┼─────────────┘
        │            │            │            │
        └────────────┴─────┬──────┴────────────┘
                           │ HTTP + JWT
        ┌──────────────────┴──────────────────┐
        │              Backend                 │
        │  ┌──────────┐  ┌──────────┐         │
        │  │   Auth   │  │   API    │         │
        │  │  (JWT)   │  │  Routes  │         │
        │  └────┬─────┘  └────┬─────┘         │
        │       │             │               │
        │  ┌────┴─────┐  ┌────┴─────┐         │
        │  │ Services │  │ Storage  │         │
        │  │          │  │ (SQLite) │         │
        │  └────┬─────┘  └──────────┘         │
        │       │                              │
        │  ┌────┴─────┐                        │
        │  │  MinIO   │  (图片存储)            │
        │  │ Client   │                        │
        │  └──────────┘                        │
        └──────────────────────────────────────┘
```

### 2.2 技术选型

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 认证方式 | JWT (JSON Web Token) | 无状态，易扩展 |
| 密码加密 | bcrypt | 安全可靠 |
| 图片存储 | MinIO | S3 兼容，对象存储 |
| 数据库 | 保留 SQLite | 轻量够用 |

---

## 3. 数据库设计

### 3.1 新增用户表

```sql
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,        -- 用户名（登录用）
    email TEXT UNIQUE NOT NULL,           -- 邮箱
    password_hash TEXT NOT NULL,          -- 加密后的密码
    nickname TEXT,                        -- 昵称（可选）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

### 3.2 修改衣物表

```sql
-- 衣物表（添加 user_id）
CREATE TABLE IF NOT EXISTS clothes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,              -- 新增：所属用户 ID
    category TEXT NOT NULL,
    item TEXT NOT NULL,
    style_semantics TEXT,                  -- JSON array
    season_semantics TEXT,                 -- JSON array
    usage_semantics TEXT,                  -- JSON array
    color_semantics TEXT,
    description TEXT,
    image_key TEXT NOT NULL,               -- 改为：MinIO 对象 key
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 用户衣物索引
CREATE INDEX IF NOT EXISTS idx_clothes_user_id ON clothes(user_id);
CREATE INDEX IF NOT EXISTS idx_clothes_category_user ON clothes(category, user_id);
```

### 3.3 星座运势表（也需隔离）

```sql
-- 星座运势缓存表（添加 user_id）
CREATE TABLE IF NOT EXISTS horoscope_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,              -- 新增：所属用户 ID
    record_date TEXT NOT NULL,
    zodiac_sign TEXT NOT NULL,
    zodiac_name TEXT NOT NULL,
    source_provider TEXT NOT NULL,
    source_payload TEXT NOT NULL,
    llm_status TEXT NOT NULL DEFAULT 'pending',
    llm_reasoning TEXT,
    llm_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, record_date, zodiac_sign),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_horoscope_user ON horoscope_records(user_id, record_date, zodiac_sign);
```

---

## 4. MinIO 存储设计

### 4.1 存储结构

```
AIWardrobe Bucket:
├── {user_id}/                          # 用户目录
│   ├── clothes/                        # 衣物图片
│   │   ├── {uuid1}.png
│   │   ├── {uuid2}.png
│   │   └── ...
│   └── avatars/                        # 头像（预留）
│       └── ...
```

### 4.2 MinIO 配置

```python
# 配置项（环境变量）
MINIO_ENDPOINT = "localhost:9000"       # MinIO 服务地址
MINIO_ACCESS_KEY = "minioadmin"         # 访问密钥
MINIO_SECRET_KEY = "minioadmin"         # 秘密密钥
MINIO_BUCKET = "aiwardrobe"             # 存储桶名称
MINIO_SECURE = False                    # 是否使用 HTTPS
```

### 4.3 API 设计

```python
# 上传图片
POST /api/upload
Headers: Authorization: Bearer {jwt_token}
Body: file (multipart)

# 返回
{
    "image_key": "1/clothes/550e8400-e29b-41d4-a716-446655440000.png",
    "image_url": "http://minio:9000/aiwardrobe/1/clothes/xxx.png"
}

# 获取图片URL
GET /api/images/{image_key}
```

---

## 5. API 设计

### 5.1 认证 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/refresh | 刷新 Token |
| GET | /api/auth/me | 获取当前用户信息 |

### 5.2 衣物 API（需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/clothes | 获取当前用户的所有衣物 |
| POST | /api/upload | 上传新衣物（需登录） |
| PUT | /api/clothes/{id} | 更新衣物 |
| DELETE | /api/clothes/{id} | 删除衣物 |

### 5.3 响应示例

```json
// 登录响应
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
}

// 获取衣物列表（已隔离）
GET /api/clothes
{
    "items": [
        {
            "id": 1,
            "user_id": 1,
            "category": "top",
            "item": "T-shirt",
            "image_url": "http://minio:9000/aiwardrobe/1/clothes/xxx.png"
        }
    ],
    "total": 10
}
```

---

## 6. 前端设计

### 6.1 新增页面

| 页面 | 路径 | 说明 |
|------|------|------|
| 登录页 | /login | 用户登录 |
| 注册页 | /register | 用户注册 |
| 首页 | / (已改) | 引导登录 |

### 6.2 状态管理

```javascript
// AuthContext - 管理登录状态
{
    user: { id, username, email, nickname },
    token: "jwt_token",
    isAuthenticated: true/false
}

// API 请求自动携带 Token
headers: {
    Authorization: `Bearer ${token}`
}
```

### 6.3 路由保护

```javascript
// 需要登录的路由
const ProtectedRoute = ({ children }) => {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? children : <Navigate to="/login" />;
};

// 使用
<Route path="/wardrobe" element={
    <ProtectedRoute><WardrobePage /></ProtectedRoute>
} />
```

---

## 7. 安全设计

### 7.1 密码安全
- 使用 bcrypt 加密，salt 轮数 12
- 密码要求：至少 6 位

### 7.2 Token 安全
- Access Token：1 小时有效期
- Refresh Token：7 天有效期
- 存储在 HTTP-only Cookie 或 localStorage

### 7.3 数据隔离
- 所有 API 需带有效 JWT
- 查询自动添加 `WHERE user_id = ?`
- 删除衣物同时删除 MinIO 中的图片

---

## 8. 部署设计

### 8.1 Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_FILE_PATH=/data/wardrobe.db
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
    volumes:
      - ./data:/data
    depends_on:
      - minio

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
    volumes:
      - ./minio-data:/data
```

### 8.2 环境变量

```bash
# 认证
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=aiwardrobe
MINIO_SECURE=false
```

---

## 9. 迁移计划

### Phase 1: 用户系统
1. 创建用户表和模型
2. 实现注册/登录 API
3. 添加 JWT 认证中间件
4. 修改衣物表添加 user_id

### Phase 2: 前端登录
1. 创建登录/注册页面
2. 实现 AuthContext
3. 添加路由保护

### Phase 3: MinIO 集成
1. 创建 MinIO 服务
2. 修改图片上传 API
3. 删除旧图片文件

### Phase 4: 数据迁移
1. 为现有数据创建默认用户
2. 迁移图片到 MinIO
3. 更新 image_filename → image_key

---

## 10. 待确定事项

1. **是否保留管理员用户？** 用于管理所有用户
2. **是否支持第三方登录？** (Google, GitHub)
3. **用户初始衣物如何处理？** 迁移到新用户或创建默认用户
4. **MinIO 是否需要高可用？** 单机还是集群

---

*文档版本: 1.0*
*创建日期: 2026-05-12*