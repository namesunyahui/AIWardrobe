# AIWardrobe 多用户系统实施计划

**项目:** AIWardrobe 多用户系统  
**目标:** 将单用户应用改为多用户 + MinIO 存储 + Android App  
**设计文档:** design-system/aiwardrobe/ 目录下的 7 个文件

---

## 阶段总览

| 阶段 | 名称 | 优先级 | 预计工作量 |
|------|------|--------|------------|
| 1 | 数据库迁移 | P0 | 1-2h |
| 2 | 后端 - 用户认证 | P0 | 3-4h |
| 3 | 后端 - 数据隔离 | P0 | 2-3h |
| 4 | 后端 - MinIO 集成 | P1 | 2-3h |
| 5 | 后端 - 管理员功能 | P1 | 2h |
| 6 | 前端 - 登录注册 | P0 | 2-3h |
| 7 | 前端 - 状态管理 | P0 | 1-2h |
| 8 | 前端 - 路由保护 | P0 | 1h |
| 9 | 前端 - 个人中心 | P1 | 2h |
| 10 | Android App 打包 | P2 | 2h |

---

## 阶段 1: 数据库迁移

### 目标
在现有 SQLite 数据库上添加多用户支持

### 任务清单
- [ ] 1.1 在 users 表添加 role 字段
- [ ] 1.2 创建 user_settings 表
- [ ] 1.3 创建 refresh_tokens 表
- [ ] 1.4 创建 admins 表
- [ ] 1.5 创建 admin_logs 表
- [ ] 1.6 创建 recommendation_records 表
- [ ] 1.7 创建 favorite_recommendations 表
- [ ] 1.8 修改 clothes 表添加 user_id 和 image_key
- [ ] 1.9 修改 horoscope_records 表添加 user_id
- [ ] 1.10 创建默认用户并迁移现有数据

### 涉及文件
- `backend/storage/models.py` - 添加新表 SQL
- `backend/storage/db.py` - 添加新表初始化
- `backend/storage/migrations/` - 迁移脚本（新建）

### 依赖
- 无

---

## 阶段 2: 后端 - 用户认证

### 目标
实现用户注册、登录、Token 刷新功能

### 任务清单
- [ ] 2.1 创建用户模型 (User, UserCreate, UserResponse)
- [ ] 2.2 创建认证服务 (auth service)
- [ ] 2.3 实现密码加密 (bcrypt)
- [ ] 2.4 创建 JWT 工具函数
- [ ] 2.5 实现注册 API POST /api/auth/register
- [ ] 2.6 实现登录 API POST /api/auth/login
- [ ] 2.7 实现 Token 刷新 POST /api/auth/refresh
- [ ] 2.8 实现获取当前用户 GET /api/auth/me
- [ ] 2.9 实现修改密码 PUT /api/auth/password
- [ ] 2.10 实现更新资料 PUT /api/auth/profile
- [ ] 2.11 实现退出登录 POST /api/auth/logout
- [ ] 2.12 实现账户注销 DELETE /api/auth/account

### 涉及文件
- `backend/domain/users.py` - 用户模型（新建）
- `backend/api/auth.py` - 认证 API（新建）
- `backend/services/auth.py` - 认证服务（新建）
- `backend/api/deps.py` - 依赖注入（可能需要修改）

### 依赖
- 阶段 1 完成

---

## 阶段 3: 后端 - 数据隔离

### 目标
确保用户只能访问自己的数据

### 任务清单
- [ ] 3.1 修改 clothes API 添加 user_id 过滤
- [ ] 3.2 修改 wardrobe API 添加 user_id 过滤
- [ ] 3.3 修改 upload API 关联当前用户
- [ ] 3.4 修改 horoscope API 添加 user_id 过滤
- [ ] 3.5 修改 recommendation API 添加 user_id 过滤
- [x] 3.6 创建用户设置 API (GET/PUT /api/settings)
- [x] 3.7 添加推荐历史 API
- [x] 3.8 添加收藏功能 API

### 涉及文件
- `backend/api/wardrobe.py` - 修改
- `backend/api/upload.py` - 修改
- `backend/api/horoscope.py` - 修改
- `backend/api/recommendation.py` - 修改
- `backend/api/settings.py` - 新建

### 依赖
- 阶段 2 完成

---

## 阶段 4: 后端 - MinIO 集成

### 目标
将图片存储从本地文件系统迁移到 MinIO

### 任务清单
- [x] 4.1 创建 MinIO 服务 (backend/services/minio.py)
- [x] 4.2 实现图片上传到 MinIO
- [x] 4.3 实现获取图片预签名 URL
- [x] 4.4 实现删除 MinIO 图片
- [x] 4.5 修改 upload API 使用 MinIO
- [x] 4.6 添加头像上传 API
- [x] 4.7 配置 MinIO 客户端
- [x] 4.8 更新图片 URL 返回格式

### 涉及文件
- `backend/services/minio.py` - 新建
- `backend/api/upload.py` - 修改
- `backend/api/images.py` - 新建（图片访问）
- `backend/api/avatar.py` - 新建（头像）

### 依赖
- 阶段 3 完成

---

## 阶段 5: 后端 - 管理员功能

### 目标
实现管理员管理用户的功能

### 任务清单
- [ ] 5.1 添加管理员权限检查中间件
- [ ] 5.2 实现用户列表 API GET /api/admin/users
- [ ] 5.3 实现用户详情 API GET /api/admin/users/{id}
- [ ] 5.4 实现修改用户 API PUT /api/admin/users/{id}
- [ ] 5.5 实现禁用/启用用户 API
- [ ] 5.6 实现删除用户 API
- [ ] 5.7 实现设为管理员 API
- [ ] 5.8 实现统计数据 API GET /api/admin/stats
- [ ] 5.9 添加操作日志记录

### 涉及文件
- `backend/api/admin/users.py` - 新建
- `backend/api/admin/stats.py` - 新建
- `backend/api/admin/deps.py` - 新建（权限中间件）
- `backend/api/__init__.py` - 注册 admin 路由

### 依赖
- 阶段 2、3 完成

---

## 阶段 6: 前端 - 登录注册

### 目标
创建登录和注册页面

### 任务清单
- [ ] 6.1 创建 Login.jsx 页面
- [ ] 6.2 创建 Register.jsx 页面
- [ ] 6.3 创建 AuthInput 组件
- [ ] 6.4 实现表单验证
- [ ] 6.5 集成登录 API
- [ ] 6.6 集成注册 API
- [ ] 6.7 添加多语言支持

### 涉及文件
- `frontend/src/pages/Login.jsx` - 新建
- `frontend/src/pages/Register.jsx` - 新建
- `frontend/src/components/AuthInput.jsx` - 新建
- `frontend/src/locales/` - 添加翻译

### 依赖
- 阶段 2 完成

---

## 阶段 7: 前端 - 状态管理

### 目标
管理用户认证状态

### 任务清单
- [ ] 7.1 创建 AuthContext.jsx
- [ ] 7.2 实现登录/登出状态
- [ ] 7.3 实现 Token 存储 (localStorage)
- [ ] 7.4 实现 Token 自动刷新
- [ ] 7.5 封装 authFetch 工具函数
- [ ] 7.6 修改 API_BASE 适配

### 涉及文件
- `frontend/src/contexts/AuthContext.jsx` - 新建
- `frontend/src/utils/api.js` - 修改
- `frontend/src/App.jsx` - 修改（包裹 AuthProvider）

### 依赖
- 阶段 6 完成

---

## 阶段 8: 前端 - 路由保护

### 目标
保护需要登录的页面

### 任务清单
- [ ] 8.1 创建 ProtectedRoute 组件
- [ ] 8.2 创建 PublicRoute 组件
- [ ] 8.3 修改 App.jsx 路由配置
- [ ] 8.4 更新 TabBar（未登录时显示登录入口）
- [ ] 8.5 添加登录后跳转逻辑

### 涉及文件
- `frontend/src/components/ProtectedRoute.jsx` - 新建
- `frontend/src/components/PublicRoute.jsx` - 新建
- `frontend/src/App.jsx` - 修改
- `frontend/src/components/TabBar.jsx` - 修改

### 依赖
- 阶段 7 完成

---

## 阶段 9: 前端 - 个人中心

### 目标
创建个人中心和用户管理页面

### 任务清单
- [ ] 9.1 创建 Profile.jsx 页面
- [ ] 9.2 创建 UserAvatar 组件
- [ ] 9.3 创建 ProfileMenuItem 组件
- [ ] 9.4 创建 PasswordChange.jsx 页面
- [ ] 9.5 创建 RecommendationHistory.jsx 页面
- [ ] 9.6 添加管理员入口（仅管理员可见）
- [ ] 9.7 创建 AdminUsers.jsx 页面（管理员）
- [ ] 9.8 创建 AdminStats.jsx 页面（管理员）

### 涉及文件
- `frontend/src/pages/Profile.jsx` - 新建
- `frontend/src/pages/PasswordChange.jsx` - 新建
- `frontend/src/pages/RecommendationHistory.jsx` - 新建
- `frontend/src/pages/admin/AdminUsers.jsx` - 新建
- `frontend/src/pages/admin/AdminStats.jsx` - 新建
- `frontend/src/components/UserAvatar.jsx` - 新建
- `frontend/src/components/ProfileMenuItem.jsx` - 新建

### 依赖
- 阶段 8 完成

---

## 阶段 10: Android App 打包

### 目标
将前端打包为 Android App

### 任务清单
- [ ] 10.1 安装 Capacitor 依��
- [ ] 10.2 初始化 Capacitor
- [ ] 10.3 添加 Android 平台
- [ ] 10.4 配置 Android 权限
- [ ] 10.5 修改 API 请求地址
- [ ] 10.6 集成 Camera 插件
- [ ] 10.7 集成 Preferences 插件
- [ ] 10.8 集成 Status Bar 插件
- [ ] 10.9 构建 Debug APK
- [ ] 10.10 测试并修复问题

### 涉及文件
- `frontend/capacitor.config.ts` - 新建
- `frontend/android/` - 自动生成

### 依赖
- 阶段 9 完成

---

## 文件变更清单

### 新建文件
```
backend/
├── domain/users.py
├── api/auth.py
├── api/settings.py
├── api/images.py
├── api/avatar.py
├── api/admin/users.py
├── api/admin/stats.py
├── api/admin/deps.py
├── services/auth.py
├── services/minio.py

frontend/src/
├── contexts/AuthContext.jsx
├── pages/Login.jsx
├── pages/Register.jsx
├── pages/Profile.jsx
├── pages/PasswordChange.jsx
├── pages/RecommendationHistory.jsx
├── pages/admin/AdminUsers.jsx
├── pages/admin/AdminStats.jsx
├── components/AuthInput.jsx
├── components/ProtectedRoute.jsx
├── components/PublicRoute.jsx
├── components/UserAvatar.jsx
├── components/ProfileMenuItem.jsx
```

### 修改文件
```
backend/
├── storage/models.py
├── storage/db.py
├── api/wardrobe.py
├── api/upload.py
├── api/horoscope.py
├── api/recommendation.py
├── main.py

frontend/src/
├── App.jsx
├── utils/api.js
├── components/TabBar.jsx
```

---

## 执行顺序建议

1. **先完成后端** → 阶段 1-5
2. **再完成前端** → 阶段 6-9
3. **最后打包 App** → 阶段 10

**总预计工作量:** 约 25-30 小时

---

*计划版本: 1.0*
*创建日期: 2026-05-13*
*基于设计文档: design-system/aiwardrobe/*