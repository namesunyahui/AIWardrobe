import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { Heart, ChevronLeft, Calendar, MapPin } from 'lucide-react'
import { showConfirm } from '../components/ConfirmDialog'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export default function Favorites() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { token } = useAuth()
    const [favorites, setFavorites] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchFavorites()
    }, [token])

    const fetchFavorites = async () => {
        try {
            const response = await fetch(`${API_BASE}/recommendations/favorites`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setFavorites(data.items || [])
            }
        } catch (error) {
            console.error('Failed to fetch favorites:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleRemoveFavorite = async (e, recordId) => {
        e.stopPropagation()

        const confirmed = await showConfirm({
            title: t('profile.removeFavorite'),
            message: t('profile.removeFavoriteConfirm') || '确定要取消收藏吗？',
            confirmText: t('confirm'),
            cancelText: t('cancel'),
            type: 'danger'
        })

        if (!confirmed) return

        try {
            await fetch(`${API_BASE}/recommendations/${recordId}/favorite`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` }
            })
            fetchFavorites()
        } catch (error) {
            console.error('Failed to remove favorite:', error)
        }
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
                <h1 className="text-xl font-bold">{t('profile.favorites')}</h1>
            </header>

            {/* Content */}
            <div className="px-4">
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <div className="w-8 h-8 border-4 border-zinc-200 dark:border-zinc-700 border-t-accent rounded-full animate-spin"></div>
                    </div>
                ) : favorites.length === 0 ? (
                    <div className="text-center py-20 text-zinc-500">
                        <Heart size={48} className="mx-auto mb-4 text-zinc-300" />
                        <p>{t('profile.favorites')}: 暂无收藏</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {favorites.map((item) => (
                            <div
                                key={item.id}
                                className="card p-4"
                                onClick={() => navigate(`/recommendation/${item.id}`)}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
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
                                        <p className="text-xs text-zinc-400 mt-2">
                                            收藏于: {new Date(item.favorited_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <button
                                        onClick={(e) => handleRemoveFavorite(e, item.id)}
                                        className="p-2 text-red-500"
                                    >
                                        <Heart size={20} className="fill-current" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}