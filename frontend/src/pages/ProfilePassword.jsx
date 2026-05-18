import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { ArrowLeft, Lock, Loader2, Eye, EyeOff } from 'lucide-react'

export default function ProfilePassword() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { changePassword } = useAuth()
    const [oldPassword, setOldPassword] = useState('')
    const [newPassword, setNewPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)
    const [showOld, setShowOld] = useState(false)
    const [showNew, setShowNew] = useState(false)
    const [showConfirm, setShowConfirm] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setSuccess(false)

        if (newPassword !== confirmPassword) {
            setError('新密码与确认密码不一致')
            return
        }

        if (newPassword.length < 6) {
            setError('密码长度至少为 6 位')
            return
        }

        setLoading(true)
        try {
            await changePassword(oldPassword, newPassword)
            setSuccess(true)
            setTimeout(() => {
                navigate('/profile')
            }, 2000)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const PasswordInput = ({ value, onChange, placeholder, show, onToggle }) => (
        <div className="relative">
            <input
                type={show ? 'text' : 'password'}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                className="w-full px-4 py-2.5 pr-10 rounded-xl bg-zinc-100 dark:bg-zinc-800 border-none text-sm"
            />
            <button
                type="button"
                onClick={onToggle}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400"
            >
                {show ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
        </div>
    )

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
                    {t('profile.changePassword')}
                </h1>
            </header>

            <form onSubmit={handleSubmit} className="px-4 space-y-4 pb-8">
                <div className="card p-4">
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                        当前密码
                    </label>
                    <PasswordInput
                        value={oldPassword}
                        onChange={setOldPassword}
                        placeholder="请输入当前密码"
                        show={showOld}
                        onToggle={() => setShowOld(!showOld)}
                    />
                </div>

                <div className="card p-4">
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                        新密码
                    </label>
                    <PasswordInput
                        value={newPassword}
                        onChange={setNewPassword}
                        placeholder="请输入新密码（至少6位）"
                        show={showNew}
                        onToggle={() => setShowNew(!showNew)}
                    />
                </div>

                <div className="card p-4">
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                        确认新密码
                    </label>
                    <PasswordInput
                        value={confirmPassword}
                        onChange={setConfirmPassword}
                        placeholder="请再次输入新密码"
                        show={showConfirm}
                        onToggle={() => setShowConfirm(!showConfirm)}
                    />
                </div>

                {error && (
                    <p className="text-sm text-red-500 px-2">{error}</p>
                )}

                {success && (
                    <p className="text-sm text-green-500 px-2">密码修改成功，即将返回...</p>
                )}

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full btn-primary py-3 flex items-center justify-center gap-2"
                >
                    {loading ? (
                        <Loader2 size={18} className="animate-spin" />
                    ) : (
                        <Lock size={18} />
                    )}
                    <span>修改密码</span>
                </button>
            </form>
        </div>
    )
}