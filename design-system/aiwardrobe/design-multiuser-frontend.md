# AIWardrobe 多用户前端设计

## 1. 设计原则

### 1.1 保持现有风格
- **配色方案**：保持现有的蓝(#2563EB)为主色调
- **布局**：移动端优先，最大宽度 432px
- **组件**：卡片式设计、圆角边框、磨砂玻璃效果
- **图标**：使用 lucide-react
- **字体**：Inter

### 1.2 配色变量（来自 index.css）
```css
:root {
    --bg-primary: #FAFAFA;
    --bg-card: #FFFFFF;
    --text-primary: #09090B;
    --text-secondary: #3F3F46;
    --accent: #2563EB;
    --border: #E4E4E7;
}

.dark {
    --bg-primary: #09090B;
    --bg-card: #18181B;
    --text-primary: #FAFAFA;
    --text-secondary: #A1A1AA;
    --accent: #3B82F6;
    --border: #27272A;
}
```

---

## 2. 页面设计

### 2.1 登录页 `/login`

```
┌─────────────────────────────────────┐
│  ←                        [EN/中]   │  ← 语言切换
├─────────────────────────────────────┤
│                                     │
│           [Logo/图标]               │
│                                     │
│        AIWardrobe                   │
│                                     │
│     ─────────────────────           │
│                                     │
│     账号                            │
│  ┌─────────────────────────────┐    │
│  │ username or email           │    │
│  └─────────────────────────────┘    │
│                                     │
│     密码                            │
│  ┌─────────────────────────────┐    │
│  │ ••••••••                    │    │
│  └─────────────────────────────┘    │
│                          [👁]       │  ← 密码可见切换
│                                     │
│     ┌─────────────────────────┐     │
│     │        登录              │     │
│     └─────────────────────────┘     │
│                                     │
│     还没有账号？[注册]              │
│                                     │
└─────────────────────────────────────┘
```

**设计要点：**
- 输入框样式：`input-field` 类（来自 index.css）
- 登录按钮：`btn-primary` 类
- 语言切换：右上角，可切换中/英/日
- 返回箭头：左上角，点击返回首页或上一页
- 底部注册链接：使用 `text-accent` 颜色

---

### 2.2 注册页 `/register`

```
┌─────────────────────────────────────┐
│  ←                                 │
├─────────────────────────────────────┤
│                                     │
│           [Logo/图标]               │
│                                     │
│        创建账号                     │
│                                     │
│     ─────────────────────           │
│                                     │
│     用户名                          │
│  ┌─────────────────────────────┐    │
│  │ john_doe                    │    │
│  └─────────────────────────────┘    │
│     [3-20位字母数字下划线]           │
│                                     │
│     邮箱                            │
│  ┌─────────────────────────────┐    │
│  │ john@example.com            │    │
│  └─────────────────────────────┘    │
│                                     │
│     密码                            │
│  ┌─────────────────────────────┐    │
│  │ ••••••••                    │    │
│  └─────────────────────────────┘    │
│     [至少6位]                        │
│                                     │
│     确认密码                        │
│  ┌─────────────────────────────┐    │
│  │ ••••••••                    │    │
│  └─────────────────────────────┘    │
│                                     │
│     昵称（可选）                     │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│  └─────────────────────────────┘    │
│                                     │
│     ┌─────────────────────────┐     │
│     │        注册              │     │
│     └─────────────────────────┘     │
│                                     │
│     已有账号？[登录]                │
│                                     │
└─────────────────────────────────────┘
```

**设计要点：**
- 实时验证：用户名、邮箱、密码格式验证
- 错误提示：输入框下方红色小字显示
- 密码强度指示：可选，弱/中/强
- 成功跳转：注册成功后自动登录并跳转

---

### 2.3 首页（需登录）`/`

```
┌─────────────────────────────────────┐
│  👤 {用户名}           ⚙️  🚪       │  ← 头像/设置/退出
├─────────────────────────────────────┤
│     5月13日 星期二                   │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 🌤️ 上海  22° 晴                 ││
│  │ 体感21°  湿度65%  风速15        ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 👕 衣物轮播          [查看全部] ││
│  │ ┌─────┐                         ││
│  │ │ 衣物 │ ◀  ▶                  ││
│  │ │图片  │                         ││
│  │ └─────┘                         ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ✨ 白羊座今日运势               ││
│  │ 心情：愉快 幸运色：红色        ││
│  │ 幸运数字：7                    ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
│ 🏠   ＋    👕   👤   ✨           │
│ 首页 上传 衣柜 推荐 我的          │
└─────────────────────────────────────┘
```

**改动说明：**
- 顶部导航栏：新增用户头像、设置、退出按钮
- TabBar：最后一项改为"我的"（个人中心）
- 数据隔离：只显示当前用户的衣物和运势

---

### 2.4 个人中心页 `/profile`

```
┌─────────────────────────────────────┐
│  个人中心                [编辑]     │
├─────────────────────────────────────┤
│                                     │
│         ┌───────────┐              │
│         │   头像    │              │
│         │  圆形     │              │
│         └───────────┘              │
│                                     │
│       {昵称 username}              │
│       {email@example.com}          │
│                                     │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 👤 个人资料                  │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ ⚙️ 设置                      │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 📜 推荐历史                  │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ ❤️ 收藏推荐                  │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 🔒 修改密码                  │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 🗑️ 注销账户                  │    │
│  └─────────────────────────────┘    │
│                                     │
│         ─────────────────           │
│              版本 v1.0.0             │
│                                     │
└─────────────────────────────────────┘
│ 🏠   ＋    👕   ✨   👤           │
└─────────────────────────────────────┘
```

---

### 2.5 修改密码页 `/profile/password`

```
┌─────────────────────────────────────┐
│  ←      修改密码                    │
├─────────────────────────────────────┤
│                                     │
│     当前密码                        │
│  ┌─────────────────────────────┐    │
│  │ ••••••••                    │    │
│  └─────────────────────────────┘    │
│                                     │
│     新密码                          │
│  ┌─────────────────────────────┐    │
│  │ ••••••••                    │    │
│  └─────────────────────────────┘    │
│     [至少6位]                        │
│                                     │
│     确认新密码                      │
│  ┌─────────────────────────────┐    │
│  │ ••••••••                    │    │
│  └─────────────────────────────┘    │
│                                     │
│     ┌─────────────────────────┐     │
│     │        保存              │     │
│     └─────────────────────────┘     │
│                                     │
│     [忘记当前密码？]                │
│                                     │
└─────────────────────────────────────┘
```

---

### 2.6 推荐历史页 `/profile/history`

```
┌─────────────────────────────────────┐
│  ←      推荐历史                    │
├─────────────────────────────────────┤
│                                     │
│  [全部] [已收藏]                    │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 📅 2026-05-13 上海 22° 晴      ││
│  │ 推荐：白色T恤 + 蓝色牛仔裤     ││
│  │ 🅱️ ❤️                          ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 📅 2026-05-12 北京 18° 多云    ││
│  │ 推荐：灰色卫衣 + 黑色运动裤    ││
│  │ 🅱️ ❤️                          ││
│  └─────────────────────────────────┘│
│                                     │
│              ...                    │
│                                     │
└─────────────────────────────────────┘
│ 🏠   ＋    👕   ✨   👤           │
└─────────────────────────────────────┘
```

---

## 3. 组件设计

### 3.1 AuthInput - 认证输入框

```jsx
function AuthInput({ label, type, placeholder, error, ...props }) {
    const [showPassword, setShowPassword] = useState(false)
    const isPassword = type === 'password'

    return (
        <div className="space-y-1.5">
            <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                {label}
            </label>
            <div className="relative">
                <input
                    type={isPassword && showPassword ? 'text' : type}
                    placeholder={placeholder}
                    className="input-field pr-10"
                    {...props}
                />
                {isPassword && (
                    <button
                        type="button"
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600"
                        onClick={() => setShowPassword(!showPassword)}
                    >
                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                )}
            </div>
            {error && (
                <p className="text-xs text-red-500">{error}</p>
            )}
        </div>
    )
}
```

---

### 3.2 ProfileMenuItem - 个人中心菜单项

```jsx
function ProfileMenuItem({ icon: Icon, label, onClick, danger = false }) {
    return (
        <button
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                danger
                    ? 'text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
                    : 'text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800'
            }`}
            onClick={onClick}
        >
            <Icon size={20} />
            <span className="text-sm font-medium">{label}</span>
            <ChevronRight size={18} className="ml-auto text-zinc-400" />
        </button>
    )
}
```

---

### 3.3 UserAvatar - 用户头像

```jsx
function UserAvatar({ src, size = 'md', onClick }) {
    const sizeClasses = {
        sm: 'w-8 h-8',
        md: 'w-12 h-12',
        lg: 'w-20 h-20'
    }

    return (
        <div
            className={`${sizeClasses[size]} rounded-full bg-zinc-200 dark:bg-zinc-700 overflow-hidden flex items-center justify-center cursor-pointer`}
            onClick={onClick}
        >
            {src ? (
                <img src={src} alt="avatar" className="w-full h-full object-cover" />
            ) : (
                <User size={size === 'lg' ? 32 : 20} className="text-zinc-400" />
            )}
        </div>
    )
}
```

---

### 3.4 ProtectedRoute - 路由保护

```jsx
function ProtectedRoute({ children }) {
    const { isAuthenticated } = useAuth()
    const location = useLocation()

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />
    }

    return children
}
```

---

## 4. 状态管理

### 4.1 AuthContext

```jsx
// src/contexts/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react'
import { API_BASE } from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [token, setToken] = useState(localStorage.getItem('access_token'))
    const [loading, setLoading] = useState(true)

    const isAuthenticated = !!token

    useEffect(() => {
        if (token) {
            fetchUserProfile()
        } else {
            setLoading(false)
        }
    }, [token])

    const fetchUserProfile = async () => {
        try {
            const response = await fetch(`${API_BASE}/auth/me`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (response.ok) {
                const userData = await response.json()
                setUser(userData)
            } else {
                logout()
            }
        } catch (error) {
            console.error('Failed to fetch user:', error)
            logout()
        } finally {
            setLoading(false)
        }
    }

    const login = async (username, password) => {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || '登录失败')
        }

        const data = await response.json()
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        setToken(data.access_token)
        return data
    }

    const register = async (userData) => {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || '注册失败')
        }

        return response.json()
    }

    const logout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setToken(null)
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, token, isAuthenticated, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
```

---

### 4.2 API 请求封装

```jsx
// src/utils/api.js 新增

export async function authFetch(url, options = {}) {
    const token = localStorage.getItem('access_token')

    const headers = {
        ...options.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {})
    }

    const response = await fetch(url, { ...options, headers })

    // Token 过期，尝试刷新
    if (response.status === 401) {
        const refreshed = await refreshToken()
        if (refreshed) {
            // 重试请求
            const newToken = localStorage.getItem('access_token')
            headers.Authorization = `Bearer ${newToken}`
            return fetch(url, { ...options, headers })
        } else {
            // 刷新失败，跳转登录
            localStorage.removeItem('access_token')
            window.location.href = '/login'
        }
    }

    return response
}

async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) return false

    try {
        const response = await fetch(`${API_BASE}/auth/refresh`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${refreshToken}` }
        })

        if (response.ok) {
            const data = await response.json()
            localStorage.setItem('access_token', data.access_token)
            return true
        }
    } catch (error) {
        console.error('Token refresh failed:', error)
    }

    return false
}
```

---

## 5. 路由配置

### 5.1 路由结构

```jsx
// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import TabBar from './components/TabBar'

// 公开页面
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'

// 需认证页面
import Entry from './pages/Entry'
import Wardrobe from './pages/Wardrobe'
import Outfit from './pages/Outfit'
import Recommendation from './pages/Recommendation'
import Profile from './pages/Profile'
import PasswordChange from './pages/PasswordChange'
import RecommendationHistory from './pages/RecommendationHistory'

function ProtectedRoute({ children }) {
    const { isAuthenticated, loading } = useAuth()

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="w-8 h-8 border-4 border-zinc-200 dark:border-zinc-700 border-t-accent rounded-full animate-spin"></div>
            </div>
        )
    }

    return isAuthenticated ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
    const { isAuthenticated, loading } = useAuth()

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="w-8 h-8 border-4 border-zinc-200 dark:border-zinc-700 border-t-accent rounded-full animate-spin"></div>
            </div>
        )
    }

    return isAuthenticated ? <Navigate to="/" replace /> : children
}

function AppRoutes() {
    const { isAuthenticated } = useAuth()

    return (
        <Routes>
            {/* 公开路由 */}
            <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
            <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

            {/* 需认证路由 */}
            <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/entry" element={<ProtectedRoute><Entry /></ProtectedRoute>} />
            <Route path="/wardrobe" element={<ProtectedRoute><Wardrobe /></ProtectedRoute>} />
            <Route path="/outfit" element={<ProtectedRoute><Outfit /></ProtectedRoute>} />
            <Route path="/recommendation" element={<ProtectedRoute><Recommendation /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/profile/password" element={<ProtectedRoute><PasswordChange /></ProtectedRoute>} />
            <Route path="/profile/history" element={<ProtectedRoute><RecommendationHistory /></ProtectedRoute>} />

            {/* 默认跳转 */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    )
}

export default function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <div className="min-h-screen bg-[var(--bg-primary)]">
                    <AppRoutes />
                    <TabBar />
                </div>
            </BrowserRouter>
        </AuthProvider>
    )
}
```

---

### 5.2 TabBar 更新

```jsx
// 更新 tabs 配置
const tabs = isAuthenticated ? [
    { path: '/', icon: House, label: t('tabs.home') },
    { path: '/entry', icon: PlusCircle, label: t('tabs.entry') },
    { path: '/wardrobe', icon: Search, label: t('tabs.wardrobe') },
    { path: '/recommendation', icon: Sparkles, label: t('tabs.recommendation') },
    { path: '/profile', icon: User, label: t('tabs.profile') }
] : [
    { path: '/login', icon: LogIn, label: t('tabs.login') }
]
```

---

## 6. 页面文件结构

```
frontend/src/
├── pages/
│   ├── Home.jsx              # 首页（需登录）
│   ├── Entry.jsx             # 添加衣物
│   ├── Wardrobe.jsx          # 衣柜
│   ├── Outfit.jsx            # 搭配
│   ├── Recommendation.jsx    # 推荐
│   ├── Login.jsx             # 登录（公开）
│   ├── Register.jsx          # 注册（公开）
│   ├── Profile.jsx           # 个人中心（需登录）
│   ├── PasswordChange.jsx    # 修改密码（需登录）
│   └── RecommendationHistory.jsx  # 推荐历史（需登录）
├── contexts/
│   └── AuthContext.jsx       # 认证状态管理
├── components/
│   ├── TabBar.jsx            # 底部导航（已更新）
│   ├── AuthInput.jsx         # 认证输入框
│   ├── UserAvatar.jsx        # 用户头像
│   └── ProfileMenuItem.jsx   # 个人中心菜单项
└── utils/
    └── api.js                # API 工具（新增 authFetch）
```

---

## 7. 国际化文本

```json
// locales/zh.json
{
    "auth": {
        "login": "登录",
        "register": "注册",
        "logout": "退出登录",
        "username": "用户名",
        "email": "邮箱",
        "password": "密码",
        "confirmPassword": "确认密码",
        "nickname": "昵称",
        "forgotPassword": "忘记密码？",
        "noAccount": "还没有账号？",
        "hasAccount": "已有账号？",
        "loginSuccess": "登录成功",
        "registerSuccess": "注册成功"
    },
    "profile": {
        "title": "个人中心",
        "edit": "编辑",
        "personalInfo": "个人资料",
        "settings": "设置",
        "history": "推荐历史",
        "favorites": "收藏推荐",
        "changePassword": "修改密码",
        "deleteAccount": "注销账户",
        "version": "版本"
    }
}
```

---

*文档版本: 1.0*
*更新日期: 2026-05-13*