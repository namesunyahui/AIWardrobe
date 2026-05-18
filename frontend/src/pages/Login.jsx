import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Eye, EyeOff, LogIn } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { login } = useAuth()

    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            await login(username, password)
            navigate('/')
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-[var(--bg-primary)] flex flex-col">
            {/* Header */}
            <header className="px-4 pt-6 pb-4 flex items-center justify-between">
                <button
                    className="w-10 h-10 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white/90 dark:bg-zinc-900/90 flex items-center justify-center text-zinc-600 dark:text-zinc-300 hover:text-accent transition-colors"
                    onClick={() => navigate(-1)}
                >
                    ←
                </button>
            </header>

            <main className="flex-1 px-4 py-4">
                {/* Logo */}
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                        AIWardrobe
                    </h1>
                    <p className="text-sm text-zinc-500 mt-1">{t('auth.login')}</p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* 用户名/邮箱 */}
                    <div>
                        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            {t('auth.username')}
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="input-field mt-1.5"
                            placeholder={t('auth.username')}
                            required
                        />
                    </div>

                    {/* 密码 */}
                    <div>
                        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            {t('auth.password')}
                        </label>
                        <div className="relative mt-1.5">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="input-field pr-10"
                                placeholder={t('auth.password')}
                                required
                            />
                            <button
                                type="button"
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                    </div>

                    {/* 错误提示 */}
                    {error && (
                        <p className="text-sm text-red-500">{error}</p>
                    )}

                    {/* 登录按钮 */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full mt-6"
                    >
                        {loading ? (
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : (
                            <>
                                <LogIn size={18} />
                                {t('auth.login')}
                            </>
                        )}
                    </button>
                </form>

                {/* 注册链接 */}
                <p className="text-center text-sm text-zinc-500 mt-6">
                    {t('auth.noAccount')}{' '}
                    <Link to="/register" className="text-accent hover:underline">
                        {t('auth.register')}
                    </Link>
                </p>
            </main>
        </div>
    )
}