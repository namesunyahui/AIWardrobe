import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { API_BASE, toImageUrl } from '../utils/api'
import { ArrowLeft, Users, Search, Shield, ShieldOff, RefreshCw, Loader2, ChevronDown, ChevronUp, X } from 'lucide-react'

export default function AdminUsers() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { user, token } = useAuth()
    const [users, setUsers] = useState([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [updating, setUpdating] = useState(null)
    const [selectedUser, setSelectedUser] = useState(null)
    const [userClothes, setUserClothes] = useState(null)
    const [loadingClothes, setLoadingClothes] = useState(false)
    const [previewImage, setPreviewImage] = useState(null)

    useEffect(() => {
        if (user && token && (user.role === 'admin' || user.role === 'superadmin')) {
            fetchUsers()
        } else if (user && token) {
            navigate('/')
        }
    }, [user, token])

    useEffect(() => {
        if (user && token && (user.role === 'admin' || user.role === 'superadmin') && search !== undefined) {
            fetchUsers()
        }
    }, [search])

    const fetchUsers = async () => {
        setLoading(true)
        try {
            const response = await fetch(`${API_BASE}/admin/users?search=${encodeURIComponent(search)}&limit=100`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setUsers(data.items || [])
            }
        } catch (error) {
            console.error('Failed to fetch users:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = (e) => {
        e.preventDefault()
        fetchUsers()
    }

    const toggleUserStatus = async (userId, currentStatus) => {
        setUpdating(userId)
        try {
            const newStatus = currentStatus ? 0 : 1
            const response = await fetch(`${API_BASE}/admin/users/${userId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ is_active: newStatus })
            })
            if (response.ok) {
                setUsers(users.map(u =>
                    u.id === userId ? { ...u, is_active: newStatus } : u
                ))
            }
        } catch (error) {
            console.error('Failed to update user status:', error)
        } finally {
            setUpdating(null)
        }
    }

    const changeUserRole = async (userId, newRole) => {
        setUpdating(userId)
        try {
            const response = await fetch(`${API_BASE}/admin/users/${userId}/role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ role: newRole })
            })
            if (response.ok) {
                setUsers(users.map(u =>
                    u.id === userId ? { ...u, role: newRole } : u
                ))
            }
        } catch (error) {
            console.error('Failed to update user role:', error)
        } finally {
            setUpdating(null)
        }
    }

    const viewUserDetail = async (userId) => {
        if (selectedUser === userId) {
            setSelectedUser(null)
            setUserClothes(null)
            return
        }
        setSelectedUser(userId)
        setLoadingClothes(true)
        setUserClothes(null)
        try {
            const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            console.log('User detail response:', response.status)
            if (response.ok) {
                const data = await response.json()
                console.log('User detail data:', data)
                setUserClothes(data)
            } else {
                const error = await response.json()
                console.error('Error:', error)
                alert('加载失败: ' + (error.detail || '未知错误'))
            }
        } catch (error) {
            console.error('Failed to fetch user detail:', error)
            alert('加载失败: ' + error.message)
        } finally {
            setLoadingClothes(false)
        }
    }

    const getRoleBadge = (role) => {
        const styles = {
            superadmin: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
            admin: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
            user: 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300'
        }
        const labels = {
            superadmin: '超级管理员',
            admin: '管理员',
            user: '用户'
        }
        return (
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${styles[role] || styles.user}`}>
                {labels[role] || '用户'}
            </span>
        )
    }

    if (loading && users.length === 0) {
        return (
            <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-accent animate-spin" />
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-[var(--bg-primary)]">
            {/* Header */}
            <header className="px-4 pt-6 pb-4 flex items-center gap-3">
                <button
                    onClick={() => navigate('/profile')}
                    className="w-10 h-10 rounded-xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-600 dark:text-zinc-300"
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                        {t('admin.users')}
                    </h1>
                    <p className="text-xs text-zinc-500">{users.length} 位用户</p>
                </div>
            </header>

            {/* Search */}
            <form onSubmit={handleSearch} className="px-4 pb-4">
                <div className="relative">
                    <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="搜索用户名或邮箱..."
                        className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-100 dark:bg-zinc-800 border-none text-sm"
                    />
                </div>
            </form>

            {/* User List */}
            <div className="px-4 space-y-2 pb-8">
                {users.map(u => (
                    <div key={u.id} className="card overflow-hidden">
                        {/* User Row */}
                        <div className="p-3 flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center text-zinc-500">
                                {u.username?.[0]?.toUpperCase() || 'U'}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className="font-medium text-zinc-900 dark:text-zinc-100 truncate">
                                        {u.username}
                                    </span>
                                    {getRoleBadge(u.role)}
                                </div>
                                <p className="text-xs text-zinc-500 truncate">{u.email}</p>
                            </div>
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={() => viewUserDetail(u.id)}
                                    className="p-2 rounded-lg text-zinc-400 hover:text-accent hover:bg-zinc-50 dark:hover:bg-zinc-800"
                                    title="查看详情"
                                >
                                    {selectedUser === u.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </button>
                                {u.role !== 'superadmin' && (
                                    <>
                                        <button
                                            onClick={() => toggleUserStatus(u.id, u.is_active)}
                                            disabled={updating === u.id}
                                            className={`p-2 rounded-lg ${
                                                u.is_active
                                                    ? 'text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20'
                                                    : 'text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
                                            }`}
                                            title={u.is_active ? '禁用用户' : '启用用户'}
                                        >
                                            {updating === u.id ? (
                                                <Loader2 size={16} className="animate-spin" />
                                            ) : u.is_active ? (
                                                <Shield size={16} />
                                            ) : (
                                                <ShieldOff size={16} />
                                            )}
                                        </button>
                                        {user?.role === 'superadmin' && (
                                            <select
                                                value={u.role}
                                                onChange={(e) => changeUserRole(u.id, e.target.value)}
                                                disabled={updating === u.id}
                                                className="text-xs px-2 py-1 rounded border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800"
                                            >
                                                <option value="user">用户</option>
                                                <option value="admin">管理员</option>
                                                <option value="superadmin">超级管理员</option>
                                            </select>
                                        )}
                                    </>
                                )}
                            </div>
                        </div>

                        {/* Expanded Detail */}
                        {selectedUser === u.id && (
                            <div className="border-t border-zinc-100 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-800/50">
                                {loadingClothes ? (
                                    <div className="flex items-center justify-center py-4">
                                        <Loader2 className="w-5 h-5 text-accent animate-spin" />
                                    </div>
                                ) : userClothes ? (
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-4 text-sm flex-wrap">
                                            <span className="text-zinc-500">衣物数量:</span>
                                            <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                                                {userClothes.clothes_count || 0} 件
                                            </span>
                                            <span className="text-zinc-400">|</span>
                                            <span className="text-zinc-500">状态:</span>
                                            <span className={userClothes.is_active ? 'text-green-600' : 'text-red-500'}>
                                                {userClothes.is_active ? '启用' : '禁用'}
                                            </span>
                                            <span className="text-zinc-400">|</span>
                                            <span className="text-zinc-500">注册时间:</span>
                                            <span className="text-zinc-900 dark:text-zinc-100">
                                                {userClothes.created_at?.split('T')[0] || '-'}
                                            </span>
                                        </div>

                                        {/* User's Clothes Preview */}
                                        {userClothes.clothes && userClothes.clothes.length > 0 && (
                                            <div>
                                                <p className="text-xs text-zinc-500 mb-2">衣物列表 ({userClothes.clothes.length}/{userClothes.clothes_count}):</p>
                                                <div className="flex gap-2 overflow-x-auto pb-1">
                                                    {userClothes.clothes.map((clothes) => (
                                                        <button
                                                            key={clothes.id}
                                                            onClick={() => setPreviewImage(toImageUrl(clothes.image_url))}
                                                            className="w-16 h-16 shrink-0 rounded-lg bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 p-1 hover:border-accent transition-colors"
                                                        >
                                                            {clothes.image_url ? (
                                                                <img
                                                                    src={toImageUrl(clothes.image_url)}
                                                                    alt={clothes.item}
                                                                    className="w-full h-full object-cover rounded"
                                                                />
                                                            ) : (
                                                                <div className="w-full h-full flex items-center justify-center text-zinc-300 text-xs">
                                                                    无图
                                                                </div>
                                                            )}
                                                        </button>
                                                    ))}
                                                </div>
                                                <div className="mt-2 text-xs text-zinc-500">
                                                    {userClothes.clothes.map(c => c.item).join('、')}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <p className="text-sm text-zinc-400">无法加载用户详情</p>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Image Preview Modal */}
            {previewImage && (
                <div
                    className="fixed inset-0 z-[100] bg-black/80 flex items-center justify-center p-4"
                    onClick={() => setPreviewImage(null)}
                >
                    <button
                        className="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-white hover:bg-white/30"
                        onClick={() => setPreviewImage(null)}
                    >
                        <X size={20} />
                    </button>
                    <img
                        src={previewImage}
                        alt="Preview"
                        className="max-w-full max-h-full object-contain rounded-lg"
                        onClick={(e) => e.stopPropagation()}
                    />
                </div>
            )}
        </div>
    )
}