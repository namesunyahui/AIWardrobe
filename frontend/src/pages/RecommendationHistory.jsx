import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { Heart, ChevronLeft, Calendar, MapPin, RotateCcw } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export default function RecommendationHistory() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { token, user } = useAuth()
    const [history, setHistory] = useState([])
    const [loading, setLoading] = useState(true)

    console.log('[History] Current user:', user, 'Token exists:', !!token)

    useEffect(() => {
        fetchHistory()
    }, [token])

    const fetchHistory = async () => {
        try {
            const response = await fetch(`${API_BASE}/recommendations/history?t=${Date.now()}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            console.log('[History] Response status:', response.status)
            if (response.ok) {
                const data = await response.json()
                console.log('[History] Raw data items:', JSON.stringify(data.items?.slice(0, 2)))
                const items = (data.items || []).map(item => ({
                    ...item,
                    is_favorited: Boolean(item.is_favorited)
                }))
                console.log('[History] Processed items:', items.slice(0, 2).map(i => ({ id: i.id, is_favorited: i.is_favorited })))
                setHistory(items)
            }
        } catch (error) {
            console.error('Failed to fetch history:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleFavorite = async (recordId, isFavorited) => {
        try {
            if (isFavorited) {
                await fetch(`${API_BASE}/recommendations/${recordId}/favorite`, {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${token}` }
                })
            } else {
                await fetch(`${API_BASE}/recommendations/${recordId}/favorite`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${token}` }
                })
            }
        } catch (error) {
            console.error('Failed to toggle favorite:', error)
        }
        fetchHistory()
    }

    const handleRercommend = (item) => {
        // 使用历史记录中的目标重新推荐
        const goal = item.goal_raw || ''
        const location = item.weather_location || ''
        navigate(`/recommendation?location=${encodeURIComponent(location)}&goal=${encodeURIComponent(goal)}`)
    }

    return (
        <div className="min-h-screen bg-[var(--bg-primary)]">
            {/* Header */}
            <header className="px-4 pt-6 pb-4 flex items-center gap-3">
                <button
                    onClick={() => navigate(-1)}
                    className="w-10 h-10 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white/90 dark:bg-zinc-900/90 flex items-center justify-center"
                >
                    <ChevronLeft size={20} />
                </button>
                <h1 className="text-xl font-bold">{t('profile.history')}</h1>
            </header>

            {/* Content */}
            <div className="px-4">
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <div className="w-8 h-8 border-4 border-zinc-200 dark:border-zinc-700 border-t-accent rounded-full animate-spin"></div>
                    </div>
                ) : history.length === 0 ? (
                    <div className="text-center py-20 text-zinc-500">
                        <p>{t('profile.history')}: 暂无记录</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {history.map((item) => (
                            <div
                                key={item.id}
                                className="card p-4"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1" onClick={() => navigate(`/recommendation/${item.id}`)}>
                                        <div className="flex items-center gap-2 text-sm text-zinc-500 mb-2">
                                            <Calendar size={14} />
                                            <span>{item.record_date}</span>
                                            {item.weather_location && (
                                                <>
                                                    <MapPin size={14} />
                                                    <span>{item.weather_location}</span>
                                                </>
                                            )}
                                        </div>
                                        <p className="text-sm text-zinc-700 dark:text-zinc-300 line-clamp-2">
                                            {item.recommendation_text}
                                        </p>
                                        {item.goal_raw && (
                                            <p className="text-xs text-accent mt-2">
                                                目标: {item.goal_raw}
                                            </p>
                                        )}
                                    </div>
                                    <div className="flex flex-col gap-1">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleRercommend(item)
                                            }}
                                            className="p-2 text-zinc-400 hover:text-accent"
                                            title={t('recommendation.regenerate')}
                                        >
                                            <RotateCcw size={18} />
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleFavorite(item.id, item.is_favorited)
                                            }}
                                            className="p-2 text-zinc-400 hover:text-red-500"
                                        >
                                            <Heart
                                                size={18}
                                                className={item.is_favorited ? "fill-red-500 text-red-500" : ""}
                                            />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}