# AIWardrobe 多用户 API 设计（完整版）

## 1. 认证模块 API

### 1.1 注册

```
POST /api/auth/register
```

**请求体：**
```json
{
    "username": "string",        // 必填，3-20字符，字母数字下划线
    "email": "string",           // 必填，有效邮箱格式
    "password": "string",        // 必填，至少6位
    "nickname": "string"         // 可选，默认等于 username
}
```

**成功响应 (201)：**
```json
{
    "message": "注册成功",
    "user": {
        "id": 1,
        "username": "john",
        "email": "john@example.com",
        "nickname": "John",
        "created_at": "2026-05-13T10:00:00Z"
    }
}
```

**错误响应：**
- 400: 用户名已存在
- 400: 邮箱已注册
- 422: 参数验证失败

---

### 1.2 登录

```
POST /api/auth/login
```

**请求体：**
```json
{
    "username": "string",        // 用户名或邮箱
    "password": "string"
}
```

**成功响应 (200)：**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

**错误响应：**
- 401: 用户名或密码错误
- 422: 参数验证失败

---

### 1.3 刷新 Token

```
POST /api/auth/refresh
```

**请求头：**
```
Authorization: Bearer {refresh_token}
```

**成功响应 (200)：**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

**错误响应：**
- 401: Token 无效或已过期

---

### 1.4 获取当前用户信息

```
GET /api/auth/me
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**成功响应 (200)：**
```json
{
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "nickname": "John",
    "avatar_url": "http://minio:9000/aiwardrobe/1/avatars/default.png",
    "created_at": "2026-05-13T10:00:00Z",
    "updated_at": "2026-05-13T10:00:00Z"
}
```

---

### 1.5 修改密码

```
PUT /api/auth/password
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**请求体：**
```json
{
    "old_password": "string",
    "new_password": "string"     // 至少6位
}
```

**成功响应 (200)：**
```json
{
    "message": "密码修改成功"
}
```

**错误响应：**
- 400: 旧密码错误
- 422: 新密码不符合要求

---

### 1.6 更新个人资料

```
PUT /api/auth/profile
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**请求体：**
```json
{
    "nickname": "string",         // 可选
    "avatar_key": "string"        // 可选，MinIO 中的头像 key
}
```

**成功响应 (200)：**
```json
{
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "nickname": "NewNickname",
    "avatar_url": "http://minio:9000/aiwardrobe/1/avatars/xxx.png",
    "updated_at": "2026-05-13T12:00:00Z"
}
```

---

### 1.7 退出登录

```
POST /api/auth/logout
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**成功响应 (200)：**
```json
{
    "message": "退出成功"
}
```

**说明：** 将当前 refresh_token 加入黑名单

---

### 1.8 删除账户（注销）

```
DELETE /api/auth/account
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**请求体：**
```json
{
    "password": "string"          // 确认密码
}
```

**成功响应 (200)：**
```json
{
    "message": "账户已注销"
}
```

**说明：** 软删除或级联删除用户所有数据（包括 MinIO 中的图片）

---

## 2. 衣物管理 API（需认证）

### 2.1 获取当前用户衣柜

```
GET /api/wardrobe
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**响应 (200)：**
```json
{
    "tops": [...],
    "bottoms": [...],
    "shoes": [...],
    "accessories": [...],
    "uncategorized": [...]
}
```

---

### 2.2 按分类获取衣物

```
GET /api/wardrobe/{category}
```

**category:** `top`, `bottom`, `shoes`, `accessory`, `uncategorized`

---

### 2.3 获取单个衣物详情

```
GET /api/clothes/{id}
```

**响应 (200)：**
```json
{
    "id": 1,
    "user_id": 1,
    "category": "top",
    "item": "T-shirt",
    "style_semantics": ["casual", "street"],
    "season_semantics": ["spring", "summer"],
    "usage_semantics": ["daily", "work"],
    "color_semantics": "blue",
    "description": "蓝色纯棉T恤",
    "image_url": "http://minio:9000/aiwardrobe/1/clothes/xxx.png",
    "image_key": "1/clothes/xxx.png",
    "created_at": "2026-05-13T10:00:00Z"
}
```

---

### 2.4 上传新衣物

```
POST /api/upload
```

**请求头：**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体：**
```
file: <image file>
```

**响应 (201)：**
```json
{
    "id": 1,
    "user_id": 1,
    "category": "uncategorized",
    "item": "待分类",
    "style_semantics": [],
    "season_semantics": [],
    "usage_semantics": [],
    "color_semantics": "unknown",
    "description": "请手动分类或使用AI分析",
    "image_url": "http://minio:9000/aiwardrobe/1/clothes/xxx.png",
    "image_key": "1/clothes/xxx.png",
    "created_at": "2026-05-13T10:00:00Z"
}
```

---

### 2.5 AI 分析衣物

```
POST /api/upload/analyze/{id}
```

**响应 (200)：**
```json
{
    "id": 1,
    "user_id": 1,
    "category": "top",
    "item": "T-shirt",
    "style_semantics": ["casual", "street"],
    "season_semantics": ["spring", "summer"],
    "usage_semantics": ["daily", "work"],
    "color_semantics": "blue",
    "description": "蓝色纯棉T恤",
    "image_url": "http://minio:9000/aiwardrobe/1/clothes/xxx.png",
    "image_key": "1/clothes/xxx.png",
    "created_at": "2026-05-13T10:00:00Z"
}
```

---

### 2.6 更新衣物

```
PUT /api/clothes/{id}
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**请求体：**
```json
{
    "category": "top",                    // 必填
    "item": "T-shirt",                     // 必填
    "style_semantics": ["casual"],         // 可选
    "season_semantics": ["spring"],       // 可选
    "usage_semantics": ["daily"],         // 可选
    "color_semantics": "blue",            // 可选
    "description": "蓝色纯棉T恤"           // 可选
}
```

**说明：** 只能更新自己的衣物（user_id 匹配）

---

### 2.7 删除衣物

```
DELETE /api/clothes/{id}
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**响应 (200)：**
```json
{
    "message": "删除成功",
    "id": 1
}
```

**说明：** 同时删除 MinIO 中的图片文件

---

## 3. 推荐历史 API（需认证）

### 3.1 获取推荐历史

```
GET /api/recommendations/history
```

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 20 | 返回条数 |
| offset | int | 0 | 偏移量 |

**响应 (200)：**
```json
{
    "items": [
        {
            "id": 1,
            "weather": {...},
            "horoscope": {...},
            "recommendation_text": "...",
            "outfit_summary": "...",
            "suggested_top": {...},
            "suggested_bottom": {...},
            "suggested_shoes": {...},
            "suggested_accessories": [...],
            "goal": "约会",
            "created_at": "2026-05-13T10:00:00Z"
        }
    ],
    "total": 100,
    "limit": 20,
    "offset": 0
}
```

---

### 3.2 获取单条推荐详情

```
GET /api/recommendations/{id}
```

---

### 3.3 收藏推荐

```
POST /api/recommendations/{id}/favorite
```

**响应 (201)：**
```json
{
    "message": "收藏成功",
    "id": 1
}
```

---

### 3.4 取消收藏

```
DELETE /api/recommendations/{id}/favorite
```

---

### 3.5 获取收藏列表

```
GET /api/recommendations/favorites
```

---

## 4. 用户设置 API（需认证）

### 4.1 获取用户设置

```
GET /api/settings
```

**响应 (200)：**
```json
{
    "theme": "light",
    "language": "zh-CN",
    "default_location": "上海",
    "zodiac_sign": "aries",
    "temperature_unit": "celsius",
    "notification_enabled": true,
    "created_at": "2026-05-13T10:00:00Z",
    "updated_at": "2026-05-13T10:00:00Z"
}
```

---

### 4.2 更新用户设置

```
PUT /api/settings
```

**请求体：**
```json
{
    "theme": "dark",
    "language": "en-US",
    "default_location": "北京",
    "zodiac_sign": "taurus",
    "temperature_unit": "celsius",
    "notification_enabled": false
}
```

**响应 (200)：**
```json
{
    "message": "设置已更新"
}
```

---

## 5. 图片访问 API

### 5.1 获取图片（公开）

```
GET /api/images/{image_key}
```

**响应：** 302 重定向到 MinIO 预签名 URL 或直接返回图片

**说明：**
- 使用预签名 URL，默认 1 小时过期
- 验证 image_key 格式（防止路径遍历攻击）

---

### 5.2 上传头像

```
POST /api/avatar
```

**请求头：**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体：**
```
file: <image file>
```

**响应 (201)：**
```json
{
    "avatar_url": "http://minio:9000/aiwardrobe/1/avatars/xxx.png",
    "avatar_key": "1/avatars/xxx.png"
}
```

---

## 6. 推荐 API（需认证）

### 6.1 获取推荐

```
GET /api/recommendation
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| location | string | 城市名或经纬度 |
| zodiac_sign | string | 临时指定星座 |
| goal | string | 穿搭目标 |

**响应 (200)：**
```json
{
    "weather": {...},
    "horoscope": {...},
    "recommendation_text": "...",
    "outfit_summary": "...",
    "selection_reasons": {...},
    "suggested_top": {...},
    "suggested_bottom": {...},
    "suggested_shoes": {...},
    "suggested_accessories": [...],
    "purchase_suggestions": [...],
    "goal_raw": "约会",
    "goal_normalized": "date"
}
```

**说明：** 自动保存到推荐历史

---

## 7. 星座运势 API（需认证）

### 7.1 获取今日运势

```
GET /api/horoscope
```

**请求头：**
```
Authorization: Bearer {access_token}
```

**响应 (200)：**
```json
{
    "zodiac_sign": "aries",
    "zodiac_name": "白羊座",
    "date": "2026-05-13",
    "overall_score": 85,
    "love_score": 80,
    "career_score": 90,
    "wealth_score": 75,
    "luck_color": "红色",
    "luck_number": 7,
    "summary": "...",
    "source_provider": "AI"
}
```

---

### 7.2 指定星座查询

```
GET /api/horoscope?sign=taurus
```

---

## 8. 天气 API（需认证）

### 8.1 获取天气

```
GET /api/weather
```

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| location | string | 城市名或经纬度 |

**响应 (200)：**
```json
{
    "location": "上海",
    "temperature": 22,
    "weather": "晴",
    "humidity": 65,
    "wind_speed": 15,
    "aqi": 45,
    "update_time": "2026-05-13T10:00:00Z"
}
```

---

## 9. 错误响应格式

所有错误响应统一格式：

```json
{
    "detail": "错误描述信息",
    "code": "ERROR_CODE",           // 可选，错误码
    "field": "username"             // 可选，错误字段
}
```

**常见错误码：**
| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| INVALID_CREDENTIALS | 401 | 用户名或密码错误 |
| TOKEN_EXPIRED | 401 | Token 已过期 |
| TOKEN_INVALID | 401 | Token 无效 |
| USER_NOT_FOUND | 404 | 用户不存在 |
| RESOURCE_NOT_FOUND | 404 | 资源不存在 |
| PERMISSION_DENIED | 403 | 无权限访问 |
| USERNAME_EXISTS | 400 | 用户名已存在 |
| EMAIL_EXISTS | 400 | 邮箱已注册 |
| INVALID_PASSWORD | 422 | 密码不符合要求 |
| FILE_TOO_LARGE | 413 | 文件过大 |
| INVALID_FILE_TYPE | 400 | 文件类型不支持 |

---

## 10. API 版本管理

所有 API 统一使用 `/api/v1` 前缀：

```
/api/v1/auth/register
/api/v1/auth/login
/api/v1/wardrobe
/api/v1/clothes/{id}
...
```

**说明：** 后续 API 升级可在 `/api/v2` 路径下实现

---

*文档版本: 1.1*
*更新日期: 2026-05-13*