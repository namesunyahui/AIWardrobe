import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { API_BASE } from '../utils/api'
import { ArrowLeft, Users, Shirt, Sparkles, TrendingUp, Loader2 } from 'lucide-react'

export default function AdminStats() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { user, token } = useAuth()
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (user && token && (user.role === 'admin' || user.role === 'superadmin')) {
            fetchStats()
        } else if (user && token) {
            navigate('/')
        }
    }, [user, token])

    const fetchStats = async () => {
        setLoading(true)
        try {
            const response = await fetch(`${API_BASE}/admin/stats`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setStats(data)
            }
        } catch (error) {
            console.error('Failed to fetch stats:', error)
        } finally {
            setLoading(false)
        }
    }

    const StatCard = ({ icon: Icon, label, value, color }) => (
        <div className="card p-4">
            <div className="flex items-center gap-3">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
                    <Icon size={24} className="text-white" />
                </div>
                <div>
                    <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">{value ?? '--'}</p>
                    <p className="text-xs text-zinc-500">{label}</p>
                </div>
            </div>
        </div>
    )

    if (loading) {
        return (
            <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-accent animate-spin" />
            </div>
        )
    }

    // 解析后端返回的数据
    const totalUsers = stats?.users?.total ?? 0
    const activeUsers = stats?.users?.active ?? 0
    const totalClothes = stats?.clothes?.total ?? 0
    const totalRecommendations = stats?.recommendations?.total ?? 0
    const categoryDistribution = stats?.clothes?.by_category ?? {}

    const getCategoryLabel = (category) => {
        const labels = {
            top: '上衣',
            bottom: '下装',
            shoes: '鞋子',
            accessory: '配饰'
        }
        return labels[category] || category
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
                <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                    {t('admin.stats')}
                </h1>
            </header>

            {/* Stats Grid */}
            <div className="px-4 space-y-4 pb-8">
                {/* Overview */}
                <div className="grid grid-cols-2 gap-3">
                    <StatCard
                        icon={Users}
                        label="总用户数"
                        value={totalUsers}
                        color="bg-blue-500"
                    />
                    <StatCard
                        icon={Shirt}
                        label="服装物品"
                        value={totalClothes}
                        color="bg-green-500"
                    />
                    <StatCard
                        icon={Sparkles}
                        label="推荐次数"
                        value={totalRecommendations}
                        color="bg-purple-500"
                    />
                    <StatCard
                        icon={TrendingUp}
                        label="活跃用户"
                        value={activeUsers}
                        color="bg-orange-500"
                    />
                </div>

                {/* Category Distribution */}
                {Object.keys(categoryDistribution).length > 0 && (
                    <div className="card p-4">
                        <h3 className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-3">
                            服装分类统计
                        </h3>
                        <div className="space-y-2">
                            {Object.entries(categoryDistribution).map(([category, count]) => (
                                <div key={category} className="flex items-center justify-between">
                                    <span className="text-sm text-zinc-600 dark:text-zinc-400">
                                        {getCategoryLabel(category)}
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <div className="w-24 h-2 bg-zinc-100 dark:bg-zinc-700 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-accent rounded-full"
                                                style={{
                                                    width: `${(count / (totalClothes || 1)) * 100}%`
                                                }}
                                            />
                                        </div>
                                        <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100 w-8 text-right">
                                            {count}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Today's Stats */}
                <div className="card p-4">
                    <h3 className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-3">
                        今日数据
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                            <p className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                                {stats?.users?.new_today ?? 0}
                            </p>
                            <p className="text-xs text-zinc-500">新用户</p>
                        </div>
                        <div className="text-center p-3 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                            <p className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                                {stats?.recommendations?.total_today ?? 0}
                            </p>
                            <p className="text-xs text-zinc-500">推荐次数</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}