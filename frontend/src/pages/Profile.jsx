import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { User, Settings, History, Heart, Lock, Trash2, LogOut, ChevronRight } from 'lucide-react'

function MenuItem({ icon: Icon, label, onClick, danger = false }) {
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

export default function Profile() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { user, logout } = useAuth()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <div className="min-h-screen bg-[var(--bg-primary)]">
            {/* Header */}
            <header className="px-4 pt-6 pb-4">
                <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                    {t('profile.title')}
                </h1>
            </header>

            {/* User Info */}
            <div className="px-4 pb-6">
                <div className="card p-4 flex items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center">
                        {user?.avatar_url ? (
                            <img src={user.avatar_url} alt="avatar" className="w-full h-full rounded-full object-cover" />
                        ) : (
                            <User size={32} className="text-zinc-400" />
                        )}
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                            {user?.nickname || user?.username}
                        </h2>
                        <p className="text-sm text-zinc-500">{user?.email}</p>
                    </div>
                </div>
            </div>

            {/* Menu */}
            <div className="px-4 space-y-2">
                <MenuItem
                    icon={User}
                    label={t('profile.personalInfo')}
                    onClick={() => navigate('/profile/edit')}
                />
                <MenuItem
                    icon={Settings}
                    label={t('profile.settings')}
                    onClick={() => navigate('/settings')}
                />
                <MenuItem
                    icon={History}
                    label={t('profile.history')}
                    onClick={() => navigate('/profile/history')}
                />
                <MenuItem
                    icon={Heart}
                    label={t('profile.favorites')}
                    onClick={() => navigate('/profile/favorites')}
                />
                <MenuItem
                    icon={Lock}
                    label={t('profile.changePassword')}
                    onClick={() => navigate('/profile/password')}
                />
            </div>

            {/* Admin Section */}
            {user?.role === 'admin' || user?.role === 'superadmin' ? (
                <div className="px-4 mt-6">
                    <h3 className="text-sm font-medium text-zinc-500 px-4 mb-2">管理员</h3>
                    <div className="space-y-2">
                        <MenuItem
                            icon={User}
                            label="用户管理"
                            onClick={() => navigate('/admin/users')}
                        />
                        <MenuItem
                            icon={Settings}
                            label="数据统计"
                            onClick={() => navigate('/admin/stats')}
                        />
                    </div>
                </div>
            ) : null}

            {/* Logout */}
            <div className="px-4 mt-6">
                <MenuItem
                    icon={LogOut}
                    label={t('auth.logout')}
                    onClick={handleLogout}
                    danger
                />
            </div>

            {/* Version */}
            <div className="px-4 mt-8 pb-8">
                <p className="text-center text-xs text-zinc-400">
                    {t('profile.version')} v1.0.0
                </p>
            </div>
        </div>
    )
}