import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowLeft, RefreshCw, Save, Tag, Shirt, Palette, Layers, CloudSun, FileText } from 'lucide-react'

import { API_BASE, toImageUrl } from '../utils/api'
import MultiSelect from '../components/MultiSelect'
import { useAuth } from '../contexts/AuthContext'

const STYLE_OPTIONS = ['casual', 'formal', 'sport', 'business', 'vintage', 'minimal', 'daily', 'commute']
const SEASON_OPTIONS = ['spring', 'summer', 'autumn', 'winter']

export default function ClothesDetail() {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const { id } = useParams()
    const { token } = useAuth()
    const [item, setItem] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [isEditing, setIsEditing] = useState(false)
    const [saving, setSaving] = useState(false)
    const [formData, setFormData] = useState({
        item: '',
        category: 'top',
        description: '',
        color_semantics: '',
        style_semantics: [],
        season_semantics: []
    })

    useEffect(() => {
        fetchClothesDetail()
    }, [id])

    const fetchClothesDetail = async () => {
        setLoading(true)
        setError('')
        try {
            const response = await fetch(`${API_BASE}/clothes/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (!response.ok) {
                throw new Error(response.status === 404 ? 'NOT_FOUND' : 'FETCH_FAILED')
            }
            const data = await response.json()
            setItem(data)
            setFormData({
                item: data.item,
                category: data.category,
                description: data.description || '',
                color_semantics: data.color_semantics || '',
                style_semantics: data.style_semantics || [],
                season_semantics: data.season_semantics || []
            })
        } catch (err) {
            setItem(null)
            setError(err.message || 'FETCH_FAILED')
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleMultiSelectChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleSave = async () => {
        setSaving(true)
        try {
            const payload = {
                ...formData,
                image_filename: item.image_url.split('/').pop()
            }
            const response = await fetch(`${API_BASE}/clothes/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            })
            if (response.ok) {
                const event = new CustomEvent('show-toast', {
                    detail: { type: 'success', message: t('entry.saveSuccess') }
                })
                window.dispatchEvent(event)
                setIsEditing(false)
                fetchClothesDetail()
            } else {
                throw new Error('Save failed')
            }
        } catch (error) {
            const event = new CustomEvent('show-toast', {
                detail: { type: 'error', message: t('entry.saveFailed') }
            })
            window.dispatchEvent(event)
        } finally {
            setSaving(false)
        }
    }

    const startEdit = () => {
        setFormData({
            item: item.item,
            category: item.category,
            description: item.description || '',
            color_semantics: item.color_semantics || '',
            style_semantics: item.style_semantics || [],
            season_semantics: item.season_semantics || []
        })
        setIsEditing(true)
    }

    const renderTags = (values) => {
        if (!Array.isArray(values) || values.length === 0) {
            return <span className="text-sm text-zinc-400">{t('clothesDetail.empty')}</span>
        }
        return (
            <div className="flex flex-wrap gap-2">
                {values.map(value => (
                    <span key={value} className="px-2 py-1 text-xs rounded-md bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300">
                        {value}
                    </span>
                ))}
            </div>
        )
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-[var(--bg-primary)] flex flex-col items-center justify-center">
                <div className="w-10 h-10 border-4 border-zinc-200 dark:border-zinc-700 border-t-accent rounded-full animate-spin"></div>
                <p className="mt-4 text-sm text-zinc-500">{t('clothesDetail.loading')}</p>
            </div>
        )
    }

    if (!item || error) {
        return (
            <div className="min-h-screen bg-[var(--bg-primary)] p-4">
                <header className="glass-header px-4 py-4 -mx-4">
                    <button className="btn-icon" onClick={() => navigate('/wardrobe')}>
                        <ArrowLeft size={22} />
                    </button>
                </header>
                <div className="mt-8 card p-6 text-center space-y-4">
                    <p className="text-sm text-zinc-500">
                        {error === 'NOT_FOUND' ? t('clothesDetail.notFound') : t('clothesDetail.loadFailed')}
                    </p>
                    <button className="btn-secondary mx-auto" onClick={fetchClothesDetail}>
                        <RefreshCw size={16} />
                        {t('clothesDetail.retry')}
                    </button>
                </div>
            </div>
        )
    }

    if (isEditing) {
        return (
            <div className="min-h-screen bg-[var(--bg-primary)] flex flex-col animate-fade-in">
                <header className="glass-header px-4 py-4 flex items-center justify-between sticky top-0">
                    <button className="btn-icon" onClick={() => setIsEditing(false)}>
                        <ArrowLeft size={24} />
                    </button>
                    <h2 className="text-xl font-serif font-semibold text-[var(--text-primary)]">{t('entry.editTitle')}</h2>
                    <button
                        className={`text-sm font-medium px-4 py-2 rounded-lg flex items-center gap-1.5 transition-colors ${saving ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400' : 'bg-accent text-white hover:bg-blue-700'}`}
                        onClick={handleSave}
                        disabled={saving}
                    >
                        {saving ? <span className="w-4 h-4 border-2 border-zinc-300 border-t-zinc-500 rounded-full animate-spin"></span> : <Save size={18} />}
                        <span>{saving ? t('entry.saving') : t('entry.save')}</span>
                    </button>
                </header>

                <div className="flex-1 overflow-y-auto pb-24 px-4 space-y-6">
                    <div className="w-full aspect-square bg-zinc-100 dark:bg-zinc-800 rounded-2xl overflow-hidden shadow-sm border border-zinc-200 dark:border-zinc-700 p-2 flex items-center justify-center mt-4">
                        <img
                            src={toImageUrl(item.image_url)}
                            alt="Preview"
                            className="w-full h-full object-contain"
                        />
                    </div>

                    <div className="space-y-6">
                        <section className="bg-white dark:bg-zinc-900 p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
                            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 mb-2">{t('entry.basicInfo')}</h3>

                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                                    <Tag className="text-accent" size={16} /> {t('entry.name')}
                                </label>
                                <input
                                    type="text"
                                    name="item"
                                    value={formData.item}
                                    onChange={handleChange}
                                    placeholder={t('entry.namePlaceholder')}
                                    className="input-field"
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                                    <Shirt className="text-accent" size={16} /> {t('entry.category')}
                                </label>
                                <select
                                    name="category"
                                    value={formData.category}
                                    onChange={handleChange}
                                    className="input-field appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M5%208l5%205%205-5%22%20stroke%3D%22%239ca3af%22%20stroke-width%3D%222%22%20fill%3D%22none%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')] bg-[length:20px_20px] bg-[right_10px_center] bg-no-repeat pr-10"
                                >
                                    <option value="top">{t('entry.categoryTop')}</option>
                                    <option value="bottom">{t('entry.categoryBottom')}</option>
                                    <option value="shoes">{t('entry.categoryShoes')}</option>
                                    <option value="accessory">{t('entry.categoryAccessory')}</option>
                                    <option value="uncategorized">{t('entry.categoryUncategorized')}</option>
                                </select>
                            </div>
                        </section>

                        <section className="bg-white dark:bg-zinc-900 p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
                            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 mb-2">{t('entry.features')}</h3>

                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                                    <Palette className="text-accent" size={16} /> {t('entry.color')}
                                </label>
                                <input
                                    type="text"
                                    name="color_semantics"
                                    value={formData.color_semantics}
                                    onChange={handleChange}
                                    placeholder={t('entry.colorPlaceholder')}
                                    className="input-field"
                                />
                            </div>

                            <MultiSelect
                                label={t('entry.style')}
                                icon={Layers}
                                name="style_semantics"
                                value={formData.style_semantics}
                                options={STYLE_OPTIONS}
                                onChange={handleMultiSelectChange}
                                placeholder={t('entry.stylePlaceholder')}
                                translateKey="filter."
                            />

                            <MultiSelect
                                label={t('entry.season')}
                                icon={CloudSun}
                                name="season_semantics"
                                value={formData.season_semantics}
                                options={SEASON_OPTIONS}
                                onChange={handleMultiSelectChange}
                                placeholder={t('entry.seasonPlaceholder')}
                                translateKey="filter."
                            />
                        </section>

                        <section className="bg-white dark:bg-zinc-900 p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm space-y-4">
                            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 flex items-center gap-1.5 mb-2">
                                <FileText className="text-accent" size={16} /> {t('entry.description')}
                            </h3>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                rows={4}
                                placeholder={t('entry.descriptionPlaceholder')}
                                className="input-field resize-none"
                            />
                        </section>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="bg-[var(--bg-primary)] pb-8 animate-fade-in">
            <header className="glass-header px-4 py-4 flex items-center justify-between sticky top-0">
                <div className="flex items-center gap-2">
                    <button className="btn-icon" onClick={() => navigate('/wardrobe')}>
                        <ArrowLeft size={22} />
                    </button>
                    <h1 className="text-xl font-serif font-semibold text-[var(--text-primary)]">{t('clothesDetail.title')}</h1>
                </div>
                <button
                    className="text-sm font-medium px-4 py-2 rounded-lg bg-accent text-white hover:bg-blue-700 flex items-center gap-1.5 transition-colors"
                    onClick={startEdit}
                >
                    <Tag size={16} />
                    {t('entry.edit')}
                </button>
            </header>

            <div className="p-4 space-y-4">
                <article className="card overflow-hidden">
                    <div className="aspect-square bg-zinc-100 dark:bg-zinc-800 p-2 flex items-center justify-center">
                        <img
                            src={toImageUrl(item.image_url)}
                            alt={item.item}
                            className="w-full h-full object-contain"
                        />
                    </div>
                    <div className="p-4 border-t border-zinc-100 dark:border-zinc-800">
                        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">{item.item}</h2>
                        <p className="text-sm text-zinc-500 mt-1">{item.category}</p>
                    </div>
                </article>

                <section className="card p-4 space-y-4">
                    <div>
                        <h3 className="text-sm font-medium text-zinc-500">{t('clothesDetail.description')}</h3>
                        <p className="mt-1 text-sm text-zinc-800 dark:text-zinc-200">{item.description || t('clothesDetail.empty')}</p>
                    </div>

                    <div>
                        <h3 className="text-sm font-medium text-zinc-500">{t('clothesDetail.color')}</h3>
                        <p className="mt-1 text-sm text-zinc-800 dark:text-zinc-200">{item.color_semantics || t('clothesDetail.empty')}</p>
                    </div>

                    <div>
                        <h3 className="text-sm font-medium text-zinc-500">{t('clothesDetail.style')}</h3>
                        <div className="mt-1">{renderTags(item.style_semantics)}</div>
                    </div>

                    <div>
                        <h3 className="text-sm font-medium text-zinc-500">{t('clothesDetail.season')}</h3>
                        <div className="mt-1">{renderTags(item.season_semantics)}</div>
                    </div>
                </section>
            </div>
        </div>
    )
}
