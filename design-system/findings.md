# 研究发现

## 设计文档分析

### 已确认的设计文件 (7个)

1. **design-multiuser-minio.md** - 原始需求文档
   - 目标：多用户 + MinIO 存储
   - 当前状态：单用户，本地存储

2. **design-multiuser-api.md** - API 设计
   - 认证 API：register, login, refresh, me, password, profile, logout, delete
   - 衣物 API：需认证，自动 user_id 隔离
   - 推荐历史 API：history, favorite, unfavorite
   - 用户设置 API：settings
   - 管理员 API：users, stats, config

3. **design-multiuser-database.md** - 数据库设计
   - 新增表：users, user_settings, refresh_tokens, admins, admin_logs, recommendation_records, favorite_recommendations
   - 修改表：clothes (+user_id, +image_key), horoscope_records (+user_id)
   - 迁移脚本：完整的 V1→V2 SQL

4. **design-multiuser-frontend.md** - 前端设计
   - 页面：Login, Register, Home(改), Profile, PasswordChange, History
   - 组件：AuthInput, UserAvatar, ProfileMenuItem, ProtectedRoute
   - 状态管理：AuthContext
   - 样式：保持现有蓝+白+磨砂玻璃风格

5. **design-multiuser-admin.md** - 管理员设计
   - 角色：user / admin / superadmin
   - 权限：独立 admins 表，细粒度控制
   - API：用户管理、统计、系统配置
   - 安全：权限中间件 + 操作日志

6. **design-app-android.md** - Android 打包
   - 方案：Capacitor
   - 插件：Camera, Filesystem, Preferences, StatusBar, Haptics
   - 权限：相机、存储、网络
   - 构建：assembleDebug / assembleRelease

7. **MASTER.md** - 设计系统主文件
   - 配色：Primary #18181B, CTA #2563EB
   - 字体：Inter + Playfair Display
   - 规范：无 emoji 图标、cursor-pointer、过渡动画

---

## 现有代码结构分析

### 后端 (FastAPI)
- `backend/api/` - 7个路由文件
- `backend/services/` - 业务逻辑
- `backend/domain/` - 数据模型
- `backend/storage/` - 数据库操作

### 前端 (React)
- `frontend/src/pages/` - 6个页面
- `frontend/src/components/` - 5个组件
- `frontend/src/contexts/` - 3个上下文
- `frontend/src/utils/` - API 工具

---

## 关键技术点

1. **认证**: JWT + bcrypt + refresh_token
2. **数据隔离**: 所有查询添加 user_id 条件
3. **图片存储**: MinIO 对象存储，预签名 URL
4. **权限管理**: admins 表 + 中间件检查
5. **App 打包**: Capacitor + WebView

---

## 待确认问题

- [x] 是否需要管理员 → 已确认（方案 B）
- [x] 目标平台 → Android
- [ ] 数据库是否切换 → 不需要，SQLite 支持
- [ ] 是否保留现有数据 → 迁移到默认用户

---

*更新日期: 2026-05-13*