import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect, useRef } from 'react'
import { useAuth } from './contexts/AuthContext'
import Home from './pages/Home'
import Entry from './pages/Entry'
import Wardrobe from './pages/Wardrobe'
import ClothesDetail from './pages/ClothesDetail'
import Outfit from './pages/Outfit'
import Recommendation from './pages/Recommendation'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import RecommendationHistory from './pages/RecommendationHistory'
import Favorites from './pages/Favorites'
import AdminUsers from './pages/AdminUsers'
import AdminStats from './pages/AdminStats'
import ProfileEdit from './pages/ProfileEdit'
import ProfilePassword from './pages/ProfilePassword'
import SettingsPage from './pages/SettingsPage'
import TabBar from './components/TabBar'
import ToastContainer from './components/Toast'
import ConfirmDialog from './components/ConfirmDialog'
import './index.css'

function ScrollManager({ children }) {
  const location = useLocation()
  const scrollRef = useRef(null)
  const prevPathRef = useRef(null)

  // 监听滚动事件，实时保存滚动位置
  useEffect(() => {
    const scrollContainer = scrollRef.current
    if (!scrollContainer) return

    const handleScroll = () => {
      const path = location.pathname
      // 只保存非详情页的滚动位置
      if (!path.startsWith('/clothes/')) {
        sessionStorage.setItem(`scroll_${path}`, scrollContainer.scrollTop.toString())
      }
    }

    scrollContainer.addEventListener('scroll', handleScroll, { passive: true })
    return () => scrollContainer.removeEventListener('scroll', handleScroll)
  }, [location.pathname])

  // 路由变化时恢复滚动位置
  useEffect(() => {
    const scrollContainer = scrollRef.current
    if (!scrollContainer) return

    const currentPath = location.pathname
    const prevPath = prevPathRef.current

    // 进入 clothes 详情页：滚动到顶部
    if (currentPath.startsWith('/clothes/')) {
      scrollContainer.scrollTop = 0
    }

    // 从 clothes 返回其他页面：恢复滚动位置
    if (prevPath && prevPath.startsWith('/clothes/')) {
      const savedPos = sessionStorage.getItem(`scroll_${currentPath}`)
      if (savedPos) {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            scrollContainer.scrollTop = parseInt(savedPos, 10)
          })
        })
      }
    }

    prevPathRef.current = currentPath
  }, [location.pathname])

  return (
    <div ref={scrollRef} className="overflow-y-auto" style={{ height: 'calc(100dvh - 64px - env(safe-area-inset-bottom, 0px))' }}>
      {children}
    </div>
  )
}

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

function AdminRoute({ children }) {
  const { user, isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-zinc-200 dark:border-zinc-700 border-t-accent rounded-full animate-spin"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!user?.role || !['admin', 'superadmin'].includes(user.role)) {
    return <Navigate to="/profile" replace />
  }

  return children
}

function AppRoutes() {
  return (
    <>
      <ScrollManager>
        <Routes>
          {/* 公开路由 */}
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

          {/* 需认证路由 */}
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/entry" element={<ProtectedRoute><Entry /></ProtectedRoute>} />
          <Route path="/wardrobe" element={<ProtectedRoute><Wardrobe /></ProtectedRoute>} />
          <Route path="/clothes/:id" element={<ProtectedRoute><ClothesDetail /></ProtectedRoute>} />
          <Route path="/outfit" element={<ProtectedRoute><Outfit /></ProtectedRoute>} />
          <Route path="/recommendation" element={<ProtectedRoute><Recommendation /></ProtectedRoute>} />
          <Route path="/recommendation/:id" element={<ProtectedRoute><Recommendation /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/profile/history" element={<ProtectedRoute><RecommendationHistory /></ProtectedRoute>} />
          <Route path="/profile/favorites" element={<ProtectedRoute><Favorites /></ProtectedRoute>} />
          <Route path="/profile/edit" element={<ProtectedRoute><ProfileEdit /></ProtectedRoute>} />
          <Route path="/profile/password" element={<ProtectedRoute><ProfilePassword /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
          <Route path="/admin/stats" element={<AdminRoute><AdminStats /></AdminRoute>} />

          {/* 默认跳转 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ScrollManager>
      <TabBar />
    </>
  )
}

function App() {
  return (
    <Router>
      <ToastContainer />
      <ConfirmDialog />
      <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] pb-safe max-w-md mx-auto relative shadow-sm">
        <AppRoutes />
      </div>
    </Router>
  )
}

export default App