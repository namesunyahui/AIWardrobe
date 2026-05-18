import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Eye, EyeOff, UserPlus } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Register() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { register } = useAuth()

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        nickname: ''
    })
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')

        // 验证密码
        if (formData.password !== formData.confirmPassword) {
            setError('两次输入的密码不一致')
            return
        }

        if (formData.password.length < 6) {
            setError('密码至少6位')
            return
        }

        setLoading(true)

        try {
            await register({
                username: formData.username,
                email: formData.email,
                password: formData.password,
                nickname: formData.nickname || formData.username
            })
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
                        {t('auth.register')}
                    </h1>
                    <p className="text-sm text-zinc-500 mt-1">创建您的账号</p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* 用户名 */}
                    <div>
                        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            {t('auth.username')} <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            className="input-field mt-1.5"
                            placeholder="3-20位字母数字下划线"
                            required
                            minLength={3}
                            maxLength={20}
                            pattern="^\w+$"
                        />
                    </div>

                    {/* 邮箱 */}
                    <div>
                        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            {t('auth.email')} <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className="input-field mt-1.5"
                            placeholder="example@email.com"
                            required
                        />
                    </div>

                    {/* 密码 */}
                    <div>
                        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            {t('auth.password')} <span className="text-red-500">*</span>
                        </label>
                        <div className="relative mt-1.5">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                className="input-field pr-10"
                                placeholder="至少6位"
                                required
                                minLength={6}
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

                    {/* 确认密码 */}
                    <div>
                        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            {t('auth.confirmPassword')} <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            className="input-field mt-1.5"
                            placeholder="再次输入密码"
                            required
                        />
                    </div>

                    {/* 昵称 */}
                    <div>
                        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            {t('auth.nickname')} <span className="text-zinc-400">(可选)</span>
                        </label>
                        <input
                            type="text"
                            name="nickname"
                            value={formData.nickname}
                            onChange={handleChange}
                            className="input-field mt-1.5"
                            placeholder="默认使用用户名"
                        />
                    </div>

                    {/* 错误提示 */}
                    {error && (
                        <p className="text-sm text-red-500">{error}</p>
                    )}

                    {/* 注册按钮 */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full mt-6"
                    >
                        {loading ? (
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : (
                            <>
                                <UserPlus size={18} />
                                {t('auth.register')}
                            </>
                        )}
                    </button>
                </form>

                {/* 登录链接 */}
                <p className="text-center text-sm text-zinc-500 mt-6">
                    {t('auth.hasAccount')}{' '}
                    <Link to="/login" className="text-accent hover:underline">
                        {t('auth.login')}
                    </Link>
                </p>
            </main>
        </div>
    )
}