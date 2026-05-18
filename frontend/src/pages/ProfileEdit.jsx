import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { ArrowLeft, User, Loader2 } from 'lucide-react'

export default function ProfileEdit() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { user, updateProfile, token } = useAuth()
    const [nickname, setNickname] = useState(user?.nickname || '')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            await updateProfile({ nickname })
            navigate('/profile')
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-[var(--bg-primary)]">
            <header className="px-4 pt-6 pb-4 flex items-center gap-3">
                <button
                    onClick={() => navigate('/profile')}
                    className="w-10 h-10 rounded-xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-600 dark:text-zinc-300"
                >
                    <ArrowLeft size={20} />
                </button>
                <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                    {t('profile.personalInfo')}
                </h1>
            </header>

            <form onSubmit={handleSubmit} className="px-4 space-y-4 pb-8">
                <div className="card p-4">
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                        {t('auth.username')}
                    </label>
                    <input
                        type="text"
                        value={user?.username || ''}
                        disabled
                        className="w-full px-4 py-2.5 rounded-xl bg-zinc-100 dark:bg-zinc-800 border-none text-sm text-zinc-500"
                    />
                    <p className="text-xs text-zinc-400 mt-1">用户名不可修改</p>
                </div>

                <div className="card p-4">
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                        昵称
                    </label>
                    <input
                        type="text"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
                        placeholder="请输入昵称"
                        className="w-full px-4 py-2.5 rounded-xl bg-zinc-100 dark:bg-zinc-800 border-none text-sm"
                    />
                </div>

                <div className="card p-4">
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                        邮箱
                    </label>
                    <input
                        type="email"
                        value={user?.email || ''}
                        disabled
                        className="w-full px-4 py-2.5 rounded-xl bg-zinc-100 dark:bg-zinc-800 border-none text-sm text-zinc-500"
                    />
                </div>

                {error && (
                    <p className="text-sm text-red-500 px-2">{error}</p>
                )}

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full btn-primary py-3 flex items-center justify-center gap-2"
                >
                    {loading ? (
                        <Loader2 size={18} className="animate-spin" />
                    ) : (
                        <User size={18} />
                    )}
                    <span>保存</span>
                </button>
            </form>
        </div>
    )
}