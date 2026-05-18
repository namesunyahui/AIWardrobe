# AIWardrobe 管理员设计

## 1. 角色体系

| 角色 | 说明 | 权限 |
|------|------|------|
| `user` | 普通用户 | 管理自己的衣物、数据 |
| `admin` | 管理员 | 管理所有用户、查看统计 |
| `superadmin` | 超级管理员 | 管理其他管理员、系统配置 |

---

## 2. 数据库设计

### 2.1 users 表（添加 role 字段）

```sql
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';
-- role: 'user' | 'admin' | 'superadmin'
```

### 2.2 admins 管理员扩展表

```sql
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    permissions TEXT,                    -- JSON array: ["users:read", "users:write", "stats:read"]
    created_by INTEGER,                  -- 创建者 ID（superadmin）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_admins_user_id ON admins(user_id);
```

### 2.3 操作日志表（可选）

```sql
CREATE TABLE IF NOT EXISTS admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,           -- 操作的管理员 ID
    action TEXT NOT NULL,                -- 操作类型: "disable_user", "delete_data", etc.
    target_type TEXT NOT NULL,           -- 目标类型: "user", "clothes", "config"
    target_id INTEGER,                   -- 目标 ID
    details TEXT,                        -- 详情 JSON
    ip_address TEXT,                     -- 操作 IP
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_admin_logs_admin ON admin_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_created ON admin_logs(created_at);
```

---

## 3. 权限说明

| 权限 | 说明 |
|------|------|
| `users:read` | 查看用户列表 |
| `users:write` | 修改用户资料 |
| `users:disable` | 禁用/启用用户 |
| `users:delete` | 删除用户 |
| `users:promote` | 提升为管理员 |
| `stats:read` | 查看统计数据 |
| `config:read` | 查看系统配置 |
| `config:write` | 修改系统配置 |
| `data:export` | 导出数据 |
| `data:delete` | 删除用户数据 |

```sql
-- 超级管理员（所有权限）
INSERT INTO admins (user_id, permissions)
VALUES (1, '["*"]');  -- * 表示所有权限

-- 普通管理员（部分权限）
INSERT INTO admins (user_id, permissions)
VALUES (2, '["users:read", "users:disable", "stats:read"]');
```

---

## 4. 管理员 API

### 4.1 用户管理

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /api/admin/users | users:read | 用户列表 |
| GET | /api/admin/users/{id} | users:read | 用户详情 |
| PUT | /api/admin/users/{id} | users:write | 修改用户 |
| POST | /api/admin/users/{id}/disable | users:disable | 禁用用户 |
| POST | /api/admin/users/{id}/enable | users:disable | 启用用户 |
| DELETE | /api/admin/users/{id} | users:delete | 删除用户 |
| POST | /api/admin/users/{id}/promote | users:promote | 设为管理员 |

### 4.2 统计

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /api/admin/stats | stats:read | ��计数据 |
| GET | /api/admin/stats/users | stats:read | 用户统计 |
| GET | /api/admin/stats/usage | stats:read | 使用统计 |

### 4.3 系统配置

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /api/admin/config | config:read | 查看配置 |
| PUT | /api/admin/config | config:write | 修改配置 |

---

## 5. API 响应示例

### 5.1 用户列表

```
GET /api/admin/users?page=1&limit=20&search=john
```

```json
{
    "items": [
        {
            "id": 1,
            "username": "john",
            "email": "john@example.com",
            "nickname": "John",
            "role": "user",
            "is_active": true,
            "clothes_count": 15,
            "created_at": "2026-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "username": "admin1",
            "email": "admin@example.com",
            "nickname": "Admin",
            "role": "admin",
            "is_active": true,
            "clothes_count": 0,
            "created_at": "2026-01-15T00:00:00Z"
        }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
}
```

### 5.2 统计数据

```
GET /api/admin/stats
```

```json
{
    "users": {
        "total": 150,
        "active": 145,
        "inactive": 5,
        "new_today": 3,
        "new_this_month": 25
    },
    "clothes": {
        "total": 1234,
        "by_category": {
            "top": 400,
            "bottom": 350,
            "shoes": 280,
            "accessory": 204
        }
    },
    "recommendations": {
        "total_today": 89,
        "total_this_month": 2345
    },
    "storage": {
        "images_count": 1234,
        "storage_used_mb": 256.5
    }
}
```

---

## 6. 前端页面

### 6.1 管理员入口

在个人中心添加管理员入口（仅管理员可见）：

```
┌─────────────────────────────────────┐
│  个人中心                [编辑]     │
├─────────────────────────────────────┤
│         ┌───────────┐              │
│         │   头像    │              ���
│         └───────────┘              │
│       {昵称 username}              │
├─────────────────────────────────────┤
│  ⚙️ 设置                            │
│  📜 推荐历史                        │
│  ❤️ 收藏推荐                       │
│  🔒 修改密码                        │
├─────────────────────────────────────┤  ← 仅管理员可见
│  👑 用户管理          →            │
│  📊 数据统计          →            │
│  ⚙️ 系统设置          →            │
├─────────────────────────────────────┤
│  🗑️ 注销账户                        │
└─────────────────────────────────────┘
```

### 6.2 用户管理页 `/admin/users`

```
┌─────────────────────────────────────┐
│  ←      用户管理          [搜索]   │
├─────────────────────────────────────┤
│  🔍 搜索用户名/邮箱...              │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐│
│  │ 👤 john          15件衣物    ● ││
│  │    john@email.com              ││
│  │    2026-01-01 注册            ││
│  │    [禁用] [删除] [设为管理员] ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 👑 admin1       0件衣物      ● ││
│  │    admin@email.com             ││
│  │    2026-01-15 注册             ││
│  │    [禁用] [删除]              ││
│  └─────────────────────────────────┘│
│                                     │
│         < 1 2 3 ... 8 >            │
└─────────────────────────────────────┘
```

### 6.3 数据统计页 `/admin/stats`

```
┌─────────────────────────────────────┐
│  ←      数据统计                    │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │ 📊 用户  │ │ 👕 衣物  │        │
│  │   150    │ │  1234    │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  用户增长                          │
│  ┌─────────────────────────────┐   │
│  │    📈 折线图                │   │
│  │    近30天用户增长趋势       │   │
│  └─────────────────────────────┘   │
│                                     │
│  衣物分类分布                      │
│  ┌─────────────────────────────���   │
│  │ 上衣   ████████████  400   │   │
│  │ 裤子   ██████████    350   │   │
│  │ 鞋子   ████████      280   │   │
│  │ 配饰   ██████        204   │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 7. 安全设计

### 7.1 权限检查中间件

```python
# backend/api/admin/deps.py
from fastapi import Depends, HTTPException
from services.auth import get_current_user

async def require_permission(permission: str):
    async def checker(current_user = Depends(get_current_user)):
        if current_user.role not in ['admin', 'superadmin']:
            raise HTTPException(403, "权限不足")

        # superadmin 拥有所有权限
        if current_user.role == 'superadmin':
            return current_user

        # 检查具体权限
        admin = await get_admin(current_user.id)
        if permission == '*' or permission in (admin.permissions or []):
            return current_user

        raise HTTPException(403, "权限不足")

    return checker
```

### 7.2 操作日志

每次敏感操作自动记录：

```python
async def log_admin_action(admin_id: int, action: str, target_type: str, target_id: int, details: dict):
    await db.execute(
        """
        INSERT INTO admin_logs (admin_id, action, target_type, target_id, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (admin_id, action, target_type, target_id, json.dumps(details), get_client_ip())
    )
```

---

## 8. 初始设置

```sql
-- 1. 给 users 表添加 role 字段
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';

-- 2. 创建管理员表
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    permissions TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. 创建操作日志表
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

-- 4. 创建索引
CREATE INDEX IF NOT EXISTS idx_admins_user_id ON admins(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin ON admin_logs(admin_id);
```

---

*文档版本: 1.0*
*更新日期: 2026-05-13*